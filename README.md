# sky
Sky view
**How to use the new Storage configuration**

If you run the script exactly as you have been doing, it will default to saving files in the same folder as your code:

**Bash :**

`python3 main.py`
However, if you plug a USB flash drive into your Raspberry Pi (which usually mounts to `/media/pi/` or `/mnt/`), you can route all images and videos to that drive instantly by using the `-s` (or `--storage`) flag:

**Bash :**

`python3 main.py -s /mnt/usb_drive/astrophotography`
The app will immediately create `/mnt/usb_drive/astrophotography/captures`, `/processed`, and `/manual` for you, and securely route all web gallery requests and camera saves to the external drive, completely protecting your SD card from wear and tear.
