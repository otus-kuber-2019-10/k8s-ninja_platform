# Выполнено ДЗ №9

 - [x] Основное ДЗ

## В процессе сделано:
 - Задеплоен consul в HA
 - Задеплоен vault в HA
 - Vault был unsealed
```
kubectl exec -it vault-2 -- vault status
Key                    Value
---                    -----
Seal Type              shamir
Initialized            true
Sealed                 false
Total Shares           1
Threshold              1
Version                1.3.2
Cluster Name           vault-cluster-d384df8a
Cluster ID             8ddaece0-c6b2-5d46-737f-c7aa3b7111f4
HA Enabled             true
HA Cluster             https://10.12.2.4:8201
HA Mode                standby
Active Node Address    http://10.12.2.4:8200
```
 - Login в Vault с использованием root пароля
```
kubectl exec -it vault-0 -- vault login
Token (will be hidden):
Key                  Value
---                  -----
token                s.KrAmNNzr6ts5weZ12AuKbyru
token_accessor       2OoXjpOQGfgQooXL029dXGKK
token_duration       ∞
token_renewable      false
token_policies       ["root"]
identity_policies    []
policies             ["root"]
```
 - Завели тестовые секреты и получили их из Vault
```
kubectl exec -it vault-0 -- vault kv get otus/otus-rw/config
====== Data ======
Key         Value
---         -----
username    otus
kubectl exec -it vault-0 -- vault read otus/otus-ro/config
Key                 Value
---                 -----
refresh_interval    768h
username            otus
```
 - Включим авторизацию через k8s
```
kubectl exec -it vault-0 -- vault auth list
Path           Type          Accessor                    Description
----           ----          --------                    -----------
kubernetes/    kubernetes    auth_kubernetes_03ede639    n/a
token/         token         auth_token_d5843e8a         token based credentials
```
 - запустим пример из vault-guides и проверим `index.html`
```
root@vault-agent-example:/usr/share/nginx/html# cat index.html
  <html>
  <body>
  <p>Some secrets:</p>
  <ul>
  <li><pre>username: otus</pre></li>
  <li><pre>password: <no value></pre></li>
  </ul>

  </body>
  </html>
```
 - выдадим и ревоукним сертификат
