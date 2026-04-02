#!/bin/bash

export SUPPRESS_LABEL_WARNING=True

# Variaveis de ambiente e caminhos absolutos
CONFIG_FILE="/home/zabbix/.oci/config"
OCI_BIN="/root/bin/oci"
JQ_BIN="/bin/jq"

$OCI_BIN search resource structured-search \
  --config-file "$CONFIG_FILE" \
  --query-text "query loadbalancer resources" \
  --output json | $JQ_BIN '
  [
    .data.items[] | {
      "{#HOSTNAME}": ."display-name" | ascii_upcase,
      "{#OCID}": .identifier,
      "{#ENVIRONMENT}": (if (."display-name" | ascii_downcase | startswith("bcoi")) then "Homologacao" else "Producao" end)
    }
  ]'
