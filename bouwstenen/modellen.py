"""3D-modellen: batterij, tafellamp, pomp en waterrad, plus de belichting en de gloeiende peer.

Witte, doorschijnende, belichte vormen (stijl.mat) met alleen randlijnen: ringen waar de vorm een knik heeft,
plus de omtrek zoals de camera die ziet. Op schaal: 1 eenheid = 10 cm.
"""
import numpy as np
import manimgx as m

from .stijl import *
from .kring import LINKS, RECHTS, Z, BAT_HALF

CM = 0.1  # scène-eenheden per centimeter


class Draaivorm:
    """Een omwentelingsvorm rond een verticale as: profiel [(straal, hoogte), ...] in cm."""

    def __init__(self, profiel, plaats=(0, 0, 0), randen=None, opacity=MAT_DOORZICHT):
        self.r, self.z = (np.array(profiel, float) * CM).T
        self.plaats = np.array(plaats, float) * CM
        r, z, s = self.r, self.z, np.linspace(0, 1, len(self.r))
        self.vlak = m.Surface(lambda u, v: self.plaats + [np.interp(v, s, r) * np.cos(u), np.interp(v, s, r) * np.sin(u),
                                                          np.interp(v, s, z)],
                              u_range=(0, m.TAU), v_range=(0, 1), resolution=(48, len(r) * 2))
        mat(self.vlak, opacity)
        knikken = range(len(r)) if randen is None else randen
        self.ringen = m.VGroup(*(m.Circle(radius=r[i]).move_to(self.plaats + [0, 0, z[i]])
                                 for i in knikken if r[i] > 0)).set_stroke(WIT, RAND_DIKTE)

    def omtrek(self, theta):
        """De twee zijlijnen die de camera (op hoek theta rond de z-as) als rand van de vorm ziet."""
        opzij = np.array([-np.sin(theta), np.cos(theta), 0])
        punt = lambda i, kant: self.plaats + kant * self.r[i] * opzij + [0, 0, self.z[i]]
        return m.VGroup(*(m.Line(punt(i, kant), punt(i + 1, kant)) for kant in (-1, 1)
                          for i in range(len(self.r) - 1) if self.z[i] != self.z[i + 1]  # vlakke bodems: dat zijn de ringen al
                          )).set_stroke(WIT, RAND_DIKTE)


def aa_batterij(plaats):
    """AA-cel: Ø14,5 mm × 50,5 mm, met pluspool-nopje van Ø5,5 mm."""
    r, h = 0.725, 5.05
    return [Draaivorm([(0, 0), (r * 0.9, 0), (r, 0.05), (r, h - 0.2), (r * 0.8, h - 0.1), (0.275, h - 0.1),
                       (0.275, h), (0, h)], plaats)]


def peerprofiel():
    """Gloeilamp: hals van Ø2,4 cm die overgaat in een bol van Ø6 cm (middelpunt op 36,5 cm)."""
    z = np.linspace(31, 39.5, 24)
    return [(1.2 + (z - 31) * 0.23 if z < 34.2 else np.sqrt(max(9 - (z - 36.5) ** 2, 0)), z) for z in z]


def tafellamp():
    """Ronde voet, slanke stang, fitting met peer en een kegelvormige stoffen kap."""
    return [Draaivorm([(0, 0), (7.5, 0), (7.5, 1), (5, 2.5), (1.2, 3), (0, 3)]),           # voet
            Draaivorm([(0.6, 3), (0.6, 27)]),                                                # stang
            Draaivorm([(0, 27), (1.8, 27), (1.8, 31), (0, 31)]),                             # fitting
            Draaivorm(peerprofiel(), randen=[0]),                                           # peer: glad
            Draaivorm([(15, 24), (9, 45)], opacity=0.2)]                                     # kap: open kegel


