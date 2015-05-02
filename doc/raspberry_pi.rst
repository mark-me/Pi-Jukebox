==============================
Preparing your Raspberry Pi
==============================

------------------------------
Hardware
------------------------------
For my raspberry pi jukebox I used the following hardware:

    - Raspberry Pi, I used a B+ model, but any will model do as long as it fits with the:
    - Capacitive Touchscreen from Adafruit: http://www.adafruit.com/products/2423
    - 8 GB SD card
    - USB audiocard (since the jack output on the Raspberry Pi gave me too much of a headache)

I also built my own case with speakers and in-built amp, but I'll spare you these ;-).

-------------------------------
Installing the operating system
-------------------------------
I installed a raspbian pre-configured for the Capacitive touchscreen with an image downloaded from this page: https://learn.adafruit.com/adafruit-2-8-pitft-capacitive-touch/easy-install. Since the installation instructions differ per operating system and provided on this page are quite good, you can follow these.

-----------------------------
Configuring the Raspberry Pi
-----------------------------
You can configure some settings on your Raspberry Pi using the command sudo raspi-config Here you can easily do some configurations. Some that I preferred to do:

    - Expand the file-system (1) - The initial installation of the OS does not make full use of your SD card. Why throw away so much space?. This option makes sure you use your whole SD card.
    - Internationalization options (4) - Configure your timezone and locale settings
    - Advanced options (8) - Host name (A2) - Of course you want your Pi-Jukebox recognizable in the network as such, so change it to 'pi-jukebox'. This step is not a necessity for following steps.

---------------------------------
Configuring the USB music device
---------------------------------
To configure the sound card's initial volume I used alsamixer. Because we want to configure the USB soundcard, and not the HDMI or jack output we use the -c 1 switch, like so:

.. highlight:: bash

::

   alsamixer -c 1


Since we want to make sure the volume settings are kept on reboot we use:

.. code-block:: bash

   sudo alsactl store

------------------------------------
Installing and configuring mpd
------------------------------------
First, we'll just install mpd.

.. code-block:: bash

   sudo apt-get install mpd mpc

Then we configure mpd's settings with:

.. code-block:: bash

   sudo nano /etc/mpd.conf

Some mpd clients use zero-conf so that accessing the mpd is made extremely easy. For that I will install the necessary components in a later step. For now we can already set-up the feature in the config by un-comment the line containing:


.. code-block:: bash

   zeroconf_enabled        "yes"

and change the line for the zero-conf name so becomes:

.. code-block:: bash

   zeroconf_name           "Pi-Jukebox"


last.fm scrobbling
==================

Since I have an last.fm account I also want to scrobble my plays to it. Luckily a nice little tool called mpdscribble allows us to do just that. Install it with

.. code-block:: bash

   sudo apt-get install mpdscribble

Configure it:

.. code-block:: bash

   sudo nano /etc/default/mpdscribble

Here we change "MPD_SYSTEMWIDE=0" to "MPD_SYSTEMWIDE=1" and add the lines:

.. code-block:: bash

   [last.fm]
   url=http://post.audioscrobbler.com/
   username=_yourusername_
   password=_yourpassword_
   journal=/var/cache/mpdscribble/lastfm.journal   # The file where mpdscribble should store its Last.fm journal in case you do not have a connection to the Last.fm server.


last.fm suggestions
===================

Wouldn't it be neat if your playlist would be supplemented with music similar to the last track in your playlist? A tool called mpd-sima does just that. We install and start it with:

.. code-block:: bash

   sudo apt-get install mpd-sima
   sudo service mpd-sima start

This automatically adds 1 track whenever your player reaches the last track in your current playlist. You can change some of it's behaviour by editing the, self explanatory, configuration file and restarting the service after that:

.. code-block:: bash

   sudo nano /etc/mpd-sima.cfg 
   sudo service mpd-sima restart

--------------------------------
Setting up the music library
--------------------------------

Setting up the NAS drive
========================
My NAS drive contains a publicly (LAN public) available directory called Public, which in turn contains my music folder surprisingly called 'Music'. 

