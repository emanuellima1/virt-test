# Virtualization Test with Avocado

On this document, L1 is the host OS and L2 is the guest.

## Preparing the virtual machine

To save time and focus on the task at hand, I used my own personal system as L1.
It runs Manjaro 22 (Sikaris) with kernel 5.19.16, QEMU version 7.1.0,
libvirt version 8.8.0, Virt Manager 4.1.0 and Avocado 98.0.
My system of choice for L2 was Fedora 36 Server, to avoid the overhead of graphical interfaces.
I proceeded as follows:

1. I downloaded Fedora 36 Server from it's official website
2. Imported Fedora's GPG keys with `curl -O <https://getfedora.org/static/fedora.gpg>`
3. Verified the validity of the CHECKSUM with `gpgv --keyring ./fedora.gpg *-CHECKSUM`
4. Verified the ISO with `sha256sum -c *-CHECKSUM`

After verifying the ISO:

1. I Created the Fedora VM with Virt Manager
2. Installed and updated the OS
3. Transferred my public key with `ssh-copy-id`
4. Connected through SSH

As such, we have:

- Libvirt URI: `qemu:///system`
- Libvirt domain: `fedora36`
- VM hostname: `fedora36`
- SSH connection is done through keys
- Avocado is installed on L1
