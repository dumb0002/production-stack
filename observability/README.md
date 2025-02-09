# Observability dashboard

![image](https://github.com/user-attachments/assets/225feb01-ac0f-4bf9-9da3-7bf955b2aa56)

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


## Access the Grafana dashboard

1. If using plain K8s clusters:
   
   Forward the Grafana dashboard port to the local node-port

   ```bash
   sudo kubectl --namespace monitoring port-forward svc/kube-prom-stack-grafana 3000:80 --address 0.0.0.0
   ```

   Open the webpage at `http://<IP of your node>:3000` to access the Grafana web page. The default user name is `admin` and the password can be configured in `values.yaml` (default is `prom-operator`).

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
