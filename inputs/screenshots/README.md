# Simulatoraufnahmen für Stable 1.4.3

Beide Bilder zeigen das vollständige 480 × 480 Fenster von ScootUI im Simulator. Grundlage ist der in Stable 1.4.3 gepinnte öffentliche Stand [scootui-qt `9db25f53`](https://github.com/librescoot/scootui-qt/tree/9db25f53db2e8675e198fb28413693d956b6da6d). Die Anwendung lief mit XCB und OpenGL unter Xvfb, mit isoliertem Redis und dem produktionsnah gepatchten QMapLibre. Die Uhr des Aufnahmeprozesses war auf 15. Juni 2026, 10:08 Uhr gestellt. Die Bilder wurden direkt aus dem Dashboard-Fenster aufgenommen.

- `fahrtenbuch-1.4.3-de.png` / `trip-history-1.4.3-en.png`: synthetische Fahrt vom selben Tag um 09:00 Uhr, 6,0 km in 27 Minuten. Die Spur folgt einer Beispielroute in Berlin mit Kartendaten von [OpenStreetMap-Mitwirkenden](https://www.openstreetmap.org/copyright). Die Karte verwendet lokale Vektorkacheln; Start und Ende sind unterscheidbar. Weder Route noch Statistik beschreiben eine tatsächliche Fahrt.
- `doctor-1.4.3-de.png` / `doctor-1.4.3-en.png`: Das echte Dashboard zeigt zwei synthetische Doctor-Antworten mit jeweils sechs erfolgreichen Prüfungen. Die Ergebnisse stammen nicht von einem Fahrzeug. Die Diagnoseprozesse waren für die Aufnahme durch lokale Testantworten ersetzt; der SSH-Aufruf war isoliert und konnte kein Fahrzeug erreichen.
- `cluster-parked-dark-en.png`: Englisches Dashboard im Parkmodus (dunkles Design, 10:08 Uhr, zwei synthetische Fahrakkus 80 % und 75 %, keine aktiven Fehler).
- `navigation-1.4.3-de.png` / `navigation-1.4.3-en.png`: Aktive 3D-Navigation im hellen Design entlang der eingebauten Berliner Simulator-Testroute (`route2`, 28 km/h in Fahrtrichtung Spandauer Straße Richtung Anna-Louisa-Karsch-Straße, 10:08 Uhr, konsistente ETA 10:18 Uhr, lokale Vektorkacheln, OpenStreetMap-Daten).

Es wurde keine Hardware bedient. Die Bilder sind in den Bildunterschriften als simulierte Beispiele gekennzeichnet.
