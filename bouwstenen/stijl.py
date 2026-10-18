"""Huisstijl: alle looks van de reeks op één plek. Pas hier iets aan, en elke video verandert mee.

Regels van de stijl
-------------------
- Kleur = betekenis. Een grootheid heeft overal dezelfde kleur: in de schakeling,
  in de formule, in de grafiek (U geel, I blauw, R oranje, P groen, E rood, Q blauw).
  Al het andere is wit/grijs op zwart. ACCENT (rood) alleen voor "let op" en kaders.
- Symbolen volgens Binas (Europees): weerstand = rechthoek, lamp = cirkel met kruis (zie symbolen.py).
- Tempo: SNEL / NORMAAL / TRAAG voor run_time, PAUZE na elke nieuwe stap.
- Getallen met decimale komma: waarde("U", 6, "V") geeft U = 6,0 V; komma() in zelf geschreven formules.
- Stroom (witte pijltjes) loopt van + naar −; elektronen (gele bolletjes) andersom; water (blauw) zoals de stroom.
  Q_KLEUR is de kleur van de letter Q in formules, niet van de elektronen.
"""
import re

import numpy as np
import manimgx as m

# ── Kleuren ────────────────────────────────────────────────────────────────
# Huispalet: alleen deze zeven kleuren (plus grijs als mengsel van wit en zwart).
WIT, ZWART = "#FFFFFF", "#000000"
ROOD, ORANJE, GEEL, GROEN, BLAUW = "#FF0020", "#FF601C", "#FFB31F", "#15CD36", "#008EFE"

BG = ZWART
TEKST = WIT
DRAAD = WIT
GEDEMPT = "#808080"  # bijzaken, uitgegrijsde onderdelen
ACCENT = ROOD

U_KLEUR = GEEL     # spanning
I_KLEUR = BLAUW    # stroom
R_KLEUR = ORANJE   # weerstand
P_KLEUR = GROEN    # vermogen
E_KLEUR = ROOD     # energie (deelt rood met ACCENT: vijf kleuren voor zes grootheden)
Q_KLEUR = BLAUW    # lading / elektronen: zelfde familie als stroom
LICHT = GEEL       # brandende lamp

# Hoofdletters die formule() automatisch kleurt.
# shortcut: kleurt ook letters in \text{...}; gebruik dan m.MathTex direct.
GROOTHEDEN = {"U": U_KLEUR, "I": I_KLEUR, "R": R_KLEUR, "P": P_KLEUR, "E": E_KLEUR, "Q": Q_KLEUR}

# ── Letters en maten ───────────────────────────────────────────────────────
FONT = ""  # Manims standaardletter (New Computer Modern), op elke machine gelijk
TITEL, KOP, LABEL, KLEIN, FORMULE = 48, 36, 28, 22, 44
STREEP = 4      # symbolen
LENGTE = 1.2    # lengte van elk symbool, aansluitdraadjes meegerekend

DRAAD_DIKTE = 3 # alle draden: schema's, 3D-kringen, meetdraadjes
MAATLAT_DIKTE = 4

# ── Stroom, elektronen, water ──────────────────────────────────────────────
PIJL_KLEUR = WIT
PIJL_VOOR, PIJL_ACHTER, PIJL_BREED = 0.08, 0.05, 0.06  # stroompijltje: punt vóór het midden, achterkant, halve breedte
ELEKTRON_KLEUR = GEEL   # elektronen: kleine gele bolletjes
WATER_KLEUR = BLAUW     # water: blauwe bolletjes (stroomt andersom dan de elektronen, net als de stroom)
DEELTJE_STRAAL = 0.03

# ── Brandende lamp ─────────────────────────────────────────────────────────
GLOED_STRAAL, GLOED_RINGEN, GLOED_DEKKING = (0.35, 1.0), 8, 0.08    # 2D: zachte ringen om het lampsymbool
HALO_STRAAL, HALO_LAGEN, HALO_DEKKING = (0.35, 1.0), 10, 0.09       # 3D: bollen om de peer
LAMPLICHT = 5                                                       # 3D: sterkte van het licht uit de peer

