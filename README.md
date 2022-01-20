# PoC to demonstrate problems with Ingress upgrades when using Metacontroller

## Instructions

Prerequisites:
* Minikube
* Helm

1. Start Minikube

It's important that we install the version that supports `Ingress` resource in both `extensions/v1beta1` and `networking.k8s.io/v1`

```
$ minikube start --kubernetes-version=v1.20.2
```

2. Install Metacontroller:

```
git clone https://github.com/metacontroller/metacontroller.git
cd  metacontroller
helm package deploy/helm/metacontroller --destination deploy/helm
helm install metacontroller deploy/helm/metacontroller-v*.tgz
```

3. Create relevant resources:

```
kubectl create configmap hello-controller --from-file=sync.py
kubectl create -f crd.yml -f controller.yml -f webhook.yml -f hello_old.yml
```

4. Ensure Ingress object is present:
```
$ kubectl get ing -A                                                                                minikube
NAMESPACE   NAME        CLASS    HOSTS           ADDRESS   PORTS   AGE
default     ingress-0   <none>   weirdhost.dev             80      5s
```

5. Bump the version of the Ingress returned:
```
$ kubectl apply -f hello_new.yml
```

Look at the logs of Metacontroller to notice the infinite loop:
```
$ kubectl logs -f metacontroller-0
```

Look at Ingress object (especially at the AGE - a new one is constant):

```
$ kubectl get ing -A                                                                                minikube
NAMESPACE   NAME        CLASS    HOSTS           ADDRESS   PORTS   AGE
default     ingress-0   <none>   weirdhost.dev              80      0s
```