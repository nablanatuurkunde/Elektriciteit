"""Video 1 – Lading: atomen, protonen en elektronen, de elementaire lading, ionen en vrije elektronen in een metaal.

Haak: de lithium-ion-accu in je telefoon (wat is een ion?). Opbouw: atoom (lithium: 3 protonen, 4 neutronen,
3 elektronen) → lading van proton en elektron → elementaire lading e uit Binas → neutraal atoom (+3e − 3e = 0)
→ positief ion (een elektron vliegt weg) → negatief ion (er komt er een bij) → Q = n·e, 1 C ≈ 6,2·10¹⁸ elektronen
→ metaal: rooster van positieve ionen met vrije elektronen (brug naar de waterkring) → ladingsbehoud → samenvatting.

Run vanuit de repo-root:  python -m manimgx render scenes/01_lading.py -o videos/Lading.mp4
"""
import numpy as np
import manimgx as m
from bouwstenen import *


PROTON, NEUTRON = ROOD, GEDEMPT
GULDEN_HOEK = np.pi * (3 - np.sqrt(5))


def kern(protonen, neutronen, straal=0.11):
    """Bolletjes dicht op elkaar (Fibonacci-bol), protonen en neutronen door elkaar."""
    n = protonen + neutronen
    kleuren = [PROTON] * protonen + [NEUTRON] * neutronen
    soorten = [kleuren[i] for i in np.random.default_rng(n).permutation(n)]  # door elkaar, maar elke render gelijk
    r = 1.1 * straal * n ** (1 / 3)
    bollen = []
    for i, kleur in enumerate(soorten):
        y = 1 - 2 * (i + 0.5) / n
        p = r * np.array([np.sqrt(1 - y * y) * np.cos(i * GULDEN_HOEK), np.sqrt(1 - y * y) * np.sin(i * GULDEN_HOEK), y])
        bollen.append(mat(m.Sphere(p, radius=straal, resolution=(12, 6)), 1, kleur, 0.4))
    return m.Group(*bollen)


class Schil:
    """Een elektronenbaan: kring met straal r, gekanteld; elektronen draaien erover rond."""

    def __init__(self, r, kantel_x, kantel_y, snelheid):
        self.r, self.snelheid = r, snelheid
        self.draai = (lambda v: m.rotate_vector(m.rotate_vector(v, kantel_x, m.RIGHT), kantel_y, m.UP))
        self.ring = m.Circle(radius=r).set_stroke(GEDEMPT, RAND_DIKTE, 0.6)
        self.ring.apply_function(self.draai)

    def plek(self, hoek):
        return self.draai(self.r * np.array([np.cos(hoek), np.sin(hoek), 0]))


def elektron(schil, hoek):
    """Geel bolletje dat over zijn schil draait, tot e.vrij = True (dan kun je het zelf bewegen)."""
    e = m.Sphere(radius=0.08, resolution=(10, 5)).set_fill(ELEKTRON_KLEUR, 1).set_stroke(width=0)
    e.hoek, e.vrij = hoek, False
    e.move_to(schil.plek(hoek))

    def draai(mob, dt):
        if mob.vrij:
            return
        mob.hoek += dt * schil.snelheid
        mob.move_to(schil.plek(mob.hoek))
    e.add_updater(draai)
    return e


def legenda():
    regels = [(PROTON, "proton:  +e"), (NEUTRON, "neutron:  0"), (ELEKTRON_KLEUR, "elektron:  −e")]
    return paneel(*(m.VGroup(m.Dot(radius=0.1, color=k), tekst(t, LABEL)).arrange(m.RIGHT, buff=0.25)
                    for k, t in regels), hoek=m.UL)


