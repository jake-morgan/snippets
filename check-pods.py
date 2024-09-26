import kr8s
from pprint import pprint

def get_pod_status(namespace):
    pods_status = []
    pods = kr8s.get("pods", namespace=namespace)
    for pod in pods:
        pod_state = {
            "Name": pod.name,
            "Namespace": namespace,
            "Phase": pod.status.phase,
        }
        for condition in pod.status.conditions:
            pod_state[condition["type"]] = condition["status"]
        pods_status.append(pod_state)

    return pods_status

namespaces = kr8s.get("namespaces")

pods_status = []
for namespace in namespaces:
    pods_status.extend(get_pod_status(namespace.name))

test_pass = True
for pod in pods_status:
    print(pod["Name"])
    print(f"    Phase:       {pod["Phase"]}")
    print(f"    Scheduled:   {pod["PodScheduled"]}")
    print(f"    Initialized: {pod["Initialized"]}")
    print(f"    Ready:       {pod["Ready"]}")
    if pod["Phase"] != "Running" or all([pod["PodScheduled"], pod["Initialized"], pod["Ready"]]) is False:
        test_pass = False

print(f"\nTest Pass: {test_pass}")
