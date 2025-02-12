#!/usr/bin/env python3
import re
from datetime import datetime


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


# Extract memory profile latency
def get_model_weight_time(logs):
    t = 0
    pattern = "Time took to download weights for"
    
    for line in logs:
        sentence = line.strip("\n")
        match = re.search(pattern, sentence)

        if match:
            new_sentence=(sentence.split("]")[1]).split(":")
            match = re.findall(r"-?\d+\.\d+|-?\d+", new_sentence[1])  # The regex pattern matches one or more digits (\d+)

            if match:
               t = match[0]
               break
            else:
                continue
        else:
            continue
    return t


# Extract Engine Initialization
def get_engine_init_time(logs):
    pattern1 = "Automatically detected platform cuda."
    pattern2 = "Starting to load model"

    t = 0
    m1=False
    m2=False
    
    for line in logs:
        sentence = line.strip("\n")
        match_1 = re.search(pattern1, sentence)
        match_2 = re.search(pattern2, sentence)

        if match_1 and not m1:
           t1 = sentence.split(" ")[2]
           m1=True
        elif match_2 and not m2:
           t2 = sentence.split(" ")[2]
           m2=True
        else:
           continue

        # compute the time
        if m1 and m2:
           format_string = "%H:%M:%S"
           d1 = datetime.strptime(t1, format_string)
           d2 = datetime.strptime(t2, format_string)
           delta = d2 - d1
           t = delta.seconds
           break
    return t


# Extract Model Loading latency
def get_model_load_time(logs):
    pattern1 = "Starting to load model"
    pattern2 = "Capturing cudagraphs for decoding"
    
    t = 0
    m1=False
    m2=False
    
    for line in logs:
        sentence = line.strip("\n")
        match_1 = re.search(pattern1, sentence)
        match_2 = re.search(pattern2, sentence)

        if match_1 and not m1:
           t1 = sentence.split(" ")[2]
           m1=True
        elif match_2 and not m2:
           t2 = sentence.split(" ")[2]
           m2=True
        else:
           continue

        # compute the time
        if m1 and m2:
           format_string = "%H:%M:%S"
           d1 = datetime.strptime(t1, format_string)
           d2 = datetime.strptime(t2, format_string)
           delta = d2 - d1
           t = delta.seconds
           break
    return t


def get_apiserver_init_time (logs):
    pattern1 = "init engine"
    pattern2 = "Route: /invocations, Methods: POST"
    
    t = 0
    m1=False
    m2=False
    
    for line in logs:
        sentence = line.strip("\n")
        match_1 = re.search(pattern1, sentence)
        match_2 = re.search(pattern2, sentence)

        if match_1 and not m1:
           t1 = sentence.split(" ")[2]
           m1=True
        elif match_2 and not m2:
           t2 = sentence.split(" ")[2]
           m2=True
        else:
           continue

        # compute the time
        if m1 and m2:
           format_string = "%H:%M:%S"
           d1 = datetime.strptime(t1, format_string)
           d2 = datetime.strptime(t2, format_string)
           delta = d2 - d1
           t = delta.seconds
           break
    return t