"""Gedeelde bouwstenen voor alle video's. Een scène doet: `from bouwstenen import *`.

stijl.py       alle looks: kleuren, letters, maten, materiaal, tempo   ← hier pas je het uiterlijk aan
symbolen.py    2D-schemasymbolen (Binas) en het tekenen van schakelingen
kring.py       de tafelkring van video 2–5: rondgang, schema, maskeren, hoogte-kring
schakeling.py  schakelingen met meerdere onderdelen en vertakkingen (video 6–9)
modellen.py    3D-modellen: batterij, tafellamp, pomp, waterrad, belichting
verhaal.py     ondertitels (zeg), panelen, kaarten en Les, de basis voor elke video
"""
from .stijl import *
from .symbolen import *
from .kring import *
from .schakeling import *
from .modellen import *
from .verhaal import *