class LiggendeBatterij:
    """De AA-cel, op zijn kant op tafel: as langs +y, pluspool naar +y."""

    def __init__(self, min_pool):
        self.d = aa_batterij((0, 0, 0))[0]
        self.plaats = np.array(min_pool, float)
        for mob in (self.d.vlak, self.d.ringen):
            mob.rotate(-m.PI / 2, m.RIGHT, about_point=m.ORIGIN).shift(self.plaats)  # z-as → y-as

    def omtrek(self, phi, theta):
        """Zijlijnen van een liggende omwentelingsvorm, zoals de camera ze ziet."""
        kijk = np.array([np.sin(phi) * np.cos(theta), np.sin(phi) * np.sin(theta), np.cos(phi)])
        opzij = np.cross(m.UP, kijk)
        opzij /= np.linalg.norm(opzij)
        r, z = self.d.r, self.d.z
        punt = lambda i, kant: self.plaats + [0, z[i], 0] + kant * r[i] * opzij
        return m.VGroup(*(m.Line(punt(i, kant), punt(i + 1, kant)) for kant in (-1, 1)
                          for i in range(len(r) - 1) if z[i] != z[i + 1])).set_stroke(WIT, RAND_DIKTE)


def tafellamp_op(x):
    """De tafellamp, met zijn voet op (x, 0) op de vloer; geeft (lampdelen, beugel)."""
    lamp3d = tafellamp()
    for d in lamp3d:
        d.plaats = d.plaats + [x, 0, 0]  # omtrek() rekent vanuit plaats
        d.vlak.shift(x * m.RIGHT)
        d.ringen.shift(x * m.RIGHT)
    beugel = m.VGroup(*(m.Line([x, 0, 3.3], [x + 0.9 * np.cos(a), 0.9 * np.sin(a), 4.5])
                        for a in np.arange(0, m.TAU, m.TAU / 3))).set_stroke(WIT, RAND_DIKTE)
    lamp3d[3].vlak.set_material(None)  # peer altijd onbelicht (eigen kleur), ook vóór hij gloeit: geen sprong
    return lamp3d, beugel


def opstelling():
    """Tafellamp rechts en liggende batterij links (de tafelkring); geeft (lampdelen, beugel, batterij)."""
    return (*tafellamp_op(RECHTS), LiggendeBatterij([LINKS, -BAT_HALF, Z]))


def gloeiende_peer(lamp3d, g, x=RECHTS):
    """Licht en halo rond de peer van een tafellamp op x, aangestuurd door ValueTracker g (0 = uit, 1 = aan).
    Geeft (licht, halo)."""
    peer, midden = lamp3d[3].vlak, np.array([x, 0, 3.65])
    licht = m.PointLight(midden, LICHT, intensity=0, radius=6)
    halo = m.Group(*(m.Sphere(midden, radius=r, resolution=(24, 12)).set_fill(LICHT, 0).set_stroke(width=0)
                     for r in np.linspace(*HALO_STRAAL, HALO_LAGEN)))

    def gloei(h):
        v = g.get_value()
        peer.set_fill(m.interpolate_color(m.ManimColor(WIT), m.ManimColor(LICHT), v), 0.35 + 0.65 * v)
        for i, bol in enumerate(h):
            bol.set_fill(opacity=v * HALO_DEKKING * (1 - i / len(h)))
        licht.intensity = LAMPLICHT * v
    halo.add_updater(gloei)
    return licht, halo


def zon_en_schemer():
    # Zon zonder schaduw: anders werpt de (onzichtbare) halo rond de peer ineens schaduw op de kap
    return m.AmbientLight(intensity=0.25), m.SunLight([-4, -6, 8], intensity=2.5, shadows=False)


