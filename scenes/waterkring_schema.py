"""Waterkring, gevolgd door de overgang naar het schakelschema.

Deel 1 is precies waterkring.py (Waterkring.waterdeel). Deel 2 is de overgang uit kring_3d_naar_2d.py:
de camera gaat naar het bovenaanzicht, batterij en lamp vloeien ter plekke over in hun symbool
en de draden worden rechte lijnen.

Run vanuit de repo-root:  python -m manimgx render scenes/waterkring_schema.py -o videos/WaterkringSchema.mp4
"""
import manimgx as m
from stijl import *
import kring_3d_naar_2d as kr
import waterkring as wk  # als modules: anders telt deze file meer dan één scène


class WaterkringSchema(wk.Waterkring):
    def construct(self):
        s = self.waterdeel()
        Z = kr.Z

        # ── Waarom een schema? Eerst naar het bovenaanzicht ──
        d = zeg(self, "Zo'n kring telkens netjes natekenen is veel werk. "
                      "Daarom gebruiken we een schematische weergave: het schakelschema.")
        self.move_camera(phi=0, theta=-90 * m.DEGREES, zoom=1.4, frame_center=[-0.5, 0, Z], focal_distance=400,
                         added_anims=[*(m.FadeOut(x) for x in (*s["samenvatting"][0], s["samenvatting"][1])),
                                      m.FadeOut(s["labels"])], run_time=d)

        # ── Draden worden rechte lijnen, onderdelen worden symbolen ──
        bron_s, lamp_s = kr.schema_symbolen()
        # zelfde looprichting als de 3D-draden (min_: − → lamp, plus: lamp → +), anders zwiept de Transform om
        min_s = draad(pool_b(bron_s), [kr.LINKS, -kr.HALF, Z], [kr.RECHTS, -kr.HALF, Z], pool_a(lamp_s))
        plus_s = draad(pool_b(lamp_s), [kr.RECHTS, kr.HALF, Z], [kr.LINKS, kr.HALF, Z], pool_a(bron_s))
        for x in (min_s, plus_s):
            x.set_stroke(WIT, 3)
        for x in (*s["lamp_delen"], *s["bat_delen"], s["halo"], s["elektronen"]):
            x.clear_updaters()  # always_redraw-omtrek, gloed en stroming stoppen voor het vervagen

        d = zeg(self, "Hierin zijn de stroomdraden rechte lijnen, en krijgt elk ander onderdeel een eigen symbool.")
        self.play(m.FadeOut(s["lamp_delen"]), m.FadeOut(s["bat_delen"]), m.FadeOut(s["halo"]),
                  m.FadeOut(s["elektronen"]), m.FadeIn(bron_s), m.FadeIn(lamp_s),
                  m.Transform(s["min_"], min_s), m.Transform(s["plus"], plus_s), run_time=min(d, 2.5))
        s["licht"].intensity = 0
        self.wait(max(d - 2.5, 0))

        # ── De twee symbolen ──
        bron_l = label("spanningsbron", bron_s, m.LEFT, size=LABEL, kleur=TEKST)
        d = zeg(self, "De batterij wordt een spanningsbron: de lange dunne streep is de plus, de korte dikke streep de min.")
        self.play(m.FadeIn(bron_l), m.Indicate(bron_s, color=U_KLEUR), run_time=d)

        lamp_l = label("lamp", lamp_s, m.RIGHT, size=LABEL, kleur=TEKST)
        d = zeg(self, "De lamp wordt een cirkel met een kruis erin. Hij brandt nog steeds.")
        self.play(m.FadeIn(lamp_l), lamp_s[2].animate.set_fill(LICHT, 1), m.FadeIn(kr.schemagloed(lamp_s)),
                  run_time=d)

        d = zeg(self, "Met zulke symbolen teken je elke stroomkring snel en overzichtelijk.")
        self.wait(d)
        zeg(self, "")
        self.wait(2)
