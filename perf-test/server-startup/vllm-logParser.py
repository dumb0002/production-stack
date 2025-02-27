#!/usr/bin/env python3
import os
import re
import sys
import argparse
from parserHelper import *


class Parser():
    def compute_server_latencies(self, fname, output_dir):

        fin = open(fname, "r")
        fout = open(output_dir + "/vllm-server-startup-latency.txt", "w")

        # Compute the breakdow of the e2e startup latency for the VLLM server  
        logs = fin.readlines()

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
        t8 = get_apiserver_init_time_simple(logs)
        print('--------------------------------------')
        fout.write(str(t1) + "\t" + str(t2) + "\t" + str(t3) + "\t" + str(t4) + "\t" + str(t5) + "\t" + str(t6) + "\t" + str(t7) + "\t" + str(t8) + "\n")
        fout.flush()
        fout.close()
            
if __name__=="__main__": 

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", help="input filename (e.g., vllm-logs.txt)")
    parser.add_argument("-o", "--output", default="vllm-log-dir", help="path to directory for output files (must exist)")
    args = parser.parse_args()
   
    fname = args.filename
    output_dir=args.output
    
    c = Parser()
    c.compute_server_latencies(fname, output_dir)