"""AA-batterij en tafellamp in een stroomkring (3D), die overgaat in het 2D-schakelschema.

De draden liggen plat op tafel (het xy-vlak) als een rechthoek: links de liggende batterij,
rechts tegenover de staande lamp. De camera gaat naar het bovenaanzicht; daar is de kring al
het schema, en batterij en lamp vloeien ter plekke over in hun symbool.
Schaal als in batterij_lamp.py: 1 eenheid = 10 cm.

Run vanuit de repo-root:  python -m manimgx render scenes/kring_3d_naar_2d.py -o videos/Kring3DNaar2D.mp4
"""
import numpy as np
import manimgx as m
from stijl import *
import batterij_lamp as bl

LINKS, RECHTS, HALF = -2.5, 1.5, 2.0  # kring: x van batterij- tot lampzijde, y van -HALF tot HALF
Z = 0.0725                            # hoogte van de draden: de as van de liggende batterij (Ø14,5 mm)
BAT_HALF = 0.2525                     # halve lengte AA (50,5 mm)
VOET = 0.75                           # straal van de lampvoet: daar komen de draden binnen


class LiggendeBatterij:
    """De AA-cel uit batterij_lamp.py, op zijn kant op tafel: as langs +y, pluspool naar +y."""

    def __init__(self, min_pool):
        self.d = bl.aa_batterij((0, 0, 0))[0]
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
                          for i in range(len(r) - 1) if z[i] != z[i + 1])).set_stroke(WIT, 2)


def lijn(*punten_xy):
    return draad(*([x, y, Z] for x, y in punten_xy)).set_stroke(WIT, 3)


def opstelling():
    """Tafellamp rechts en liggende batterij links; geeft (lampdelen, beugel, batterij)."""
    lamp3d = bl.tafellamp()
    for d in lamp3d:
        d.plaats = d.plaats + [RECHTS, 0, 0]  # omtrek() rekent vanuit plaats
        d.vlak.shift(RECHTS * m.RIGHT)
        d.ringen.shift(RECHTS * m.RIGHT)
    beugel = m.VGroup(*(m.Line([RECHTS, 0, 3.3], [RECHTS + 0.9 * np.cos(a), 0.9 * np.sin(a), 4.5])
                        for a in np.arange(0, m.TAU, m.TAU / 3))).set_stroke(WIT, 2)
    lamp3d[3].vlak.set_material(None)  # peer altijd onbelicht (eigen kleur), ook vóór hij gloeit: geen sprong
    return lamp3d, beugel, LiggendeBatterij([LINKS, -BAT_HALF, Z])


def gloeiende_peer(lamp3d, g):
    """Licht en halo rond de peer, aangestuurd door ValueTracker g (0 = uit, 1 = aan). Geeft (licht, halo)."""
    peer, midden = lamp3d[3].vlak, np.array([RECHTS, 0, 3.65])
    licht = m.PointLight(midden, LICHT, intensity=0, radius=6)
    halo = m.Group(*(m.Sphere(midden, radius=r, resolution=(24, 12)).set_fill(LICHT, 0).set_stroke(width=0)
                     for r in np.linspace(0.35, 1.0, 10)))

    def gloei(h):
        v = g.get_value()
        peer.set_fill(m.interpolate_color(m.ManimColor(WIT), m.ManimColor(LICHT), v), 0.35 + 0.65 * v)
        for i, bol in enumerate(h):
            bol.set_fill(opacity=v * 0.09 * (1 - i / len(h)))
        licht.intensity = 5 * v
    halo.add_updater(gloei)
    return licht, halo


def zon_en_schemer():
    # Zon zonder schaduw: anders werpt de (onzichtbare) halo rond de peer ineens schaduw op de kap
    return m.AmbientLight(intensity=0.25), m.SunLight([-4, -6, 8], intensity=2.5, shadows=False)


