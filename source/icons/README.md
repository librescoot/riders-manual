# Drucksymbole

`extract_icons.py` erzeugt die Dashboard-Symbole aus den öffentlichen Quellen unter `inputs/code/scootui-qt` (Commit `220cf2498881bd93a1c6e8fd2f2286b7be71089c`, scootui-qt v1.24.0).

- Originalkonturen: `assets/icons/librescoot-*.svg`.
- Kältewarnung, Zuhause und Arbeit: Konturen der im Dashboard eingebundenen Schrift `assets/fonts/subset/MaterialSymbolsOutlined-Filled.ttf`, Codepoints aus `qml/widgets/components/MaterialIcon.qml`. Die Kälteanzeige verwendet tatsächlich `iconSevereCold` (Schneeflocke mit Ausrufezeichen), nicht ein beliebiges Schneeflockenzeichen.
- Farben sind für weißen Papiergrund angepasst. Schwarze Symbole entsprechen den im dunklen Dashboard weißen Konturen; Gelb ist auf Papier dunkler gesetzt. Keine Emojis oder Ersatzzeichnungen für Dashboard-Symbole.
- Repository und Lizenz: https://github.com/librescoot/scootui-qt/tree/220cf2498881bd93a1c6e8fd2f2286b7be71089c ; projektweite Lizenz unter `inputs/code/scootui-qt/LICENSE`. Die Material-Schrift enthält den Copyright-Vermerk Google LLC.
- `led-blink.svg` ist eine eigene Druckgrafik mit acht Blinkstrahlen. Im gesicherten Stand 1.4.0 ist sie grün: damalige Einschaltfarbe `ColorGreen`, `StartBlink()` wechselt zwischen `On()` und `Off()`. Im 1.4.2-Kandidaten ist sie gelb: `publishLearnState()` setzt jetzt `SetFeedbackMode("master-bootstrap")`; `indicator.go` wählt dafür `ColorAmber`. Die Farbe wurde daher auf diesem Branch angepasst.

## Ergänzungen für die Vorbereitung auf 1.4.2

Die oben genannten ScootUI-Assets sind gegenüber dem Kandidaten `103e3f6d5156517b342db3a613d42e62d6545621` unverändert.

- `led-armed.svg`: eigene Druckgrafik für den kurzen roten Alarm-Puls; gleiche Blinkstrahlen wie bei `led-blink.svg`. Beleg: `keycard-service` bei `9dea604ccb2d4cff4999273fa6f945ef7b671c1e`, `keycard/indicator.go` und `alarm_indicator.go`. Keine zusätzliche Leuchte am Fahrzeug.
- `trip-start.svg`, `trip-end.svg`: Kreismarkierungen mit Originalfarben und weißem Rand entsprechend `scootui-qt/qml/screens/TripHistoryMap.qml` im Kandidaten. Die Kartendarstellung erzeugt diese Kreise zur Laufzeit; sie liegen dort nicht als SVG-Dateien vor.
- Diese drei Dateien sind handgepflegte Ergänzungen und werden von `extract_icons.py` nicht erzeugt.

Verwendung in HTML: `{{icon:parking}}`, `{{icon:seat-open}}` usw. Der Builder bettet alle Konturen inline ein, vergibt pro Verwendung eindeutige Clip-/Masken-IDs und lässt die zugänglichen Beschriftungen bestehen.
