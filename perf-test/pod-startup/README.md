## Measure VLLM PodStartupLatency

### Prerequisites
- A running Kubernetes (K8s) environment with GPUs


In this tutorial, we will use [clusterloader2](https://github.com/kubernetes/perf-tests/tree/master/clusterloader2) tool to measure the VLLM pod startup latency as following:

#### 1. Clone the following clusterloader2 repo:

   ```bash 
   git clone -b vllm-exp https://github.com/dumb0002/perf-tests.git
   ```

#### 2. Configure clusterloader2:

   Starting from a local directory containing this repo, run the following script to set-up your environment:

   a) cd into the `/production-stack/perf-test` directory from your local copy of the vllm production stack repo, for example:

   ```bash 
   cd $HOME/production-stack/perf-test
   ```

   b) set-up your environment:

   First, set the variable `CL2_DIR` to the path of the subdirectory `clusterloader2/` of the cloned repo in step 1. For example: 

   ```bash 
   export CL2_DIR=$HOME/perf-tests/clusterloader2
   ```

   Then, run the set-up script as following:
   ```bash 
   ./setup-clusterloader2.sh
   ```

#### 3. Configure the parameters of your workload:  

   a) cd into the load configuration directory.

   ```bash 
   cd  $CL2_DIR/testing/load/
   ```
  
   b) configure the parameters to create the workload traffic.
   
   ```bash 
   vi vllm-config.yaml
   ``` 

   More specifically, configure the following parameter: 

   - *namespace*: name prefix for the target namespace (e.g., `vllm-test`)
   - *deploymentReplicas*: number of VLLM deployment replicas (default value: `1`)
   - *modelName*: name of the VLLM model to be served by the instance (default value: `gpt2`)
   - *modelRepo*: repo of the LLM model (default value: `openai-community/gpt2`)
   - *podReplicas*: number of pod replicas per deployment (default value: `1`)

   
#### 4. Deploy your first VLLM app workload and measure the PodStartupLatency:

   Use a command of the following form to create the workload. The value given to the `--kubeconfig` flag should be a pathname of the kubeconfig of your k8s cluster.

   ```bash
   cd $CL2_DIR
   go run cmd/clusterloader.go --testconfig=./testing/load/vllm-config.yaml --kubeconfig=${KUBECONFIG:-$HOME/.kube/config} --provider=local --v=2
   ```

   At the end of clusterloader output you should see pod startup latency:

   ```console
   {
      "data": {
        "Perc50": 28571.352,
        "Perc90": 28571.352,
        "Perc99": 28571.352
      },
      "unit": "ms",
      "labels": {
        "Metric": "pod_startup"
      }
    },
   ```

   `pod_startup` measures time since pod was created until it was observed via watch as running. However, this time does not include the time it takes to bring up the vllm server with a model. More precisely, how long it takes for a `running` pod to reach the `ready` state

   You should also see that test succeeded:

   ```console
    --------------------------------------------------------------------------------
    Test Finished
    Test: ./testing/load/vllm-config.yaml
    Status: Success
    --------------------------------------------------------------------------------
   ```

