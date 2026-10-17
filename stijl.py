"""Huisstijl voor de elektriciteitsvideo's (ManimGX). Elke scène: `from stijl import *`.

Regels van de stijl
-------------------
- Kleur = betekenis. Een grootheid heeft overal dezelfde kleur: in de schakeling,
  in de formule, in de grafiek (U geel, I blauw, R oranje, P groen, E rood, Q blauw).
  Al het andere is wit/grijs op zwart. ACCENT (rood) alleen voor "let op" en kaders.
- Symbolen volgens Binas (Europees): weerstand = rechthoek, lamp = cirkel met kruis.
- Indeling: titel linksboven, schakeling links (SCHAKELING), formules rechts (FORMULES).
- Tempo: SNEL / NORMAAL / TRAAG voor run_time, PAUZE na elke nieuwe stap.
- Getallen met decimale komma: waarde("U", 6, "V") geeft U = 6,0 V.
- Stroom (I_KLEUR, pijlen) loopt van + naar −; elektronen (Q_KLEUR, bolletjes) andersom.
- Gesproken tekst: d = zeg(self, "zin"), daarna animaties die samen d seconden duren.
"""
import textwrap

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
STREEP = 4      # draden en symbolen
LENGTE = 1.2    # lengte van elk symbool, aansluitdraadjes meegerekend

# ── Tempo ──────────────────────────────────────────────────────────────────
SNEL, NORMAAL, TRAAG, PAUZE = 0.5, 1.0, 2.0, 1.0

# ── Indeling (beeld is 14,2 × 8) ───────────────────────────────────────────
SCHAKELING = 3 * m.LEFT + 0.3 * m.DOWN
FORMULES = 3.6 * m.RIGHT + 0.3 * m.DOWN

m.config.background_color = BG


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


# ── Ondertitels ────────────────────────────────────────────────────────────
ONDERTITEL_IN_BEELD = True  # False: alleen de .srt naast de video (voor YouTube-ondertitels)
WOORDEN_PER_SEC = 2.6       # spreektempo; stem af op je eigen voice-over


def zeg(scene, s, duur=None):
    """Toon s als ondertitel (in beeld en in de .srt) en geef de spreektijd terug.
    Vul die tijd daarna met animaties of wait(). zeg(scene, "") haalt de ondertitel weg."""
    if getattr(scene, "_ondertitel", None) is not None:
        scene.remove(scene._ondertitel)
        scene._ondertitel = None
    if not s:
        return 0
    duur = duur or max(1.2, len(s.split()) / WOORDEN_PER_SEC)
    scene.add_subcaption(s, duration=duur)
    if ONDERTITEL_IN_BEELD:
        t = tekst("\n".join(textwrap.wrap(s, 64)), KLEIN + 4).to_edge(m.DOWN, buff=0.3)
        achter = m.BackgroundRectangle(t, color=BG, fill_opacity=0.8, buff=0.12)
        scene._ondertitel = m.VGroup(achter, t).set_z_index(10)
        if isinstance(scene, m.ThreeDScene):
            scene.add_fixed_in_frame_mobjects(scene._ondertitel)
        else:
            scene.add(scene._ondertitel)
    return duur


# ── Formules ───────────────────────────────────────────────────────────────
def formule(tex, size=FORMULE, **kw):
    """MathTex waarin U, I, R, P, E, Q automatisch hun eigen kleur krijgen."""
    kleuren = {k: v for k, v in GROOTHEDEN.items() if k in tex}
    return m.MathTex(tex, tex_to_color_map=kleuren, font_size=size, color=TEKST, **kw)


def waarde(symbool, getal, eenheid, decimalen=1, size=FORMULE):
    """waarde("I", 0.25, "A", 2) -> I = 0,25 A (Nederlandse komma)."""
    g = f"{getal:.{decimalen}f}".replace(".", r"\mathord{,}")  # zonder spatie na de komma
    return formule(rf"{symbool} = {g}\ \mathrm{{{eenheid}}}", size)


def kader(mob, kleur=ACCENT):
    return m.SurroundingRectangle(mob, color=kleur, buff=0.2, corner_radius=0.12, stroke_width=3)


