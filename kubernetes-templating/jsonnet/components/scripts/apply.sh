#!/bin/bash -e
{% set i = inventory.parameters %}

DIR=$(dirname ${BASH_SOURCE[0]})

for SECTION in manifests
do
  echo "## run kubectl apply for ${SECTION}"
  kubectl apply -f ${DIR}/../${SECTION}/ --validate -n {{i.namespace}} | column -t
done