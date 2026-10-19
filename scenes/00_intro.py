"""Video 0 – Intro: waarom gaat de lamp meteen aan, als elektronen zo traag zijn?

In de stijl van de reeks: de tafellamp (bouwstenen/modellen.py) en een 3D-lichtknopje aan de muur, met een snoer
ertussen. Knopje om → lamp meteen aan. Inzoomen op het snoer tot het koperrooster met vrije elektronen uit video 1;
één elektron volgen: het schuift maar een paar honderdste millimeter per seconde op, en doet over een halve meter snoer
zo'n drie uur (driftsnelheid ≈ I / (n·A·e) ≈ 0,05 mm/s). De vraag blijft staan (het antwoord komt in de
waterkring-video). Dan het overzicht van de reeks naast het schema uit video 2–5. Daarna volgt in de film het
Nabla-logo (assets/Intro.mov, zie film.py).

Run vanuit de repo-root:  python -m manimgx render scenes/00_intro.py -o videos/Intro.mp4
"""
import numpy as np
import manimgx as m
from bouwstenen import *


LAMP_X = 1.5                 # de tafellamp staat met zijn voet op (1,5; 0)
MUUR_Y = 1.8                 # voorkant van de muur
KNOP = np.array([-2.6, MUUR_Y, 2.6])
SNOER = [KNOP + [0, -0.06, -0.5], [-2.6, MUUR_Y - 0.06, 0.03], [LAMP_X, MUUR_Y - 0.06, 0.03], [LAMP_X, 0.75, 0.03]]

ONDERWERPEN = [("lading", ELEKTRON_KLEUR), ("de waterkring", WATER_KLEUR), ("stroom", I_KLEUR), ("spanning", U_KLEUR),
               ("weerstand", R_KLEUR), ("serie en parallel", TEKST), ("vermogen", P_KLEUR), ("sensoren", TEKST),
               ("elektriciteit in huis", TEKST)]


def muur():
    """Doorschijnende muur achter de lamp, met een rand."""
    vlak = mat(m.Prism(dimensions=[9, 0.1, 6]), 0.12).move_to([-0.5, MUUR_Y + 0.05, 3])
    rand = m.Rectangle(width=9, height=6).rotate(m.PI / 2, m.RIGHT).move_to([-0.5, MUUR_Y, 3]).set_stroke(WIT, RAND_DIKTE)
    return m.Group(vlak, rand)


def lichtknopje():
    """Inbouwschakelaar: een plaatje op de muur met een wipknop erin. Geeft (knopje, wip); de wip kantelt om x."""
    plaat = mat(m.Prism(dimensions=[0.8, 0.1, 0.8]), 0.5).move_to(KNOP + [0, -0.05, 0])
    plaat_rand = m.Square(side_length=0.8).rotate(m.PI / 2, m.RIGHT).move_to(KNOP + [0, -0.101, 0]).set_stroke(WIT, RAND_DIKTE)
    wip = m.Group(mat(m.Prism(dimensions=[0.34, 0.12, 0.5]), 0.8),
                  m.Rectangle(width=0.34, height=0.5).rotate(m.PI / 2, m.RIGHT).shift([0, -0.061, 0])
                  .set_stroke(WIT, RAND_DIKTE)).move_to(KNOP + [0, -0.16, 0])
    wip.rotate(-12 * m.DEGREES, m.RIGHT, about_point=KNOP + [0, -0.1, 0])  # uit: bovenkant naar voren
    return m.Group(plaat, plaat_rand, wip), wip


def klokje(uren):
    """Platte klok (vast in beeld) waarvan wijzer en getal de ValueTracker `uren` volgen."""
    rand = m.Circle(radius=0.45, color=TEKST, stroke_width=3, fill_color=BG, fill_opacity=1)
    streepjes = m.VGroup(*(m.Line(0.36 * m.UP, 0.45 * m.UP, stroke_width=2, color=TEKST)
                           .rotate(-k * m.TAU / 12, about_point=m.ORIGIN) for k in range(12)))
    wijzer = m.Line(m.ORIGIN, 0.33 * m.UP, color=ACCENT, stroke_width=4)
    klok = m.VGroup(rand, streepjes, wijzer, tekst("0 uur", LABEL).next_to(rand, m.RIGHT, buff=0.2))

    def volg(k):
        c = k[0].get_center()
        k[2].put_start_and_end_on(c, c + 0.33 * m.rotate_vector(m.UP, -m.TAU * uren.get_value()))
        k[3].become(tekst(f"{int(uren.get_value())} uur", LABEL).next_to(k[0], m.RIGHT, buff=0.2))
    klok.add_updater(volg)
    return klok


