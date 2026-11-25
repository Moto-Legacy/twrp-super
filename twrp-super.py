#!/usr/bin/env python3
"""Make an official TWRP image find a retrofit super partition.

Adds androidboot.super_partition=system and androidboot.boot_devices=msm_sdcc.1
to the kernel command line stored in the image header (Android boot image
v0/v1/v2): TWRP then looks super up as the stock system partition, through
the /dev/block/by-name links ueventd only creates for the boot devices. Nothing else changes: same size, same kernel, same
ramdisk.

Usage: twrp-super.py <official twrp.img> <output.img>
"""
import sys

ARGS = [b"androidboot.super_partition=system", b"androidboot.boot_devices=msm_sdcc.1"]
CMDLINE_OFF, CMDLINE_LEN = 64, 512

def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    src, dst = sys.argv[1:]
    img = bytearray(open(src, "rb").read())
    if img[:8] != b"ANDROID!":
        sys.exit("not an Android boot image")
    # header_version in v1+ headers; Qualcomm's v0 keeps the QCDT dt.img size
    # there. Only v3/v4 move the command line elsewhere.
    version = int.from_bytes(img[40:44], "little")
    if version in (3, 4):
        sys.exit("boot image header v%d is not supported" % version)
    cmdline = bytes(img[CMDLINE_OFF:CMDLINE_OFF + CMDLINE_LEN]).split(b"\0")[0]
    missing = [a for a in ARGS if a not in cmdline.split()]
    if not missing:
        sys.exit("the image already has both arguments")
    new = b" ".join([cmdline] + missing).strip()
    if len(new) >= CMDLINE_LEN:
        sys.exit("no room left in the header command line")
    img[CMDLINE_OFF:CMDLINE_OFF + CMDLINE_LEN] = new + b"\0" * (CMDLINE_LEN - len(new))
    open(dst, "wb").write(img)
    print("cmdline:", new.decode())

if __name__ == "__main__":
    main()
