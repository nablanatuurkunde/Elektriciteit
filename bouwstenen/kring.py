"""De tafelkring van video 1 t/m 4: liggende batterij links, lamp rechts, draden plat op tafel als rechthoek.

Bevat de maten van die kring, de rondgang (PAD/LUS) waarover elektronen, water en stroompijltjes bewegen
(overal even snel, want naar afgelegde afstand), het schakelschema dat er van boven op ligt, het maskeren van
pijltjes onder symbolen, en de hoogte-kring (hoogte = spanning) uit de spanningsvideo.
"""
import numpy as np
import manimgx as m

from .stijl import *
from .symbolen import *

# ── Maten van de tafelkring (1 eenheid = 10 cm) ───────────────────────────
LINKS, RECHTS, HALF = -2.5, 1.5, 2.0  # kring: x van batterij- tot lampzijde, y van -HALF tot HALF
Z = 0.0725                            # hoogte van de draden: de as van de liggende batterij (Ø14,5 mm)
BAT_HALF = 0.2525                     # halve lengte AA (50,5 mm)
VOET = 0.75                           # straal van de lampvoet: daar komen de draden binnen


def lijn(*punten_xy):
    """Draad plat op tafel door de punten (x, y)."""
    return draad(*([x, y, Z] for x, y in punten_xy))


def schema_symbolen():
    """Bron links (+ naar boven, zoals de liggende batterij) en lamp rechts, plat in het xy-vlak op tafelhoogte."""
    bron_s = plaats(bron(), [LINKS, LENGTE / 2, Z], [LINKS, -LENGTE / 2, Z])  # pool a (+) boven
    lamp_s = plaats(lamp(), [RECHTS, -LENGTE / 2, Z], [RECHTS, LENGTE / 2, Z])
    return bron_s, lamp_s


def schemagloed(lamp_s):
    """Zachte platte halo net onder het lampsymbool."""
    return lampgloed(lamp_s[2].get_center() - 0.01 * m.OUT)


# ── De rondgang ────────────────────────────────────────────────────────────
# Elektronen verlaten de − pool (voorkant, -y), gaan door de lamp en komen bij de + pool (achterkant) terug.
PAD = [(LINKS, -BAT_HALF), (LINKS, -HALF), (RECHTS, -HALF), (RECHTS, -VOET),
       (RECHTS, VOET), (RECHTS, HALF), (LINKS, HALF), (LINKS, BAT_HALF)]


class Rondgang:
    """De gesloten kring als lus (ook door batterij/pomp heen), geparametriseerd naar afgelegde afstand:
    alles wat hierover beweegt, gaat overal even snel (point_from_proportion doet dat per segment, niet per lengte)."""

    def __init__(self):
        self.p = np.array([[x, y, Z] for x, y in PAD + PAD[:1]], float)
        self.seg = np.linalg.norm(np.diff(self.p, axis=0), axis=1)
        self.cum = np.concatenate([[0], np.cumsum(self.seg)])
        self.lengte = self.cum[-1]

    def punt(self, s):
        s %= self.lengte
        i = min(np.searchsorted(self.cum, s, side="right") - 1, len(self.seg) - 1)
        return self.p[i] + (s - self.cum[i]) / self.seg[i] * (self.p[i + 1] - self.p[i])

    def stuk(self, s, l, k=10):
        """Punten van afstand s tot s + l, ook om hoeken heen."""
        return [self.punt(s + l * j / k) for j in range(k + 1)]


LUS = Rondgang()
assert np.isclose(np.linalg.norm(LUS.punt(0.1) - LUS.punt(0.0)), 0.1)  # gelijke stap = gelijke afstand


def stromer(groep, tempo, zet, richting=1):
    """Laat groep met snelheid tempo (eenheden/s) rond de lus schuiven; zet(lid, s) plaatst een lid op afstand s.
    richting 1 = zoals PAD (elektronen: − → lamp → +), -1 = andersom (stroom en water: + → lamp → −)."""
    groep.s = 0.0
    n = len(groep)

    def schuif(g, dt):
        g.s += richting * dt * tempo.get_value()
        for i, lid in enumerate(g):
            zet(lid, g.s + i * LUS.lengte / n)
    groep.add_updater(schuif)
    schuif(groep, 0)
    return groep