```
kubectl exec -it vault-0 -- vault write pki_int/issue/example-dot-ru common_name="gitlab.example.ru" ttl="24h"
Key                 Value
---                 -----
ca_chain            [-----BEGIN CERTIFICATE-----
MIIDnDCCAoSgAwIBAgIUCzHmvS4BKEtnB+I2r2fHU9Tmr5wwDQYJKoZIhvcNAQEL
BQAwFTETMBEGA1UEAxMKZXhhbXBsZS5ydTAeFw0yMDAyMjQxNjQ2NDJaFw0yNTAy
MjIxNjQ3MTJaMCwxKjAoBgNVBAMTIWV4YW1wbGUucnUgSW50ZXJtZWRpYXRlIEF1
dGhvcml0eTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAO1wwNIwRa8t
Iz4tG29+OgMwdnCUTK9xjSLsr/cMZg48KHaT0zLCOBSELjtH5hTXgNBZ3Q8cEb/0
MfId2pwkDOepyguq7bnHk8Wmptk+eKDW8EGvsp6sYWzbZu207oZwlOt9cDMbMec5
y74TQtM3J5aUAZmJ+zyTzi5GMjgbZdKgLbsamfachbMXbAr59jC/jFE/ZR/IbEzM
CUiMjvoWyEC4G9ImRyZZIUMFwLIdUK2l1Pvf/vKb0AOfhjkU2cAGo8JupB5lg8MI
Nc2Da1sAkDQq6ZzqS9Max0cD3AbxUeDjBqmpSNyw4H8N1z4gu1fxBNGpl6WiGCNc
JJUld5R2nR8CAwEAAaOBzDCByTAOBgNVHQ8BAf8EBAMCAQYwDwYDVR0TAQH/BAUw
AwEB/zAdBgNVHQ4EFgQU9TqAnPFrj6pFKbgfwVsQI9uj05MwHwYDVR0jBBgwFoAU
5jlDGb3703SdZOGFvfZPB6puRMAwNwYIKwYBBQUHAQEEKzApMCcGCCsGAQUFBzAC
hhtodHRwOi8vdmF1bHQ6ODIwMC92MS9wa2kvY2EwLQYDVR0fBCYwJDAioCCgHoYc
aHR0cDovL3ZhdWx0OjgyMDAvdjEvcGtpL2NybDANBgkqhkiG9w0BAQsFAAOCAQEA
Zi+z9smEuszE/dkOFzV4vjs10voMKHyNmsqPhKAmVavcRYxoSiT2L48t8PDFMfHS
3byTiytPcRfdnLPAW5b+qTGdF9EqgBoQ/JR9LBeJKX//6BOKpJzMvSSsJW7x/Dz5
RCjz1kngD9PhRizx8F0f2+e+ddtADHEZJwwlknQYUGOqfGYvBmXHDT63k42UtIy+
WfkuAyJXpKRyktVgTbCKLXb6IQC4Lz+XqDCHyT9wugcD6mjfxJbaOFuGz1AOg07u
Tb5qBsj51bP4QnniZi8eHLwi45+aLoj9tTURPkSGunf20wFRepu6SIoet0CBbTom
WGEqFtLvcRpJGkFXnWHV2A==
-----END CERTIFICATE-----]
certificate         -----BEGIN CERTIFICATE-----
MIIDZzCCAk+gAwIBAgIUWpJpVPun5bD6ImOmqvJaEyoRT1UwDQYJKoZIhvcNAQEL
BQAwLDEqMCgGA1UEAxMhZXhhbXBsZS5ydSBJbnRlcm1lZGlhdGUgQXV0aG9yaXR5
MB4XDTIwMDIyNDE2NTQxN1oXDTIwMDIyNTE2NTQ0NlowHDEaMBgGA1UEAxMRZ2l0
bGFiLmV4YW1wbGUucnUwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDA
fXNuFlpEnsWognYC36SVPrLVZ8KxYy+E28G6xKo5LEBKmiO8nPALpFG1Tf+I6TXT
9SdGO3mog2TgwlOa7h/rFHktOi4KB8MSx0kimlsFWQkpk0UX9Dcp/AO6QUywS0V3
Y2be/PC2nIfpx6cEbzGUWv6PTStK3TwzJS0rJ+6+8xWMZUfW/hPtsWD1Gj0L16Ec
sEzSRQRuvIfjGChmPp25TRxlpkwKwuqlO2MAs0+poGFmoW1nadh4o50shtEbOoKw
s0Uh75KX2oOjahZwscwVY8TYHI5Gp8hvfDyHMfRLykPziG3e2PtYX0TR9H9O+0kQ
KEjZMJ5kLT39AU7ve/bRAgMBAAGjgZAwgY0wDgYDVR0PAQH/BAQDAgOoMB0GA1Ud
JQQWMBQGCCsGAQUFBwMBBggrBgEFBQcDAjAdBgNVHQ4EFgQUsEl9Yadmw6tZetrm
zugYp3xo8UIwHwYDVR0jBBgwFoAU9TqAnPFrj6pFKbgfwVsQI9uj05MwHAYDVR0R
BBUwE4IRZ2l0bGFiLmV4YW1wbGUucnUwDQYJKoZIhvcNAQELBQADggEBAEAoWZtx
c3lzIOmCsJc+4pkMFb3j6X7QKBXz4AxP3HnglajbBkG18fLDjbiPWETGHgRuA2c2
VF1HsejI01F71rJdF1kKQ1yQz9X5Cv62pebeDPE6oNYAMuy8eBYmR8k+UtXLhy8h
GsgthgrVIsINJUTrL8FkINACk4bAVLMg3pOcBMDN42tC/mu/eIEgelTBBKHqALSS
AXgcYFK0CGUzpqCnFmKdaXaYtTX0Ra2jcq1XSDIpdZM4JXEI03a7Y7vD3HiWz8WI
tSUlKct3zhmyP8S9RZVq0lCKYF9ncseS7QM2CoEnJL2lvgizMOnmHG5YXbdQV8yZ
g/S2AjKdhyi3J14=
-----END CERTIFICATE-----
expiration          1582649686
issuing_ca          -----BEGIN CERTIFICATE-----
MIIDnDCCAoSgAwIBAgIUCzHmvS4BKEtnB+I2r2fHU9Tmr5wwDQYJKoZIhvcNAQEL
BQAwFTETMBEGA1UEAxMKZXhhbXBsZS5ydTAeFw0yMDAyMjQxNjQ2NDJaFw0yNTAy
MjIxNjQ3MTJaMCwxKjAoBgNVBAMTIWV4YW1wbGUucnUgSW50ZXJtZWRpYXRlIEF1
dGhvcml0eTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAO1wwNIwRa8t
Iz4tG29+OgMwdnCUTK9xjSLsr/cMZg48KHaT0zLCOBSELjtH5hTXgNBZ3Q8cEb/0
MfId2pwkDOepyguq7bnHk8Wmptk+eKDW8EGvsp6sYWzbZu207oZwlOt9cDMbMec5
y74TQtM3J5aUAZmJ+zyTzi5GMjgbZdKgLbsamfachbMXbAr59jC/jFE/ZR/IbEzM
CUiMjvoWyEC4G9ImRyZZIUMFwLIdUK2l1Pvf/vKb0AOfhjkU2cAGo8JupB5lg8MI
Nc2Da1sAkDQq6ZzqS9Max0cD3AbxUeDjBqmpSNyw4H8N1z4gu1fxBNGpl6WiGCNc
JJUld5R2nR8CAwEAAaOBzDCByTAOBgNVHQ8BAf8EBAMCAQYwDwYDVR0TAQH/BAUw
AwEB/zAdBgNVHQ4EFgQU9TqAnPFrj6pFKbgfwVsQI9uj05MwHwYDVR0jBBgwFoAU
5jlDGb3703SdZOGFvfZPB6puRMAwNwYIKwYBBQUHAQEEKzApMCcGCCsGAQUFBzAC
hhtodHRwOi8vdmF1bHQ6ODIwMC92MS9wa2kvY2EwLQYDVR0fBCYwJDAioCCgHoYc
aHR0cDovL3ZhdWx0OjgyMDAvdjEvcGtpL2NybDANBgkqhkiG9w0BAQsFAAOCAQEA
Zi+z9smEuszE/dkOFzV4vjs10voMKHyNmsqPhKAmVavcRYxoSiT2L48t8PDFMfHS
3byTiytPcRfdnLPAW5b+qTGdF9EqgBoQ/JR9LBeJKX//6BOKpJzMvSSsJW7x/Dz5
RCjz1kngD9PhRizx8F0f2+e+ddtADHEZJwwlknQYUGOqfGYvBmXHDT63k42UtIy+
WfkuAyJXpKRyktVgTbCKLXb6IQC4Lz+XqDCHyT9wugcD6mjfxJbaOFuGz1AOg07u
Tb5qBsj51bP4QnniZi8eHLwi45+aLoj9tTURPkSGunf20wFRepu6SIoet0CBbTom
WGEqFtLvcRpJGkFXnWHV2A==
-----END CERTIFICATE-----
private_key         -----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAwH1zbhZaRJ7FqIJ2At+klT6y1WfCsWMvhNvBusSqOSxASpoj
vJzwC6RRtU3/iOk10/UnRjt5qINk4MJTmu4f6xR5LTouCgfDEsdJIppbBVkJKZNF
F/Q3KfwDukFMsEtFd2Nm3vzwtpyH6cenBG8xlFr+j00rSt08MyUtKyfuvvMVjGVH
1v4T7bFg9Ro9C9ehHLBM0kUEbryH4xgoZj6duU0cZaZMCsLqpTtjALNPqaBhZqFt
Z2nYeKOdLIbRGzqCsLNFIe+Sl9qDo2oWcLHMFWPE2ByORqfIb3w8hzH0S8pD84ht
3tj7WF9E0fR/TvtJEChI2TCeZC09/QFO73v20QIDAQABAoIBAQC8QrX/iIsWq/aD
fb0vyE2uzhiYEZhgZ7KVDV1nbmtR6Y6jqCellBROPpLPcQ6od/Z2bEHSNd8hygiC
rmyYjabYAzkU298lXjwTBKfp2O+GxnLon6mm6Op+/IUkyDLaBXRWdPiqxNYks+lV
4zfdZWcnQuvPedkKql/zYbvQhojBZUchhQtITFhW4YMum7zJPVZ7DSAPoXyundXr
jAeI7sxYFjDKpkhcXWQMMn4SHQIndid0SmzcuDPpjDk9Yqcbjfo9NKEA4CrkL4HD
WV39UOK2P91YIvdwRtRXxvezsEpuyfRwcEsUsaSOqSLQD9vUdDY/tRJSorIKfscl
YYrJv+8lAoGBAMfWNvrLHuZEAls4FodCKG19bQaiEXZV+wFYjebTLS3F05lKF1hd
sBME10As601RTiLO1pYRmHRhravL38cgsobZ3FeyPoEQ93bM9iu8HuhpjgRyAo3Z
9hxBLuysqAJmE18vWKfIGGAogOqhvVAvycl3o5+tdmADRiVSLr/wh2W/AoGBAPaW
p+viX0cVWV40Ko28k2SWGzLOf9BxmGG7Pxb5prviaxo7MrpDtdVnTrkyauOkQ9Kc
XrFEshR0lApE9oAljsEaf18Q6R/bE+V1PVeY++4WP1RER5MEdoMDSTRI6mPnemuc
xoHbOUQtejfaAe3hJbCDkpqDoltvCLX56XBw6WdvAoGBAL1K5fN0eoWGAHFl1Lk0
6tSkDaVN2ZqtYUFqH6h5ev8zt/cpHqn+vO2XFUpeAlnP3WLNaKjoa/A6ImdsjEG0
cEeakMSlO93IM5DeH4VYAjMG4ZbGZDL4Ns+W0xsvhUoYZNsyHxl3Sde0JkGbCZeu
XMcxQ9XaWxohn810ZoI8FhVDAoGALDXaqXoOpwn22eL0djEHJBOdkMBhPhf/wBX4
O8BK2oi/txZCBA87vKUnAiE99M5wsoQCnjm4y94S5Lx0jYkuTQTZLUw039dBe/RH
KTtuf8NRW2RaiMtWDCs8prkj/QF1e3HCTWnmnIiizvyxN9sUDM+qKzXKmCYSI75I
0jYMQtUCgYAcEe129FcwI8oI2iwpgRA11x9xa2+QTmNkUuNVTHPJHwx2BPIGK4JV
xVSMUsdchNdT5zz8RXxYpxFQrOjy1/GqsxPQElam0yanZBgiOnjuKgbFoocJS1NB
QPZ9iLa8Nr5gMn9i1047sCxJAUJkLj/fjByd7OIYVosYSApdTPNuFQ==
-----END RSA PRIVATE KEY-----
private_key_type    rsa
serial_number       5a:92:69:54:fb:a7:e5:b0:fa:22:63:a6:aa:f2:5a:13:2a:11:4f:55

kubectl exec -it vault-0 -- vault write pki_int/revoke serial_number="5a:92:69:54:fb:a7:e5:b0:fa:22:63:a6:aa:f2:5a:13:2a:11:4f:55"
Key                        Value
---                        -----
revocation_time            1582563383
revocation_time_rfc3339    2020-02-24T16:56:23.445781419Z
```
 - Включим tls для волт (для этого нужно поправить values для соответствующего чарта)
