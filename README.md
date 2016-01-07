# Photobooth

## Credits

Raspberry Pi PhotoBooth by **Bret Lanuis** | modified by **Tim Reasa**

## Requirements

* `sudo apt-get install python-picamera`
* `sudo apt-get install python-imaging-tk`

## Raspberry Pi Configuration

Edit the configuration file so set the display to 800px x 1280px

`sudo nano /boot/config.txt`

`
display_rotate=0        Normal
display_rotate=1         90 degrees
display_rotate=2        180 degrees
display_rotate=3        270 degrees
display_rotate=0x10000  horizontal flip
display_rotate=0x20000  vertical flip
`

After exiting the editor, restart using the command

`sudo reboot`