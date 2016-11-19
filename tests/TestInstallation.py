import unittest

from tests.docker import docker_util


class TestInstallation(unittest.TestCase):

    def test_archlinux(self):
        self.assertTrue(docker_util.run_image("archlinux"))

    def test_debian8(self):
        self.assertTrue(docker_util.run_image("debian8"))

    def test_ubuntu1404(self):
        self.assertTrue(docker_util.run_image("ubuntu1404"))

    def test_ubuntu1604(self):
        self.assertTrue(docker_util.run_image("ubuntu1604"))

    def test_kali(self):
        self.assertTrue(docker_util.run_image("kali"))

    def tearDown(self):
        docker_util.remove_containers()