def waterrad(tempo):
    """Rad met schoepen, as langs x, op de plek van de lamp; draait mee met het water (tempo)."""
    straal, c = 0.45, np.array([RECHTS, 0, Z + 0.45])
    schoepen = m.Group(*(mat(m.Prism(dimensions=[0.3, 0.03, 0.2])).move_to(c + [0, 0, straal - 0.1])
                         .rotate(k * m.TAU / 8, m.RIGHT, about_point=c) for k in range(8)))
    as_ = mat(m.Cylinder(radius=0.04, height=0.5, direction=m.RIGHT)).move_to(c)
    randen = m.VGroup(*(m.Circle(radius=straal).rotate(m.PI / 2, m.UP).move_to(c + [dx, 0, 0])
                        for dx in (-0.15, 0.15))).set_stroke(WIT, RAND_DIKTE)
    rad = m.Group(schoepen, as_, randen)
    # water langs de rechterkant stroomt naar -y; de onderkant van het rad gaat mee (draaien om +x duwt die naar +y)
    rad.add_updater(lambda r, dt: r.rotate(-2.5 * tempo.get_value() * dt, m.RIGHT, about_point=c))
    return rad


def pomp(tempo):
    """Pomp in lijn met de draad, op de plek van de batterij: doorzichtig huis met een draaiende schroef (helix).

    Het blad ligt op hoek a = k·y rond de as (y). Draaien over φ om +y (rechterhand) geeft a = k·y − φ:
    de schroefdraad schuift met ω/k langs de as. In de pomp stroomt het water van − naar + (het komt er aan de
    + kant uit), dus naar +y; met ω = k·tempo schuift de draad precies even snel mee als het water."""
    c = np.array([LINKS, 0, Z])
    huis = mat(m.Cylinder(radius=0.2, height=0.5, direction=m.UP), opacity=0.2).move_to(c)
    randen = m.VGroup(*(m.Circle(radius=0.2).rotate(m.PI / 2, m.RIGHT).move_to(c + [0, dy, 0])
                        for dy in (-0.25, 0.25))).set_stroke(WIT, RAND_DIKTE)
    lengte, slagen = 0.44, 1.5
    k = m.TAU * slagen / lengte
    blad = m.Surface(lambda r, y: c + [r * np.cos(k * y), y, r * np.sin(k * y)],
                     u_range=(0.03, 0.17), v_range=(-lengte / 2, lengte / 2), resolution=(4, 48))
    as_ = m.Cylinder(radius=0.03, height=lengte, direction=m.UP).move_to(c)
    schroef = m.Group(mat(blad, 0.6), mat(as_, 0.6))
    schroef.add_updater(lambda s, dt: s.rotate(k * tempo.get_value() * dt, m.UP, about_point=c))
    return m.Group(huis, randen, schroef)


# ── Een stukje koperdraad van binnen: koperionen met vrije elektronen ──────
def rooster():
    """Metaalrooster: positieve koperionen (oranje) op vaste plekken."""
    return m.Group(*(mat(m.Sphere([x, y, z], radius=0.17, resolution=(12, 6)), 1, ORANJE, 0.4, 0.8)
                     for x in np.arange(-3, 3.1, 1.0) for y in (-1, 0, 1) for z in (-1, 0, 1)))


def vrije_elektronen(n, rng, drift=0.0):
    """Gele bolletjes die kriskras tussen de ionen door schieten. drift > 0: netto heel traag naar +x (er loopt
    stroom); wie rechts uit het stukje draad verdwijnt, komt links weer binnen."""
    e = m.Group(*(m.Sphere([rng.uniform(-3.3, 3.3), rng.uniform(-1.3, 1.3), rng.uniform(-1.3, 1.3)], radius=0.06,
                           resolution=(8, 4)).set_fill(ELEKTRON_KLEUR, 1).set_stroke(width=0) for _ in range(n)))

    def beweeg(g, dt):
        for d in g:
            p = d.get_center() + rng.normal(0, 0.45 * np.sqrt(dt), 3) + [drift * dt, 0, 0]
            p = np.clip(p, [-3.4 - drift, -1.4, -1.4], [3.4 + drift, 1.4, 1.4])
            if p[0] > 3.4:
                p[0] -= 6.8
            d.move_to(p)
    e.add_updater(beweeg)
    return e
