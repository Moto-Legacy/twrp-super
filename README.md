# TWRP for retrofit dynamic partitions

The Moto-Legacy LineageOS 23.2 builds for **falcon** and **peregrine** keep
the stock partition table (the bootloader only boots Motorola signed tables)
and lay a retrofit `super` over the stock `system` and `cache` partitions.
The official TWRP 3.5 already handles dynamic partitions, it just doesn't know
where `super` is. `twrp-super.py` tells it, by adding two arguments to the
kernel command line stored in the image header:

| Argument | Why |
| --- | --- |
| `androidboot.super_partition=system` | `super` starts on the stock `system` partition (its metadata is there) |
| `androidboot.boot_devices=msm_sdcc.1` | ueventd only creates the `/dev/block/by-name` links `super` is found through for the boot devices |

Nothing else changes: same size, same kernel, same ramdisk.

## Making the image

1. Download the official TWRP **3.5.0_9-0** for your device from twrp.me and
   check it:

   | Device | Official image | sha256 |
   | --- | --- | --- |
   | falcon | [`twrp-3.5.0_9-0-falcon.img`](https://dl.twrp.me/falcon/) | `b719f0a03c7c916cd191363ff0564e1b6ed6c45ede0e8af8442fbfdf541b256c` |
   | peregrine | [`twrp-3.5.0_9-0-peregrine.img`](https://dl.twrp.me/peregrine/) | `d0768c890643db71b0193717d2a12bebff20c596665961b003b8de20e1a179f0` |

2. Patch it (Python 3, no dependencies):

   ```sh
   ./twrp-super.py twrp-3.5.0_9-0-falcon.img twrp-3.5.0_9-0-falcon-super.img
   ```

3. The result should match:

   | Device | Patched image | sha256 |
   | --- | --- | --- |
   | falcon | `twrp-3.5.0_9-0-falcon-super.img` | `979b08f0637da5220818a56622f8f30b41b64059e618e983f0885a32edb9032f` |
   | peregrine | `twrp-3.5.0_9-0-peregrine-super.img` | `51d35d94abbe91cefb4475061706d2cfbde8fb9fcaaf18db23400db9c0fcaa23` |

4. Flash or boot it:

   ```sh
   fastboot flash recovery twrp-3.5.0_9-0-falcon-super.img
   # or, without flashing:
   fastboot boot twrp-3.5.0_9-0-falcon-super.img
   ```

Then install the ROM with `adb sideload` as usual.

The falcon image is the one the LineageOS 23.2 retrofit builds were installed
with. The peregrine one is made the same way from the same TWRP release but
hasn't been tested on a device yet.

## Alternative: LineageOS recovery

The device trees can also build Android 16's own recovery, which knows the
dynamic partitions too. It doesn't fit the 10 MB recovery partition, so it is
only for `fastboot boot`:

```sh
MSM8226_BUILD_RECOVERY=true mka recoveryimage
fastboot boot out/target/product/falcon/recovery.img
```
