## Measure vLLM Server StartupLatency


### Prerequisites: 
- A running Kubernetes (K8s) environment with GPUs
-  [python3](https://www.python.org/downloads/) with all the dependencies listed [here](requirements.txt) installed. We recommend to create a python virtual environment `.venv` under `perf-test/server-startup`, for example: 

```bash
cd perf-test/server-startup 
python3 -m venv .venv
. .venv/bin/activate
pip3 install -r requirements.txt
```

In this tutorial, we will compute the breakdown of the e2e latency for a vLLM server running in a Kubernetes cluster as following:

### Steps

#### 1. Compute the startup latency for a vLLM server deployed in a Kubernetes cluster:

   Open a new terminal and cd into the `perf-test/server-startup` directory from your local copy of this repo repo, for example:
   
   ```bash 
   cd $HOME/production-stack/perf-test/server-startup
   ```

   Then, run the metrics collection script:

   ```bash
   python3 vllm-serverStartupLatency.py -cfg <kubeconfig> -ctx <k8s-context-name> -l <pod-label-selector>  -c <container-name> -n <namespace> -m <model-name> -o <output-directory>
   ```

   For example:
   
   ```bash 
   python3 vllm-serverStartupLatency.py -cfg $HOME/.kube/config -ctx wec1 -l environment=test -c vllm -n vllm-test -m gpt2 -o $HOME/data
   ```

   Below is a detailed explanation of the input parameters:
   - `--config (-cfg)`: path to the kubeconfig file (default: `$HOME/.kube/config`)
   - `--context (-ctx)`: name of the context for the k8s cluster, e.g., `wec1`
   - `--label (-l)`: label of the vLLM pods, e.g., `environment=test`
   - `--containername (-c)`: name of container in vLLM pod (default: `None`)
   - `--namespace (-n)`: namespace for the vLLM pods (default: `default`)
   - `--model (-m)`: LLM model name, e.g., `gpt2`.
   - `--output (-o)`: path to the directory for the output data files, e.g., `$HOME/data`


   The flags `--context` and `--containername` are optional. Furthermore, if the flag `--config` is set to `None`, we will use the current context set in the kubeconfig file set by the `KUBECONFIG` env variable. For example:

   ```bash 
   python3 vllm-serverStartupLatency.py -cfg None -l environment=test -m gpt2 -o $HOME/data
   ```

   The generated output from the script are two files. The first is a tab-delimited file named `<model-name>_vllm-server-startup-latency.txt` with the following structure:

   ```console 
   <pod-name> <process-startup> <engine-initalization-time> <model-weights-download-time> <model-weights-loading-time> <model-weights-loading_GB><time_before_torch_compile> <torch_compile_time> <CUDA-graph-capture> <api-readiness>
   ```

   Also, the unit of measurement for each value is `seconds` in the generated output file, except for the value in the first colum which corresponds to the VLLM pod name, and the `<model-weights-loading_GB>` which has unit of GB. 

   For example: 

   ```bash
   cd $HOME/data
   cat granite-3.1-8b_vllm-server-startup-latency.txt
   ```
 
   Sample output:

   ```console 
  vllm-granite-3-0-2b-instruct-df585f45d-pcv   10   19   17.23   7  4.72   3.66  39.34  23   10
   ```

   The second file contains the logs of the vLLM pods. For example:

   ```bash
   cat vllm-granite-3-0-2b-instruct-6f9cb88444-2czvd-log.txt
   ```

   Sample output:
   ``` bash
   INFO 02-26 18:56:48 gpu_model_runner.py:1049] Starting to load model ibm-granite/granite-3.0-2b-base...
   INFO 02-26 18:56:48 topk_topp_sampler.py:36] Using FlashInfer for top-p & top-k sampling.
   INFO 02-26 18:56:48 rejection_sampler.py:37] Using FlashInfer for rejection sampling.
   INFO 02-26 18:56:48 weight_utils.py:254] Using model weights format ['*.safetensors']
   INFO 02-26 18:57:05 weight_utils.py:270] Time spent downloading weights for ibm-granite/granite-3.0-2b-base: 17.230355 seconds
   Loading safetensors checkpoint shards:   0% Completed | 0/3 [00:00<?, ?it/s]
   Loading safetensors checkpoint shards:  33% Completed | 1/3 [00:02<00:05,  2.98s/it]
   Loading safetensors checkpoint shards:  67% Completed | 2/3 [00:05<00:02,  2.83s/it]
   Loading safetensors checkpoint shards: 100% Completed | 3/3 [00:05<00:00,  1.66s/it]
   Loading safetensors checkpoint shards: 100% Completed | 3/3 [00:05<00:00,  1.99s/it]

   INFO 02-26 18:57:12 gpu_model_runner.py:1060] Loading model weights took 4.7196 GB
   INFO 02-26 18:57:21 backends.py:408] Using cache directory: /data/cache/vllm/torch_compile_cache/56cafb45fd/rank_0 for vLLM's torch.compile
   INFO 02-26 18:57:21 backends.py:418] Dynamo bytecode transform time: 9.54 s
   INFO 02-26 18:57:24 backends.py:132] Cache the graph of shape None for later use
   INFO 02-26 18:57:52 backends.py:144] Compiling a graph for general shape takes 29.79 s
   INFO 02-26 18:57:55 monitor.py:33] torch.compile takes 39.34 s in total
   INFO 02-26 18:57:55 kv_cache_utils.py:522] # GPU blocks: 7124
   INFO 02-26 18:57:55 kv_cache_utils.py:525] Maximum concurrency for 4096 tokens per request: 27.83x
   INFO 02-26 18:58:18 gpu_model_runner.py:1339] Graph capturing finished in 23 secs, took 0.59 GiB
   INFO 02-26 18:58:18 core.py:116] init engine (profile, create kv cache, warmup model) took 66.74 seconds
   INFO 02-26 18:58:18 api_server.py:958] Starting vLLM API server on http://0.0.0.0:8000
   INFO 02-26 18:58:18 launcher.py:23] Available routes are:
   INFO 02-26 18:58:18 launcher.py:31] Route: /openapi.json, Methods: GET, HEAD
   ```


#### 2. Clean up the generated workload Kubernetes API objects from your cluster:

   ```bash 
   kubectl -n <namespace> delete pods -l <pod-label-selector>
   ```

   For example:

   ```console
   kubectl -n vllm-test delete pods -l environment=test
   ```

#### 3. Compute the startup latencies of the vLLM server by analyzing an existing log text file (OPTIONAL):

   Run the metrics collection script:

   ```bash
   python3 vllm-logParser.py -f <vllm-log-file> -o <output-directory>
   ```

   For example:
   
   ```bash 
   python3 vllm-logParser.py -f $HOME/logs/pod-vllm-logs.txt -o $HOME/data
   ```

   Below is a detailed explanation of the input parameters:
   - `--filename (-f)`: text file with the vLLM logs,  e.g., `$HOME/logs/pod-vllm-logs.txt`
   - `--output (-o)`: path to the directory for the output data files, e.g., `$HOME/data`

   Below is a snapshot of few lines for the begining of a valid VLLM log file:

   ```
   INFO 02-26 18:56:29 __init__.py:207] Automatically detected platform cuda.
   INFO 02-26 18:56:32 api_server.py:912] vLLM API server version 0.7.3
   INFO 02-26 18:56:32 api_server.py:913] args: Namespace(subparser='serve', model_tag='ibm-granite/granite-3.0-2b-base', config='', host='0.0.0.0', port=8000, uvicorn_log_level='info', allow_credentials=False, allowed_origins=['*'], allowed_methods=['*'], allowed_headers=['*'], api_key=None, lora_modules=None, prompt_adapters=None, chat_template=None, chat_template_content_format='auto', response_role='assistant', ssl_keyfile=None, ssl_certfile=None, ssl_ca_certs=None, ssl_cert_reqs=0, root_path=None, middleware=[], return_tokens_as_token_ids=False, disable_frontend_multiprocessing=False, enable_request_id_headers=False, enable_auto_tool_choice=False, enable_reasoning=False, reasoning_parser=None, tool_call_parser=None, tool_parser_plugin='', model='ibm-granite/granite-3.0-2b-base', task='auto', tokenizer=None, skip_tokenizer_init=False, revision=None, code_revision=None, tokenizer_revision=None, tokenizer_mode='auto', trust_remote_code=False, allowed_local_media_path=None, download_dir=None, load_format='auto', config_format=<ConfigFormat.AUTO: 'auto'>, dtype='auto', kv_cache_dtype='auto', max_model_len=None, guided_decoding_backend='xgrammar', logits_processor_pattern=None, model_impl='auto', distributed_executor_backend=None, pipeline_parallel_size=1, tensor_parallel_size=1, max_parallel_loading_workers=None, ray_workers_use_nsight=False, block_size=None, enable_prefix_caching=None, disable_sliding_window=False, use_v2_block_manager=True, num_lookahead_slots=0, seed=0, swap_space=4, cpu_offload_gb=0, gpu_memory_utilization=0.9, num_gpu_blocks_override=None, max_num_batched_tokens=None, max_num_partial_prefills=1, max_long_partial_prefills=1, long_prefill_token_threshold=0, max_num_seqs=None, max_logprobs=20, disable_log_stats=False, quantization=None, rope_scaling=None, rope_theta=None, hf_overrides=None, enforce_eager=False, max_seq_len_to_capture=8192, disable_custom_all_reduce=False, tokenizer_pool_size=0, tokenizer_pool_type='ray', tokenizer_pool_extra_config=None, limit_mm_per_prompt=None, mm_processor_kwargs=None, disable_mm_preprocessor_cache=False, enable_lora=False, enable_lora_bias=False, max_loras=1, max_lora_rank=16, lora_extra_vocab_size=256, lora_dtype='auto', long_lora_scaling_factors=None, max_cpu_loras=None, fully_sharded_loras=False, enable_prompt_adapter=False, max_prompt_adapters=1, max_prompt_adapter_token=0, device='auto', num_scheduler_steps=1, multi_step_stream_outputs=True, scheduler_delay_factor=0.0, enable_chunked_prefill=None, speculative_model=None, speculative_model_quantization=None, num_speculative_tokens=None, speculative_disable_mqa_scorer=False, speculative_draft_tensor_parallel_size=None, speculative_max_model_len=None, speculative_disable_by_batch_size=None, ngram_prompt_lookup_max=None, ngram_prompt_lookup_min=None, spec_decoding_acceptance_method='rejection_sampler', typical_acceptance_sampler_posterior_threshold=None, typical_acceptance_sampler_posterior_alpha=None, disable_logprobs_during_spec_decoding=None, model_loader_extra_config=None, ignore_patterns=[], preemption_mode=None, served_model_name=None, qlora_adapter_name_or_path=None, otlp_traces_endpoint=None, collect_detailed_traces=None, disable_async_output_proc=False, scheduling_policy='fcfs', scheduler_cls='vllm.core.scheduler.Scheduler', override_neuron_config=None, override_pooler_config=None, compilation_config=None, kv_transfer_config=None, worker_cls='auto', generation_config=None, override_generation_config=None, enable_sleep_mode=False, calculate_kv_scales=False, additional_config=None, disable_log_requests=False, max_log_len=None, disable_fastapi_docs=False, enable_prompt_tokens_details=False, dispatch_function=<function ServeSubcommand.cmd at 0x7fed3ebb7240>)
   ```


   The generated output from the script are two files. The first is a tab-delimited file named `vllm-server-startup-latency.txt` with the following structure:

   ```console 
   <engine-initalization-time> <model-weights-download-time> <model-weights-loading-time> <model-weights-loading_GB><time_before_torch_compile> <torch_compile_time> <CUDA-graph-capture> <api-readiness>
   ```

   For example: 

   ```bash
   cd $HOME/data
   cat vllm-server-startup-latency.txt
   ```
 
   Sample output:

   ```console 
  19   17.23   7  4.72   3.66   39.34   23  0
   ```


