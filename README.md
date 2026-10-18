# Elektriciteit

ManimGX-code voor YouTube-video's natuurkunde HAVO 5 / VWO 6: elektriciteit en schakelingen.

```
bouwstenen/          gedeelde code; elke scène doet `from bouwstenen import *`
  stijl.py           ALLE LOOKS: kleuren, letters, lijndiktes, 3D-materiaal, tempo   ← hier pas je het uiterlijk aan
  symbolen.py        2D-schemasymbolen (Binas) en het tekenen van schakelingen
  kring.py           de tafelkring van video 2–5: rondgang, schema, maskeren, hoogte-kring
  schakeling.py      schakelingen met meerdere onderdelen en vertakkingen (video 6–9)
  modellen.py        3D-modellen: batterij, tafellamp, pomp, waterrad, belichting
  verhaal.py         ondertitels (zeg), panelen, kaarten, en Les: de basis voor elke video
scenes/              de video's van de reeks, in volgorde; ze importeren elkaar niet
  00_intro.py … 09_thuis.py
  extra/             alles wat niet in de film zit (transformator, demo's, voorlopers)
film.py              maakt de hele film
videos/              renders (niet in git)
```

Vuistregel: wat meer dan één video gebruikt, staat in `bouwstenen/`; wat maar in één video voorkomt
(bijvoorbeeld de zon en thermometer van de sensoren), staat in die video zelf.

## Werken

Draai alles vanuit de repo-root, anders vindt een scène `bouwstenen/` niet.

- **Live preview:** VS Code-taak **ManimGX: preview** (Ctrl+Shift+B) op het geopende scènebestand.
- **Eén video renderen:** taak **ManimGX: render**, of
  `python -m manimgx render scenes/03_stroom.py -o videos/Stroom.mp4`
- **De hele film:** taak **Film maken**, of `python film.py`. Rendert alleen de delen die veranderd zijn
  (een wijziging in `bouwstenen/` telt voor alle delen), plakt ze aan elkaar en voegt de ondertitels samen tot
  `videos/Elektriciteit.mp4` en `videos/Elektriciteit.srt`. Alles opnieuw: `python film.py --opnieuw`.

## Een nieuwe video

Maak `scenes/10_naam.py` met een klasse die van `Les` erft, en zet hem in `DELEN` in `film.py`:

```python
from bouwstenen import *


class Naam(Les):
    def construct(self):
        self.add(*zon_en_schemer())
        d = zeg(self, "Eerste zin.")          # ondertitel; d = spreektijd
        self.doe(d, iets.animate.shift(m.UP)) # korte animatie, dan stilstaan tot de zin klaar is
```
