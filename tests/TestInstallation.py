import unittest

from tests.docker import docker_util


class TestInstallation(unittest.TestCase):

    REBUILD_IMAGES = False # Rebuild images, even if they are present

    def test_archlinux(self):
        self.assertTrue(docker_util.run_image("archlinux", rebuild=self.REBUILD_IMAGES))

    def test_debian8(self):
        self.assertTrue(docker_util.run_image("debian8", rebuild=self.REBUILD_IMAGES))

    def test_ubuntu1404(self):
        self.assertTrue(docker_util.run_image("ubuntu1404", rebuild=self.REBUILD_IMAGES))

    def test_ubuntu1604(self):
        self.assertTrue(docker_util.run_image("ubuntu1604", rebuild=self.REBUILD_IMAGES))

    def test_kali(self):
        self.assertTrue(docker_util.run_image("kali", rebuild=self.REBUILD_IMAGES))

    def tearDown(self):
        docker_util.remove_containers()