class Intro(Les):
    def construct(self):
        self.add(*zon_en_schemer())
        rng = np.random.default_rng(3)

        # ═══ De kamer: knopje om, lamp meteen aan ═══
        lamp3d, beugel = tafellamp_op(LAMP_X)
        knopje, wip = lichtknopje()
        snoer = draad(*SNOER)
        omtrek = m.always_redraw(lambda: m.VGroup(*(d.omtrek(self.camera.get_theta()) for d in lamp3d)))
        kamer = m.Group(muur(), knopje, snoer, *(d.vlak for d in lamp3d), *(d.ringen for d in lamp3d), beugel, omtrek)
        g = m.ValueTracker(0)
        licht, halo = gloeiende_peer(lamp3d, g, x=LAMP_X)
        self.set_camera_orientation(phi=72 * m.DEGREES, theta=-68 * m.DEGREES, zoom=0.95, frame_center=[-0.4, 0.6, 2.2])
        self.add(kamer, licht, halo)

        d = zeg(self, "Je drukt op het lichtknopje, en de lamp gaat aan.")
        self.move_camera(theta=-74 * m.DEGREES, run_time=d - 0.3, rate_func=m.linear)
        self.play(m.Rotate(wip, 24 * m.DEGREES, m.RIGHT, about_point=KNOP + [0, -0.1, 0]), run_time=0.15)
        g.set_value(1)  # meteen aan: geen fade
        self.play(m.Flash(wip, color=WIT, flash_radius=0.4), run_time=0.15)
        d = zeg(self, "Meteen. Je denkt er nooit over na.")
        self.move_camera(theta=-78 * m.DEGREES, run_time=d, rate_func=m.linear)

        # ═══ Het snoer: een halve meter ═══
        vloerstuk = m.Line(SNOER[1], SNOER[2])
        maat = m.VGroup(m.Brace(m.Line([SNOER[1][0], 0, 0], [SNOER[2][0], 0, 0]), m.DOWN, color=TEKST),
                        tekst("0,5 m", KOP))
        maat[1].next_to(maat[0], m.DOWN, buff=0.15)
        staand(maat).move_to(vloerstuk.get_center() + [0, -0.25, 0.55])  # rechtop voor de muur, boven het snoer
        d = zeg(self, "Maar hier zit iets vreemds. Tussen het knopje en de lamp zit zo'n halve meter snoer.")
        self.move_camera(phi=82 * m.DEGREES, theta=-90 * m.DEGREES, zoom=1.15, frame_center=[-0.5, MUUR_Y, 0.9],
                         run_time=d * 0.6)
        self.doe(d * 0.4, m.GrowFromCenter(maat[0]), m.FadeIn(maat[1]), duur=d * 0.4)

        # ═══ In het snoer: het koperrooster uit video 1 ═══
        d = zeg(self, "In dat snoer zit koperdraad, met heel veel vrije elektronen.")
        self.move_camera(zoom=60, frame_center=vloerstuk.get_center(), added_anims=[m.FadeOut(maat)], run_time=1.5,
                         rate_func=m.rush_into)
        omtrek.clear_updaters()
        halo.clear_updaters()
        self.remove(kamer, licht, halo, maat)
        ionen, vrij = rooster(), vrije_elektronen(63, rng, drift=0.05)
        self.set_camera_orientation(phi=65 * m.DEGREES, theta=-70 * m.DEGREES, zoom=4, frame_center=m.ORIGIN)
        self.move_camera(zoom=1.0, added_anims=[m.FadeIn(ionen), m.FadeIn(vrij)], run_time=1.5, rate_func=m.rush_from)
        self.begin_ambient_camera_rotation(rate=0.02)
        self.wait(max(d - 3, 0))

        # één elektron volgen, op een routekaartje van knopje naar lamp
        volg = m.Sphere(radius=0.09, resolution=(12, 6)).set_fill(ELEKTRON_KLEUR, 1).set_stroke(width=0).move_to([-1.5, 0.3, 0.4])
        volg.add_updater(lambda v, dt: v.shift(0.05 * dt * m.RIGHT + rng.normal(0, 0.05 * np.sqrt(dt), 3)))
        ring = mat(m.Torus(major_radius=0.25, minor_radius=0.02, resolution=(24, 8)), 1, ACCENT, 0.4)
        ring.add_updater(lambda r: r.move_to(volg))
        kaart_k, kaart_l = schakelaar(open=False).scale(0.6), lamp().scale(0.6)
        kaart = m.VGroup(kaart_k, m.Line(3.5 * m.LEFT, 3.5 * m.RIGHT, color=DRAAD, stroke_width=DRAAD_DIKTE), kaart_l)
        kaart.arrange(m.RIGHT, buff=0).move_to(3.45 * m.UP)
        kaart.add(label("knopje", kaart_k, m.LEFT), label("lamp", kaart_l, m.RIGHT))
        uren = m.ValueTracker(0)
        stip = m.Dot(radius=0.09, color=ELEKTRON_KLEUR).add_updater(
            lambda s: s.move_to(kaart[1].point_from_proportion(min(uren.get_value() / 3, 1))))
        d = zeg(self, "Loopt er stroom, dan schuiven die elektronen allemaal een kant op. Maar heel langzaam: "
                      "gemiddeld maar een paar honderdste millimeter per seconde.")
        self.hud(kaart, stip)
        self.doe(d, m.FadeIn(volg), m.FadeIn(ring), m.FadeIn(kaart), m.FadeIn(stip), duur=1.5)

        klok = klokje(uren).move_to([1.8, 1.4, 0])
        d = zeg(self, "Een elektron dat bij het knopje vertrekt, doet er zo'n drie uur over om bij de lamp te komen.")
        self.play(*self.toon(klok), run_time=SNEL)
        self.play(uren.animate.set_value(3), run_time=max(d - SNEL, 4), rate_func=m.linear)  # 0,5 m / 0,05 mm/s ≈ 3 uur

        # ═══ Toch brandt de lamp meteen: de vraag ═══
        d = zeg(self, "Toch brandt de lamp binnen een fractie van een seconde.")
        kaart_l[2].set_fill(LICHT, 1)
        self.doe(d, m.Flash(kaart_l, color=LICHT, flash_radius=0.5), duur=SNEL)
        vraag = tekst("Hoe kan de lamp meteen aan,\nals elektronen zo traag zijn?", KOP + 4)
        vraag_kader = m.VGroup(vraag, kader(vraag))
        d = zeg(self, "Hoe kan dat?")
        self.stop_ambient_camera_rotation()
        weg = [ionen, vrij, volg, ring, kaart, stip, klok]
        self.play(*(m.FadeOut(x) for x in weg), run_time=SNEL)
        for x in weg:
            x.clear_updaters()
        self.remove(*weg)
        self.doe(d - SNEL, *self.toon(vraag_kader))
        d = zeg(self, "Denk je het antwoord al te weten? Pauzeer even en probeer het voor jezelf te formuleren.")
        self.wait(d + 1)
        d = zeg(self, "Zo niet, geen probleem: dat is precies waar we naartoe werken. "
                      "Straks, bij de waterkring, komt het antwoord.")
        self.wait(d)

        # ═══ De reeks: het schema uit de video's, met het overzicht ═══
        self.set_camera_orientation(phi=0, theta=-90 * m.DEGREES, zoom=0.9, frame_center=[1.9, 0, Z], focal_distance=400)
        sch = schema()
        tempo = m.ValueTracker(2 * LUS.lengte / int(LUS.lengte / 0.3))  # zelfde tempo als in 03_stroom.py
        pijlen = maskeer(lus_pijltjes(tempo), [MASKER_BRON, MASKER_LAMP], m.ValueTracker(1))
        lijst = m.VGroup(*(m.VGroup(m.Dot(radius=0.08, color=k), tekst(f"{n}  {s}", LABEL)).arrange(m.RIGHT, buff=0.25)
                           for n, (s, k) in enumerate(ONDERWERPEN, 1)))
        lijst.arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.22).to_edge(m.RIGHT, buff=0.8).shift(0.4 * m.UP)
        d = zeg(self, "In deze reeks bouwen we elektriciteit op vanaf de grond.")
        self.play(m.FadeOut(vraag_kader), run_time=SNEL)
        self.doe(d - SNEL, m.FadeIn(sch["min_"]), m.FadeIn(sch["plus"]), m.FadeIn(sch["symbolen"]),
                 m.FadeIn(sch["gloed"]), m.FadeIn(sch["labels"]), m.FadeIn(pijlen))
        d = zeg(self, "Eerst lading, de waterkring en stroom. Dan spanning en weerstand.")
        self.na_elkaar(lijst[:5], d)
        d = zeg(self, "Daarna schakelingen in serie en parallel, vermogen, sensoren, en de elektriciteit in je eigen huis.")
        self.na_elkaar(lijst[5:], d)
        d = zeg(self, "Aan het eind kun je elke schakeling op het vwo-examen ontleden, en snap je ook waarom het werkt.")
        self.doe(d, m.Indicate(sch["symbolen"][1], color=LICHT, scale_factor=1.15))

        # ═══ Naar zwart: in de film volgt het Nabla-logo (assets/Intro.mov) ═══
        zeg(self, "")
        pijlen.clear_updaters()
        self.play(*(m.FadeOut(x) for x in (*sch.values(), pijlen, *lijst)), run_time=NORMAAL)
        self.wait(0.5)
