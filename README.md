# Librescoot Rider's Manual

Illustrated A5 rider's manual for the unu Scooter Pro running **Librescoot** (Stable 1.4.3 / Installer 1.4.10), built from HTML and SVG sources via GitHub Actions.

PDFs are built automatically in CI and published on GitHub Releases rather than committed as binaries in Git.

## Languages

- **German (`de`)**: `source/de/` -> `librescoot-riders-manual-de.pdf` (46 pages), `librescoot-riders-manual-de-sample.pdf` (12 pages)
- **English (`en`)**: `source/en/` -> `librescoot-riders-manual-en.pdf` (46 pages), `librescoot-riders-manual-en-sample.pdf` (12 pages)

## Repository layout

- `source/build.py`: multi-language offline PDF builder and strict layout/reference/font verifier.
- `source/extract_icons.py`: extracts and recolors dashboard icons from `inputs/code/scootui-qt`.
- `source/style.css`: shared A5 print layout.
- `source/svg/` and `source/icons/`: shared language-neutral vector drawings, QR codes, and icons.
- `source/<lang>/`: language configuration (`lang.json`), chapter HTML files (`chapters/`), sample booklet (`sample.html`), and localized diagram SVGs (`svg/`).
- `inputs/`: self-contained build inputs (fonts, screenshots, icons, release manifests).
- `docs/`: source verification notes ([1.4.3 changelog/audit](docs/AENDERUNGEN-1.4.3.md), [baseline audit](docs/QUELLENPRUEFUNG.md)).
- `.github/workflows/build.yml`: builds all languages with `--strict`, uploads artifacts, and publishes release PDFs on tags.

## Building locally

Requirements:

- Python 3 with `fonttools`
- Chrome or Chromium (headless)
- Poppler (`pdftoppm`, `pdfinfo`, `pdffonts`)
- ImageMagick (`montage`, only needed when generating preview sheets)

Build all languages and run strict checks:

```sh
python3 source/build.py --lang all --strict --version 1.4.3
```

Build a single language or target:

```sh
python3 source/build.py --lang de full --strict
python3 source/build.py --lang en full --strict
python3 source/build.py --lang de sample --strict --no-previews
```

Outputs are written to `dist/` (gitignored):

- `dist/librescoot-riders-manual-<lang>.pdf`
- `dist/librescoot-riders-manual-<lang>-sample.pdf`
- `dist/previews/<lang>-<target>/` (PNG pages and contact sheet unless `--no-previews` is set)
- `tmp/build/<lang>/report-<target>.json`

The build requires no network access.

## Adding a language

1. Create `source/<lang>/lang.json` with localized prefixes (`page_prefix`, `fig_prefix`, `chapter_prefix`), output filenames, and image mappings.
2. Add translated chapters under `source/<lang>/chapters/` and optional `source/<lang>/sample.html`.
3. Place localized text-bearing diagram SVGs (`schnellmenue.svg`, `stopps.svg`, `zeitfenster.svg`, `zustaende.svg`) in `source/<lang>/svg/` to override the shared fallbacks.
4. Run `python3 source/build.py --lang <lang> --strict` and inspect the rendered previews.

## Sources and license

This manual is licensed under **CC BY-NC-SA 4.0** (see [LICENSE](LICENSE)).

Website assets are tracked in [inputs/website-snapshot.json](inputs/website-snapshot.json). Dashboard icons come from `scootui-qt` (see [source/icons/README.md](source/icons/README.md)), and the logotype from the 1.4.3 pin (`9db25f53db2e8675e198fb28413693d956b6da6d`). Simulator screenshots and their provenance are documented in [inputs/screenshots/README.md](inputs/screenshots/README.md). Map data copyright OpenStreetMap contributors.