def schema_symbolen():
    """Bron links (+ naar boven, zoals de liggende batterij) en lamp rechts, plat in het xy-vlak op tafelhoogte."""
    bron_s = plaats(bron(), [LINKS, LENGTE / 2, Z], [LINKS, -LENGTE / 2, Z])  # pool a (+) boven
    lamp_s = plaats(lamp(), [RECHTS, -LENGTE / 2, Z], [RECHTS, LENGTE / 2, Z])
    return bron_s, lamp_s


def schemagloed(lamp_s):
    """Zachte platte halo net onder het lampsymbool."""
    return m.VGroup(*(m.Circle(radius=r, stroke_width=0, fill_color=LICHT, fill_opacity=0.08 * (1 - i / 8))
                      for i, r in enumerate(np.linspace(0.35, 1.0, 8)))).move_to(lamp_s[2]).shift(-0.01 * m.OUT)


class Kring3DNaar2D(m.ThreeDScene):
    def construct(self):
        self.add(*zon_en_schemer())

        # ── 3D: lamp rechts, batterij links op zijn kant, draden plat op tafel ──
        lamp3d, beugel, bat = opstelling()
        plus = lijn((LINKS, BAT_HALF), (LINKS, HALF), (RECHTS, HALF), (RECHTS, VOET))      # + → achterkant voet
        min_ = lijn((LINKS, -BAT_HALF), (LINKS, -HALF), (RECHTS, -HALF), (RECHTS, -VOET))  # − → voorkant voet

        self.set_camera_orientation(phi=65 * m.DEGREES, theta=-60 * m.DEGREES, zoom=1.1, frame_center=[-0.5, 0, 1.3])
        omtrek = m.always_redraw(lambda: m.VGroup(
            *(d.omtrek(self.camera.get_theta()) for d in lamp3d),
            bat.omtrek(self.camera.get_phi(), self.camera.get_theta())))
        drie_d = [*(d.vlak for d in lamp3d), *(d.ringen for d in lamp3d), bat.d.vlak, bat.d.ringen, beugel]
        self.add(*drie_d, omtrek)
        self.wait(0.5)
        self.move_camera(theta=-70 * m.DEGREES, added_anims=[m.Create(plus), m.Create(min_)], run_time=2.5)

        # Kring dicht: de peer gloeit (zoals in batterij_lamp.py, maar constant aan)
        g = m.ValueTracker(0)
        licht, halo = gloeiende_peer(lamp3d, g)
        self.add(licht, halo)
        self.move_camera(theta=-80 * m.DEGREES, added_anims=[g.animate.set_value(1)], run_time=2.5)

        # ── Overgang: eerst naar het bovenaanzicht, perspectief eruit ──
        self.move_camera(phi=0, theta=-90 * m.DEGREES, zoom=1.4, frame_center=[-0.5, 0, Z], focal_distance=400,
                         run_time=3)
        self.wait(0.5)

        # Schema op dezelfde plek, plat in het xy-vlak: bron links (+ naar boven, zoals de batterij), lamp rechts
        bron_s, lamp_s = schema_symbolen()
        plus_s = draad(pool_a(bron_s), [LINKS, HALF, Z], [RECHTS, HALF, Z], pool_b(lamp_s)).set_stroke(WIT, 3)
        min_s = draad(pool_b(bron_s), [LINKS, -HALF, Z], [RECHTS, -HALF, Z], pool_a(lamp_s)).set_stroke(WIT, 3)

        omtrek.clear_updaters()
        halo.clear_updaters()
        self.play(*(m.FadeOut(x) for x in (*drie_d, omtrek, halo)), m.FadeIn(bron_s), m.FadeIn(lamp_s),
                  m.Transform(plus, plus_s), m.Transform(min_, min_s), run_time=2)
        licht.intensity = 0
        # Schemalamp brandt ook: gele vulling plus een zachte platte halo, net onder het symbool
        gloed = schemagloed(lamp_s)
        self.play(lamp_s[2].animate.set_fill(LICHT, 1), m.FadeIn(gloed), run_time=SNEL)
        self.wait(2)
