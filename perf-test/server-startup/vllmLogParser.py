#!/usr/bin/env python3
import re


# Extract CUDA graph instantiation latency
def get_graph_capture_time(logs):
    t = 0
    pattern = "Graph capturing finished"

    for line in logs:
        sentence = line.strip("\n")
        match = re.search(pattern, sentence)

        if match:
            new_sentence=sentence.split("]")
            match = re.findall(r"-?\d+\.\d+|-?\d+", new_sentence[1])  # The regex pattern matches one or more digits (\d+)

            if match:
               t = match[0]
               break
            else:
                continue
        else:
            continue
    return t

# Extract memory profile latency
def get_memory_profile_time(logs):
    t = 0
    pattern = "Memory profiling takes"
    
    for line in logs:
        sentence = line.strip("\n")
        match = re.search(pattern, sentence)

        if match:
            new_sentence=sentence.split("]")
            match = re.findall(r"-?\d+\.\d+|-?\d+", new_sentence[1])  # The regex pattern matches one or more digits (\d+)

            if match:
               t = match[0]
               break
            else:
                continue
        else:
            continue
    return t

