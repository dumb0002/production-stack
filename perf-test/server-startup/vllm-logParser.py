#!/usr/bin/env python3
import os
import re
import sys
from parserHelper import *


class Parser():
    def compute_server_latencies(self, fname, output_dir):

        fin = open(fname, "r")
        fout = open(output_dir + "/vllm-server-startup-latency.txt", "w")

        # Compute the breakdow of the e2e startup latency for the VLLM server  
        logs = fin.readlines()

        print("Extracting engine initalization latency ...")
        t1 = get_engine_init_time(logs)

        print("Extracting Model Loading latency ...")
        t2 = get_model_load_time(logs)

        print("Extracting Model Weight Loading GB latency ...")
        t3 = get_model_weight_gb(logs)

        print("Extracting time before torch.compile...")
        tx = get_before_torch_compile_time(logs)

        print("Extracting torch.compile time ...")
        t5 = get_torch_compile_time(logs)
        t4 = round(float(tx) - float(t5), 3) # computing time before torch.compile

        print("Extracting CUDA graph instantiation latency ...")
        t6 = get_cuda_graph_time(logs)

        print("Computing API Server Init latency ...")
        t7 = get_apiserver_init_time_simple(logs)

        print('--------------------------------------')
        fout.write(str(t1) + "\t" + str(t2) + "\t" + str(t3) + "\t" + str(t4) + "\t" + str(t5) + "\t" + str(t6) + "\t" + str(t7) + "\n")
        fout.flush()
        fout.close()
            
if __name__=="__main__": 

    fname = str(sys.argv[1])  # input filename (e.g., vllm-logs.txt)
    output_dir = str(sys.argv[2]) # path to the directory for the output files (e.g., $HOME/data/)

    c = Parser()
    c.compute_server_latencies(fname, output_dir)