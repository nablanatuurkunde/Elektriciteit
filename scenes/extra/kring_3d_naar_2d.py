"""AA-batterij en tafellamp in een stroomkring (3D), die overgaat in het 2D-schakelschema.

De draden liggen plat op tafel (het xy-vlak) als een rechthoek: links de liggende batterij,
rechts tegenover de staande lamp. De camera gaat naar het bovenaanzicht; daar is de kring al
het schema, en batterij en lamp vloeien ter plekke over in hun symbool.
Schaal als in extra/batterij_lamp.py: 1 eenheid = 10 cm.

Run vanuit de repo-root:  python -m manimgx render scenes/extra/kring_3d_naar_2d.py -o videos/Kring3DNaar2D.mp4
"""
import numpy as np
import manimgx as m
from bouwstenen import *


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
        plus_s = draad(pool_a(bron_s), [LINKS, HALF, Z], [RECHTS, HALF, Z], pool_b(lamp_s))
        min_s = draad(pool_b(bron_s), [LINKS, -HALF, Z], [RECHTS, -HALF, Z], pool_a(lamp_s))

        omtrek.clear_updaters()
        halo.clear_updaters()
        self.play(*(m.FadeOut(x) for x in (*drie_d, omtrek, halo)), m.FadeIn(bron_s), m.FadeIn(lamp_s),
                  m.Transform(plus, plus_s), m.Transform(min_, min_s), run_time=2)
        licht.intensity = 0
        # Schemalamp brandt ook: gele vulling plus een zachte platte halo, net onder het symbool
        gloed = schemagloed(lamp_s)
        self.play(lamp_s[2].animate.set_fill(LICHT, 1), m.FadeIn(gloed), run_time=SNEL)
        self.wait(2)
