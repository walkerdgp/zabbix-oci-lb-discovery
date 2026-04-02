#!/usr/bin/env python3
import sys
import json
import oci

CONFIG_PATH = "/home/zabbix/.oci/config"

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Faltando parametro OCID"}))
        sys.exit(2)

    lb_id = sys.argv[1]

    try:
        config = oci.config.from_file(file_location=CONFIG_PATH)
        lb = oci.load_balancer.LoadBalancerClient(config)

        lb_info = lb.get_load_balancer(load_balancer_id=lb_id).data
        overall_health = lb.get_load_balancer_health(load_balancer_id=lb_id).data

        backend_sets_total = 0
        backends_healthy = 0
        backends_unhealthy = 0
        backends_unknown = 0
        
        backends_status = {}

        backend_sets = lb.list_backend_sets(load_balancer_id=lb_id).data
        backend_sets_total = len(backend_sets)

        for bs in backend_sets:
            bs_name = bs.name
            try:
                bs_health = lb.get_backend_set_health(load_balancer_id=lb_id, backend_set_name=bs_name).data
                backends = lb.list_backends(load_balancer_id=lb_id, backend_set_name=bs_name).data

                critical_bks = bs_health.critical_state_backend_names or []
                warning_bks = bs_health.warning_state_backend_names or []
                unknown_bks = bs_health.unknown_state_backend_names or []

                for backend in backends:
                    b_name = backend.name
                    
                    if b_name in critical_bks:
                        st = "CRITICAL"
                        backends_unhealthy += 1
                    elif b_name in warning_bks:
                        st = "WARNING"
                        backends_unhealthy += 1
                    elif b_name in unknown_bks:
                        st = "UNKNOWN"
                        backends_unknown += 1
                    else:
                        st = "OK"
                        backends_healthy += 1
                        
                    backends_status[b_name] = st

            except Exception:
                pass 

        output = {
            "name": lb_info.display_name,
            "updown": "UP" if str(lb_info.lifecycle_state) == "ACTIVE" else "DOWN",
            "lifecycle_state": str(lb_info.lifecycle_state),
            "overall_health": str(overall_health.status),
            "backend_sets_total": backend_sets_total,
            "backends_healthy": backends_healthy,
            "backends_unhealthy": backends_unhealthy,
            "backends_unknown": backends_unknown,
            "backends_status": backends_status
        }

        print(json.dumps(output))
        sys.exit(0)

    except Exception as e:
        # Garante o retorno do erro real formatado em JSON para debug no Zabbix
        print(json.dumps({"error": str(e)}))
        sys.exit(2)

if __name__ == "__main__":
    main() 
