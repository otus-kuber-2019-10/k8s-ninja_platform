# Выполнено ДЗ №12

 - [x] Основное ДЗ
 - [x] Задание со :star: | Исправление сетевой политики
 - [x] Задание со :star: | Вывод имени пода вместо IP адреса

## В процессе сделано:
 - Запущен дебаг контейнер в agentless режиме
 ```
 > docker inspect 8a6e2676d0b8
 ...
 "CapAdd": null,
 "CapDrop": null,
 "Capabilities": null,
 ...
 ```
 Версия приложения v0.0.1, а коммит, содержащий добавление капабилитис:
 ```
 CapAdd:      strslice.StrSlice([]string{"SYS_PTRACE", "SYS_ADMIN"}),
 ```
 был релизнут в версии v0.1.1. После обновления `strace` работает как нужно:
 ```
 kubectl debug web --agentless=false --port-forward=true
 pod web PodIP 10.12.1.8, agentPodIP 10.128.0.27
 wait for forward port to debug agent ready...
 Forwarding from 127.0.0.1:10027 -> 10027
 Forwarding from [::1]:10027 -> 10027
 Handling connection for 10027
                             pulling image nicolaka/netshoot:latest...
 latest: Pulling from nicolaka/netshoot
 Digest: sha256:99d15e34efe1e3c791b0898e05be676084638811b1403fae59120da4109368d4
 Status: Image is up to date for nicolaka/netshoot:latest
 starting debug container...
 container created, open tty...
 bash-5.0# strace -c -p1
 strace: Process 1 attached
 ^Cstrace: Process 1 detached
```
 - Запущен `netperf-operator`:
 ```
 k describe netperfs.app.example.com example
 Name:         example
 Namespace:    default
 Labels:       <none>
 Annotations:  kubectl.kubernetes.io/last-applied-configuration:
                {"apiVersion":"app.example.com/v1alpha1","kind":"Netperf","metadata":{"annotations":{},"name":"example","namespace":"default"}}
 API Version:  app.example.com/v1alpha1
 Kind:         Netperf
 Metadata:
   Creation Timestamp:  2020-03-29T19:26:19Z
   Generation:          4
   Resource Version:    41379
   Self Link:           /apis/app.example.com/v1alpha1/namespaces/default/netperfs/example
   UID:                 e007b7d5-09db-48ac-b32f-cd47995c6060
 Spec:
   Client Node:
   Server Node:
 Status:
   Client Pod:          netperf-client-cd47995c6060
   Server Pod:          netperf-server-cd47995c6060
   Speed Bits Per Sec:  8696.76
   Status:              Done
 Events:                <none>
 ```
 - Создана и применена сетевая политика для netperf-client
 В первоначальном варианте наблюдался дроп пакетов
 ```
 > iptables --list -nv | grep DROP
 23  1380 DROP       all  --  *      *       0.0.0.0/0            0.0.0.0/0            /* cali:He8TRqGPuUw3VGwk */
 > iptables --list -nv | grep LOG
 30  1800 LOG        all  --  *      *       0.0.0.0/0            0.0.0.0/0            /* cali:B30DykF1ntLW86eD */ LOG flags 0 level 5 prefix "calico-packet: "
 ```
 - После настройки kubernetes-iptables-tailer мы получаем сообщения о дропе пакетов прямо в ивенты
 ```
 Events:
  Type     Reason      Age   From                                    Message
  ----     ------      ----  ----                                    -------
  Normal   Scheduled   109s  default-scheduler                       Successfully assigned default/netperf-server-0d76dca7165d to gke-infra-infra-eb42c575-hpts
  Normal   Pulled      109s  kubelet, gke-infra-infra-eb42c575-hpts  Container image "tailoredcloud/netperf:v2.7" already present on machine
  Normal   Created     109s  kubelet, gke-infra-infra-eb42c575-hpts  Created container netperf-server-0d76dca7165d
  Normal   Started     108s  kubelet, gke-infra-infra-eb42c575-hpts  Started container netperf-server-0d76dca7165d
  Warning  PacketDrop  107s  kube-iptables-tailer                    Packet dropped when receiving traffic from 10.12.0.18
 ```
 - Исправление сетевой политики: разрешила исходящий и входящий трафик подам, подходящим по селектору
 ```
   ingress:
    - action: Allow
      source:
        selector: app=netperf-operator
    - action: Log
    - action: Deny
  egress:
    - action: Allow
      destination:
        selector: app=netperf-operator
    - action: Log
    - action: Deny
 ```
 - Вывод имени пода вместо IP адреса задается переменной в манифесте даемонсета:
 ```
 ...
  - name: "POD_IDENTIFIER"
    value: "name"
 ...
 default       5s          Warning   PacketDrop         pod/netperf-client-d9cec4059102   Packet dropped when sending traffic to netperf-server-d9cec4059102 (10.12.0.9)
 default       5s          Warning   PacketDrop         pod/netperf-server-d9cec4059102   Packet dropped when receiving traffic from netperf-client-d9cec4059102 (10.12.0.10)
 ```

## Как запустить проект:
```
kubectl apply -f strace/agent_daemonset.yml
kubectl apply -f kit/deploy/
```

## Как проверить работоспособность:
```
kubectl get pods
kubectl describe netperfs.app.example.com example
```

## PR checklist:
 - [x] Выставлен label с номером домашнего задания
