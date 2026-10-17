"""AA-batterij en klassieke tafellamp als witte, belichte lijntekening; de camera draait eromheen.

Alleen randen: ringen waar de vorm een knik heeft, plus de omtrek zoals de camera die ziet.
Op schaal: 1 eenheid = 10 cm (AA: 50,5 mm × Ø14,5 mm; lamp ±45 cm hoog, kap Ø30 cm).

Run vanuit de repo-root:  python -m manimgx render scenes/batterij_lamp.py -o videos/BatterijLamp.mp4
"""
import numpy as np
import manimgx as m
from stijl import *

CM = 0.1  # scène-eenheden per centimeter


class Onderdeel:
    """Een omwentelingsvorm rond een verticale as: profiel [(straal, hoogte), ...] in cm."""

    def __init__(self, profiel, plaats=(0, 0, 0), randen=None, opacity=0.35):
        self.r, self.z = (np.array(profiel, float) * CM).T
        self.plaats = np.array(plaats, float) * CM
        r, z, s = self.r, self.z, np.linspace(0, 1, len(self.r))
        self.vlak = m.Surface(lambda u, v: self.plaats + [np.interp(v, s, r) * np.cos(u), np.interp(v, s, r) * np.sin(u),
                                                          np.interp(v, s, z)],
                              u_range=(0, m.TAU), v_range=(0, 1), resolution=(48, len(r) * 2))
        self.vlak.set_fill(WIT, opacity).set_stroke(width=0).set_material(m.Material(roughness=0.5))
        knikken = range(len(r)) if randen is None else randen
        self.ringen = m.VGroup(*(m.Circle(radius=r[i]).move_to(self.plaats + [0, 0, z[i]])
                                 for i in knikken if r[i] > 0)).set_stroke(WIT, 2)

    def omtrek(self, theta):
        """De twee zijlijnen die de camera (op hoek theta rond de z-as) als rand van de vorm ziet."""
        opzij = np.array([-np.sin(theta), np.cos(theta), 0])
        punt = lambda i, kant: self.plaats + kant * self.r[i] * opzij + [0, 0, self.z[i]]
        return m.VGroup(*(m.Line(punt(i, kant), punt(i + 1, kant)) for kant in (-1, 1)
                          for i in range(len(self.r) - 1) if self.z[i] != self.z[i + 1]  # vlakke bodems: dat zijn de ringen al
                          )).set_stroke(WIT, 2)


def aa_batterij(plaats):
    """AA-cel: Ø14,5 mm × 50,5 mm, met pluspool-nopje van Ø5,5 mm."""
    r, h = 0.725, 5.05
    return [Onderdeel([(0, 0), (r * 0.9, 0), (r, 0.05), (r, h - 0.2), (r * 0.8, h - 0.1), (0.275, h - 0.1),
                       (0.275, h), (0, h)], plaats)]


def peerprofiel():
    """Gloeilamp: hals van Ø2,4 cm die overgaat in een bol van Ø6 cm (middelpunt op 36,5 cm)."""
    z = np.linspace(31, 39.5, 24)
    return [(1.2 + (z - 31) * 0.23 if z < 34.2 else np.sqrt(max(9 - (z - 36.5) ** 2, 0)), z) for z in z]


def tafellamp():
    """Ronde voet, slanke stang, fitting met peer en een kegelvormige stoffen kap."""
    return [Onderdeel([(0, 0), (7.5, 0), (7.5, 1), (5, 2.5), (1.2, 3), (0, 3)]),           # voet
            Onderdeel([(0.6, 3), (0.6, 27)]),                                                # stang
            Onderdeel([(0, 27), (1.8, 27), (1.8, 31), (0, 31)]),                             # fitting
            Onderdeel(peerprofiel(), randen=[0]),                                           # peer: glad
            Onderdeel([(15, 24), (9, 45)], opacity=0.2)]                                     # kap: open kegel


class BatterijLamp(m.ThreeDScene):
    def construct(self):
        self.add(m.AmbientLight(intensity=0.25), m.SunLight([-4, -6, 8], intensity=2.5))
        delen = tafellamp() + aa_batterij((12, -4, 0))  # batterij staat op de tafel naast de voet
        beugel = m.VGroup(*(m.Line([0, 0, 33 * CM], [9 * CM * np.cos(a), 9 * CM * np.sin(a), 45 * CM])
                            for a in np.arange(0, m.TAU, m.TAU / 3))).set_stroke(WIT, 2)
        self.set_camera_orientation(phi=70 * m.DEGREES, theta=-60 * m.DEGREES, frame_center=[0.3, 0, 2.2], zoom=1.4)
        omtrek = m.always_redraw(lambda: m.VGroup(*(d.omtrek(self.camera.get_theta()) for d in delen)))
        self.add(*(d.vlak for d in delen), *(d.ringen for d in delen), beugel, omtrek)

        # Peer gloeit periodiek: peer zelf geel, een halo eromheen en echt licht in de kap
        peer, midden = delen[3].vlak.set_material(None), np.array([0, 0, 36.5 * CM])  # zonder materiaal: eigen licht
        licht = m.PointLight(midden, LICHT, intensity=0, radius=6)
        halo = m.Group(*(m.Sphere(midden, radius=r, resolution=(24, 12)).set_fill(LICHT, 0).set_stroke(width=0)
                         for r in np.linspace(0.35, 1.0, 10)))  # veel dunne lagen: zachte gloed
        halo.t = 0.0

        def gloei(h, dt):
            h.t += dt
            g = np.clip(2 * np.sin(m.TAU * h.t / 4) + 0.5, 0, 1)  # periode 4 s: ±1,7 s aan, ±1,7 s uit
            peer.set_fill(m.interpolate_color(m.ManimColor(WIT), m.ManimColor(LICHT), g), 0.35 + 0.65 * g)
            for i, bol in enumerate(h):
                bol.set_fill(opacity=g * 0.09 * (1 - i / len(h)))
            licht.intensity = 5 * g
        halo.add_updater(gloei)
        self.add(licht, halo)
        self.begin_ambient_camera_rotation(rate=0.4)  # één rondje in ±16 s
        self.wait(m.TAU / 0.4)