Mounting the NAS
----------------
For mpd to be able to make use of your NAS drive you need to mount it at boot time. First create a directory where the NAS drive will be mounted:

.. code-block:: bash

   sudo mkdir /mnt/nas_drive

Then, to make sure the drive mounts on boot, edit fstab:

.. code-block:: bash

   sudo nano /etc/fstab

and add something along the following line

.. code-block:: bash

   //_your.nas.drive.ip_/Public /mnt/nas_drive cifs guest,uid=1000,gid=1000,iocharset=utf8 0 0


Now everything should be ready to mount the NAS at boot. To mount without rebooting now (and test whether it works), do:

.. code-block:: bash

   sudo mount -a

Hopefully you didn't get an error message. See if the NAS content is available on your Pi-Jukebox, do:

.. code-block:: bash

   ls -l /mnt/nas_drive

Does the output look familiar? Then everything should be fine

Making the NAS available for mpd
--------------------------------
In order for mpd to be able to scan the music on the NAS we must make a link to the NAS drive in the directory where mpd scans it's music. Keep in mind that I stored my music in a subdirectory called 'Music' of the just mounted directory 'Public'. Make the link like so:

.. code-block:: bash

   sudo ln -s /mnt/nas_drive/Music/  /var/lib/mpd/music/

Setting up USB stick configuration
==================================
Because I wanted to make sure I was able to access the USB stick, whatever name it might have, I made use of usbmount. This utility mounts all usb drives in the directory /media in subdirectories called usb0,usb1 and so on.

.. code-block:: bash

   sudo apt-get install usbmount

To make the mounted (or future mounted) USB sticks available to mpd scanning we also make a link to these:

.. code-block:: bash

   sudo ln -s /media/ /var/lib/mpd/music/
   
Finally: adding the music to the mpd library
============================================
To scan all the music sources you just added so the music can actually be reached through mpd:

.. code-block:: bash

   mpc update
   
Depending on the size of your library this can take some time. Make sure the scan is completed before rebooting or turning off your Raspberry or you'll have to start scanning again. I suggest to do the scanning after completing the rest of the set-up.

--------------------------------------------
Zeroconf
--------------------------------------------


Zeroconf, sometimes called bonjour, is a group of utilities that allows for easy networking without special configuration or any manual operations. I also wanted the possibility to control the Pi-Jukebox from other devices within the network I thought this would be a useful addition. The installation is quite straightforward:

.. code-block:: bash

   sudo apt-get install libnss-mdns

Starting the zeroconf deamon:

.. code-block:: bash

   sudo service avahi-daemon restart


------------------------------------
Samba server
------------------------------------

We need to put the pi-jukebox program on the device, and it is also nice if we can access the USB storage devices so we can put some files on them. For this we're going to create two window shares. One for the home directory of the user 'pi' and one for the USB mount directory.

First we're going to install samba and related packages:

.. code-block:: bash

   sudo apt-get install samba samba-common-bin 

Now we create the shares by editing the samba config:

.. code-block:: bash

   sudo nano /etc/samba/smb.conf

and adding the entries

.. code-block:: bash

   [pihome]
      comment= Pi Home
      path=/home/pi
      browseable=Yes
      writeable=Yes
      only guest=no
      create mask=0777
      directory mask=0777
      public=no

   [piusb]
      comment= Pi USB drives
      path=/media
      browseable=Yes
      writeable=Yes
      only guest=no
      create mask=0777
      directory mask=0777
      public=no

Then we're going to set the samba user pi's password. I'm going to share a big secret here: I kept it the same as the default pi account: 'raspberry'

.. code-block:: bash

   sudo smbpasswd -a pi

To make the changes effective we're going to restart the samba server:

.. code-block:: bash

   sudo service samba restart


-------------
WiFi
-------------
You want to enable your WiFi right? Is there life worth living without 
wifi? So bet your life I'm on it! I'm all about 'making magic happen'. 
In time it will be all right here... Wait, see and weep.

