#!/bin/bash

export SUPPRESS_LABEL_WARNING=True

# Variaveis de ambiente e caminhos absolutos
CONFIG_FILE="/home/zabbix/.oci/config"
OCI_BIN="/usr/local/bin/oci"  # <-- Substitua pelo resultado do 'which oci'
JQ_BIN="/usr/bin/jq"          # <-- Substitua pelo resultado do 'which jq'

# Executa a busca com caminho absoluto
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
