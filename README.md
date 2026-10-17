# Elektriciteit

ManimGX-code voor YouTube-video's natuurkunde HAVO 5 / VWO 6: elektriciteit en schakelingen.

```
stijl.py        huisstijl: kleuren, letters, tempo, Binas-symbolen, stroom, formules
scenes/         één bestand per (deel van een) video; elke scène doet `from stijl import *`
videos/         renders (niet in git)
```

## Werken

Draai alles vanuit de repo-root met `python -m manimgx`, anders vindt een scène `stijl.py` niet.

- Live preview: VS Code-taak **ManimGX: preview** (Ctrl+Shift+B) op het geopende scènebestand.
- Eindrender: taak **ManimGX: render**, of
  `python -m manimgx render scenes/stijl_demo.py WetVanOhm -o videos/WetVanOhm.mp4`

De stijlregels staan bovenaan [stijl.py](stijl.py); [scenes/stijl_demo.py](scenes/stijl_demo.py) laat ze zien.