```
/ # export VAULT_ADDR=https://vault:8200
/ # export KUBE_TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
/ # curl -s --cacert /var/run/secrets/kubernetes.io/serviceaccount/ca.crt --request POST --data '{"jwt": "'$KUBE_TOKEN'", "role": "otus"}' $VAULT_ADDR/v1/auth/kubernetes/login
{"request_id":"5ac78404-0839-dfb1-718b-e56ce43fd58f","lease_id":"","renewable":false,"lease_duration":0,"data":null,"wrap_info":null,"warnings":null,"auth":{"client_token":"s.vHLKQOAq67ShTfcnU73YS5Xq","accessor":"vENQfkgvJ6I3WciYSb7BZTpB","policies":["default","otus-policy"],"token_policies":["default","otus-policy"],"metadata":{"role":"otus","service_account_name":"vault-auth","service_account_namespace":"default","service_account_secret_name":"vault-auth-token-fqh4z","service_account_uid":"3551d3a5-4e62-4d2d-bd37-800ca5ddde68"},"lease_duration":86400,"renewable":true,"entity_id":"d769617a-171c-dd1f-0dfe-149d788d136b","token_type":"service","orphan":true}}
```
## Как запустить проект:
```
# deploy consul
helm install consul consul-helm
#deploy vault
helm install vault .
# deploy example of vault-guides
kubectl create configmap example-vault-agent-config --from-file=./configs-k8s/
kubectl apply -f example-k8s-spec.yml --record
```
 - динамические сертификаты для nginx: надо было изменить политику otus-policy, добавив права на изменение PKI и задеплоить nginx с listen 443 ssl
<img width="972" alt="Screenshot 2020-02-28 at 03 08 17" src="https://user-images.githubusercontent.com/20466436/75498387-13e7fc80-59d8-11ea-8ef4-abd57bc63978.png">
<img width="972" alt="Screenshot 2020-02-28 at 03 09 17" src="https://user-images.githubusercontent.com/20466436/75498397-1c403780-59d8-11ea-855c-61bdf08c6e2a.png">

## Как проверить работоспособность:
```
helm status vault
NAME: vault
LAST DEPLOYED: Sun Feb 23 19:31:02 2020
NAMESPACE: default
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
Thank you for installing HashiCorp Vault!
```

## PR checklist:
 - [x] Выставлен label с номером домашнего задания

## Ответы на вопросы:
- Конструкция с sed убирает ASCII символы с подсветкой из аутпута
- В политику нужно добавить пермиссию "update"