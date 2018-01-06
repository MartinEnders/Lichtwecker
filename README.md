RaspberryPi Lichtwecker
=======================

Lichtwecker
------------
Zum aufwecken wird eine Gluehbirne langsam immer heller.


Umsetzung
------------
Ueber den RaspberryPi wird einen Weboberflaeche zur Verfuegung gestellt ueber die die Weckzeit (und andere Parameter) eingestellt werden kann.

Zum Dimmen wird ein Leistungssteller via PWM-Signal vom RaspberryPi angesteuert.

GPIO (on/off, pwm):
* http://abyz.co.uk/rpi/pigpio/pigpiod.html

Aktueller Stand der Dokumentation
------------------------------------
2018-01-06:

Erweiterung der Weboberflaeche um einen Shutdown-Button.
Um den Raspberrypi herunterzufahren gibt es jetzt einen Shutdown-Button am unteren Ende der Weboberflaeche. Der Button muss zweimal innerhalb von fuenf Sekunden betaetigt werden um den Pi heruterzufahren.


2015-12-12:

Python Skript (Backend - wecker_web.py) und JavaScript (Frontend static/main.js)

Diese Loesung ist ein erster Entwurf - die Implentierung ist noch sehr verbesserungsfaehig (-:


Screenshot
------------
Screenshot der Weboberflaeche auf einem iPhone 5:

![Screenshot](pictures/weboberflaeche-iphone.png)


Bemerkungen
---------------

#### pigpiod starten

Bei der Installation von pigpiod ist schon ein initscript dabei. (Quelle: https://gpiozero.readthedocs.io/en/stable/remote_gpio.html)

```bash
sudo systemctl enable pigpiod
```

#### Webserver starten

Im Verzeichnis ```init-scripts``` liegen Skripte fuer ```/etc/init.d/``` (Webserver und gpiod) und fuer den Webserver fuer ```sytsemd```.

Fuer ```systemd``` bei pigpiod am besten das mitgelieferte script verwenden.

#### Webserver
Der Pythonwebserver ist manchmal nicht zugreifbar, geht aber wieder nachdem man sich via SSH auf dem PI angemeldet hat.
Viellicht ist das unter folgendem Link eine Loesung: https://wiki.archlinux.org/index.php/Systemd/User#Automatic_start-up_of_systemd_user_instances

Der Zugriff auf den Webserver lag scheinbar daran, dass sich der WLAN-Stick den ich verwende schlafen gelegt hat. Man konnte sich dann auch nicht via ssh verbinden.

Das script unter wlan-helper-script/wlan.sh lasse ich jetzt mit einem cronjob minuetlich laufen - damit funktioniert der Zugriff auf den Pi via WLAN jetzt zuverlaessig.


#### Tonwecker
Zusaetzlicher Ton zum Licht der langsam immer lauter wird:

omxplayer: http://elinux.org/Omxplayer
omxplayer Python: https://github.com/willprice/python-omxplayer-wrapper

Test mit omxplayer hat einwandrei funktioniert:
```bash
omxplayer test.mp3
```
