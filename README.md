```markdown
# Zabbix OCI Load Balancer Discovery & Monitoring

Solução open-source para descoberta automatizada (LLD) e monitoramento granular de Load Balancers da Oracle Cloud Infrastructure (OCI) e seus respectivos Backends. 

Projetada para ambientes de NOC/SOC operando com Zabbix (6.4+), a solução minimiza o consumo de requisições de API utilizando o conceito de **Master Items** e **Dependent Items**, garantindo escalabilidade e alertas precisos sem gerar gargalos ou custos extras na nuvem.



## 🏗 Arquitetura

A coleta é dividida em três scripts principais executados via *External Check* no Zabbix Server/Proxy:

1. **`oci_lb_discovery.sh`**: Realiza a busca global na *Tenancy* utilizando o OCI CLI e retorna um JSON estruturado para o LLD de Hosts do Zabbix. Descobre dinamicamente novos Load Balancers.
2. **`oci_lb_details.py`**: Atua como *Master Item*. Conecta via SDK Python, coleta a saúde geral do LB e mapeia o status de cada backend associado em uma única chamada de API.
3. **`oci_lb_discovery_backends.py`**: Realiza o LLD interno dos LBs para descobrir as rotas (IP:Porta) dos backends em cada Pool/Backend Set e vinculá-las ao Master Item.



## ⚙️ Pré-requisitos

### Sistema Operacional (Zabbix Server / Proxy)
* Distribuição baseada em Linux (Homologado em Oracle Linux 8 e Ubuntu).
* **Python 3.9+** com a biblioteca nativa da OCI:
  ```bash
  pip3 install oci
  ```
* **OCI CLI** instalado globalmente:
  ```bash
  bash -c "$(curl -L [https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh](https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh))" -- --accept-all-defaults --install-dir /usr/local/lib/oracle-cli --exec-dir /usr/local/bin
  ```
* Utilitários auxiliares: `jq` e `dos2unix`.

### Permissões na Oracle Cloud (IAM Policies)
O usuário de serviço (Zabbix) requer uma API Key configurada e permissões de leitura nos recursos de rede. Adicione as seguintes políticas no seu *Compartment* ou *Tenancy*:
```text
Allow group ZabbixMonitorGroup to inspect load-balancers in tenancy
Allow group ZabbixMonitorGroup to read load-balancers in tenancy
```



## 🚀 Instalação e Configuração

### 1. Configuração de Autenticação OCI
O Zabbix executa os scripts através do usuário do sistema operacional `zabbix`. A chave de API da Oracle deve estar restrita e acessível apenas por ele.

```bash
# Crie o diretório do usuário zabbix
mkdir -p /home/zabbix/.oci

# Copie sua chave PEM e crie o arquivo de config
# Ajuste as permissões de segurança restritas (Obrigatório)
chown -R zabbix:zabbix /home/zabbix/.oci
chmod 600 /home/zabbix/.oci/*.pem
```

Exemplo da estrutura exigida para o `/home/zabbix/.oci/config`:
```ini
[DEFAULT]
user=ocid1.user.oc1..xxxx
fingerprint=xx:xx:xx:xx:xx:xx:xx:xx
key_file=/home/zabbix/.oci/zabbix_api_key.pem
tenancy=ocid1.tenancy.oc1..xxxx
region=sa-saopaulo-1
```

### 2. Implantação dos Scripts
Mova os três scripts deste repositório para o diretório de *ExternalScripts* do seu ambiente Zabbix (Padrão: `/usr/lib/zabbix/externalscripts/`).

```bash
# Atribuir permissão de execução
chmod +x /usr/lib/zabbix/externalscripts/oci_lb_*.sh
chmod +x /usr/lib/zabbix/externalscripts/oci_lb_*.py

# Corrigir possíveis quebras de linha (CRLF -> LF) e garantir o formato UNIX puro
dos2unix /usr/lib/zabbix/externalscripts/oci_lb_discovery.sh
```

### 3. Ajuste de Timeout no Zabbix
Consultas a APIs de Cloud demandam um tempo de resposta maior do que o padrão de 3 segundos do Zabbix. 

Edite o `/etc/zabbix/zabbix_server.conf` (ou `zabbix_proxy.conf`):
```ini
Timeout=30
```
Reinicie o serviço:
```bash
systemctl restart zabbix-server
```


## 🖥 Configuração no Frontend do Zabbix

1. Importe os templates XML inclusos neste repositório.
2. Crie um Host Pai no Zabbix (ex: `MASTER HOST - OCI LOAD BALANCERS`).
3. Adicione a interface fictícia (Agent IP: `127.0.0.1`, Porta: `10050`) para permitir o vínculo de templates.
4. Vincule o template de **Discovery** neste Host Pai.
5. **Comportamento Esperado:**
   * O Zabbix descobrirá os Load Balancers e criará os Hosts automaticamente.
   * O template de **Coleta** será atachado a cada LB gerado.
   * Os Backends (IP:Porta) serão descobertos nativamente dentro de cada host de LB.
   * Triggers granulares gerarão incidentes no SOC contendo a identificação exata da falha: `OCI LB: {HOST.NAME} - Backend {#BACKEND_NAME} (Pool: {#BACKEND_SET}) está CRITICAL`.


## 🛠 Troubleshooting Rápido

* **Erro "cannot parse as a valid JSON object" na regra de Discovery:** Verifique se o caminho do binário `jq` no shell script corresponde ao do seu SO (`which jq`) e assegure-se de ter rodado o utilitário `dos2unix` no arquivo `.sh`.
* **Itens com status "Not Supported" ou "Preprocessing Failed":** Execute o script Python manualmente com o usuário Zabbix no terminal para capturar exceções brutas (como falta de permissão na chave PEM ou ausência do módulo Python `oci`):
  ```bash
  su - zabbix -s /bin/bash -c "python3 /usr/lib/zabbix/externalscripts/oci_lb_details.py <OCID_DO_LB>"
  ```
```
