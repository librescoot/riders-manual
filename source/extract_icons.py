#!/usr/bin/env python3
"""Bereitet echte scootui-qt-Symbole als skalierbare Druckgrafiken auf.

Konturen unverändert, Farben für weißen Papiergrund angepasst. Die drei
Material-Symbol-Konturen stammen aus derselben Schrift wie die Dashboard-UI.
"""
from pathlib import Path
import xml.etree.ElementTree as ET
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

SRC = Path(__file__).resolve().parent
QT = SRC.parent / 'inputs/code/scootui-qt'
OUT = SRC / 'icons'
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
# Kurzname: Originaldatei, zugängliche Beschriftung, Druckfarbe
ICONS = {
    'parking': ('parking-brake', 'Parkmodus', '#b91c24'),
    'hazards': ('hazards', 'Warnblinker', '#b91c24'),
    'engine': ('engine-warning', 'Motorwarnung', '#a88000'),
    'turtle': ('turtle-mode', 'Leistungsbegrenzung', '#b86a00'),
    'seat-open': ('seatbox-open', 'Sitzbank offen', '#1d1d1b'),
    'seat-button': ('seatbox-button', 'Sitzbank-Schalter', '#1d1d1b'),
    'turn-left': ('turn-left', 'Blinker links', '#198226'),
    'turn-right': ('turn-right', 'Blinker rechts', '#198226'),
    'gps': ('gps-fix-established', 'GPS-Empfang', '#1d1d1b'),
    'bluetooth': ('bluetooth-connected', 'Bluetooth verbunden', '#1d1d1b'),
    'cloud': ('internet-cloud-connected', 'Cloud verbunden', '#1d1d1b'),
    'internet': ('internet-modem-connected-4', 'Mobilfunk verbunden', '#1d1d1b'),
    'cbb': ('cb-battery-level-100', 'CBB-Stützbatterie', '#1d1d1b'),
    'aux': ('aux-battery-level-100', '12-V-Stützbatterie', '#1d1d1b'),
    'battery': ('main-battery-blank', 'Fahrakku', '#1d1d1b'),
    'battery-fault': ('main-battery-fault', 'Fahrakku mit Fehler', '#b91c24'),
    'download': ('ota-status-downloading', 'Update herunterladen', '#1d1d1b'),
    'preparing': ('ota-status-preparing', 'Update vorbereiten', '#1d1d1b'),
    'installing': ('ota-status-installing', 'Update installieren', '#1d1d1b'),
    'reboot': ('ota-status-waiting-for-reboot', 'Update wartet auf Neustart', '#1d1d1b'),
}


def decorate(root, name, label, color):
    root.attrib.pop('width', None)
    root.attrib.pop('height', None)
    root.set('class', 'inline-icon icon-' + name)
    root.set('role', 'img')
    root.set('aria-label', label)
    root.set('style', 'color:' + color)
    return root


def main():
    OUT.mkdir(exist_ok=True)
    for name, (original, label, color) in ICONS.items():
        root = ET.parse(QT / 'assets/icons' / ('librescoot-' + original + '.svg')).getroot()
        # Masken und Clip-Pfade bleiben unverändert; nur sichtbare Farben ersetzen.
        def recolor(node, masked=False):
            masked = masked or node.tag.rsplit('}', 1)[-1] in ('mask', 'clipPath', 'defs')
            if not masked:
                for attr in ('fill', 'stroke'):
                    if attr in node.attrib and node.attrib[attr] not in ('none', 'transparent'):
                        node.set(attr, 'currentColor')
            for child in node:
                recolor(child, masked)
        recolor(root)
        decorate(root, name, label, color)
        (OUT / (name + '.svg')).write_text(ET.tostring(root, encoding='unicode') + '\n')

    font = TTFont(QT / 'assets/fonts/subset/MaterialSymbolsOutlined-Filled.ttf')
    glyphs, cmap = font.getGlyphSet(), font.getBestCmap()
    em = font['head'].unitsPerEm
    for name, cp, label in [('cold', 0xebd3, 'Kältewarnung'), ('home', 0xe9b2, 'Zuhause'), ('work', 0xe943, 'Arbeit')]:
        pen = SVGPathPen(glyphs)
        glyphs[cmap[cp]].draw(pen)
        root = ET.Element('{' + NS + '}svg', {'viewBox': f'0 0 {em} {em}'})
        decorate(root, name, label, '#1d1d1b')
        ET.SubElement(root, '{' + NS + '}path', {
            'fill': 'currentColor', 'transform': f'translate(0 {em}) scale(1 -1)', 'd': pen.getCommands()})
        (OUT / (name + '.svg')).write_text(ET.tostring(root, encoding='unicode') + '\n')
    print('Drucksymbole aus scootui-qt:', len(ICONS) + 3)


if __name__ == '__main__':
    main()
