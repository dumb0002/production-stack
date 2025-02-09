## Deploying the stack via Kubectl

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Prerequisites](#prerequisites)
- [Steps](#steps)
  - [1. Deploy VLLM router](#1-deploy-vllm-router)
  - [2. Deploy VLLM app](#2-deploy-vllm-app)
  - [3. Check GPUs allocated to the deployed VLLM application](#3-check-gpus-allocated-to-the-deployed-vllm-application)
  - [4. Send a Query to the Stack](#4-send-a-query-to-the-stack)
    - [4.1. Forward the Service Port](#41-forward-the-service-port)
    - [4.2. Query the OpenAI-Compatible API to list the available models](#42-query-the-openai-compatible-api-to-list-the-available-models)
    - [4.3. Query the OpenAI Completion Endpoint](#43-query-the-openai-completion-endpoint)
  - [5. Uninstall](#5-uninstall)


### Prerequisites

- A running Kubernetes (K8s) environment with GPUs

### Steps

Each component of the vLLM Production Stack can be individually deployed using yaml as following:

Starting from a local directory containing this git repo:

#### 1. Deploy VLLM router

   First, set the variable `NAMESPACE` to the name of a target namespace (e.g., `vllm-test`). For example:

   ```bash
   NS=vllm-test
   ```

   Then, deploy the router app: 

   ```bash
   kubectl create ns vllm-test
   sed s/%TARGET_NS%/$NS/g router-master.yaml | kubectl -n $NS apply -f -
   ```

   Optionally, check the deployment of the router app:

   ```bash
   kubectl -n $NS get all
   ```

   Sample output:

   ```console
    NAME                                         READY   STATUS    RESTARTS   AGE
    pod/vllm-deployment-router-xx-yy              1/1     Running     0       12s

    NAME                          TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)   AGE
    service/vllm-router-service   ClusterIP   172.21.165.147     <none>       80/TCP    19s

    NAME                                     READY   UP-TO-DATE   AVAILABLE   AGE
    deployment.apps/vllm-deployment-router    1/1      1            1         19s

    NAME                                               DESIRED   CURRENT   READY   AGE
    replicaset.apps/vllm-deployment-router-xx           1         1         1       12s
   ```


#### 2. Deploy VLLM app

   First, set the variables `INSTANCE_NAME` and `MODEL_URL` to the given name and model URL for a VLLM instance. For example:

   ```bash
   INSTANCE_NAME=vllm-1
   MODEL_URL=facebook/opt-125m
   ```

   Then, deploy the vllm instance in the target namespace (e.g., `vllm-test`): 

   ```bash
   sed -e s,%INSTANCE_NAME%,$INSTANCE_NAME,g -e s,%MODEL_URL%,$MODEL_URL,g  vllm-master.yaml | kubectl -n $NS apply -f -
   ```

   Deploy a second vllm instance with a `gpt2` model:

   ```bash
   INSTANCE_NAME=vllm-2
   MODEL_URL=openai-community/gpt2
   sed -e s,%INSTANCE_NAME%,$INSTANCE_NAME,g -e s,%MODEL_URL%,$MODEL_URL,g  vllm-master.yaml | kubectl -n $NS apply -f -
   ```
   
   Optionally, check the deployment of the vllm apps:

   ```bash
   kubectl -n $NS get pods -l environment=test
   ``` 

   Sample output:
   ```console
   NAME                                      READY   STATUS    RESTARTS   AGE
   vllm-1-deployment-vllm-abcd-yyy           1/1     Running     0        6m28s
   vllm-2-deployment-vllm-abcd-xyx           1/1     Running     0        112s
   ```

#### 3. Check GPUs allocated to the deployed VLLM application

In certain situations, if your cluster offers various GPU types, you can determine which GPU was chosen for a deployed VLLM instance with a specific model by using the tool [nvidia-smi](https://developer.download.nvidia.com/compute/DCGM/docs/nvidia-smi-367.38.pdf).

This can be done with any pod capable of utilizing a GPU and with the open source vllm image from `vllm/vllm-openai:version`. Proceed as following:

Exec into the vllm pod and list the NVIDIA GPUs in the system:

a) For `vllm-1` instance:

   ```bash
   kubectl -n $NS exec -it vllm-1-deployment-vllm-abcd-yyy -- nvidia-smi -L
   ```
   Sample output:

   ```console
   GPU 0: Tesla V100-PCIE-16GB (UUID: GPU-xxxxxx-d4ef-5ee2-3995-yyyyyyy)
   ```

b) For `vllm-2` instance:

   ```bash
   kubectl -n $NS exec -it vllm-2-deployment-vllm-abcd-xyx -- nvidia-smi -L
   ```
   Sample output:

   ```console
   GPU 0: Tesla V100-PCIE-16GB (UUID: GPU-yyyyyy-8224-b69d-3b55-xxxxx)
   ```

Furthermore, you can also query for more detailed information about NVIDIA GPUs in the system (i.e, memory usage, etc.):

```bash
kubectl -n $NS exec -it vllm-1-deployment-vllm-abcd-yyy -- nvidia-smi
```

Sample output:

```console
Mon Feb 10 11:49:44 2025       
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 550.54.15              Driver Version: 550.54.15      CUDA Version: 12.4     |
|-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  Tesla V100-PCIE-16GB           On  |   00000000:00:1E.0 Off |                    0 |
| N/A   31C    P0             38W /  250W |   14555MiB /  16384MiB |      0%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+
                                                                                         
+-----------------------------------------------------------------------------------------+
| Processes:                                                                              |
|  GPU   GI   CI        PID   Type   Process name                              GPU Memory |
|        ID   ID                                                               Usage      |
|=========================================================================================|
+-----------------------------------------------------------------------------------------+
```


#### 4. Send a Query to the Stack

#### 4.1: Forward the Service Port

Expose the `vllm-router-service` port to the host machine:

```bash
sudo kubectl -n $NS port-forward svc/vllm-router-service 30080:80
```

#### 4.2: Query the OpenAI-Compatible API to list the available models

Open a new terminal and test the stack's OpenAI-compatible API by querying the available models:

```bash
curl -o- http://localhost:30080/models
```

Expected output:

```json
{
  "object": "list",
  "data": [
    {
      "id": "facebook/opt-125m",
      "object": "model",
      "created": 1739156592,
      "owned_by": "vllm",
      "root": null
    },
    {
      "id": "openai-community/gpt2",
      "object": "model",
      "created": 1739156824,
      "owned_by": "vllm",
      "root": null
    }
  ]
}
```

#### 4.3: Query the OpenAI Completion Endpoint

a) Send a query to the OpenAI `/completion` endpoint to generate a completion for a prompt using the `facebook/opt-125m` model:

```bash
curl -X POST http://localhost:30080/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "facebook/opt-125m",
    "prompt": "The capital of France is,",
    "max_tokens": 10
  }' \
  | jq
```

Sample output:

```json
{
  "id": "cmpl-8e6eb10325484c52ab5e7666d452c14c",
  "object": "text_completion",
  "created": 1739157366,
  "model": "facebook/opt-125m",
  "choices": [
    {
      "index": 0,
      "text": " surprisingly, a French swim pool. Seriously, no",
      "logprobs": null,
      "finish_reason": "length",
      "stop_reason": null,
      "prompt_logprobs": null
    }
  ],
  "usage": {
    "prompt_tokens": 7,
    "total_tokens": 17,
    "completion_tokens": 10,
    "prompt_tokens_details": null
  }
}
```

b) Send a query to the OpenAI `/completion` endpoint to generate a completion for a prompt using the `openai-community/gpt2` model:

```bash
curl -s http://localhost:30080/completions \
  -H "Content-Type: application/json" \
  -d '{
        "model": "openai-community/gpt2",
        "prompt": "The capital of France is",
        "max_tokens": 17,
        "temperature": 0.2
      }' \
  | jq
```

Sample output:

```json
{
  "id": "cmpl-0d5c63917f0f4ebb8eca62170fd1b4a4",
  "object": "text_completion",
  "created": 1739157195,
  "model": "openai-community/gpt2",
  "choices": [
    {
      "index": 0,
      "text": " the capital of the French Republic. The French Republic is the largest state in the world",
      "logprobs": null,
      "finish_reason": "length",
      "stop_reason": null,
      "prompt_logprobs": null
    }
  ],
  "usage": {
    "prompt_tokens": 5,
    "total_tokens": 22,
    "completion_tokens": 17,
    "prompt_tokens_details": null
  }
}
```

This demonstrates the model generating a continuation for the provided prompt for both `facebook/opt-125m` and `openai-community/gpt2` models.

#### 5. Uninstall

To remove the deployment, run:

```bash
kubectl -n $NS delete -f router-master.yaml
kubectl -n $NS delete all -l environment=test
kubectl delete ns $NS
```



