#!/usr/bin/env python3
import argparse
import os
import re
import sys

from parserHelper import *


class Parser:
    def compute_server_latencies(self, fname, output_dir, cached):

        fin = open(fname, "r")
        fout = open(output_dir + "/vllm-server-startup-latency.txt", "w")

        # Compute the breakdow of the e2e startup latency for the VLLM server
        logs = fin.readlines()

        print("Extracting engine initalization latency ...")
        t1 = get_engine_init_time(logs)

        print("Extracting Model Weight Download latency ...")
        if cached == "no":
            t2 = get_model_weight_download_time(logs)
        else:
            t2 = 0

        print("Extracting Model Weight Loading latency ...")
        t3 = get_model_weight_load_time(logs)

        print("Extracting Model Weight Loading GB latency ...")
        t4 = get_model_weight_gb(logs)

        print("Extracting time before torch.compile...")
        tx = get_before_torch_compile_time(logs)

        print("Extracting torch.compile time ...")
        t6 = get_torch_compile_time(logs)
        t5 = round(float(tx) - float(t6), 3)  # computing time before torch.compile

        print("Extracting CUDA graph instantiation latency ...")
        t7 = get_cuda_graph_time(logs)

        print("Computing API Server Init latency ...")
        t8 = get_apiserver_init_time_simple(logs)

        print("Extracting time to sleep ...")
        t9 = get_time_to_sleep(logs)

        print("Extracting sleeping memory free & kept ...")
        t10a, t10b = get_sleep_memory_freed_kept(logs)

        print("Extracting time to wake ...")
        t11 = get_time_to_wake(logs)

        print("Computing init start time (sum) ...")
        t12 = float(t1) + float(t2) + float(t3) + t5 + float(t6) + float(t7) + float(t8)

        print("--------------------------------------")
        fout.write(
            str(t1)
            + "\t"
            + str(t2)
            + "\t"
            + str(t3)
            + "\t"
            + str(t4)
            + "\t"
            + str(t5)
            + "\t"
            + str(t6)
            + "\t"
            + str(t7)
            + "\t"
            + str(t8)
            + "\t"
            + str(t9)
            + "\t"
            + str(t10a)
            + "\t"
            + str(t10b)
            + "\t"
            + str(t11)
            + "\t"
            + str(t12)
            + "\n"
        )
        fout.flush()
        fout.close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", help="input filename (e.g., vllm-logs.txt)")
    parser.add_argument(
        "--model-cached",
        default="no",
        help="helpful description if model already in cache",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="vllm-log-dir",
        help="path to directory for output files (must exist)",
    )
    args = parser.parse_args()

    fname = args.filename
    output_dir = args.output
    cached = args.model_cached

    c = Parser()
    c.compute_server_latencies(fname, output_dir, cached)