def deeltjes(kleur, tempo, richting, afstand=0.3):
    """Kleine bolletjes (onzichtbaar bij de start), gelijkmatig over de hele kring, met snelheid tempo (ValueTracker)."""
    g = m.Group(*(m.Sphere(radius=DEELTJE_STRAAL, resolution=(8, 4)).set_fill(kleur, 0).set_stroke(width=0)
                  for _ in range(int(LUS.lengte / afstand))))
    return stromer(g, tempo, lambda bol, s: bol.move_to(LUS.punt(s)), richting)


def elektronen_in_kring(tempo, afstand=0.3):
    """Gele elektronen: van de − pool door de lamp naar de + pool."""
    return deeltjes(ELEKTRON_KLEUR, tempo, 1, afstand)


def waterdeeltjes(tempo, afstand=0.3):
    """Blauw water: stroomt andersom dan de elektronen, net als de (conventionele) stroom: + → lamp → −."""
    return deeltjes(WATER_KLEUR, tempo, -1, afstand)


# ── Maskeren: pijltjes vervagen onder een symbool ─────────────────────────
METER_X = -0.5  # plek van de stroommeter (en het telvlak) op de voorste draad

_s_raster = np.linspace(0, LUS.lengte, 16001)
_p_raster = np.array([LUS.punt(s) for s in _s_raster])


def s_op(x, y):
    """Afstand langs de lus van het punt (x, y) op de kring."""
    return _s_raster[np.argmin(np.linalg.norm(_p_raster[:, :2] - [x, y], axis=1))]


def interval(p, q):
    a, b = s_op(*p), s_op(*q)
    return min(a, b), max(a, b)


MASKER_BRON = interval((LINKS, 0.13), (LINKS, -0.13))   # tussen de platen van de bron
MASKER_LAMP = interval((RECHTS, -0.3), (RECHTS, 0.3))   # binnen de cirkel van de lamp
MASKER_METER = interval((METER_X - 0.32, -HALF), (METER_X + 0.32, -HALF))


def maskeer(groep, maskers, zicht, rand=0.05):
    """Zichtbaarheid per lid: zicht (ValueTracker) maal 0 onder een symbool, met een zachte rand van `rand`.
    maskers is een lijst van (s_begin, s_eind); later toevoegen kan (de stroommeter)."""
    n = len(groep)

    def bijwerken(g):
        for i, lid in enumerate(g):
            s = (g.s + i * LUS.lengte / n) % LUS.lengte
            f = 1.0
            for a, b in maskers:
                d = 0.0 if a <= s <= b else min(abs(s - a), abs(s - b))
                f = min(f, np.clip(d / rand, 0, 1))
            lid.set_fill(opacity=zicht.get_value() * f)
    groep.add_updater(bijwerken)
    bijwerken(groep)
    return groep


def lus_pijltjes(tempo, naar_3d=lambda q: q, afstand=0.6):
    """Stroompijltjes die van + door de lamp naar − trekken (andersom dan de elektronen).
    naar_3d(punt) zet een punt van het platte schema op zijn plek in 3D: in de hoogte-kring kantelen ze mee."""
    pijlen = m.VGroup(*(m.VMobject().set_fill(PIJL_KLEUR, 0).set_stroke(width=0)
                        for _ in range(int(LUS.lengte / afstand))))

    def zet(p, s):
        a, b = LUS.punt(s), LUS.punt(s - 1e-3)  # richting -1: op weg naar kleinere s
        hoeken = pijlhoeken(a, (b - a) / np.linalg.norm(b - a))
        p.set_points_as_corners([naar_3d(q) for q in hoeken + hoeken[:1]])
    return stromer(pijlen, tempo, zet, richting=-1)


