# Observability dashboard

<p align="center">
  <img src="https://github.com/user-attachments/assets/05766673-c449-4094-bdc8-dea6ac28cb79" alt="Grafana dashboard to monitor the deployment" width="80%"/>
</p>

## Deploy the observability stack

1. If using plain K8s clusters:

   The observability stack is based on [kube-prom-stack](https://github.com/prometheus-community/helm-charts/blob/main/charts/kube-prometheus-stack/README.md).

   To launch the observability stack:

   ```bash
   sudo bash install.sh
   ```

   After installing, the dashboard can be accessed through the service `service/kube-prom-stack-grafana` in the `monitoring` namespace.

2. If using OpenShift clusters:

   Follow the instructions [here](INSTRUCTIONS.md) if you need to set up Grafana on Red Hat OpenShift Container Platform (OCP).

   Then, configure Prometheus to scrape metrics from a running vllm instance:  

   ```bash
   kubectl -n k -n openshift-monitoring create -f vllm-sm.yaml
   ```

   Optionally, check the prometheus service monitor object was created:

   ```bash
   kubectl -n openshift-monitoring get servicemonitor -l app=vllm
   ```

   Sample output:

   ```bash
      NAME                          AGE
      test-vllm-monitor2            6d3h
   ```
   
   Lastly, Grafana dashboard can be accessed through the openshift route in the Grafana namespace. 


## Access the Grafana & Prometheus dashboard

1. If using plain K8s clusters:
   
   Forward the Grafana dashboard port to the local node-port

```bash
kubectl --namespace monitoring port-forward svc/kube-prom-stack-grafana 3000:80 --address 0.0.0.0
```

Forward the Prometheus dashboard

```bash
kubectl --namespace monitoring port-forward prometheus-kube-prom-stack-kube-prome-prometheus-0 9090:9090
```
   ```bash
   sudo kubectl --namespace monitoring port-forward svc/kube-prom-stack-grafana 3000:80 --address 0.0.0.0
   ```

   Open the webpage at `http://<IP of your node>:3000` to access the Grafana web page. The default user name is `admin` and the password can be configured in `values.yaml` (default is `prom-operator`).

Import the dashboard using the `vllm-dashboard.json` in this folder.

## Use Prometheus Adapter to export vLLM metrics

The vLLM router can export metrics to Prometheus using the [Prometheus Adapter](https://github.com/prometheus-community/helm-charts/tree/main/charts/prometheus-adapter).
When running the `install.sh` script, the Prometheus Adapter will be installed and configured to export the vLLM metrics.

We provide a minimal example of how to use the Prometheus Adapter to export vLLM metrics. See [prom-adapter.yaml](prom-adapter.yaml) for more details.

The exported metrics can be used for different purposes, such as horizontal scaling of the vLLM deployments.

To verify the metrics are being exported, you can use the following command:

```bash
kubectl get --raw /apis/custom.metrics.k8s.io/v1beta1/namespaces/default/metrics | jq | grep vllm_num_requests_waiting -C 10
```

You should see something like the following:

```json
    {
      "name": "namespaces/vllm_num_requests_waiting",
      "singularName": "",
      "namespaced": false,
      "kind": "MetricValueList",
      "verbs": [
        "get"
      ]
    }
```

The following command will show the current value of the metric:

```bash
kubectl get --raw /apis/custom.metrics.k8s.io/v1beta1/namespaces/default/metrics/vllm_num_requests_waiting | jq
```

The output should look like the following:

```json
{
  "kind": "MetricValueList",
  "apiVersion": "custom.metrics.k8s.io/v1beta1",
  "metadata": {},
  "items": [
    {
      "describedObject": {
        "kind": "Namespace",
        "name": "default",
        "apiVersion": "/v1"
      },
      "metricName": "vllm_num_requests_waiting",
      "timestamp": "2025-03-02T01:56:01Z",
      "value": "0",
      "selector": null
    }
  ]
}
```

## Uninstall the observability stack

```bash
sudo bash uninstall.sh
```
2. If using OpenShift clusters:
   
   Get the URL for Grafana:

   ```bash
   oc -n grafana-operator get route grafana-ui -o jsonpath='{"https://"}{.spec.host}{"\n"}'
   ```

   Browse to the URL from above, and sign in with default administrator credentials. 
   
   You can obtain the default administrator from the following secret:

     ```bash
     oc -n grafana-operator get secret grafana-a-admin-credentials -o yaml
     ```

   Then, use `base64 -d` to decode and obtain the raw text of the credentials

3. Create the Grafana dashboard for vllm:

   ```bash
   kubectl  -n grafana-operator create -f vllm-dashboard.yaml
   ```
   The above command uses the dashboard `vllm-dashboard.yaml` in this folder.
