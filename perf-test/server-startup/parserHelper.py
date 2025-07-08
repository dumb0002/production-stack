#!/usr/bin/env python3
import re
from datetime import datetime

import pytz


# Extract Process Startup end time: vllm_first_log_message_timestamp
def get_log_first_timestamp(logs):
    d = None
    pattern = "Automatically detected platform cuda."

    for line in logs:
        sentence = line.strip("\n")
        match = re.search(pattern, sentence)

        if match:
            current_datetime = datetime.now()
            current_year = current_datetime.year
            t = (
                str(current_year)
                + "-"
                + sentence.split(" ")[1]
                + " "
                + sentence.split(" ")[2]
            )

            # convert to UTC timezone:
            d = convert_pt_to_utc(t)
            break
        else:
            continue
    return d


# Extract Engine Initialization
def get_engine_init_time(logs):
    pattern1 = "Automatically detected platform cuda."
    pattern2 = "Starting to load model"

    t = 0
    m1 = False
    m2 = False

    for line in logs:
        sentence = line.strip("\n")
        match_1 = re.search(pattern1, sentence)
        match_2 = re.search(pattern2, sentence)

        if match_1 and not m1:
            t1 = sentence.split(" ")[2]
            m1 = True
        elif match_2 and not m2:
            t2 = sentence.split(" ")[2]
            m2 = True
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


# Extract Model Weight Download latency
def get_model_weight_download_time(logs):
    t = 0
    pattern = "Time spent downloading weights"

    for line in logs:
        sentence = line.strip("\n")
        match = re.search(pattern, sentence)
        if match:
            new_sentence = (sentence.split("]")[1]).split(":")
            match = re.findall(
                r"-?\d+\.\d+|-?\d+", new_sentence[1]
            )  # The regex pattern matches one or more digits (\d+)

            if match:
                t = match[0]
                break
            else:
                continue
        else:
            continue
    return t


# Extract Model Weight Load latency
def get_model_weight_load_time(logs):
    t = 0
    pattern = "Loading weights took"

    for line in logs:
        sentence = line.strip("\n")
        match = re.search(pattern, sentence)
        if match:
            new_sentence = sentence.split("]")[1]
            match = re.findall(
                r"-?\d+\.\d+|-?\d+", new_sentence
            )  # The regex pattern matches one or more digits (\d+)

            if match:
                t = match[0]
                break
            else:
                continue
        else:
            continue
    return t


# Extract Model weight loading (GB)
def get_model_weight_gb(logs):
    t = 0
    pattern = "Model loading took"

    for line in logs:
        sentence = line.strip("\n")
        match = re.search(pattern, sentence)

        if match:
            new_sentence = sentence.split("]")
            match = re.findall(
                r"-?\d+\.\d+|-?\d+", new_sentence[1]
            )  # The regex pattern matches one or more digits (\d+)

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
            new_sentence = sentence.split("]")
            match = re.findall(
                r"-?\d+\.\d+|-?\d+", new_sentence[1]
            )  # The regex pattern matches one or more digits (\d+)

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
    pattern1 = "Loading weights took"
    pattern2 = "torch.compile takes"

    t = 0
    m1 = False
    m2 = False

    for line in logs:
        sentence = line.strip("\n")
        match_1 = re.search(pattern1, sentence)
        match_2 = re.search(pattern2, sentence)

        if match_1 and not m1:
            t1 = sentence.split(" ")[2]
            m1 = True
        elif match_2 and not m2:
            t2 = sentence.split(" ")[2]
            m2 = True
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
            new_sentence = sentence.split("]")
            match = re.findall(
                r"-?\d+\.\d+|-?\d+", new_sentence[1]
            )  # The regex pattern matches one or more digits (\d+)

            if match:
                t = match[0]
                break
            else:
                continue
        else:
            continue
    return t


# Extract init engine time
def get_apiserver_init_time(logs):
    d = None
    pattern = "init engine"

    for line in logs:
        sentence = line.strip("\n")
        match = re.search(pattern, sentence)

        if match:
            current_datetime = datetime.now()
            current_year = current_datetime.year

            t = (
                str(current_year)
                + "-"
                + sentence.split(" ")[1]
                + " "
                + sentence.split(" ")[2]
            )

            # convert to UTC timezone:
            d = convert_pt_to_utc(t)
            break
        else:
            continue
    return d


# Extract API Readiness time: an approximation for this computation
def get_apiserver_init_time_simple(logs):
    # pattern1 = "init engine"
    pattern1 = "Graph capturing finished"
    pattern2 = "Route: /metrics, Methods: GET"

    t = 0
    m1 = False
    m2 = False

    for line in logs:
        sentence = line.strip("\n")
        match_1 = re.search(pattern1, sentence)
        match_2 = re.search(pattern2, sentence)

        if match_1 and not m1:
            t1 = sentence.split(" ")[2]
            m1 = True
        elif match_2 and not m2:
            t2 = sentence.split(" ")[2]
            m2 = True
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


def convert_string_to_datetime(date_string, format_string):
    try:
        datetime_object = datetime.strptime(date_string, format_string)
        return datetime_object

    except ValueError:
        return None


def convert_pt_to_utc(pt_datetime_str, pt_timezone_str="US/Pacific"):
    pt_timezone = pytz.timezone(pt_timezone_str)
    pt_datetime = datetime.strptime(pt_datetime_str, "%Y-%m-%d %H:%M:%S")

    # Make the datetime object timezone-aware
    pt_datetime_aware = pt_timezone.localize(pt_datetime)

    # Convert to UTC
    utc_datetime = pt_datetime_aware.astimezone(pytz.utc)
    return utc_datetime


# Extract Time to Sleep
def get_time_to_sleep(logs):
    t = 0
    pattern = "seconds to fall asleep"

    for line in logs:
        sentence = line.strip("\n")
        match = re.search(pattern, sentence)

        if match:
            new_sentence = sentence.split("]")
            match = re.findall(
                r"-?\d+\.\d+|-?\d+", new_sentence[1]
            )  # The regex pattern matches one or more digits (\d+)

            if match:
                t = match[0]
                break
            else:
                continue
        else:
            continue
    return t


# Extract sleeping GPU memory freed in GB
def get_sleep_memory_freed_kept(logs):
    t1 = 0
    t2 = 0
    pattern = "Sleep mode freed"

    for line in logs:
        sentence = line.strip("\n")
        match = re.search(pattern, sentence)

        if match:
            new_sentence = (sentence.split("]")[1]).split(",")
            match1 = re.findall(r"-?\d+\.\d+|-?\d+", new_sentence[0])
            match2 = re.findall(r"-?\d+\.\d+|-?\d+", new_sentence[1])

            if match1 and match2:
                t1 = match1[0]
                t2 = match2[0]
                break
            else:
                continue
        else:
            continue
    return t1, t2


# Extract Time to Wake_up
def get_time_to_wake(logs):
    t = 0
    pattern = "seconds to wake up tags"

    for line in logs:
        sentence = line.strip("\n")
        match = re.search(pattern, sentence)

        if match:
            new_sentence = sentence.split("]")
            match = re.findall(
                r"-?\d+\.\d+|-?\d+", new_sentence[1]
            )  # The regex pattern matches one or more digits (\d+)

            if match:
                t = match[0]
                break
            else:
                continue
        else:
            continue
    return t
