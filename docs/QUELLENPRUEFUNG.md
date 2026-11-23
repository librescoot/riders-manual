# Quellcode-Abgleich des Fahrerhandbuchs

Diese historische Basisprüfung dokumentiert den Stand 1.4.0/1.4.1. Für die aktuelle Ausgabe gilt der [Versionsabgleich 1.4.3](AENDERUNGEN-1.4.3.md). Die Bewertung unten bleibt zur Nachvollziehbarkeit erhalten.

## Umfang und Stand

Geprüft wurden die offenen Softwareangaben aus dem Review: deutsche Menünamen und Menüstruktur, Kartenverwaltung und Android-NFC-Schlüssel, LED-Rückmeldungen, USB-Ablauf, Cloud-Kopplung, Update-Neustarts sowie die B-/E-Fehlercodes. Ergänzend wurden Menübedienung, SMS-Bedienung, Versionsbox und Teile der Routenbedienung gelesen. Dies ist kein vollständiger Audit aller Aussagen des Handbuchs und kein Fahrzeugtest.

Die öffentlichen Repositories wurden für die Basisprüfung unter `inputs/code/` abgelegt. Dieses Handbuch-Repository enthält daraus nur die benötigten Build-Eingaben; die vollständigen Quellen sind über die unten genannten Commits zugeordnet. Es wurde kein Fahrzeug angesprochen und keine Anwendung oder Dienstsoftware daraus gestartet. Die Prüfung erfolgte statisch am Quellcode; vorhandene Unit-Tests wurden nicht ausgeführt.

Versionen wurden anhand von `librescoot/stable.env` in den Tags `v1.4.0` und `v1.4.1` zugeordnet, nicht anhand gleichlautender Versionsnummern der Einzelkomponenten. Zwischen diesen beiden Manifesten ändern sich nur `scootui-qt` und `radio-gaga`. Die hier geprüften Menüs, Übersetzungen, Schlüssel-, USB- und Update-Dienste unterscheiden sich dabei nicht. Der scootui-Diff ergänzt Start-/Endmarkierungen in der Fahrtenverlaufs-Karte und einen Benachrichtigungstest. Diese Markierungen wurden nicht als Eigenschaft von 1.4.0 ins Handbuch aufgenommen.

