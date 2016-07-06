from tests.docker import docker_util


def test_archlinux():
    docker_util.run_image("archlinux")