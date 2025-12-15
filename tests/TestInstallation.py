import unittest

from subprocess import call, DEVNULL
import time

from tests.docker import docker_util


class VMHelper(object):
    def __init__(
        self,
        vm_name: str,
        shell: str = "",
        ssh_username: str = None,
        ssh_port: str = None,
    ):
        self.vm_name = vm_name
        self.shell = shell  # like cmd.exe /c
        self.ssh_username = ssh_username
        self.ssh_port = ssh_port

        self.use_ssh = self.ssh_username is not None and self.ssh_port is not None
        self.__vm_is_up = False

    def start_vm(self):
        call('VBoxManage startvm "{0}"'.format(self.vm_name), shell=True)

    def stop_vm(self, save=True):
        if save:
            call(
                'VBoxManage controlvm "{0}" savestate'.format(self.vm_name), shell=True
            )
            return
        if self.use_ssh:
            self.send_command("sudo shutdown -h now")
        else:
            call(
                'VBoxManage controlvm "{0}" acpipowerbutton'.format(self.vm_name),
                shell=True,
            )

    def wait_for_vm_up(self):
        if not self.__vm_is_up:
            print("Waiting for {} to come up.".format(self.vm_name))
            command = "ping -c 1" if self.use_ssh else "ping -n 1"
            command += " github.com"

            while (
                self.__send_command(command, hide_output=True, print_command=False) != 0
            ):
                time.sleep(1)

            self.__vm_is_up = True

    def send_command(self, command: str) -> int:
        self.wait_for_vm_up()
        return self.__send_command(command)

    def __send_command(
        self, command: str, hide_output=False, print_command=True
    ) -> int:
        if self.use_ssh:
            fullcmd = [
                "ssh",
                "-p",
                str(self.ssh_port),
                "{0}@127.0.0.1".format(self.ssh_username),
                '"{0}"'.format(command),
            ]
        else:
            fullcmd = (
                ["VBoxManage", "guestcontrol", '"{0}"'.format(self.vm_name), "run"]
                + self.shell.split(" ")
                + ['"{0}"'.format(command)]
            )

        kwargs = {"stdout": DEVNULL, "stderr": DEVNULL} if hide_output else {}

        fullcmd = " ".join(fullcmd)

        if print_command:
            print("\033[1m" + fullcmd + "\033[0m")

        return call(fullcmd, shell=True, **kwargs)


class TestInstallation(unittest.TestCase):
    def test_linux(self):
        distributions = [
            # "archlinux",
            "debian8",
            # "ubuntu1404",
            "ubuntu1604",
            # "kali",
            # "gentoo"   # can't test gentoo till this bug is fixed: https://github.com/docker/docker/issues/1916#issuecomment-184356102
        ]

        for distribution in distributions:
            self.assertTrue(
                docker_util.run_image(distribution, rebuild=False), msg=distribution
            )

    def test_windows(self):
        r"""
        Run the unittests on Windows + Install via Pip

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
        :return:
        """
        target_dir = r"C:\urh"
        vm_helper = VMHelper("Windows 10", shell="cmd.exe /c")
        vm_helper.start_vm()
        vm_helper.send_command("pip uninstall urh")
        vm_helper.send_command("rd /s /q {0}".format(target_dir))
        vm_helper.send_command("git clone https://github.com/jopohl/urh " + target_dir)
        rc = vm_helper.send_command(r"python C:\urh\src\urh\cythonext\build.py")
        self.assertEqual(rc, 0)

        rc = vm_helper.send_command(r"py.test C:\urh\tests".format(target_dir))
        self.assertEqual(rc, 0)

        vm_helper.send_command("pip install urh")
        time.sleep(0.5)
        rc = vm_helper.send_command("urh autoclose")
        self.assertEqual(rc, 0)
        vm_helper.send_command("pip uninstall urh")
        vm_helper.stop_vm()

    def test_osx(self):
        """
        Run Unittests + Pip Installation on OSX

        :return:
        """

        vm_helper = VMHelper("OSX", ssh_port="3022", ssh_username="boss")
        vm_helper.start_vm()

        python_bin_dir = "/Library/Frameworks/Python.framework/Versions/3.5/bin/"
        target_dir = "/tmp/urh"
        vm_helper.send_command("rm -rf {0}".format(target_dir))
        vm_helper.send_command("git clone https://github.com/jopohl/urh " + target_dir)

        # Build extensions
        rc = vm_helper.send_command(
            "{0}python3 {1}/src/urh/cythonext/build.py".format(
                python_bin_dir, target_dir
            )
        )
        self.assertEqual(rc, 0)

        # Run Unit tests
        rc = vm_helper.send_command(
            "{1}py.test {0}/tests".format(target_dir, python_bin_dir)
        )
        self.assertEqual(rc, 0)

        vm_helper.send_command(
            "{0}pip3 --no-cache-dir install urh".format(python_bin_dir)
        )
        rc = vm_helper.send_command("{0}urh autoclose".format(python_bin_dir))
        self.assertEqual(rc, 0)
        vm_helper.send_command("{0}pip3 uninstall --yes urh".format(python_bin_dir))
        vm_helper.stop_vm()
