"""AA-batterij en klassieke tafellamp als witte, belichte lijntekening; de camera draait eromheen.

Alleen randen: ringen waar de vorm een knik heeft, plus de omtrek zoals de camera die ziet.
Op schaal: 1 eenheid = 10 cm (AA: 50,5 mm × Ø14,5 mm; lamp ±45 cm hoog, kap Ø30 cm).

Run vanuit de repo-root:  python -m manimgx render scenes/extra/batterij_lamp.py -o videos/BatterijLamp.mp4
"""
import numpy as np
import manimgx as m
from bouwstenen import *


class BatterijLamp(m.ThreeDScene):
    def construct(self):
        self.add(m.AmbientLight(intensity=0.25), m.SunLight([-4, -6, 8], intensity=2.5))
        delen = tafellamp() + aa_batterij((12, -4, 0))  # batterij staat op de tafel naast de voet
        beugel = m.VGroup(*(m.Line([0, 0, 33 * CM], [9 * CM * np.cos(a), 9 * CM * np.sin(a), 45 * CM])
                            for a in np.arange(0, m.TAU, m.TAU / 3))).set_stroke(WIT, RAND_DIKTE)
        self.set_camera_orientation(phi=70 * m.DEGREES, theta=-60 * m.DEGREES, frame_center=[0.3, 0, 2.2], zoom=1.4)
        omtrek = m.always_redraw(lambda: m.VGroup(*(d.omtrek(self.camera.get_theta()) for d in delen)))
        self.add(*(d.vlak for d in delen), *(d.ringen for d in delen), beugel, omtrek)

        # Peer gloeit periodiek: peer zelf geel, een halo eromheen en echt licht in de kap
        peer, midden = delen[3].vlak.set_material(None), np.array([0, 0, 36.5 * CM])  # zonder materiaal: eigen licht
        licht = m.PointLight(midden, LICHT, intensity=0, radius=6)
        halo = m.Group(*(m.Sphere(midden, radius=r, resolution=(24, 12)).set_fill(LICHT, 0).set_stroke(width=0)
                         for r in np.linspace(*HALO_STRAAL, HALO_LAGEN)))  # veel dunne lagen: zachte gloed
        halo.t = 0.0

        def gloei(h, dt):
            h.t += dt
            g = np.clip(2 * np.sin(m.TAU * h.t / 4) + 0.5, 0, 1)  # periode 4 s: ±1,7 s aan, ±1,7 s uit
            peer.set_fill(m.interpolate_color(m.ManimColor(WIT), m.ManimColor(LICHT), g), 0.35 + 0.65 * g)
            for i, bol in enumerate(h):
                bol.set_fill(opacity=g * HALO_DEKKING * (1 - i / len(h)))
            licht.intensity = LAMPLICHT * g
        halo.add_updater(gloei)
        self.add(licht, halo)
        self.begin_ambient_camera_rotation(rate=0.4)  # één rondje in ±16 s
        self.wait(m.TAU / 0.4)