| Quelle | Geprüfter Commit |
| --- | --- |
| [librescoot v1.4.0](https://github.com/librescoot/librescoot/tree/v1.4.0) | `924bb399d1bdb593e7cf81abe2dfc67a4eb18577` |
| [scootui-qt v1.24.0](https://github.com/librescoot/scootui-qt/tree/220cf2498881bd93a1c6e8fd2f2286b7be71089c) | `220cf2498881bd93a1c6e8fd2f2286b7be71089c` |
| [scootui-qt v1.24.1](https://github.com/librescoot/scootui-qt/tree/4e058ca83189aee3464aca5b465b4b09901cd1aa), Diff zu v1.24.0 | `4e058ca83189aee3464aca5b465b4b09901cd1aa` |
| keycard-service v0.6.1 | `65146e8d6df1f44d2c33d7ff638a1ee68a62c2c1` |
| vehicle-service v0.14.3 | `0db4145fda08e6cd6f4d7910757ec1e48588173c` |
| ums-service v0.7.0 | `3fd5f6250971300e570d253eb632b645940f03b3` |
| update-service v0.17.6 | `1fad3ec4d0942b4645de5fc0b6751c4b7bed7241` |
| bluetooth-service v0.19.0 | `49e82fbd62a4077c7f5030ac9831304d96637dcc` |
| dbc-backlight-service v0.8.0 | `d3fdae95c067b4bfd32ae458ca67d055277b69f9` |
| mobile-app, öffentlicher Stand vom 1. November 2026, `pubspec.yaml`: 1.3.0+66 | `81ecdceb8dc9e6b17834e825ac89b95a96c2083a` |

Die App wird unabhängig von der Roller-Firmware versioniert. Ihre Aussagen gelten für den oben genannten Quellstand, nicht pauschal für jede installierte APK.

## Ergebnisse und Änderungen

### Menünamen: Konflikt aufgelöst

`scootui-qt/src/l10n/Translations.cpp` bestätigt:

- `menuAppearance`: Darstellung
- `menuTripCounter`: Fahrtenzähler
- `menuAlarm`: Alarm
- `menuAlarmEnable`: Bei Sperre aktivieren
- `menuMapNav`: Karte & Navigation
- `menuTripHistory`: Fahrtenverlauf
- `menuKeycards`: Schlüsselkarten
- `keycardEnrollTitle`: Karte oder Handy hinzufügen

`src/stores/MenuStore.cpp` bestätigt die zugehörigen Elternknoten: Darstellung, Fahrzeug, Karte & Navigation, Schlüsselkarten, System und Cloud liegen unter Einstellungen; Info und Fahrtenverlauf direkt im Hauptmenü. Statusleiste und Design liegen unter Darstellung, Alarm und Fahrtenzähler unter Fahrzeug, Updates und Sprache unter System. Das Handbuch hatte diese Struktur bereits richtig. Die abweichenden Bezeichnungen aus der Web-Dokumentation sind dafür nicht maßgeblich. Der falsche Anlerntext auf Seite 17 wurde ersetzt.

### Android-NFC: wesentliche Einschränkung ergänzt

In `mobile-app/lib/feature_flags.dart`, Zeilen 5 bis 9, gilt:

```dart
!releaseMode && platform == TargetPlatform.android
```

Damit ist die Telefonschlüssel-Einrichtung im geprüften Quellstand in Release-Builds ausgeblendet. Auch die geprüften Nightly-/Testbuild-Workflows bauen mit `--release`; allein die Bezeichnung Nightly ist deshalb keine ausreichende Empfehlung. Das Handbuch nennt jetzt einen Build mit freigeschalteter Funktion, ohne eine konkrete verfügbare APK zu behaupten.

`lib/ui/screens/ls_keycard_screen.dart`, ab Zeile 224, zeigt den zunächst eingeklappten Abschnitt `Use this Android phone as a key`, den Schalter `Provide NFC phone key` und die Schaltfläche `Set up / show phone key`. Diese Texte sind dort tatsächlich Englisch, auch bei deutscher App-Sprache. `assets/i18n/de.json` nennt die übergeordnete Seite tatsächlich `Keycards`. Der Zugang in `settings_screen.dart` setzt erfolgreich geladene Kartendaten der verbundenen App voraus. Deshalb ist die Bluetooth-Verbindung als Einrichtungsschritt ergänzt.

`android/app/src/main/res/xml/phone_key_service.xml` verlangt entsperrtes Gerät und eingeschaltetes Display. `keycard-service/README.md` beschreibt NFC/HCE, Anlernen mit Anlernkarte und den Verlust des Geräteschlüssels bei App-Neuinstallation. Diese Anforderungen stehen jetzt ausdrücklich auf Seite 18; Seite 6 und Musterseite 5 verweisen beziehungsweise schränken entsprechend ein.

### Karten und LED

`keycard-service/keycard/service.go` bestätigt getrennte Anlern-/Entsperrrollen, Lernmodus über Anlernkarte, Speichern beim Beenden, rote Ablehnung schon registrierter Karten und das Bootstrap-Verhalten ohne gespeicherte Karten. `scootui-qt/src/stores/MenuStore.cpp`, ab Zeile 1385, bestätigt getrennte Gruppen und Rückfragen beim Entfernen der letzten Karte beziehungsweise des letzten alleinigen Telefonschlüssels.

Die Farbrückmeldungen sind durch `service.go` und `lp5562.go` belegt. Die physische Zuordnung ist nicht aus diesem Code ableitbar, wurde aber anschließend durch den Nutzer bestätigt: Die in der Website-Animation aufleuchtende untere Stelle ist die Status-LED. Sie sitzt vertikal mittig im Gehäuse; der obere Punkt ist der darüberliegende Lichtsensor. Beide Zeichnungen und die Führungslinie wurden entsprechend korrigiert. Dies ist eine Nutzerbestätigung, kein eigener Fahrzeugtest.

### Nachtrag: Symbole und Blinkfarbe

Die Symbolkonturen im Handbuch stammen jetzt direkt aus `scootui-qt/assets/icons/` beziehungsweise für Kälte, Zuhause und Arbeit aus der im Dashboard eingebundenen Material-Symbols-Schrift. `qml/widgets/components/MaterialIcon.qml` liefert die Codepoints; `qml/widgets/indicators/StatusIndicators.qml` verwendet für die Kältewarnung `iconSevereCold`. Herkunft und Druckanpassungen stehen in `source/icons/README.md`.

Die bislang weiße Darstellung des Blinkens ist korrigiert: Für den beschriebenen Erst-Anlernmodus wird Grün gezeigt, mit Blinkstrahlen. Beleg: `keycard-service/keycard/lp5562.go` initialisiert die gespeicherte Einschaltfarbe mit `ColorGreen`; `StartBlink()` wechselt zwischen `On()` (gespeicherte Farbe) und `Off()`. `enterMasterBootstrap()` in `service.go` startet dieses Blinken. Die hellere grüne, bernsteinfarbene und dunklere rote Darstellung ist eine Druckillustration, keine Farbmessung am Fahrzeug.

### USB: tatsächliches Beenden ergänzt

`scootui-qt/src/core/Application.cpp`, ab Zeile 1051, setzt nach Bestätigung am Display `usb.mode=ums-by-dbc`. `ums-service/internal/service/service.go`, Funktion `onDeviceDetached` ab Zeile 1057, wartet in diesem Modus auf zwei Trennungen: zuerst internes Display-Kabel, dann Computer. Die zweite beendet den Updatemodus.

Seite 30 sagt deshalb nicht mehr nur unbestimmt den Updatemodus verlassen: Laufwerk sauber auswerfen, Computer-USB-Kabel abziehen, internes Display-Kabel wieder anschließen. Letzteres ist auch für die anschließende Übertragung von Karten oder Firmware zum Display nötig. Der Updatemodus wird weiterhin vor dem Abziehen des Display-Kabels gewählt.

### Cloud: Öffnen und Starten getrennt

`MenuStore.cpp`, ab Zeile 1791, öffnet mit Konto verbinden lediglich die Kopplungsseite. `qml/screens/CloudPairingScreen.qml`, ab Zeile 71, startet erst dort mit `onRightTap()` die Kopplung. Seite 33 unterscheidet diese beiden Schritte jetzt und nennt Kopplung starten. Die Sichtbarkeitsbedingung des Cloud-Menüs (MDB-Verbindung und Internetstatus Connected) stimmt.

### Neustarts: USB-Ausnahme statt pauschaler Aussage

`update-service/internal/updater/mdb_reboot.go` und `updater.go` (`dbcRebootAllowedState`) verlangen Standby für die betreffenden Neustarts des Update-Dienstes. Der USB-Dienst besitzt aber einen eigenen MDB-Neustartpfad: `ums-service/internal/service/service.go`, `rebootAllowedVehicleStates` und `reconcileRebootOwner`, lässt auch Parkmodus und Herunterfahren zu. Dies ist bereits im Manifest von 1.4.0 enthalten und unverändert in 1.4.1.

Seite 32 weist daher auf den möglichen Hauptcomputer-Neustart im Parkmodus nach USB-Updates hin. Musterseite 12 sagt allgemeiner, dass die neue Version nach dem Neustart aktiv wird. Keine neuen Neustartregeln wurden aus Vermutungen über 1.4.1 ergänzt.

### Fehlercodes: vollständig statt gruppiert

`src/utils/FaultFormatter.cpp` und `src/l10n/Translations.cpp` definieren die Einzelbedeutungen. `src/core/Application.cpp` leitet die Schweregrade an die Benachrichtigungen weiter; `qml/notifications/NotificationCard.qml` definiert deren Farben.

Seiten 35 und 36 führen jetzt alle dort definierten B- und E-Codes einzeln mit Farbe auf. B5, B6, B14, B32, B34 und B35 sind kritisch/rot, die übrigen aufgeführten B-Codes Warnungen/orange. Bei E ist nur E14 orange, die anderen aufgeführten E-Codes sind rot. Reservierte B-Codes sind als reserviert benannt, nicht mit erfundener Bedeutung gefüllt. E20 ist der Ausfall der ECU-Kommunikation. Die praktischen Akku-Hinweise stammen weiterhin aus dem Web-Handbuch; aus UI-Quellcode allein lassen sich keine Reparatur- oder Ladesicherheitsregeln ableiten.

## Grenzen und noch offene Arbeit

- LED und Lichtsensor sind nach Nutzerangabe zugeordnet und positioniert. Ihr genauer Abstand ist schematisch, nicht vermessen.
- Die Lenker-Bildschritte sind eine schematische Ableitung der freigegebenen Zeichnung, keine am Fahrzeug gemessene Perspektive oder Endanschlag-Geometrie.
- Kein kompletter Quellabgleich von Installer, Ladeverhalten, Akkugrenzwerten, Pflege und allen Winterschlafdetails in dieser Runde.
- Neue Screenshots, Sitzkasten-/Akkuwechselbilder und gestalterische Überarbeitung der luftigen Seiten stehen weiterhin aus.
- Nach den Änderungen werden beide Handbuch-Builds geprüft. Tatsächlich ausgeführte Build- und Sichtprüfungen stehen im aktuellen Abschnitt von `HANDOFF.md`.
