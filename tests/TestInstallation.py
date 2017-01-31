import os
import tempfile
import unittest

from subprocess import call, DEVNULL
import time

import sys

from tests.docker import docker_util


class VMHelper(object):
    def __init__(self, vm_name: str, shell: str, ssh_username: str = None, ssh_port: str = None):
        self.vm_name = vm_name
        self.shell = shell # like bash -c or cmd.exe /c
        self.ssh_username = ssh_username
        self.ssh_port = ssh_port

        self.use_ssh = self.ssh_username is not None and self.ssh_port is not None
        self.__vm_is_up = False

    def start_vm(self):
        call('VBoxManage startvm "{0}"'.format(self.vm_name), shell=True)

    def stop_vm(self):
        if self.use_ssh:
            self.send_command("sudo shutdown -h now")
        else:
            call('VBoxManage controlvm "{0}" acpipowerbutton'.format(self.vm_name), shell=True)

    def wait_for_vm_up(self):
        if not self.__vm_is_up:
            print("Waiting for {} to come up.".format(self.vm_name))
            while self.__send_command("echo", hide_output=True, print_command=False) != 0:
                time.sleep(1)
            self.__vm_is_up = True

    def send_command(self, command: str) -> int:
        self.wait_for_vm_up()
        return self.__send_command(command)

    def __send_command(self, command: str, hide_output=False, print_command=True) -> int:
        cmd = list(self.shell.split(" "))
        cmd.extend(command.split(" "))

        if self.use_ssh:
            fullcmd = ["ssh", "-p", str(self.ssh_port), "{0}@127.0.0.1".format(self.ssh_username),
                       '"{0}"'.format(" ".join(cmd))]
        else:
            fullcmd = ["VBoxManage", "guestcontrol", self.vm_name, "run"] + cmd

        if print_command:
            print("Running", " ".join(fullcmd))

        kwargs = {"stdout": DEVNULL, "stderr": DEVNULL} if hide_output else {}

        return call(fullcmd, **kwargs)


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

    def test_linux(self):
        distributions = [
            #"archlinux",
            "debian8",
            #"ubuntu1404",
            "ubuntu1604",
            #"kali",
            # "gentoo"   # cant test gentoo till this bug is fixed: https://github.com/docker/docker/issues/1916#issuecomment-184356102
        ]

        for distribution in distributions:
            self.assertTrue(docker_util.run_image(distribution, rebuild=False), msg=distribution)

    def test_windows(self):
        """
        Run the unittests on Windows + Install via Pip
        :return:
        """
        target_dir = r"C:\urh"
        vm_helper = VMHelper("Windows 10", shell="cmd.exe /c")
        vm_helper.start_vm()
        vm_helper.send_command("rd /s /q {0}".format(target_dir))
        vm_helper.send_command("git clone https://github.com/jopohl/urh " + target_dir)
        rc = vm_helper.send_command(r"python C:\urh\src\urh\cythonext\build.py")
        self.assertEqual(rc, 0)

        rc = vm_helper.send_command(r"set PYTHONPATH={0}\src && py.test C:\urh\tests".format(target_dir))
        self.assertEqual(rc, 0)
        # "set PYTHONPATH={0}\src && py.test C:\urh\tests ".format(target_dir)
        #vm_helper.stop_vm()
        #vm_helper.send_command("git clone ")



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

        # -v -p no:cacheprovider

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
