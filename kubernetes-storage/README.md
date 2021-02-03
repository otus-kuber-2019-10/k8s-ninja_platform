1. Для начала задеплоим CRDs для [CSI VolumeSnapshot beta](https://github.com/kubernetes-csi/external-snapshotter) и для Snaphot Controller
```
SNAPSHOTTER_VERSION=v2.0.1

# Apply VolumeSnapshot CRDs
kubectl apply -f https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/${SNAPSHOTTER_VERSION}/config/crd/snapshot.storage.k8s.io_volumesnapshotclasses.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/${SNAPSHOTTER_VERSION}/config/crd/snapshot.storage.k8s.io_volumesnapshotcontents.yaml

# Create snapshot controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/${SNAPSHOTTER_VERSION}/deploy/kubernetes/snapshot-controller/rbac-snapshot-controller.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/${SNAPSHOTTER_VERSION}/deploy/kubernetes/snapshot-controller/setup-snapshot-controller.yaml
```

Дождемся успешного запуска `snaphot-controller`:
```
k get pods
NAME                    READY   STATUS    RESTARTS   AGE
snapshot-controller-0   1/1     Running   0          22s
```
2. Для деплоя CSI воспользуемся инструкцией из репозитория (подключим его как submodule в папку `hw`)
```
cd csi-driver-host-path
deploy/kubernetes-latest/deploy-hostpath.sh
```
Убедимся, что деплой закончился успешно:
```
NAME                         READY   STATUS    RESTARTS   AGE
csi-hostpath-attacher-0      1/1     Running   0          85s
csi-hostpath-provisioner-0   1/1     Running   0          83s
csi-hostpath-resizer-0       1/1     Running   0          82s
csi-hostpath-snapshotter-0   1/1     Running   0          82s
csi-hostpath-socat-0         1/1     Running   0          81s
csi-hostpathplugin-0         3/3     Running   0          84s
```
3. Создадим PVC и Pod с использованием этого PVC. Стоит отметить, что в любом случае необходимо создать объект типа `StorageClass` с использованием установленного CSI.
```
> k get sc
csi-hostpath-sc      hostpath.csi.k8s.io     Delete          Immediate              true                   39s
standard (default)   rancher.io/local-path   Delete          WaitForFirstConsumer   false                  15m

> k get pvc
NAME          STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS      AGE
storage-pvc   Bound    pvc-3730cb4b-99e0-4798-93a2-166a5753ca3d   1Gi        RWO            csi-hostpath-sc   5s

> k get pv
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM                 STORAGECLASS      REASON   AGE
pvc-3730cb4b-99e0-4798-93a2-166a5753ca3d   1Gi        RWO            Delete           Bound    default/storage-pvc   csi-hostpath-sc            43s
```
4. Проверим, что работает, как нужно:
```
k exec -ti storage-pod sh
/ # touch data/test.txt
/ # echo "hello" > data/test.txt
/ # exit

kubectl exec -it $(kubectl get pods --selector app=csi-hostpathplugin -o jsonpath='{.items[*].metadata.name}') -c hostpath /bin/sh
/ # cd csi-data-dir/868dc843-783e-11ea-836d-86cbe24e9ca2/
/csi-data-dir/868dc843-783e-11ea-836d-86cbe24e9ca2 # ls
test.txt
/csi-data-dir/868dc843-783e-11ea-836d-86cbe24e9ca2 # cat test.txt
hello
/csi-data-dir/868dc843-783e-11ea-836d-86cbe24e9ca2 #
```