# ── Panelen (vast in beeld) ────────────────────────────────────────────────
PANEEL_DEKKING = 0.9

# ── 3D-materiaal: de witte, doorschijnende, belichte stof van lamp, batterij, pomp en waterrad ──
MAT_DOORZICHT = 0.35
MAT_RUW = 0.5
RAND_DIKTE = 2  # randlijnen van 3D-modellen

# ── Tempo ──────────────────────────────────────────────────────────────────
SNEL, NORMAAL, TRAAG, PAUZE = 0.5, 1.0, 2.0, 1.0

# ── Indeling (beeld is 14,2 × 8) ───────────────────────────────────────────
SCHAKELING = 3 * m.LEFT + 0.3 * m.DOWN
FORMULES = 3.6 * m.RIGHT + 0.3 * m.DOWN

m.config.background_color = BG


def mat(mob, opacity=MAT_DOORZICHT, kleur=WIT, ruw=MAT_RUW, metaal=0.0):
    """Kleur + materiaal: het object wordt belicht door de lampen in de scène."""
    return mob.set_fill(kleur, opacity).set_stroke(width=0).set_material(m.Material(metallic=metaal, roughness=ruw))


def pijlhoeken(plek, richting):
    """De drie hoeken van een stroompijltje op plek, wijzend in richting (eenheidsvector in het xy-vlak)."""
    q = np.array([-richting[1], richting[0], 0])
    return [plek + PIJL_VOOR * richting, plek - PIJL_ACHTER * richting + PIJL_BREED * q,
            plek - PIJL_ACHTER * richting - PIJL_BREED * q]


def lampgloed(midden, sterkte=1.0):
    """Zachte gele ringen om een brandend lampsymbool (2D); teken hem net onder het symbool."""
    return m.VGroup(*(m.Circle(radius=r, stroke_width=0).set_fill(LICHT, GLOED_DEKKING * (1 - i / GLOED_RINGEN) * sterkte)
                      for i, r in enumerate(np.linspace(*GLOED_STRAAL, GLOED_RINGEN)))).move_to(midden)


# ── Tekst ──────────────────────────────────────────────────────────────────
def tekst(s, size=LABEL, kleur=TEKST, **kw):
    return m.Text(s, font=FONT, font_size=size, color=kleur, **kw)


def titel(s):
    t = tekst(s, TITEL, weight="BOLD").to_corner(m.UL, buff=0.5)
    streep = m.Line(t.get_corner(m.DL), t.get_corner(m.DL) + 1.2 * m.RIGHT,
                    color=ACCENT, stroke_width=6).shift(0.15 * m.DOWN)
    return m.VGroup(t, streep)


def label(s, doel, richting=m.UP, size=KLEIN, kleur=GEDEMPT):
    return tekst(s, size, kleur).next_to(doel, richting, buff=0.15)


def kader(mob, kleur=ACCENT):
    return m.SurroundingRectangle(mob, color=kleur, buff=0.2, corner_radius=0.12, stroke_width=3)


# ── Formules ───────────────────────────────────────────────────────────────
def formule(tex, size=FORMULE, **kw):
    """MathTex waarin U, I, R, P, E, Q automatisch hun eigen kleur krijgen."""
    kleuren = {k: v for k, v in GROOTHEDEN.items() if k in tex}
    return m.MathTex(tex, tex_to_color_map=kleuren, font_size=size, color=TEKST, **kw)


def komma(s):
    r"""Nederlandse decimale komma zonder spatie erachter; alleen tussen twee cijfers (dus niet in \, of a, b)."""
    return re.sub(r"(?<=\d),(?=\d)", lambda _: r"\mathord{,}", s)


def waarde(symbool, getal, eenheid, decimalen=1, size=FORMULE):
    """waarde("I", 0.25, "A", 2) -> I = 0,25 A (Nederlandse komma)."""
    g = f"{getal:.{decimalen}f}".replace(".", r"\mathord{,}")  # zonder spatie na de komma
    return formule(rf"{symbool} = {g}\ \mathrm{{{eenheid}}}", size)