# ── Symbolen (Binas) ───────────────────────────────────────────────────────
# Elk symbool ligt horizontaal, LENGTE breed, gecentreerd op de oorsprong.
# Submobject 0 en 1 zijn de aansluitdraadjes: pool_a()/pool_b() blijven kloppen na draaien.
def _symbool(half, *lichaam):
    a = m.Line(LENGTE / 2 * m.LEFT, half * m.LEFT)
    b = m.Line(half * m.RIGHT, LENGTE / 2 * m.RIGHT)
    return m.VGroup(a, b, *lichaam).set_stroke(TEKST, STREEP)


def pool_a(sym):
    return sym[0].get_start()


def pool_b(sym):
    return sym[1].get_end()


def bron(plus=True):
    """Spanningsbron: lange dunne plaat = +, korte dikke plaat = −. Pool a is +."""
    s = _symbool(0.1, m.Line(0.1 * m.LEFT + 0.35 * m.UP, 0.1 * m.LEFT + 0.35 * m.DOWN),
                 m.Line(0.1 * m.RIGHT + 0.18 * m.UP, 0.1 * m.RIGHT + 0.18 * m.DOWN))
    s[3].set_stroke(width=2.5 * STREEP)
    if plus:
        s.add(tekst("+", LABEL).move_to(0.3 * m.LEFT + 0.35 * m.UP))
    return s


def weerstand():
    return _symbool(0.35, m.Rectangle(width=0.7, height=0.28, fill_color=BG, fill_opacity=1))


def weerstand_zigzag(tanden=6):
    """Weerstand als zigzag (Amerikaanse notatie; Binas en het examen gebruiken de rechthoek: weerstand())."""
    xs = np.linspace(-0.35, 0.35, 2 * tanden + 1)
    punten = [[x, 0 if i in (0, 2 * tanden) else 0.14 * (-1) ** i, 0] for i, x in enumerate(xs)]
    return _symbool(0.35, m.VMobject().set_points_as_corners(punten))


def variabele_weerstand():
    s = weerstand()
    s.add(m.Arrow(0.45 * m.DL, 0.45 * m.UR, buff=0, stroke_width=STREEP, color=TEKST,
                  max_tip_length_to_length_ratio=0.25))
    return s


def ntc():
    s = weerstand()
    s.add(m.VMobject().set_points_as_corners([0.5 * m.LEFT + 0.3 * m.DOWN, 0.3 * m.LEFT + 0.3 * m.DOWN,
                                              0.3 * m.RIGHT + 0.3 * m.UP]).set_stroke(TEKST, STREEP / 2),
          tekst("−t°", KLEIN).move_to(0.45 * m.RIGHT + 0.4 * m.DOWN))
    return s


def ptc():
    """PTC: als de NTC, maar met +t° (warmer = grotere weerstand)."""
    s = weerstand()
    s.add(m.VMobject().set_points_as_corners([0.5 * m.LEFT + 0.3 * m.DOWN, 0.3 * m.LEFT + 0.3 * m.DOWN,
                                              0.3 * m.RIGHT + 0.3 * m.UP]).set_stroke(TEKST, STREEP / 2),
          tekst("+t°", KLEIN).move_to(0.45 * m.RIGHT + 0.4 * m.DOWN))
    return s


def ldr():
    s = weerstand()
    for dx in (-0.12, 0.12):  # licht valt erop: pijlen naar het symbool toe
        s.add(m.Arrow(dx * m.RIGHT + 0.75 * m.UP + 0.25 * m.LEFT, dx * m.RIGHT + 0.2 * m.UP,
                      buff=0, stroke_width=STREEP / 2, color=TEKST, max_tip_length_to_length_ratio=0.3))
    return s


def lamp():
    c = m.Circle(radius=0.28, fill_color=BG, fill_opacity=1)
    k = 0.28 / np.sqrt(2)
    return _symbool(0.28, c, m.Line(k * m.UL, k * m.DR), m.Line(k * m.UR, k * m.DL))


def diode():
    """Doorlaatrichting van a naar b."""
    driehoek = m.Polygon(0.18 * m.LEFT + 0.22 * m.UP, 0.18 * m.LEFT + 0.22 * m.DOWN, 0.18 * m.RIGHT)
    return _symbool(0.18, driehoek, m.Line(0.18 * m.RIGHT + 0.22 * m.UP, 0.18 * m.RIGHT + 0.22 * m.DOWN))


def led():
    s = diode()
    for dx in (-0.05, 0.15):  # licht gaat eruit: pijlen van het symbool af
        s.add(m.Arrow(dx * m.RIGHT + 0.25 * m.UP, dx * m.RIGHT + 0.25 * m.RIGHT + 0.7 * m.UP,
                      buff=0, stroke_width=STREEP / 2, color=TEKST, max_tip_length_to_length_ratio=0.3))
    return s


