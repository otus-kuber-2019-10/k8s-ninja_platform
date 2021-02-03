#!/bin/bash -e
{% set i = inventory.parameters %}
KUBECTX="kubectx {{i.target}}"

${KUBECTX} $@