# Measure vLLM Server StartupLatency

## Prerequisites

- A running Kubernetes (K8s) environment with GPUs available
- [python3](https://www.python.org/downloads/) with all the dependencies listed [here](requirements.txt) installed. We recommend to create a python virtual environment `.venv` under `perf-test/server-startup`, for example:

```bash
cd perf-test/server-startup
python3 -m venv .venv
. .venv/bin/activate
pip3 install -r requirements.txt
```

In this tutorial, we will compute the breakdown of the e2e latency for a vLLM server running in a Kubernetes cluster as following:

## Steps

### 1. Compute the startup latency for a vLLM server deployed in a Kubernetes cluster

   Open a new terminal and cd into the `perf-test/server-startup` directory from your local copy of this repo repo, for example:

   ```bash
   cd $HOME/production-stack/perf-test/server-startup
   ```

   Then, run the metrics collection script:

   ```bash
   python3 vllm-serverStartupLatency.py -cfg <kubeconfig> -ctx <k8s-context-name> -l <pod-label-selector>  -c <container-name> -n <namespace> -m <model-name> --model-cached <yes/no> -o <output-directory>
   ```

   For example:

   ```bash
   python3 vllm-serverStartupLatency.py -cfg $HOME/.kube/config -ctx wec1 -l environment=test -c vllm -n vllm-test -m gpt2 --model-cached no -o $HOME/data
   ```

   Below is a detailed explanation of the input parameters:
      - `--config (-cfg)`: path to the kubeconfig file (default: `$HOME/.kube/config`)
      - `--context (-ctx)`: name of the context for the k8s cluster, e.g., `wec1`
      - `--label (-l)`: label of the vLLM pods, e.g., `environment=test`
      - `--containername (-c)`: name of container in vLLM pod (default: `None`)
      - `--namespace (-n)`: namespace for the vLLM pods (default: `default`)
      - `--model (-m)`: LLM model name, e.g., `gpt2`.
      - `--model-cached`: if model already in cache or not (default: `no`)
      - `--output (-o)`: path to the directory for the output data files, e.g., `$HOME/data`

   The flags `--context` and `--containername` are optional. Furthermore, if the flag `--config` is set to `None`, we will use the current context set in the kubeconfig file set by the `KUBECONFIG` env variable. For example:

   ```bash
   python3 vllm-serverStartupLatency.py -cfg None -l environment=test -m ibm-granite--granite-3.3-2b-instruct -o $HOME/data
   ```

   The generated output from the script are two files. The first is a tab-delimited file named `<model-name>_vllm-server-startup-latency.txt` with the following structure:

   ```console
   <process-startup>|<engine-initalization-time>|<model-weights-download-time>|<model-weights-loading-time>|<model-weights-loading_GB>|<time-before-torch-compile>|<torch-compile-time>|<CUDA-graph-capture>|<api-readiness>|<time-to-sleep>|<GPU-memory-freed>|<GPU-memory-kept>|<time-to-wake>|<initial start time (sum)>
   ```

   Also, the unit of measurement for each value is `seconds` in the generated output file, except for the value in the first colum which corresponds to the VLLM pod name, and the `<model-weights-loading_GB>` which has unit of GB.

   For example:

   ```bash
   cd $HOME/data
   cat ibm-granite--granite-3.3-2b-instruct_vllm-server-startup-latency.txt
   ```

   Sample output:

   ```console
   11 17 0  3.17  4.7351   19.54 42.46 22 3  0  0  0  0  107.17
   ```

   The second file contains the logs of the vLLM pods. For example:

   ```bash
   cat vllm-granite-3-0-2b-instruct-6f9cb88444-2czvd-log.txt
   ```

   Sample output:

   ``` bash
   INFO 07-08 13:53:14 [__init__.py:244] Automatically detected platform cuda.
   WARNING 07-08 13:53:18 [api_server.py:913] SECURITY WARNING: Development endpoints are enabled! This should NOT be used in production!
   INFO 07-08 13:53:18 [api_server.py:1395] vLLM API server version 0.9.2
   INFO 07-08 13:53:18 [cli_args.py:325] non-default args: {'host': '0.0.0.0', 'model': '/var/hf-mount/vcp/hf/models--ibm-granite--granite-3.3-2b-instruct/snapshots/707f574c62054322f6b5b04b6d075f0a8f05e0f0', 'enable_sleep_mode': True}
   INFO 07-08 13:53:23 [config.py:841] This model supports multiple tasks: {'classify', 'generate', 'embed', 'reward'}. Defaulting to 'generate'.
   INFO 07-08 13:53:23 [config.py:1472] Using max model len 131072
   INFO 07-08 13:53:24 [config.py:2285] Chunked prefill is enabled with max_num_batched_tokens=2048.
   INFO 07-08 13:53:28 [__init__.py:244] Automatically detected platform cuda.
   WARNING 07-08 13:53:30 [api_server.py:913] SECURITY WARNING: Development endpoints are enabled! This should NOT be used in production!
   INFO 07-08 13:53:30 [core.py:526] Waiting for init message from front-end.
   INFO 07-08 13:53:30 [core.py:69] Initializing a V1 LLM engine (v0.9.2) with config: model='/var/hf-mount/vcp/hf/models--ibm-granite--granite-3.3-2b-instruct/snapshots/707f574c62054322f6b5b04b6d075f0a8f05e0f0', speculative_config=None, tokenizer='/var/hf-mount/vcp/hf/models--ibm-granite--granite-3.3-2b-instruct/snapshots/707f574c62054322f6b5b04b6d075f0a8f05e0f0', skip_tokenizer_init=False, tokenizer_mode=auto, revision=None, override_neuron_config={}, tokenizer_revision=None, trust_remote_code=False, dtype=torch.bfloat16, max_seq_len=131072, download_dir=None, load_format=LoadFormat.AUTO, tensor_parallel_size=1, pipeline_parallel_size=1, disable_custom_all_reduce=False, quantization=None, enforce_eager=False, kv_cache_dtype=auto,  device_config=cuda, decoding_config=DecodingConfig(backend='auto', disable_fallback=False, disable_any_whitespace=False, disable_additional_properties=False, reasoning_backend=''), observability_config=ObservabilityConfig(show_hidden_metrics_for_version=None, otlp_traces_endpoint=None, collect_detailed_traces=None), seed=0, served_model_name=/var/hf-mount/vcp/hf/models--ibm-granite--granite-3.3-2b-instruct/snapshots/707f574c62054322f6b5b04b6d075f0a8f05e0f0, num_scheduler_steps=1, multi_step_stream_outputs=True, enable_prefix_caching=True, chunked_prefill_enabled=True, use_async_output_proc=True, pooler_config=None, compilation_config={"level":3,"debug_dump_path":"","cache_dir":"","backend":"","custom_ops":[],"splitting_ops":["vllm.unified_attention","vllm.unified_attention_with_output"],"use_inductor":true,"compile_sizes":[],"inductor_compile_config":{"enable_auto_functionalized_v2":false},"inductor_passes":{},"use_cudagraph":true,"cudagraph_num_of_warmups":1,"cudagraph_capture_sizes":[512,504,496,488,480,472,464,456,448,440,432,424,416,408,400,392,384,376,368,360,352,344,336,328,320,312,304,296,288,280,272,264,256,248,240,232,224,216,208,200,192,184,176,168,160,152,144,136,128,120,112,104,96,88,80,72,64,56,48,40,32,24,16,8,4,2,1],"cudagraph_copy_inputs":false,"full_cuda_graph":false,"max_capture_size":512,"local_cache_dir":null}
   INFO 07-08 13:53:31 [parallel_state.py:1076] rank 0 in world size 1 is assigned as DP rank 0, PP rank 0, TP rank 0, EP rank 0
   INFO 07-08 13:53:31 [topk_topp_sampler.py:49] Using FlashInfer for top-p & top-k sampling.
   INFO 07-08 13:53:31 [gpu_model_runner.py:1770] Starting to load model /var/hf-mount/vcp/hf/models--ibm-granite--granite-3.3-2b-instruct/snapshots/707f574c62054322f6b5b04b6d075f0a8f05e0f0...
   INFO 07-08 13:53:31 [gpu_model_runner.py:1775] Loading model from scratch...
   INFO 07-08 13:53:32 [cuda.py:284] Using Flash Attention backend on V1 engine.

   Loading safetensors checkpoint shards:   0% Completed | 0/2 [00:00<?, ?it/s]

   Loading safetensors checkpoint shards:  50% Completed | 1/2 [00:02<00:02,  2.98s/it]

   Loading safetensors checkpoint shards: 100% Completed | 2/2 [00:03<00:00,  1.33s/it]

   Loading safetensors checkpoint shards: 100% Completed | 2/2 [00:03<00:00,  1.58s/it]

   INFO 07-08 13:53:35 [default_loader.py:272] Loading weights took 3.17 seconds
   INFO 07-08 13:53:35 [gpu_model_runner.py:1801] Model loading took 4.7351 GiB and 3.341612 seconds
   ```

### 2. Clean up the generated workload Kubernetes API objects from your cluster

   ```bash
   kubectl -n <namespace> delete pods -l <pod-label-selector>
   ```

   For example:

   ```console
   kubectl -n vllm-test delete pods -l environment=test
   ```

### 3. Compute the startup latencies of the vLLM server by analyzing an existing log text file (OPTIONAL)

   Run the metrics collection script:

   ```bash
   python3 vllm-logParser.py -f <vllm-log-file> --model-cached <yes/no> -o <output-directory>
   ```

   For example:

   ```bash
   python3 vllm-logParser.py -f $HOME/logs/pod-vllm-logs.txt --model-cached yes -o $HOME/data
   ```

   Below is a detailed explanation of the input parameters:
      - `--filename (-f)`: text file with the vLLM logs,  e.g., `$HOME/logs/pod-vllm-logs.txt`
      - `--output (-o)`: path to the directory for the output data files, e.g., `$HOME/data`
      - `--model-cached`: if model already in cache or not (default: `no`)

   Below is a snapshot of few lines for the begining of a valid VLLM log file:

   ```console
   INFO 06-20 09:36:18 [__init__.py:244] Automatically detected platform cuda.
   INFO 06-20 09:36:27 [api_server.py:1287] vLLM API server version 0.9.1
   INFO 06-20 09:36:27 [cli_args.py:309] non-default args: {'host': '0.0.0.0', 'model': 'ibm-granite/granite-3.3-8b-instruct', 'enable_sleep_mode': True}
   INFO 06-20 09:36:37 [config.py:823] This model supports multiple tasks: {'embed', 'reward', 'score', 'generate', 'classify'}. Defaulting to 'generate'.
   INFO 06-20 09:36:37 [config.py:2195] Chunked prefill is enabled with max_num_batched_tokens=2048.
   WARNING 06-20 09:36:41 [env_override.py:17] NCCL_CUMEM_ENABLE is set to 0, skipping override. This may increase memory overhead with cudagraph+allreduce: https://github.com/NVIDIA/nccl/issues/1234
   INFO 06-20 09:36:44 [__init__.py:244] Automatically detected platform cuda.
   INFO 06-20 09:36:47 [core.py:455] Waiting for init message from front-end.
   INFO 06-20 09:36:47 [core.py:70] Initializing a V1 LLM engine (v0.9.1) with config: model='ibm-granite/granite-3.3-8b-instruct', speculative_config=None, tokenizer='ibm-granite/granite-3.3-8b-instruct', skip_tokenizer_init=False, tokenizer_mode=auto, revision=None, override_neuron_config={}, tokenizer_revision=None, trust_remote_code=False, dtype=torch.bfloat16, max_seq_len=131072, download_dir=None, load_format=LoadFormat.AUTO, tensor_parallel_size=1, pipeline_parallel_size=1, disable_custom_all_reduce=False, quantization=None, enforce_eager=False, kv_cache_dtype=auto,  device_config=cuda, decoding_config=DecodingConfig(backend='auto', disable_fallback=False, disable_any_whitespace=False, disable_additional_properties=False, reasoning_backend=''), observability_config=ObservabilityConfig(show_hidden_metrics_for_version=None, otlp_traces_endpoint=None, collect_detailed_traces=None), seed=0, served_model_name=ibm-granite/granite-3.3-8b-instruct, num_scheduler_steps=1, multi_step_stream_outputs=True, enable_prefix_caching=True, chunked_prefill_enabled=True, use_async_output_proc=True, pooler_config=None, compilation_config={"level":3,"debug_dump_path":"","cache_dir":"","backend":"","custom_ops":["none"],"splitting_ops":["vllm.unified_attention","vllm.unified_attention_with_output"],"use_inductor":true,"compile_sizes":[],"inductor_compile_config":{"enable_auto_functionalized_v2":false},"inductor_passes":{},"use_cudagraph":true,"cudagraph_num_of_warmups":1,"cudagraph_capture_sizes":[512,504,496,488,480,472,464,456,448,440,432,424,416,408,400,392,384,376,368,360,352,344,336,328,320,312,304,296,288,280,272,264,256,248,240,232,224,216,208,200,192,184,176,168,160,152,144,136,128,120,112,104,96,88,80,72,64,56,48,40,32,24,16,8,4,2,1],"cudagraph_copy_inputs":false,"full_cuda_graph":false,"max_capture_size":512,"local_cache_dir":null}
   WARNING 06-20 09:36:50 [utils.py:2737] Methods determine_num_available_blocks,device_config,get_cache_block_size_bytes,initialize_cache not implemented in <vllm.v1.worker.gpu_worker.Worker object at 0x7fc6d289e750>
   INFO 06-20 09:36:50 [parallel_state.py:1065] rank 0 in world size 1 is assigned as DP
   ```

   The generated output from the script are two files. The first is a tab-delimited file named `vllm-server-startup-latency.txt` with the following structure:

   ```console
   <engine-initalization-time>|<model-weights-download-time>|<model-weights-loading-time>|<model-weights-loading_GB>|<time-before-torch-compile>|<torch-compile-time>|<CUDA-graph-capture>|<api-readiness>|<time-to-sleep>|<GPU-memory-freed>|<GPU-memory-kept>|<time-to-wake>|<initial start time (sum)>
   ```

   For example:

   ```bash
   cd $HOME/data
   cat vllm-server-startup-latency.txt
   ```

   Sample output:

   ```console
   132   38.668196   5.09  15.2512  51.12 57.88 35 1  10.961203   71.43 1.18  1.529967 220.758196
   ```
