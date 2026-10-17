"""Voorbeelden van de huisstijl. Run vanuit de repo-root:  python -m manimgx render scenes/stijl_demo.py WetVanOhm -o videos/WetVanOhm.mp4"""
import numpy as np
import manimgx as m
from stijl import *


class Symbolen(m.Scene):
    def construct(self):
        self.play(m.Write(titel("Symbolen")))
        namen = [("spanningsbron", bron()), ("weerstand", weerstand()), ("variabele weerstand", variabele_weerstand()),
                 ("lamp", lamp()), ("schakelaar", schakelaar()), ("stroommeter", meter("A")),
                 ("spanningsmeter", meter("V")), ("diode", diode()), ("LED", led()),
                 ("LDR", ldr()), ("NTC", ntc())]
        cellen = m.VGroup(*(m.VGroup(s, label(n, s, m.DOWN, kleur=TEKST)) for n, s in namen))
        cellen.arrange_in_grid(rows=3, buff=(1.0, 0.7)).move_to(0.4 * m.DOWN)
        self.play(m.LaggedStart(*(m.FadeIn(c) for c in cellen), lag_ratio=0.1), run_time=TRAAG)
        self.wait(PAUZE)


class WetVanOhm(m.Scene):
    def construct(self):
        self.play(m.Write(titel("De wet van Ohm")))

        # Rechthoekige kring rond SCHAKELING: bron links, weerstand boven, lamp rechts, meter onder
        lb, rb, ro, lo = (SCHAKELING + np.array(v) for v in ([-2.5, 1.6, 0], [2.5, 1.6, 0], [2.5, -1.6, 0], [-2.5, -1.6, 0]))
        # tak(lb, lo, ...) zet pool a (+) boven: de stroom gaat bij + de kring in
        kring = m.VGroup(tak(lb, lo, bron()), tak(lb, rb, weerstand()),
                         tak(rb, ro, lamp()), tak(ro, lo, meter("A")))
        self.play(m.Create(kring), run_time=TRAAG)
        self.play(m.FadeIn(label("R", kring[1][1], kleur=R_KLEUR, size=LABEL)),
                  m.FadeIn(label("U", kring[0][1], m.LEFT, kleur=U_KLEUR, size=LABEL)))
        self.wait(PAUZE)

        # Stroom: pijltjes van + naar −; lamp gaat branden
        pad = [lo, lb, rb, ro, lo]
        i = stroom(pad)
        self.play(m.FadeIn(i), kring[2][1][2].animate.set_fill(LICHT, 0.6))
        self.wait(2)

        # Formules rechts, één voor één
        f1 = formule(r"U = I \cdot R")
        f2 = waarde("U", 6, "V")
        f3 = waarde("R", 24, "\\Omega", 0)
        f4 = waarde("I", 0.25, "A", 2)
        rij = m.VGroup(f1, f2, f3, f4).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.4).move_to(FORMULES)
        self.play(m.Write(f1), run_time=NORMAAL)
        self.play(m.Create(kader(f1)))
        for f in (f2, f3, f4):
            self.play(m.FadeIn(f, shift=0.2 * m.UP), run_time=SNEL)
            self.wait(PAUZE)

        # Elektronen bewegen de andere kant op
        self.play(m.FadeOut(i), m.FadeIn(e := elektronen(pad)))
        self.wait(3)
