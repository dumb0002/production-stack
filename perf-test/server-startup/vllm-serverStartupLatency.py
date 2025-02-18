#!/usr/bin/env python3

import os
import kubernetes
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import re
import sys
from parserHelper import *


class Collector():
    def __init__(self, kubeconfig=None, k8s_context=None):
        self.kubeconfig = kubeconfig
        self.context = k8s_context
        self.core_v1_api, self.app_v1_api, self.custom_objects_api = self.load_kubeconfig(kubeconfig, k8s_context)

    def load_kubeconfig(self, kubeconfig, context):

        if kubeconfig != None and context == None:
            config.load_kube_config(config_file=kubeconfigg)
        elif kubeconfig != None and context != None:
            config.load_kube_config(config_file=kubeconfig, context=context)
        else:
            config.load_kube_config()

        api_client = kubernetes.client.ApiClient()
        core_v1_api = kubernetes.client.CoreV1Api(api_client)
        app_v1_api  = kubernetes.client.AppsV1Api(api_client)
        custom_objects_api = kubernetes.client.CustomObjectsApi(api_client)

        return core_v1_api, app_v1_api, custom_objects_api


    def read_pod_logs(self, pod_name, namespace="default"):
        try:
            logs = self.core_v1_api.read_namespaced_pod_log(name=pod_name, namespace=namespace)
            return logs

        except client.exceptions.ApiException as e:
            print(f"Error reading logs: {e}")
            return None


    def find_pod_by_label(self, label_selector, namespace="default"):
        pods = self.core_v1_api.list_namespaced_pod(namespace, label_selector=label_selector).items
        return pods

    def get_pod_readiness_time(self, pod_name, namespace="default"):
        for cond in pod.status.conditions:
           if cond.type == "Ready":
              t = cond.last_transition_time
              return t

    def get_container_running_time(self, pod_name, namespace="default"):
        t = (pod.status.container_statuses[0]).state.running.started_at
        print(t)
        return t

            
if __name__=="__main__": 

    kubeconfig = str(sys.argv[1]) # path to the kubeconfig file (e.g., "kscore-config)
    k8s_context = str(sys.argv[2]) # name of the k8s cluster context (e.g., 'wec1')
    label_selector = str(sys.argv[3]) # vllm pod label selector (e.g, 'environment=test')
    namespace = str(sys.argv[4]) # vllm pod namespace (e.g., `vllm-test`)
    model_name = str(sys.argv[5])
    output_dir = str(sys.argv[6]) # path to the directory for the output files (e.g., $HOME/data/)

    c = Collector()
    pods = c.find_pod_by_label(label_selector, namespace)

    fout = open(output_dir + "/" + model_name + "_vllm-server-startup-latency.txt", "w")

    if pods:
        for pod in pods:
            name = pod.metadata.name
           
            # Check if the pod is running and condition status is 'ready'
            if pod.status.phase == "Running" and any(cond.status == "True" for cond in pod.status.conditions if cond.type == "Ready"):
                print("Pod is running and condition status is 'ready': ", name)

                pod_logs = c.read_pod_logs(name, namespace) 
                if pod_logs:
                    # save the logs into a file
                    f = open(output_dir + "/" + name + "-log.txt", "w") 
                    f.write(pod_logs)
                    f.close()

                    # Compute the breakdow of the e2e startup latency for the VLLM server  
                    temp_logs = pod_logs.splitlines()

                    print("Computing Startup latency ...")
                    # # Extracting container running time
                    # d_0a = c.get_pod_readiness_time(name, namespace)

                    # # Extracting vllm_first_log_message_timestamp
                    # d_0b = get_log_first_timestamp(temp_logs)

                    # Compute process startup
                    # t0 = (d_0b - d_0a).seconds
                    t0 = "None"

                    print("Extracting engine initalization latency ...")
                    t1 = get_engine_init_time(temp_logs)

                    print("Extracting Model Loading latency ...")
                    t2 = get_model_load_time(temp_logs)

                    print("Extracting Model Weight Loading GB latency ...")
                    t3 = get_model_weight_gb(temp_logs)

                    print("Extracting time before torch.compile...")
                    tx = get_before_torch_compile_time(temp_logs)

                    print("Extracting torch.compile time ...")
                    t5 = get_torch_compile_time(temp_logs)
                    t4 = round(float(tx) - float(t5), 3) # computing time before torch.compile

                    print("Extracting CUDA graph instantiation latency ...")
                    t6 = get_cuda_graph_time(temp_logs)

                    print("Computing API Server Init latency ...")
                    # Extracting init engine time
                    d_7a = get_apiserver_init_time(temp_logs)
                    # Extracting pod readiness time
                    d_7b = c.get_pod_readiness_time(name, namespace)
                    # Compute init latency
                    t7 = (d_7b - d_7a).seconds
            else:
                print("Pod is not running or condition status is not 'ready': ", name)
                continue

            print('--------------------------------------')
            fout.write(name + "\t" + str(t0) +  "\t" + str(t1) + "\t" + str(t2) + "\t" + str(t3) + "\t" + str(t4) + "\t" + str(t5) + "\t" + str(t6) + "\t" + str(t7) + "\n")
            fout.flush()
        fout.close()
    else:
        print("No pods found with label: ", label_selector)
    
