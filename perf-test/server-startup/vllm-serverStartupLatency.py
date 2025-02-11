#!/usr/bin/env python3

import os
import kubernetes
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import re
import sys
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


if __name__=="__main__": 

    kubeconfig = str(sys.argv[1]) # path to the kubeconfig file (e.g., "kscore-config)
    k8s_context = str(sys.argv[2]) # name of the k8s cluster context (e.g., 'wec1')
    label_selector = str(sys.argv[3]) # vllm pod label selector (e.g, 'environment=test')
    namespace = str(sys.argv[4]) # vllm pod namespace (e.g., `vllm-test`)
    output_dir = str(sys.argv[5]) # path to the directory for the output files (e.g., $HOME/data/)

    c = Collector()
    pods = c.find_pod_by_label(label_selector, namespace)

    fname = "vllm-server-startup-latency.txt"
    fout = open(output_dir + "/" + fname, "w")

    if pods:
        for pod in pods:
            name = pod.metadata.name

            # Check if the pod is running and condition status is 'ready'
            if pod.status.phase == "Running" and any(cond.status == "True" for cond in pod.status.conditions if cond.type == "Ready"):
                print("Pod is running and condition status is 'ready': ", name)
            else:
                print("Pod is not running or condition status is not 'ready': ", name)

            pod_logs = c.read_pod_logs(name, namespace)
            
            # Compute the breakdow of the e2e startup latency for the VLLM server  
            if pod_logs:
               temp_logs = pod_logs.splitlines()

               print("Extracting engine initalization latency ...")
               t1 = get_engine_init_time(temp_logs)

               print("Extracting Model Loading latency ...")
               t2 = get_model_load_time(temp_logs)

               print("Extracting CUDA graph instantiation latency ...")
               t3 = get_graph_capture_time(temp_logs)

               print("Extracting API Server Init latency ...")
               t4 = get_apiserver_init_time(temp_logs)

            print('--------------------------------------')
            fout.write(name + "\t" + str(t1) + "\t" + str(t2) + "\t" + str(t3) + "\t" + str(t4) + "\n")
            fout.flush()
    else:
        print("No pods found with label: ", label_selector)
