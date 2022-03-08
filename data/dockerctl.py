from python_on_whales import docker


def check_containers():
    print(docker.ps())

