# Rolling Shutter

* Alles anschließen: USB-Kamera, Tastatur, (Maus kann, aber muss nicht)
* Terminal öffnen (Alt + Strg + t) und dort 'ls /dev/input/' (ohne Anführungszeichen) eingeben.
* Controller einstecken.
* Abermals 'ls /dev/input' eingeben.
* Gucken, welches Device ('event_') nun erschienen ist.
* 'nano RollingShutter.py' eingeben.
* Die Zeile im oberen Teil des Scripts suchen, die mit 'device = /dev/input/event'.. beginnt.
* 'event_' ersetzen mit dem zuvor herausgefundenen Namen des Controllers. (z. B.  device = '/dev/input/event3')
* Drauf achten, dass MODE auf "controller" steht. MODE = "desktop" auskommentieren, MODE = "controller" unkommentieren.
* Strg + X, um nano zu verlassen, bestätigen mit 'y' (falls deutsch, dann mit 'j'), dann nochmal Enter.
* 'python3 RollingShutter.py' eingeben, dann sollte es starten.
