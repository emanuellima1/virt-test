"""Disk hotplugging test"""

import os
import time
import xml.etree.ElementTree as ET

from avocado import Test, fail_on
from avocado.utils.process import CmdError, run
from avocado.utils.ssh import Session

URI = "qemu:///system"
DOMAIN = "fedora36"
HOST = "192.168.122.157"
WAIT_TIME = 30


class LibVirtTest(Test):
    """Execute the hotplugging test"""

    def setUp(self):
        """Set up the testing environment"""

        self.new_disk_path = os.path.join(self.workdir, "new_disk.raw")
        run(f"qemu-img create -f raw {self.new_disk_path} 1G")

        vm_start = run(f"virsh -c {URI} start {DOMAIN}")
        if vm_start.exit_status:
            self.fail(f"Could not start the {DOMAIN} VM")

        time.sleep(WAIT_TIME)

        self.session = Session(HOST, key="$HOME/.ssh/id_ecdsa.pub")
        if not self.session.connect():
            self.fail("Could not establish SSH connection")

    @fail_on(CmdError)
    def test(self):
        """Hotplugging test"""

        blk_pre_attach = self.session.cmd("lsblk -dno NAME", ignore_status=False)
        self.log.info("Disks pre attaching: %s", blk_pre_attach.stdout)

        add_disk = run(
            f"virsh -c {URI} attach-disk {DOMAIN} {self.new_disk_path} vdb --targetbus virtio --driver qemu --subdriver raw"
        )
        if add_disk.exit_status:
            self.fail(f"Could not add a new disk to the {DOMAIN} VM")

        blk_post_attach = self.session.cmd("lsblk -dno NAME", ignore_status=False)
        self.log.info("Disks post attaching: %s", blk_post_attach.stdout)

        assert blk_post_attach.stdout == blk_pre_attach.stdout + b"vdb\n"

        # Check if the new disk is present on the VM`s XML
        get_xml = run(f"virsh -c {URI} dumpxml {DOMAIN}")
        if get_xml.exit_status:
            self.fail(f"Could not get the XML of the {DOMAIN} VM")

        disk_files = []
        root = ET.fromstring(get_xml.stdout)
        for child in root.findall("devices"):
            for disk in child.findall("disk"):
                if disk[1].tag == "source":
                    disk_files.append(disk[1].attrib["file"])

        self.log.info("Disks XML: %s", disk_files)

        assert self.new_disk_path in disk_files

    def tearDown(self):
        """Clean up the testing environment"""

        remove_disk = run(f"virsh -c {URI} detach-disk {DOMAIN} vdb")
        if remove_disk.exit_status:
            self.fail(f"Could not detach the new disk from the {DOMAIN} VM")

        blk_post_detach = self.session.cmd("lsblk -dno NAME", ignore_status=False)
        self.log.info("Disks post detaching: %s", blk_post_detach.stdout)

        vm_stop = run(f"virsh -c {URI} shutdown {DOMAIN}")
        if vm_stop.exit_status:
            self.fail(f"Could not stop the {DOMAIN} VM")

        rm_disk = run(f"rm {self.new_disk_path}")
        if rm_disk.exit_status:
            self.fail("Could not remove the newly created disk")
