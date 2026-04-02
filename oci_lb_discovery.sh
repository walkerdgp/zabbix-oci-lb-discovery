#!/bin/bash

export SUPPRESS_LABEL_WARNING=True

# Variaveis de ambiente e caminhos absolutos
CONFIG_FILE="/home/zabbix/.oci/config"
OCI_BIN="/usr/local/bin/oci"
JQ_BIN="/usr/bin/jq"

# Executa a busca suprimindo os alertas do Python (2>/dev/null)
$OCI_BIN search resource structured-search \
  --config-file "$CONFIG_FILE" \
  --query-text "query loadbalancer resources" \
  --output json 2>/dev/null | $JQ_BIN '
  [
    .data.items[] | {
      "{#HOSTNAME}": ."display-name" | ascii_upcase,
      "{#OCID}": .identifier,
      "{#ENVIRONMENT}": (if (."display-name" | ascii_downcase | startswith("bcoi")) then "Homologacao" else "Producao" end)
    }
  ]'
