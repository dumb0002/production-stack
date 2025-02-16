#!/usr/bin/env python3
import re
import pytz
from datetime import datetime



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
    pattern2 = "Loading model weights took"
    #pattern2 = "Capturing cudagraphs for decoding"
    
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


# Extract Model weight loading (GB)
def get_model_weight_gb(logs):
    t = 0
    pattern = "Loading model weights took"
    
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


# Extract Torch compile time
def get_torch_compile_time(logs):
    t = 0
    pattern = "torch.compile takes"
    
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


# Extract before Torch compile time
def get_before_torch_compile_time(logs):
    pattern1 = "Loading model weights took"
    pattern2 = "torch.compile takes"
    
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


# Extract CUDA graph instantiation latency
def get_cuda_graph_time(logs):
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


# Extract init engine time
def get_apiserver_init_time (logs):
    d = None
    pattern = "init engine"

    for line in logs:
        sentence = line.strip("\n")
        match = re.search(pattern, sentence)

        if match:
           current_datetime = datetime.now()
           current_year = current_datetime.year

           t = str(current_year) + "-" + sentence.split(" ")[1] + " " + sentence.split(" ")[2]

           # convert to UTC timezone:
           d = convert_pt_to_utc(t)
        else:
           continue 
    return d


# # Extract API Readiness time
# def get_apiserver_init_time (logs):
#     pattern1 = "init engine"
#     pattern2 = "Route: /invocations, Methods: POST"
    
#     t = 0
#     m1=False
#     m2=False

#     for line in logs:
#         sentence = line.strip("\n")
#         match_1 = re.search(pattern1, sentence)
#         match_2 = re.search(pattern2, sentence)

#         if match_1 and not m1:
#            t1 = sentence.split(" ")[2]
#            m1=True
#         elif match_2 and not m2:
#            t2 = sentence.split(" ")[2]
#            m2=True
#         else:
#            continue

#         # compute the time
#         if m1 and m2:
#            format_string = "%H:%M:%S"
#            d1 = datetime.strptime(t1, format_string)
#            d2 = datetime.strptime(t2, format_string)
#            delta = d2 - d1
#            t = delta.seconds
#            break
#     return t

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


def convert_string_to_datetime(date_string, format_string):
    try:
      datetime_object = datetime.strptime(date_string, format_string)
      return datetime_object

    except ValueError:
      return None


def convert_pt_to_utc(pt_datetime_str, pt_timezone_str='US/Pacific'):
    pt_timezone = pytz.timezone(pt_timezone_str)
    pt_datetime = datetime.strptime(pt_datetime_str, "%Y-%m-%d %H:%M:%S")
    
    # Make the datetime object timezone-aware
    pt_datetime_aware = pt_timezone.localize(pt_datetime)
    
    # Convert to UTC
    utc_datetime = pt_datetime_aware.astimezone(pytz.utc)
    
    return utc_datetime