class Lading(Les):
    def construct(self):
        self.add(*zon_en_schemer())
        rng = np.random.default_rng(7)
        self.set_camera_orientation(phi=68 * m.DEGREES, theta=-60 * m.DEGREES, zoom=1.3, frame_center=[0, 0, 0])

        def rij(tex):
            return formule(komma(tex), size=FORMULE - 6)

        # ── Haak ──
        binnen = Schil(0.75, 65 * m.DEGREES, 10 * m.DEGREES, 1.6)
        buiten = Schil(1.45, 110 * m.DEGREES, -30 * m.DEGREES, 0.9)
        kern_li = kern(3, 4)
        elektronen = [elektron(binnen, 0), elektron(binnen, np.pi), elektron(buiten, 1.0)]
        atoom = m.Group(kern_li, binnen.ring, buiten.ring, *elektronen)
        d = zeg(self, "In je telefoon zit een lithium-ion-accu. Maar wat is eigenlijk een ion? En wat is lading? "
                      "Daar beginnen we mee, want alles in deze reeks draait om lading die beweegt.")
        self.begin_ambient_camera_rotation(rate=0.05)
        self.doe(d, m.FadeIn(atoom), duur=TRAAG)

        # ── Het atoom ──
        leg = legenda()
        d = zeg(self, "Alles om je heen is gemaakt van atomen. Een atoom heeft een kern van protonen en neutronen, "
                      "met daaromheen elektronen. Dit is een lithiumatoom.")
        self.doe(d, *self.toon(leg[0]))
        d = zeg(self, "Protonen zijn positief geladen, elektronen negatief. Neutronen hebben geen lading.")
        self.play(*self.toon(leg[1][0]), run_time=SNEL)
        self.play(*self.toon(leg[1][1]), run_time=SNEL)
        self.doe(d - 2 * SNEL, *self.toon(leg[1][2]), duur=SNEL)

        # ── Elementaire lading ──
        e_paneel = paneel(rij(r"e = 1,602 \cdot 10^{-19}\ \mathrm{C}"), tekst("Binas: elementaire lading", KLEIN + 4),
                          hoek=m.UR)
        d = zeg(self, "De lading van een proton is precies even groot als die van een elektron, alleen met een "
                      "ander teken. Die kleinste hoeveelheid lading heet de elementaire lading, e.")
        self.wait(d)
        d = zeg(self, "Lading meet je in coulomb. In Binas vind je: e is 1,602 maal 10 tot de min 19 coulomb.")
        self.doe(d, *self.toon(e_paneel))

        # ── Neutraal ──
        q_paneel = paneel(rij(r"Q = +3e - 3e = 0"), hoek=m.DR)
        q_paneel.shift(1.1 * m.UP)  # boven de ondertitels
        d = zeg(self, "Dit lithiumatoom heeft 3 protonen en 3 elektronen. Plus 3 e en min 3 e: samen nul. "
                      "Het atoom is neutraal.")
        self.doe(d, *self.toon(q_paneel))

        # ── Positief ion: een elektron vliegt weg ──
        def nieuwe_q(tex):  # het hele paneel, zodat het kader meegroeit met de formule
            return m.Transform(q_paneel, paneel(rij(tex), hoek=m.DR).shift(1.1 * m.UP))

        weg = elektronen[2]
        d = zeg(self, "Haal er één elektron af. Nu zijn er 3 protonen, maar nog maar 2 elektronen: het atoom is "
                      "positief geladen, plus e.")
        weg.vrij = True
        self.doe(d, weg.animate.move_to([4.5, -3, 2]).set_fill(opacity=0), nieuwe_q(r"Q = +3e - 2e = +e"), duur=TRAAG)
        naam = tekst("positief ion", KOP, PROTON).to_edge(m.UP, buff=0.4)
        d = zeg(self, "Een atoom met een lading noemen we een ion. Dit is een lithium-ion: precies het deeltje dat in "
                      "je accu heen en weer schuift als je hem oplaadt en weer gebruikt.")
        self.doe(d, *self.toon(naam))

        # ── Negatief ion: er komen elektronen bij ──
        terug = elektron(buiten, 1.0)
        extra = elektron(buiten, 1.0 + np.pi)
        for e_ in (terug, extra):
            e_.vrij = True
            e_.move_to(buiten.plek(e_.hoek) + np.array([3, -3, 2]))
            e_.set_fill(opacity=0)
        self.add(terug, extra)
        naam_min = tekst("negatief ion", KOP, ELEKTRON_KLEUR).to_edge(m.UP, buff=0.4)
        d = zeg(self, "Krijgt een atoom er juist elektronen bij, dan wordt het een negatief ion. "
                      "Met 3 protonen en 4 elektronen is de lading min e.")
        self.play(terug.animate.move_to(buiten.plek(terug.hoek)).set_fill(opacity=1),
                  extra.animate.move_to(buiten.plek(extra.hoek)).set_fill(opacity=1),
                  nieuwe_q(r"Q = +3e - 4e = -e"), m.FadeOut(naam), run_time=TRAAG)
        terug.vrij = extra.vrij = False  # ze draaien weer mee
        self.doe(d - TRAAG, *self.toon(naam_min), duur=SNEL)

        # ── Q = n·e en de coulomb ──
        ne = paneel(rij(r"Q = n \cdot e"), rij(r"n = \frac{1}{1,602 \cdot 10^{-19}} = 6,2 \cdot 10^{18}"),
                    tekst("elektronen in 1 C", KLEIN + 4), hoek=m.UR)
        d = zeg(self, "Lading bestaat dus altijd uit een heel aantal elementaire ladingen: Q is n maal e. "
                      "Een half elektron bestaat niet.")
        self.play(m.FadeOut(e_paneel), m.FadeOut(naam_min), m.FadeOut(q_paneel), run_time=SNEL)
        self.doe(d - SNEL, *self.toon(ne[0], ne[1][0]))
        d = zeg(self, "Hoeveel elektronen zijn samen één coulomb? 1 gedeeld door 1,602 maal 10 tot de min 19: "
                      "zo'n 6,2 maal 10 tot de 18. Een gigantisch aantal.")
        self.doe(d, *self.toon(ne[1][1], ne[1][2]))

        # ── Metaal: vrije elektronen tussen positieve ionen ──
        self.stop_ambient_camera_rotation()
        for e_ in (*elektronen, terug, extra):
            e_.clear_updaters()
        ionen, vrij = rooster(), vrije_elektronen(63, rng)
        d = zeg(self, "In een metaal zoals koper laat elk atoom een elektron los. Die vrije elektronen kunnen door "
                      "het hele metaal bewegen. Wat overblijft, zijn positieve koperionen, die op hun plek blijven.")
        self.play(m.FadeOut(atoom), m.FadeOut(terug), m.FadeOut(extra), m.FadeOut(ne), m.FadeOut(leg), run_time=SNEL)
        self.remove(atoom, terug, extra)
        self.move_camera(phi=65 * m.DEGREES, theta=-70 * m.DEGREES, zoom=1.0, added_anims=[m.FadeIn(ionen)],
                         run_time=TRAAG)
        self.add(vrij)
        self.doe(d - SNEL - TRAAG, m.FadeIn(vrij))
        d = zeg(self, "Zonder batterij schieten die vrije elektronen kriskras door elkaar, maar gemiddeld gaan ze "
                      "nergens heen. Dat verandert als je er een batterij op aansluit: dat zie je in de volgende video.")
        self.move_camera(theta=-50 * m.DEGREES, run_time=d, rate_func=m.linear)

        # ── Ladingsbehoud + samenvatting ──
        d = zeg(self, "Nog één belangrijke regel: lading kan niet verdwijnen, en ook niet uit het niets ontstaan. "
                      "Dat heet ladingsbehoud.")
        self.wait(d)
        samen = paneel(tekst("proton +e, elektron −e, neutron 0", LABEL), rij(r"e = 1,602 \cdot 10^{-19}\ \mathrm{C}"),
                       tekst("ion: atoom met te veel of te weinig elektronen", LABEL), rij(r"Q = n \cdot e"),
                       tekst("metaal: vrije elektronen tussen positieve ionen", LABEL), hoek=m.UL)
        d = zeg(self, "Samengevat:")
        vrij.clear_updaters()
        self.play(m.FadeOut(ionen), m.FadeOut(vrij), run_time=SNEL)
        self.hud(samen[0])
        self.play(m.FadeIn(samen[0]), m.LaggedStart(*(self.toon(r)[0] for r in samen[1]), lag_ratio=0.3),
                  run_time=max(d - SNEL, 4))
        zeg(self, "")
        self.wait(3)
