#!/usr/bin/env python3

import os
import kubernetes
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import re
import sys
import pandas as pd
from vllmLogParser import *


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

    # def text_to_csv(text_file_path, csv_file_path, delimiter='\t'):
    #     try:
    #        df = pd.read_csv(text_file_path, sep=delimiter)
    #        df.to_csv(csv_file_path, index=False)
    #        print(f"Successfully converted '{text_file_path}' to '{csv_file_path}'")
    #     except FileNotFoundError:
    #        print(f"Error: Text file '{text_file_path}' not found.")
    #     except Exception as e:
    #        print(f"An error occurred: {e}")

            
if __name__=="__main__": 

    kubeconfig = str(sys.argv[1]) # path to the kubeconfig file (e.g., "kscore-config)
    k8s_context = str(sys.argv[2]) # name of the k8s cluster context (e.g., 'wec1')
    label_selector = str(sys.argv[3]) # vllm pod label selector (e.g, 'environment=test')
    namespace = str(sys.argv[4]) # vllm pod namespace (e.g., `vllm-test`)
    output_dir = str(sys.argv[5]) # path to the directory for the output files (e.g., $HOME/data/)

    c = Collector()
    pods = c.find_pod_by_label(label_selector, namespace)

    fout = open(output_dir + "/vllm-server-startup-latency.txt", "w")
    #fout.write("pod_name" + "\t" + "engine_init" + "\t" + "model_loading model_weight_GB" + "\t" + "before_torch_compile" + "\t" + "torch_compile"  + "\t" + "CUDA_graph" + "\t" + "API_readiness" + "\n")
    
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

                    print("Extracting API Server Init latency ...")
                    t7 = get_apiserver_init_time(temp_logs)
            else:
                print("Pod is not running or condition status is not 'ready': ", name)
                continue

            print('--------------------------------------')
            fout.write(name + "\t" + str(t1) + "\t" + str(t2) + "\t" + str(t3) + "\t" + str(t4) + "\t" + str(t5) + "\t" + str(t6) + "\t" + str(t7) + "\n")
            fout.flush()
        fout.close()
    else:
        print("No pods found with label: ", label_selector)
    
