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
   python3 vllm-serverStartupLatency.py $HOME/.kube/config wec1 environment=test vllm-test $HOME/data
   ```

   Below is a detailed explanation of the input parameters:
   - `kubeconfig`: path to the kubeconfig file, e.g., `$HOME/.kube/config`
   - `k8s-context-name`: name of the context for the k8s cluster, e.g., `wec1`
   - `pod-label-selector`: label of the vllm pods, e.g., `environment=test` 
   - `namespace`: namespace for the vllm pods, e.g., `vllm-test`
   - `output-directory`: path to the directory for the output data files, e.g., `$HOME/data`


   The input parameter `kubeconfig` and `k8s-context-name` are optional. Setting both parameters to `None`, we will use the current context set in the kubeconfig file set by the `KUBECONFIG` env variable. For example:

   ```bash 
   python3 vllm-serverStartupLatency.py None None environment=test vllm-test $HOME/data
   ```

   The generated output from the script is tab-delimited file named `vllm-server-startup-latency.txt` with the following structure:

   ```console 
   <pod-name> <engine-initalization-time> <model-loading-time> <graph-capture-time> <api-server-init>
   ```

   For example: 

   ```bash
   cd $HOME/data
   cat vllm-server-startup-latency.txt
   ```
 
   Sample output:

   ```console 
   vllm-opt125m-deployment-vllm-xxx-yyy	 <t1>   <t2>    <t3>    <t4>
   ```

2. Clean up the generated workload Kubernetes API objects from your cluster:

   ```bash 
   kubectl -n <namespace> delete pods -l <pod-label-selector>
   ```

   For example:

   ```console
   kubectl -n vllm-test delete pods -l environment=test
   ```

