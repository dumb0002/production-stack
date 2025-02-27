#!/usr/bin/env python3

import os
import kubernetes
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import re
import sys
import argparse
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


    def read_pod_logs(self, pod_name, namespace="default", container=None):
        try:
            logs = self.core_v1_api.read_namespaced_pod_log(name=pod_name, namespace=namespace, container=container)
            return logs

        except client.exceptions.ApiException as e:
            print(f"Error reading logs: {e}")
            return None


    def find_pod_by_label(self, label_selector, namespace="default"):
        pods = self.core_v1_api.list_namespaced_pod(namespace, label_selector=label_selector).items
        return pods

    def get_pod_readiness_time(self, pod):
        for cond in pod.status.conditions:
           if cond.type == "Ready":
              t = cond.last_transition_time
              return t

    def get_container_running_time(self, pod, container=None):
        t = 0
        if container != None:
           for c in pod.status.container_statuses:
               if c.name == container:
                  t = c.state.running.started_at
        else:
            t = (pod.status.container_statuses[0]).state.running.started_at
        return t

            
if __name__=="__main__": 

    parser = argparse.ArgumentParser()
    parser.add_argument("-cfg", "--config", default="~/.kube/config", help="kubeconfig for the target cluster")
    parser.add_argument("-ctx", "--context", default=None, help="name of k8s cluster context")
    parser.add_argument("-c", "--containername", default=None, help="name of container in VLLM pod")
    parser.add_argument("-l", "--label", help="vllm pod label selector (e.g, 'environment=test')")
    parser.add_argument("-n", "--namespace", default="default", help="vllm pod namespace")
    parser.add_argument("-m", "--model", default="mymodel", help="helpful description of model run by VLLM")
    parser.add_argument("-o", "--output", default="vllm-log-dir", help="path to directory for output files (must exist)")
    args = parser.parse_args()
    kubeconfig=args.config
    k8s_context=args.context
    label_selector=args.label
    namespace=args.namespace
    model_name=args.model
    output_dir=args.output
    containername=args.containername
    
    c = Collector()
    pods = c.find_pod_by_label(label_selector, namespace)

    fout = open(output_dir + "/" + model_name + "_vllm-server-startup-latency.txt", "w")

    if pods:
        for pod in pods:
            name = pod.metadata.name
           
            # Check if the pod is running and condition status is 'ready'
            if pod.status.phase == "Running" and any(cond.status == "True" for cond in pod.status.conditions if cond.type == "Ready"):
                print("Pod is running and condition status is 'ready': ", name)

                pod_logs = c.read_pod_logs(name, namespace, containername) 
                if pod_logs:
                    # save the logs into a file
                    f = open(output_dir + "/" + name + "-log.txt", "w") 
                    f.write(pod_logs)
                    f.close()

                    # Compute the breakdow of the e2e startup latency for the VLLM server  
                    logs = pod_logs.splitlines()

                    print("Computing Startup latency ...")
                    # Extracting container running time
                    d_0a = c.get_container_running_time(pod, containername)

                    # Extracting vllm_first_log_message_timestamp
                    d_0b = get_log_first_timestamp(logs)

                    # Compute process startup
                    t0 = (d_0b - d_0a).seconds

                    print("Extracting engine initalization latency ...")
                    t1 = get_engine_init_time(logs)

                    print("Extracting Model Weight Download latency ...")
                    t2 = get_model_weight_download_time(logs)

                    print("Extracting Model Weight Loading latency ...")
                    t3 = get_model_weight_load_time(logs)

                    print("Extracting Model Weight Loading GB latency ...")
                    t4 = get_model_weight_gb(logs)

                    print("Extracting time before torch.compile...")
                    tx = get_before_torch_compile_time(logs)

                    print("Extracting torch.compile time ...")
                    t6 = get_torch_compile_time(logs)
                    t5 = round(float(tx) - float(t6), 3) # computing time before torch.compile

                    print("Extracting CUDA graph instantiation latency ...")
                    t7 = get_cuda_graph_time(logs)

                    print("Computing API Server Init latency ...")
                    # Extracting init engine time
                    d_8a = get_apiserver_init_time(logs)
                    # Extracting pod readiness time
                    d_8b = c.get_pod_readiness_time(pod)
                    # Compute init latency
                    t8 = (d_8b - d_8a).seconds
            else:
                print("Pod is not running or condition status is not 'ready': ", name)
                continue

            print('--------------------------------------')
            fout.write(name + "\t" + str(t0) +  "\t" + str(t1) + "\t" + str(t2) + "\t" + str(t3) + "\t" + str(t4) + "\t" + str(t5) + "\t" + str(t6) + "\t" + str(t7) + "\t" + str(t8) + "\n")
            fout.flush()
        fout.close()
    else:
        print("No pods found with label: ", label_selector)
    
