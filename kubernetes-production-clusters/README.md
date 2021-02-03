1. Деплоим виртуалки через terraform
2. Выполняем инструкцию по bootstrap кластера и в итоге получаем:
```
root@master:/home/g192023# kubectl get nodes
NAME      STATUS   ROLES    AGE     VERSION
master    Ready    master   3m49s   v1.17.4
worker1   Ready    <none>   45s     v1.17.4
worker2   Ready    <none>   34s     v1.17.4
worker3   Ready    <none>   29s     v1.17.4
```

3. Задеплоим тестовое приложение
```
root@master:/home/g192023# kubectl get pods
NAME                               READY   STATUS    RESTARTS   AGE
nginx-deployment-c8fd555cc-6xnb7   1/1     Running   0          13s
nginx-deployment-c8fd555cc-974b8   1/1     Running   0          13s
nginx-deployment-c8fd555cc-98d4b   1/1     Running   0          13s
nginx-deployment-c8fd555cc-b4dm8   1/1     Running   0          13s
```

4. Займемся обновлением кластера, после обновления мастера получим следующую конфигурацию:
```
root@master:/home/g192023# kubectl get nodes
NAME      STATUS   ROLES    AGE     VERSION
master    Ready    master   9m31s   v1.18.0
worker1   Ready    <none>   6m27s   v1.17.4
worker2   Ready    <none>   6m16s   v1.17.4
worker3   Ready    <none>   6m11s   v1.17.4
```
Проверим версию kubelet & kube-apiserver
```
root@master:/home/g192023# kubelet --version
Kubernetes v1.18.0

# api server разворачивается из static-manifests by kubelet
cat /etc/kubernetes/manifests/kube-apiserver.yaml
...
image: k8s.gcr.io/kube-apiserver:v1.17.4
...
```
4.1 Обновим оставшиеся компоненты, в этом нам поможет kubeadm
```
kubeadm upgrade plan
COMPONENT   CURRENT       AVAILABLE
Kubelet     3 x v1.17.4   v1.18.1
            1 x v1.18.0   v1.18.1
Upgrade to the latest stable version:
COMPONENT            CURRENT   AVAILABLE
API Server           v1.17.4   v1.18.1
Controller Manager   v1.17.4   v1.18.1
Scheduler            v1.17.4   v1.18.1
Kube Proxy           v1.17.4   v1.18.1
CoreDNS              1.6.5     1.6.7
Etcd                 3.4.3     3.4.3-0

# Проверяем
root@master:/home/g192023# kubeadm version
kubeadm version: &version.Info{Major:"1", Minor:"18", GitVersion:"v1.18.0", GitCommit:"9e991415386e4cf155a24b1da15becaa390438d8", GitTreeState:"clean", BuildDate:"2020-03-25T14:56:30
Z", GoVersion:"go1.13.8", Compiler:"gc", Platform:"linux/amd64"}

kubectl describe pods -n kube-system kube-apiserver-master
Image:         k8s.gcr.io/kube-apiserver:v1.18.0
```

4.2 Приступим к обновлению worker node (через drain, update kubeadm, uncordon):
```
root@master:/home/g192023# kubectl get nodes
NAME      STATUS   ROLES    AGE   VERSION
master    Ready    master   43m   v1.18.0
worker1   Ready    <none>   40m   v1.18.0
worker2   Ready    <none>   40m   v1.18.0
worker3   Ready    <none>   40m   v1.18.0
```
5. Деплой через kubespray:
```
root@node1:~# kubectl get no
NAME    STATUS   ROLES    AGE     VERSION
node1   Ready    master   9m3s    v1.17.4
node2   Ready    <none>   7m24s   v1.17.4
node3   Ready    <none>   7m24s   v1.17.4
node4   Ready    <none>   7m24s   v1.17.4
```

6. Задание со звездочкой: установка кластера с 3 master-нодами и 2 worker нодами
Установку производила через kubespray (без внешнего ЛБ), столкнулась с выдачей сертификатов - погуглив проблему, поставила `chrony` на все машинки для синхронизации времени и все залетело
```
cat inventory.ini
[all]
node1 ansible_host=104.197.40.145 etcd_member_name=etcd1
node2 ansible_host=34.67.16.135 etcd_member_name=etcd2
node3 ansible_host=35.226.182.176 etcd_member_name=etcd3
node4 ansible_host=34.66.22.97
node5 ansible_host=35.223.72.93

# ## configure a bastion host if your nodes are not directly reachable
# bastion ansible_host=x.x.x.x ansible_user=some_user

[kube-master]
node1
node2
node3

[etcd]
node1
node2
node3
...

kubectl get nodes
NAME    STATUS   ROLES    AGE    VERSION
node1   Ready    master   108m   v1.17.4
node2   Ready    master   106m   v1.17.4
node3   Ready    master   106m   v1.17.4
node4   Ready    <none>   104m   v1.17.4
node5   Ready    <none>   104m   v1.17.4

# откопаем конфиг nginx и увидим все три эндпойнта для апи-сервер =)
root@node5:/etc/nginx# cat nginx.conf
error_log stderr notice;

worker_processes 2;
worker_rlimit_nofile 130048;
worker_shutdown_timeout 10s;

events {
  multi_accept on;
  use epoll;
  worker_connections 16384;
}

stream {
  upstream kube_apiserver {
    least_conn;
    server 10.128.0.38:6443;
    server 10.128.0.36:6443;
    server 10.128.0.37:6443;
    }

  server {
    listen        127.0.0.1:6443;
    proxy_pass    kube_apiserver;
    proxy_timeout 10m;
    proxy_connect_timeout 1s;
  }
}

http {
  aio threads;
  aio_write on;
  tcp_nopush on;
  tcp_nodelay on;

  keepalive_timeout 5m;
  keepalive_requests 100;
  reset_timedout_connection on;
  server_tokens off;
  autoindex off;

  server {
    listen 8081;
    location /healthz {
      access_log off;
      return 200;
    }
    location /stub_status {
      stub_status on;
      access_log off;
    }
  }
  }
```