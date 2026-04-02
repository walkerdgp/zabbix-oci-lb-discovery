#!/usr/bin/env python3
import sys
import json
import oci

CONFIG_PATH = "/home/zabbix/.oci/config"

def main():
    if len(sys.argv) < 2:
        sys.exit(2)

    lb_id = sys.argv[1]

    try:
        config = oci.config.from_file(file_location=CONFIG_PATH)
        lb = oci.load_balancer.LoadBalancerClient(config)

        discovery_data = []
        backend_sets = lb.list_backend_sets(load_balancer_id=lb_id).data

        for bs in backend_sets:
            bs_name = bs.name
            # Busca oficial dos backends dentro do Backend Set
            backends = lb.list_backends(load_balancer_id=lb_id, backend_set_name=bs_name).data
            
            for backend in backends:
                discovery_data.append({
                    "{#BACKEND_NAME}": backend.name,
                    "{#BACKEND_SET}": bs_name
                })

        print(json.dumps(discovery_data, indent=2))
        sys.exit(0)

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(2)

if __name__ == "__main__":
    main() 
