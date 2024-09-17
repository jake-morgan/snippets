import kr8s
import time


def check_node_joined_cluster(node_name):
    nodes = kr8s.get("nodes", node_name)
    if len(nodes) == 1:
        print(f"    Success: Node '{node_name}' found.")
        return True
    elif len(nodes) == 0:
        print(f"    Fail: Node '{node_name}' not found.")
        return False
    else:
        print(f"    Fail: Multiple nodes match the name provided.")
        return False


def check_node_status(node_name):
    nodes = kr8s.get("nodes", node_name)
    if len(nodes) != 1:
        raise Exception(f"More than one node found with name '{node_name}'.")
    node = nodes[0]
    checks_passed = True

    desired_conditions = {
        "Ready": "True",
        "PIDPressure": "False",
        "MemoryPressure": "False",
        "DiskPressure": "False",
    }

    for condition in node.status.conditions.to_list():
        condition_type = condition["type"]
        condition_status = condition["status"]
        if desired_conditions.get(condition_type) == condition_status:
            print(f"    Success: {condition_type} is {condition_status}.")
        elif desired_conditions.get(condition_type) == None:
            print(f"Condition {condition_type} not found in list of desired conditions. Skipping.")
        else:
            print(f"    Fail: {condition_type} is {condition_status}.")
            checks_passed = False

    return checks_passed


def check_dameon_sets_running(namespace):
    daemonsets = kr8s.get("daemonset", namespace=namespace)
    checks_passed = True

    for ds in daemonsets:
        desired = ds.status["desiredNumberScheduled"]
        available = ds.status["numberAvailable"]
        if desired != available:
            print(f"    Fail: DaemonSet '{ds.name}' has {available} available pods (desired {desired}).")
            checks_passed = False
        else:
            print(f"    Success: DaemonSet '{ds.name}' has {available} available pods (desired {desired}).")

    return checks_passed


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


def main():
    print("Checking if Node has joined cluster.")
    wait_for_success(10, check_node_joined_cluster, "minikube-m03")

    print("Checking if Node is healthy.")
    wait_for_success(10, check_node_status, "minikube")

    print("Checking if desired DaemonSets are running.")
    wait_for_success(10, check_dameon_sets_running, "kube-system")


if __name__ == "__main__":
    main()
