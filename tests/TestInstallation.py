import unittest

from subprocess import call, DEVNULL
import time
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

    def test_gentoo(self):
        self.assertTrue(docker_util.run_image("gentoo", rebuild=self.REBUILD_IMAGES))

    def test_osx(self):
        call("VBoxManage startvm OSX", shell=True)
        while self.__send_command_via_ssh("boss", 3022, "ls") != 0:
            time.sleep(3)

        python_bin_path = "/Library/Frameworks/Python.framework/Versions/3.5/bin/"

        self.__send_command_via_ssh("boss", 3022, python_bin_path + "pip3 install urh")
        rc = self.__send_command_via_ssh("boss", 3022, python_bin_path + "urh autoclose")
        self.__send_command_via_ssh("boss", 3022, python_bin_path + "pip3 uninstall --yes urh")
        self.__send_command_via_ssh("boss", 3022, "sudo shutdown -h now")

        self.assertEqual(rc, 0)

    @staticmethod
    def __send_command_via_ssh(username: str, port: int, command: str) -> int:
        return call('ssh -p {0} {1}@127.0.0.1 "{2}"'.format(port, username, command), shell=True)