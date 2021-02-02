import kopf
import logging
import yaml
import kubernetes
import time
from jinja2 import Environment, FileSystemLoader

def wait_until_job_end(jobname):
    api = kubernetes.client.BatchV1Api()
    job_finished = False
    jobs = api.list_namespaced_job('default')
    while (not job_finished) and \
            any(job.metadata.name == jobname for job in jobs.items):
        time.sleep(1)
        jobs = api.list_namespaced_job('default')
        for job in jobs.items:
            if job.metadata.name == jobname:
                print(f"job with { jobname }  found,wait untill end")
                if job.status.succeeded == 1:
                    print(f"job with { jobname }  success")
                    job_finished = True
    return True


def render_template(filename, vars_dict):
    env = Environment(loader=FileSystemLoader('./templates'))
    template = env.get_template(filename)
    yaml_manifest = template.render(vars_dict)
    json_manifest = yaml.load(yaml_manifest)
    return json_manifest


def delete_success_jobs(mysql_instance_name):
    print("start deletion")
    api = kubernetes.client.BatchV1Api()
    jobs = api.list_namespaced_job('default')
    for job in jobs.items:
        jobname = job.metadata.name
        if (jobname == f"backup-{mysql_instance_name}-job") or \
                (jobname == f"restore-{mysql_instance_name}-job"):
            if job.status.succeeded == 1:
                api.delete_namespaced_job(jobname,
                                        'default',
                                        propagation_policy='Background')


@kopf.on.create('otus.homework', 'v1', 'mysqls')
# Функция, которая будет запускаться при создании объектов тип MySQL:
def mysql_on_create(body, spec, status, logger, **kwargs):
    name = body['metadata']['name']
    image = body['spec']['image']
    password = body['spec']['password']
    database = body['spec']['database']
    storage_size = body['spec']['storage_size']

    # Генерируем JSON манифесты для деплоя
    persistent_volume = render_template('mysql-pv.yml.j2',
                                        {'name': name,
                                        'storage_size': storage_size})
    persistent_volume_claim = render_template('mysql-pvc.yml.j2',
                                            {'name': name,
                                            'storage_size': storage_size})
    service = render_template('mysql-service.yml.j2', {'name': name})

    deployment = render_template('mysql-deployment.yml.j2', {
        'name': name,
        'image': image,
        'password': password,
        'database': database})
    restore_job = render_template('restore-job.yml.j2', {
        'name': name,
        'image': image,
        'password': password,
        'database': database})

    # Определяем, что созданные ресурсы являются дочерними к управляемому CustomResource:
    kopf.append_owner_reference(persistent_volume, owner=body)
    kopf.append_owner_reference(persistent_volume_claim, owner=body)  # addopt
    kopf.append_owner_reference(service, owner=body)
    kopf.append_owner_reference(deployment, owner=body)
    # kopf.append_owner_reference(restore_job, owner=body)
    # ^ Таким образом при удалении CR удалятся все, связанные с ним pv,pvc,svc, deployments

    api = kubernetes.client.CoreV1Api()
    # Создаем mysql PV:
    api.create_persistent_volume(persistent_volume)
    # Создаем mysql PVC:
    api.create_namespaced_persistent_volume_claim('default', persistent_volume_claim)
    # Создаем mysql SVC:
    api.create_namespaced_service('default', service)

    # Создаем mysql Deployment:
    api = kubernetes.client.AppsV1Api()
    api.create_namespaced_deployment('default', deployment)
    # Пытаемся восстановиться из backup
    try:
        api = kubernetes.client.BatchV1Api()
        api.create_namespaced_job('default', restore_job)
        jobs = api.list_namespaced_job('default')
        time.sleep(20)
        for job in jobs.items:
            if "restore" in job.metadata.name and job.status.succeeded == 1:
                body["status"] = dict(message="mysql-instance created with restore-job")
            else:
                kopf.event(body,
                    type='Warning',
                    reason='RestoreDB',
                    message='Database job didnt completed successfully within 20 sec, action required!')
                body["status"] = dict(message="mysql-instance created without restore-job")
    except kubernetes.client.rest.ApiException:
        body["status"] = dict(message="mysql-instance created without restore-job")
        pass

    # Cоздаем PVC  и PV для бэкапов:
    try:
        backup_pv = render_template('backup-pv.yml.j2', {'name': name})
        api = kubernetes.client.CoreV1Api()
        print(api.create_persistent_volume(backup_pv))
        api.create_persistent_volume(backup_pv)
    except kubernetes.client.rest.ApiException:
        pass

    try:
        backup_pvc = render_template('backup-pvc.yml.j2', {'name': name})
        api = kubernetes.client.CoreV1Api()
        api.create_namespaced_persistent_volume_claim('default', backup_pvc)
    except kubernetes.client.rest.ApiException:
        pass

    return body["status"]

@kopf.on.delete('otus.homework', 'v1', 'mysqls')
def delete_object_make_backup(body, **kwargs):
    name = body['metadata']['name']
    image = body['spec']['image']
    password = body['spec']['password']
    database = body['spec']['database']

    delete_success_jobs(name)

    # Cоздаем backup job:
    api = kubernetes.client.BatchV1Api()
    backup_job = render_template('backup-job.yml.j2', {
        'name': name,
        'image': image,
        'password': password,
        'database': database})
    api.create_namespaced_job('default', backup_job)
    wait_until_job_end(f"backup-{name}-job")
    return {'message': "mysql and its children resources deleted"}

@kopf.on.update('otus.homework', 'v1', 'mysqls')
def update_psswd(body, spec, diff, status, logger, **kwargs):
    name = body['metadata']['name']
    image = body['spec']['image']
    password = body['spec']['password']
    database = body['spec']['database']
    delete_success_jobs(name)
    # call tuple element
    if diff[0][1][1] == "password":
        logging.info(diff)
        change_pswd_job = render_template('change-pswd-job.yml.j2', {
            'name': name,
            'image': image,
            'old_password': diff[0][2],
            'new_password': diff[0][3],
            'database': database})
        api = kubernetes.client.BatchV1Api()
        try:
            restore_job = render_template('restore-job.yml.j2', {
            'name': name,
            'image': image,
            'password': password,
            'database': database})

            backup_job = render_template('backup-job.yml.j2', {
            'name': name,
            'image': image,
            'password': password,
            'database': database})

            api = kubernetes.client.BatchV1Api()
            api.delete_namespaced_job(restore_job["metadata"]["name"],"default")
        except:
            pass

        try:
            api.create_namespaced_job('default', change_pswd_job)
            if wait_until_job_end(f"change-pswd-{name}-job"):
                kopf.event(body,
                        type='Normal',
                        reason='PasswordChange',
                        message='Database password has been changed recently')
        except:
            api.delete_namespaced_job(change_pswd_job["metadata"]["name"],"default")
            time.sleep(5)
            api.create_namespaced_job('default', change_pswd_job)
            if wait_until_job_end(f"change-pswd-{name}-job"):
                kopf.event(body,
                        type='Normal',
                        reason='PasswordChange',
                        message='Database password has been changed recently')
                api.delete_namespaced_job(change_pswd_job["metadata"]["name"],"default")

    # update deployment manifest
    deployment = render_template('mysql-deployment.yml.j2', {
        'name': name,
        'image': image,
        'password': password,
        'database': database})
    api = kubernetes.client.AppsV1Api()
    api.patch_namespaced_deployment(deployment["metadata"]["name"],"default",deployment)