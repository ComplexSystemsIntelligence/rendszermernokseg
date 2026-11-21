#!/usr/bin/env bash
# Kiadás előkészítése: a teljes webhely fordítása, majd a PDF- és EPUB-fájlok bemásolása a kiadas/ mappába,
# hogy a GitHub-kiadás forráscsomagjával a Zenodo az olvasható könyvet is archiválja.
# Előtte frissítendő: a CITATION.cff (version, date-released) és a _shared/latex/preamble.tex \peValtozat sora.
set -euo pipefail
cd "$(dirname "$0")"
./build.sh
mkdir -p kiadas
cp _site/kezikonyv/rendszermernokseg-kezikonyv.pdf  kiadas/
cp _site/kezikonyv/rendszermernokseg-kezikonyv.epub kiadas/
cp _site/gyakorlat/rendszermernokseg-gyakorlat.pdf  kiadas/
cp _site/gyakorlat/rendszermernokseg-gyakorlat.epub kiadas/
ls -la kiadas
