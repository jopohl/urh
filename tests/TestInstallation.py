import unittest

from subprocess import call, DEVNULL
import time

import sys

from tests.docker import docker_util


class SSHHelper(object):
    def __init__(self, username: str, port: int):
        self.username = username
        self.port = port

    def wait_for_ssh_running(self):
        print("Waiting for SSH...")
        while self.send_command("ls", suppress_stdout=True) != 0:
            time.sleep(1)
        print("Can connect via SSH!")

    def send_command(self, command: str, suppress_stdout=False) -> int:
        kwargs = {} if not suppress_stdout else {"stdout": DEVNULL}
        return call('ssh -p {0} {1}@127.0.0.1 "{2}"'.format(self.port, self.username, command), shell=True, **kwargs)


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

    #def test_gentoo(self):
    #    cant test gentoo till this bug is fixed: https://github.com/docker/docker/issues/1916#issuecomment-184356102
    #    self.assertTrue(docker_util.run_image("gentoo", rebuild=self.REBUILD_IMAGES))

    def test_windows_pip(self):
        """
        To Fix Windows Error in Guest OS:
        type gpedit.msc and go to:
        Windows Settings
            -> Security Settings
                -> Local Policies
                    -> Security Options
                        -> Accounts: Limit local account use of blank passwords to console logon only
        and set it to DISABLED.


        configure pip on guest:

        %APPDATA%\Roaming\pip

        [global]
        no-cache-dir = false

        [uninstall]
        yes = true
        """
        call('VBoxManage startvm "Windows 10"', shell=True)
        time.sleep(30)

        call(r'VBoxManage guestcontrol "Windows 10" run "C:\Python35\Scripts\pip.exe" "install" "urh"', shell=True)
        rc = call(r'VBoxManage guestcontrol "Windows 10" run "C:\Python35\Scripts\urh.exe" "autoclose"', shell=True)
        call(r'VBoxManage guestcontrol "Windows 10" run "C:\Python35\Scripts\pip.exe" "uninstall" "urh"', shell=True)

        call('VBoxManage controlvm "Windows 10" acpipowerbutton', shell=True)

        self.assertEqual(rc, 0)

    def test_windows_git(self):
        call('VBoxManage startvm "Windows 10"', shell=True)
        time.sleep(30)

        target_dir = r"C:\Users\joe\urh"

        call(r'VBoxManage guestcontrol "Windows 10" run "cmd.exe" "/c" "rd" "/s" "/q" "{0}"'.format(target_dir), shell=True)
        call(r'VBoxManage guestcontrol "Windows 10" run "C:\Program Files\Git\bin\git.exe" "clone" "https://github.com/jopohl/urh" "{0}"'.format(target_dir), shell=True)
        rc = call(r'VBoxManage guestcontrol "Windows 10" run "C:\Python35\python.exe" "{0}\src\urh\main.py" "autoclose"'.format(target_dir), shell=True)

        call('VBoxManage controlvm "Windows 10" acpipowerbutton', shell=True)

        self.assertEqual(rc, 0)

    def test_osx_pip(self):
        call("VBoxManage startvm OSX", shell=True)
        ssh_helper = SSHHelper("boss", 3022)
        ssh_helper.wait_for_ssh_running()
        python_bin_path = "/Library/Frameworks/Python.framework/Versions/3.5/bin/"
        ssh_helper.send_command(python_bin_path + "pip3 --no-cache-dir install urh")
        rc = ssh_helper.send_command(python_bin_path + "urh autoclose")
        ssh_helper.send_command(python_bin_path + "pip3 uninstall --yes urh")
        ssh_helper.send_command("sudo shutdown -h now")

        self.assertEqual(rc, 0)

    def test_osx_git(self):
        call("VBoxManage startvm OSX", shell=True)
        ssh_helper = SSHHelper("boss", 3022)
        ssh_helper.wait_for_ssh_running()
        ssh_helper.send_command("cd /tmp && rm -rf urh && git clone 'https://github.com/jopohl/urh'")
        python_bin_path = "/Library/Frameworks/Python.framework/Versions/3.5/bin/"
        rc = ssh_helper.send_command(python_bin_path+"python3 /tmp/urh/src/urh/main.py autoclose")
        ssh_helper.send_command("sudo shutdown -h now")

        self.assertEqual(rc, 0)
