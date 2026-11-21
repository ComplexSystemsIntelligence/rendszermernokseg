#!/usr/bin/env bash
# A két könyv teljes fordítása és a közös webhely összeállítása a _site mappába.
# Használat: ./build.sh            (minden formátum)
#            ./build.sh html       (csak webes változat, gyors előnézet)
# ABRAK_KIHAGY=1 esetén az ábrák és a borítók nem fordulnak újra (a verziókövetett
# abrak/gen és assets/borito.png fájlok kerülnek a könyvbe); a GitHub Actions így fordít.
set -euo pipefail
GYOKER="$(cd "$(dirname "$0")" && pwd)"
FORMATUM="${1:-}"
if [ -z "${ABRAK_KIHAGY:-}" ]; then
  python3 "$GYOKER/_shared/scripts/abrak.py" kezikonyv gyakorlat
fi
for k in kezikonyv gyakorlat; do
  ( cd "$GYOKER/$k" && if [ -n "$FORMATUM" ]; then quarto render --to "$FORMATUM"; else quarto render; fi )
done
rm -rf "$GYOKER/_site" && mkdir -p "$GYOKER/_site"
cp -r "$GYOKER/kezikonyv/_book" "$GYOKER/_site/kezikonyv"
cp -r "$GYOKER/gyakorlat/_book" "$GYOKER/_site/gyakorlat"
cp "$GYOKER/landing/index.html" "$GYOKER/_site/index.html"
touch "$GYOKER/_site/.nojekyll"
# feloldatlan kereszthivatkozás nem maradhat a kimenetben
if grep -rl "quarto-unresolved-ref" "$GYOKER/_site" --include="*.html"; then
  echo "HIBA: feloldatlan kereszthivatkozás maradt (lásd a fenti fájlokat)" >&2
  exit 1
fi
echo "Kész: $GYOKER/_site"