def schakelaar(open=True):
    hoek = 30 * m.DEGREES if open else 0
    arm = m.Line(0.3 * m.LEFT, 0.3 * m.RIGHT).rotate(hoek, about_point=0.3 * m.LEFT)
    return _symbool(0.3, arm, m.Dot(0.3 * m.LEFT, radius=0.05), m.Dot(0.3 * m.RIGHT, radius=0.05))


def wisselbron():
    """Wisselspanningsbron (bijvoorbeeld het stopcontact): cirkel met een golfje."""
    xs = np.linspace(-0.17, 0.17, 25)
    golf = m.VMobject().set_points_smoothly([[x, 0.09 * np.sin(2 * np.pi * x / 0.34), 0] for x in xs])
    return _symbool(0.3, m.Circle(radius=0.3, fill_color=BG, fill_opacity=1), golf)


def meter(letter):
    """meter("A") of meter("V"). Letter blijft rechtop als je het symbool draait: zie plaats()."""
    return _symbool(0.3, m.Circle(radius=0.3, fill_color=BG, fill_opacity=1), tekst(letter, LABEL))


# ── Schakelingen bouwen ────────────────────────────────────────────────────
def plaats(sym, p, q):
    """Leg een symbool midden tussen punten p en q, in de richting p → q."""
    p, q = np.array(p, float), np.array(q, float)
    sym.rotate(m.angle_of_vector(q - p))
    sym.shift((p + q) / 2 - (pool_a(sym) + pool_b(sym)) / 2)  # op de polen centreren, niet op de omhullende
    for sub in sym:  # letters (A, V, +, −t°) rechtop houden
        if isinstance(sub, m.Text):
            sub.rotate(-m.angle_of_vector(q - p))
    return sym


def draad(*punten):
    return m.VMobject().set_points_as_corners([np.array(p, float) for p in punten]).set_stroke(DRAAD, STREEP)


def tak(p, q, sym):
    """Draad van p naar q met een symbool in het midden. Geeft VGroup(draad, symbool, draad)."""
    plaats(sym, p, q)
    return m.VGroup(draad(p, pool_a(sym)), sym, draad(pool_b(sym), q))


def knoop(p):
    return m.Dot(p, radius=0.07, color=DRAAD)


# ── Stroom en elektronen ───────────────────────────────────────────────────
def _stroming(punten, maak, snelheid, afstand, terug):
    pad = draad(*punten)
    n = max(2, int(pad.get_arc_length() / afstand))
    groep = m.VGroup(*(maak() for _ in range(n)))
    groep.snelheid = snelheid  # aanpasbaar tijdens de scène: groep.snelheid = 2
    groep.fase = 0.0
    lengte = pad.get_arc_length()

    def stap(g, dt):
        g.fase = (g.fase + dt * g.snelheid / lengte) % 1
        for i, deel in enumerate(g):
            t = (g.fase + i / n) % 1
            t = 1 - t if terug else t
            a = pad.point_from_proportion(t)
            b = pad.point_from_proportion(min(t + 1e-3, 1) if not terug else max(t - 1e-3, 0))
            deel.move_to(a)
            if hasattr(deel, "richting"):
                deel.rotate(m.angle_of_vector(b - a) - deel.richting, about_point=a)
                deel.richting = m.angle_of_vector(b - a)

    groep.add_updater(stap)
    groep.set_z_index(-1)  # achter de symbolen langs
    return groep


def stroom(punten, snelheid=1.0, afstand=0.6):
    """Conventionele stroom langs een gesloten pad (+ → −): blauwe pijltjes. Voeg toe en wacht."""
    def pijl():
        t = m.Triangle(fill_color=I_KLEUR, fill_opacity=1, stroke_width=0).scale(0.11)
        t.rotate(-m.PI / 2)  # wijst nu naar rechts
        t.richting = 0.0
        return t
    return _stroming(punten, pijl, snelheid, afstand, terug=False)


def elektronen(punten, snelheid=1.0, afstand=0.35):
    """Elektronen langs hetzelfde pad, tegen de stroomrichting in."""
    return _stroming(punten, lambda: m.Dot(radius=0.06, color=Q_KLEUR), snelheid, afstand, terug=True)
