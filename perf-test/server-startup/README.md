## Measure VLLM Server StartupLatency


### Prerequisites: 
- A running Kubernetes (K8s) environment with GPUs
-  [python3](https://www.python.org/downloads/) with all the dependencies listed [here](requirements.txt) installed. We recommend to create a python virtual environment `.venv` under `perf-test/server-startup`, for example: 

```bash
cd perf-test/server-startup 
python3 -m venv .venv
. .venv/bin/activate
pip3 install -r requirements.txt
```

In this tutorial, we will compute the breakdown of the e2e latency for a VLLM server running in a Kubernetes cluster as following:

### Steps

1. Open a new terminal and cd into the `perf-test/server-startup` directory from your local copy of this repo repo, for example:
   
   ```bash 
   cd $HOME/production-stack/perf-test/server-startup
   ```

   Then, run the metrics collection script:

   ```bash
   python3 vllm-serverStartupLatency.py <kubeconfig> <k8s-context-name> <pod-label-selector> <namespace> <output-directory>
   ```

   For example:
   
   ```bash 
   python3 vllm-serverStartupLatency.py $HOME/.kube/config wec1 environment=test vllm-test gpt2 $HOME/data
   ```

   Below is a detailed explanation of the input parameters:
   - `kubeconfig`: path to the kubeconfig file, e.g., `$HOME/.kube/config`
   - `k8s-context-name`: name of the context for the k8s cluster, e.g., `wec1`
   - `pod-label-selector`: label of the vllm pods, e.g., `environment=test` 
   - `namespace`: namespace for the vllm pods, e.g., `vllm-test`
   - `model-name`: LLM model name, e.g., `gpt2`.
   - `output-directory`: path to the directory for the output data files, e.g., `$HOME/data`


   The input parameter `kubeconfig` and `k8s-context-name` are optional. Setting both parameters to `None`, we will use the current context set in the kubeconfig file set by the `KUBECONFIG` env variable. For example:

   ```bash 
   python3 vllm-serverStartupLatency.py None None environment=test vllm-test gpt2 $HOME/data
   ```

   The generated output from the script are two files. The first is a tab-delimited file named `vllm-server-startup-latency.txt` with the following structure:

   ```console 
   <pod-name> <engine-initalization-time> <model-weights-loading-time> <model-weights-loading_GB><time_before_torch_compile> <torch_compile_time> <CUDA-graph-capture> <api-readiness>
   ```

   Also, the unit of measurement for each value is `seconds` in the generated output file, except for the value in the first colum which corresponds to the VLLM pod name, and the `<model-weights-loading_GB>` which has unit of GB. 

   For example: 

   ```bash
   cd $HOME/data
   cat gpt2_vllm-server-startup-latency.txt
   ```
 
   Sample output:

   ```console 
   vllm-granite-3-0-2b-instruct-6f9cb88444-2czv  13  14   6.1501  2.97	30.03  18  0
   ```

   The second file contains the logs of the vllm pods. For example:

   ```bash
   cat vllm-granite-3-0-2b-instruct-6f9cb88444-2czvd-log.txt
   ```

   Sample output:
   ``` bash
   INFO 02-13 15:01:07 gpu_model_runner.py:872] Loading model weights took 6.1501 GB
   INFO 02-13 15:01:13 backends.py:579] Using cache directory: /data/cache/vllm/torch_compile_cache/02bf430320/rank_0 for vLLM's torch.compile
   INFO 02-13 15:01:13 backends.py:587] Dynamo bytecode transform time: 6.77 s
   INFO 02-13 15:01:16 backends.py:311] Cache the graph of shape None for later use
   INFO 02-13 15:01:37 backends.py:323] Compiling a graph for general shape takes 23.26 s
   WARNING 02-13 15:01:39 fused_moe.py:806] Using default MoE config. Performance might be sub-optimal! Config file not found at /usr/local/lib/python3.12/dist-packages/vllm/model_executor/layers/fused_moe/configs/E=40,N=512,device_name=NVIDIA_L40S.json
   INFO 02-13 15:01:40 monitor.py:33] torch.compile takes 30.03 s in total
   INFO 02-13 15:01:40 kv_cache_utils.py:407] # GPU blocks: 33660
   INFO 02-13 15:01:40 kv_cache_utils.py:410] Maximum concurrency for 4096 tokens per request: 131.48x
   INFO 02-13 15:01:59 gpu_model_runner.py:1043] Graph capturing finished in 18 secs, took 0.62 GiB
   INFO 02-13 15:01:59 core.py:91] init engine (profile, create kv cache, warmup model) took 51.89 seconds
   INFO 02-13 15:01:59 api_server.py:756] Using supplied chat template:^M
   INFO 02-13 15:01:59 api_server.py:756] None
   INFO 02-13 15:01:59 launcher.py:21] Available routes are:
   INFO 02-13 15:01:59 launcher.py:29] Route: /openapi.json, Methods: HEAD, GET
   INFO 02-13 15:01:59 launcher.py:29] Route: /docs, Methods: HEAD, GET
   INFO 02-13 15:01:59 launcher.py:29] Route: /docs/oauth2-redirect, Methods: HEAD, GET
   INFO 02-13 15:01:59 launcher.py:29] Route: /redoc, Methods: HEAD, GET
   INFO 02-13 15:01:59 launcher.py:29] Route: /health, Methods: GET
   INFO 02-13 15:01:59 launcher.py:29] Route: /ping, Methods: GET, POST
   ```


2. Clean up the generated workload Kubernetes API objects from your cluster:

   ```bash 
   kubectl -n <namespace> delete pods -l <pod-label-selector>
   ```

   For example:

   ```console
   kubectl -n vllm-test delete pods -l environment=test
   ```