def schema(met_meter=False):
    """Het schakelschema: bron, brandende lamp met gloed, draden en labels; eventueel met stroommeter in de voorste draad."""
    bron_s, lamp_s = schema_symbolen()
    lamp_s[2].set_fill(LICHT, 1)
    L, R, H = LINKS, RECHTS, HALF
    plus_s = draad(pool_b(lamp_s), [R, H, Z], [L, H, Z], pool_a(bron_s))  # zelfde looprichting als de 3D-draden
    labels = [label("spanningsbron", bron_s, m.LEFT, size=LABEL, kleur=TEKST),
              label("lamp", lamp_s, m.RIGHT, size=LABEL, kleur=TEKST)]
    if met_meter:
        meter_s = plaats(meter("A"), [METER_X - LENGTE / 2, -H, Z], [METER_X + LENGTE / 2, -H, Z])
        min_s = m.VGroup(draad(pool_b(bron_s), [L, -H, Z], pool_a(meter_s)),
                         draad(pool_b(meter_s), [R, -H, Z], pool_a(lamp_s)))
        labels.append(label("stroommeter", meter_s, m.DOWN, size=LABEL, kleur=TEKST))
        symbolen = m.VGroup(bron_s, lamp_s, meter_s)
    else:
        min_s = draad(pool_b(bron_s), [L, -H, Z], [R, -H, Z], pool_a(lamp_s))
        symbolen = m.VGroup(bron_s, lamp_s)
    return dict(symbolen=symbolen, gloed=schemagloed(lamp_s), labels=m.VGroup(*labels), min_=min_s, plus=plus_s)


# ── De hoogte-kring: hoogte = spanning ─────────────────────────────────────
H = 1.0                         # hoogte die de batterij geeft (1,5 V)
BRON_HALF = 0.1                 # de batterij stijgt tussen de platen (y = −0,1 … 0,1)
LINKS_ZONE, RECHTS_ZONE = LINKS + 0.6, RECHTS - 0.6
# De lamp (symbool van LENGTE lang, y = −0,6 … 0,6) kantelt als stijf geheel: hoek α met sin α = H / LENGTE,
# zodat zijn polen precies op hoogte H en 0 uitkomen. Zo blijft de cirkel rond in plaats van uitgerekt.
SIN_A = H / LENGTE
COS_A = np.sqrt(1 - SIN_A ** 2)
OVERGANG = 0.4  # draadstuk buiten de lamp waarover de kanteling geleidelijk overgaat (draden en pijltjes sluiten aan)


def hoogte_vorm(p):
    """Waar een punt van het platte schema in de 3D-kring komt: de hoogte = hoe 'hoog' de stroom daar zit."""
    x, y, z = p
    if x < LINKS_ZONE:   # linkerzijde met de batterij: stijgt tussen de platen, − onder, + boven
        return np.array([x, y, z + H * np.clip((y + BRON_HALF) / (2 * BRON_HALF), 0, 1)])
    if x > RECHTS_ZONE:  # rechterzijde met de lamp: gekantelde helling naar beneden
        half = LENGTE / 2
        if abs(y) <= half:
            return np.array([x, y * COS_A, z + H / 2 + y * SIN_A])
        krimp = half * (1 - COS_A) * np.clip(1 - (abs(y) - half) / OVERGANG, 0, 1)
        return np.array([x, y - np.sign(y) * krimp, z + (H if y > 0 else 0)])
    return np.array([x, y, z + (H if y > 0 else 0)])  # achterste draad boven, voorste (met stroommeter) onder


def til(p, t):
    """Punt p van plat (t = 0) naar zijn plek in de hoogte-kring (t = 1)."""
    p = np.asarray(p, float)
    return p + t * (hoogte_vorm(p) - p)


def hoogte_maatlat(x, y, tekst_, kleur=U_KLEUR, links=False):
    """Verticale lat van hoogte 0 tot H met streepjes en een staand label: het hoogteverschil U."""
    lat = m.VGroup(m.Line([x, y, Z], [x, y, Z + H]),
                   *(m.Line([x - 0.1, y, z], [x + 0.1, y, z]) for z in (Z, Z + H))).set_stroke(kleur, MAATLAT_DIKTE)
    lbl = tekst(tekst_, LABEL, kleur).rotate(m.PI / 2, m.RIGHT)  # rechtop, naar de camera (−y)
    lbl.move_to([x + (-0.35 if links else 0.35), y, Z + H / 2])
    return m.VGroup(lat, lbl)


def staand(mob):
    """Van het xy-vlak naar het xz-vlak, rechtop naar de camera gericht."""
    return mob.rotate(m.PI / 2, m.RIGHT, about_point=m.ORIGIN)
