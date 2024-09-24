import kr8s
import time
from kr8s.objects import HorizontalPodAutoscaler
from pprint import pprint


def wait_for_success(timeout, function, *args):
    sleep_time = 5
    check_passed = False
    while check_passed is False:
        if timeout == 0:
            raise Exception("FAIL: Function did not return success within required time.")
        check_passed = function(*args)
        if check_passed is True:
            return
        elif check_passed is False and timeout == 1:
            timeout -= 1
        else:
            timeout -= 1
            print(f"    Waiting {sleep_time} seconds before next check.")
            time.sleep(sleep_time)


def check_all_pods_ready(label, namespace):
    all_pods_ready = True
    pods = kr8s.get("pods", namespace=namespace, label_selector=label)
    for pod in pods:
        if pod.ready() is False:
            print(f"Pod {pod.name} is not ready.")
            all_pods_ready = False
        else:
            print(f"Pod {pod.name} is ready.")
    return all_pods_ready


def change_min_hpa(hpa_name, min_number, namespace="ping"):
    hpa = HorizontalPodAutoscaler.get(hpa_name, namespace=namespace)
    hpa.spec.minReplicas = min_number

    hpa.patch(
        # Uses the JSON patch standard - https://jsonpatch.com
        [{"op": "replace", "path": "/spec", "value": hpa.spec}],
        type="json",
    )

def check_nodes_added_to_target_group(new_nodes, original_nodes):
    return


def main():
    hpa_name = "hello-world-hpa"
    namespace = "default"

    original_nodes = kr8s.get("nodes")
    original_size = HorizontalPodAutoscaler.get(hpa_name, namespace=namespace).spec.minReplicas
    print(f"Original number of nodes: {len(original_nodes)}")
    print(f"Original number of pods: {original_size}")

    change_min_hpa(hpa_name, 7, namespace)
    print("Changed min size of HPA to: 7")
    try:
        wait_for_success(2, check_all_pods_ready, {"app": "hello-world"}, namespace)
    except:
        change_min_hpa(hpa_name, original_size, namespace)
        print(f"Changed min size of HPA to: {original_size}")
        if HorizontalPodAutoscaler.get(hpa_name, namespace=namespace).spec.minReplicas != original_size:
            raise Exception("Did not manage to set HPA back to original value. Please check spec.")
        raise

    new_nodes = kr8s.get("nodes")
    if len(new_nodes) > len(original_nodes):
        print(f"Nodes successfully scaled to {len(new_nodes)}")

    if check_nodes_added_to_target_group(new_nodes, original_nodes):
        print("Success")
    else:
        print("Failure")


if __name__ == "__main__":
    main()
