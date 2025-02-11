#!/usr/bin/env bash


set -x # echo so that users can understand what is happening
set -e # exit on error

:
: -------------------------------------------------------------------------
: "Configuring clusterloader2 to measure VLLM PodStartupLatency"

if [ $CL2_DIR == "" ];then
   echo "Set the variable CL2_DIR to the path of the subdirectory clusterloader2/ of a cloned `https://github.com/kubernetes/perf-tests/` repo."
   exit 1;
fi

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
cp $SCRIPT_DIR/vllm-config.yaml  $CL2_DIR/testing/load
cp $SCRIPT_DIR/vllm-deployment.yaml $CL2_DIR/testing/load
cp $SCRIPT_DIR/vllm-service.yaml $CL2_DIR/testing/load
cp $SCRIPT_DIR/vllm-pvc.yaml $CL2_DIR/testing/load

