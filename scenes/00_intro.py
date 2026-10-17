"""Intro van de reeks (3D): waarom gaat de lamp meteen aan als elektronen zo traag zijn?

Assen: x naar rechts, y de diepte in (van de camera af), z omhoog.
Ondertitels, routekaartje, klok en onderwerpenlijst staan plat op het scherm.

Run vanuit de repo-root:  python -m manimgx render scenes/00_intro.py -o videos/Intro.mp4
"""
import numpy as np
import manimgx as m
from bouwstenen import *


MUUR_Y = 2.0      # voorkant van de achterwand
PLAFOND_Z = 3.4
VLOER_Z = -3.0


def rechtop(mob):
    """Zet een plat (xy-)object rechtop in het xz-vlak, met de voorkant naar de camera."""
    return mob.rotate(m.PI / 2, m.RIGHT)


def buis(*punten, dikte=0.035, kleur=WIT):
    return m.Group(*(mat(m.Line3D(a, b, thickness=dikte), 1, kleur, 0.5) for a, b in zip(punten, punten[1:])))


def kamer():
    vloer = mat(m.Prism(dimensions=[40, 12, 0.1]), 1, GEDEMPT, 0.9).move_to([0, -2.5, VLOER_Z])
    muur = mat(m.Prism(dimensions=[40, 0.2, 6.6]), 1, WIT, 0.9).move_to([0, MUUR_Y + 0.1, 0.2])
    plafond = mat(m.Prism(dimensions=[40, 12, 0.1]), 1, WIT, 0.9).move_to([0, -2.5, PLAFOND_Z + 0.05])
    plaat = mat(m.Prism(dimensions=[0.8, 0.12, 1.2]), 1, WIT, 0.4).move_to([-4.5, MUUR_Y - 0.06, 0])
    knop = mat(m.Prism(dimensions=[0.26, 0.16, 0.45]), 1, GEDEMPT, 0.4).move_to([-4.5, MUUR_Y - 0.18, -0.2])
    langs = [[-4.5, MUUR_Y - 0.05, 3.2], [2.5, MUUR_Y - 0.05, 3.2]]  # het stuk van 3 m
    snoer = buis([-4.5, MUUR_Y - 0.05, 0.6], *langs, [2.5, MUUR_Y - 0.05, PLAFOND_Z], [2.5, 0, PLAFOND_Z], [2.5, 0, 1.9])
    peer = mat(m.Sphere(radius=0.3, resolution=(24, 12)), 1, GEDEMPT, 0.3).move_to([2.5, 0, 1.6])
    return dict(vloer=vloer, muur=muur, plafond=plafond, plaat=plaat, knop=knop, snoer=snoer, peer=peer, langs=langs)


def hand3d():
    """Wijsvinger, handpalm en arm; de vinger wijst naar de muur (+y)."""
    vinger = mat(m.Cylinder(radius=0.07, height=0.6, direction=m.UP), 1, WIT, 0.7).move_to([0, -0.3, 0])
    palm = mat(m.Prism(dimensions=[0.55, 0.6, 0.3]), 1, WIT, 0.7).move_to([0.05, -0.85, -0.1])
    arm = mat(m.Cylinder(radius=0.2, height=4, direction=m.UP), 1, WIT, 0.7).move_to([0.05, -3.1, -0.15])
    return m.Group(vinger, palm, arm)


def koperdraad():
    """Uitvergrote draad langs de x-as: doorzichtige isolatie om een rooster van koperionen."""
    isolatie = mat(m.Cylinder(radius=1.7, height=16, direction=m.RIGHT, show_ends=False), 0.18, GEDEMPT, 0.4)
    ionen = m.Group(*(mat(m.Sphere(radius=0.13, resolution=(10, 6)), 1, GEDEMPT, 0.35, 0.9).move_to([x, y, z])
                      for x in np.arange(-7.2, 7.3, 0.8) for y in (-0.8, 0, 0.8) for z in (-0.8, 0, 0.8)))
    return m.Group(isolatie, ionen)


def zwerm(n, rng, straal=1.4, drift=0.06):
    """Elektronen die wild alle kanten op schieten en netto heel traag naar +x schuiven."""
    def punt():
        r, a = straal * np.sqrt(rng.uniform()), rng.uniform(0, m.TAU)
        return [rng.uniform(-7, 7), r * np.cos(a), r * np.sin(a)]
    e = m.Group(*(m.Sphere(radius=0.06, resolution=(8, 4)).set_fill(ELEKTRON_KLEUR, 1).set_stroke(width=0).move_to(punt()) for _ in range(n)))

    def beweeg(g, dt):
        for d in g:
            x, y, z = d.get_center() + [drift * dt, 0, 0] + rng.normal(0, 0.3 * np.sqrt(dt), 3)
            r = np.hypot(y, z)
            if r > straal:
                y, z = y * straal / r, z * straal / r
            d.move_to([(x + 7.5) % 15 - 7.5, y, z])
    e.add_updater(beweeg)
    return e


def klokje(uren):
    """Platte klok (voor op het scherm) waarvan wijzer en getal de ValueTracker `uren` volgen."""
    rand = m.Circle(radius=0.45, color=TEKST, stroke_width=3, fill_color=BG, fill_opacity=1)
    streepjes = m.VGroup(*(m.Line(0.36 * m.UP, 0.45 * m.UP, stroke_width=2, color=TEKST)
                           .rotate(-k * m.TAU / 12, about_point=m.ORIGIN) for k in range(12)))
    wijzer = m.Line(m.ORIGIN, 0.33 * m.UP, color=ACCENT, stroke_width=4)
    getal = tekst("0 uur", LABEL)
    klok = m.VGroup(rand, streepjes, wijzer, getal)
    getal.next_to(rand, m.RIGHT, buff=0.2)

    def volg(k):
        c = k[0].get_center()
        k[2].put_start_and_end_on(c, c + 0.33 * m.rotate_vector(m.UP, -m.TAU * uren.get_value()))
        k[3].become(tekst(f"{int(uren.get_value())} uur", LABEL).next_to(k[0], m.RIGHT, buff=0.2)
                    .add_background_rectangle(color=BG, opacity=0.85, buff=0.08))
    klok.add_updater(volg)
    return klok


def nabla_logo():
    # shortcut: nagebouwd logo; vervang door het echte logo (SVGMobject) zodra dat er is
    formules = m.VGroup(*(rechtop(formule(f, 40)).set_opacity(0.25).move_to(p) for f, p in [
        (r"U = I \cdot R", [-5, 4, 2.4]), (r"P = U \cdot I", [4.5, 4, 2.6]), (r"Q = I \cdot t", [-4, 4, -2.4]),
        (r"E = P \cdot t", [5, 4, -2.2]), (r"R = \rho \frac{l}{A}", [0.5, 4, -2.8]), (r"I = \frac{Q}{t}", [-0.5, 4, 3.0])]))
    strepen = m.Group(*(mat(m.Prism(dimensions=[0.45, 0.45, 2.4]), 1, k, 0.35).rotate(-25 * m.DEGREES, m.UP)
                        .move_to([-4.2 + 0.75 * i, 0, 0]) for i, k in enumerate([ROOD, ORANJE, GEEL, GROEN, BLAUW])))
    naam = m.VGroup(m.MathTex(r"\nabla", font_size=120, color=TEKST), tekst("Nabla", 80, weight="BOLD"))
    rechtop(naam.arrange(m.RIGHT, buff=0.3)).move_to([1.6, 0, 0])
    return formules, strepen, naam


class Intro(m.ThreeDScene):
    def construct(self):
        rng = np.random.default_rng(3)
        self.tone_mapping = "agx"
        self.bloom = 0.12
        hud = self.add_fixed_in_frame_mobjects

        # ── Donkere kamer: schakelaar om, lamp springt aan, beeld bevriest ──
        self.set_camera_orientation(phi=88 * m.DEGREES, theta=-78 * m.DEGREES, frame_center=[-1, 0, 0.2])
        k = kamer()
        lamplicht = m.PointLight([2.5, -0.1, 1.5], WIT, intensity=0, radius=25)
        gloei = m.PointLight([2.5, -0.9, 1.6], GEEL, intensity=0, radius=1.2)  # maakt de peer zelf fel
        schemer = m.AmbientLight(intensity=0.03)
        maanlicht = m.SunLight([-12, -1.5, 1], intensity=0.6, shadows=False)  # strijklicht: hand zichtbaar, muur blijft donker
        h = hand3d()
        h.shift([-4.5, -5, -0.25] - h[0].get_center())
        ruimte = m.Group(k["vloer"], k["muur"], k["plafond"], k["plaat"], k["knop"], k["snoer"], k["peer"])
        self.add(schemer, maanlicht, lamplicht, gloei, ruimte, h)

        d = zeg(self, "Je zet de schakelaar om en de lamp gaat aan.")
        top = h[0].get_boundary_point(m.UP)
        self.play(h.animate.shift([0, (MUUR_Y - 0.26) - top[1], 0]), run_time=d - 1.2)
        self.play(k["knop"].animate.shift(0.4 * m.OUT), h.animate.shift(0.4 * m.OUT), run_time=0.2)
        lamplicht.intensity, gloei.intensity, schemer.intensity = 9, 30, 0.25  # meteen aan, geen fade
        k["peer"].set_fill(GEEL)
        self.wait(1.0)

        d = zeg(self, "Meteen. Je denkt er nooit over na.")
        flits = m.FullScreenRectangle(fill_color=WIT, fill_opacity=0.35, stroke_width=0)
        hud(flits)  # het beeld bevriest
        self.play(m.FadeOut(flits), run_time=0.3)
        self.wait(d - 0.3)

        # ── Inzoomen op het snoer: 3 m ──
        d = zeg(self, "Maar hier zit iets vreemds.")
        midden = np.mean(k["langs"], axis=0)
        self.move_camera(phi=91 * m.DEGREES, theta=-90 * m.DEGREES, zoom=1.5, frame_center=midden + [0, 0, -0.8],
                         added_anims=[h.animate.shift(4 * m.DOWN)], run_time=d * 0.6)
        lijn = m.Line(*([p[0], p[2], 0] for p in k["langs"]))  # platte kopie van het stuk van 3 m
        accolade = m.Brace(lijn, m.DOWN, color=ZWART)
        maat = m.VGroup(accolade, tekst("3 m", KOP, ZWART).next_to(accolade, m.DOWN))
        rechtop(maat).move_to(midden + [0, -0.15, -0.55])  # op de muur, onder het snoer
        self.play(m.GrowFromCenter(maat[0]), m.FadeIn(maat[1]), run_time=d * 0.4)

        # ── De koperdraad in, tot we elektronen zien ──
        d = zeg(self, "Over een paar minuten gaan we uitrekenen hoe snel de elektronen in zo'n draad eigenlijk bewegen.")
        self.move_camera(zoom=80, frame_center=midden, added_anims=[m.FadeOut(maat)], run_time=1.5, rate_func=m.rush_into)
        self.remove(ruimte, h, lamplicht, gloei, maanlicht)
        schemer.intensity = 0.35
        zon = m.SunLight([-3, -4, 6], intensity=2.5)
        draad3d = koperdraad()
        e = zwerm(50, rng)
        self.add(zon)
        self.set_camera_orientation(phi=68 * m.DEGREES, theta=-62 * m.DEGREES, zoom=4, frame_center=m.ORIGIN)
        self.move_camera(zoom=1, added_anims=[m.FadeIn(draad3d), m.FadeIn(e)], run_time=1.5, rate_func=m.rush_from)
        self.begin_ambient_camera_rotation(rate=0.025)
        self.wait(d - 3)

        # Eén elektron volgen, op een routekaartje van schakelaar naar lamp
        d = zeg(self, "Dan blijkt dat een elektron dat bij de schakelaar vertrekt, er meer dan tien uur over doet om bij de lamp te komen.")
        volg = m.Sphere(radius=0.12, resolution=(12, 6)).set_fill(ELEKTRON_KLEUR, 1).set_stroke(width=0).move_to([-1, 0.3, 0.3])
        volg.add_updater(lambda v, dt: v.shift(0.05 * dt * m.RIGHT + rng.normal(0, 0.06 * np.sqrt(dt), 3)))
        ring = mat(m.Torus(major_radius=0.3, minor_radius=0.025, resolution=(24, 8)), 1, ACCENT, 0.4)
        ring.add_updater(lambda r: r.move_to(volg))
        kaart_s, kaart_l = schakelaar(open=False).scale(0.6), lamp().scale(0.6)
        kaart = m.VGroup(kaart_s, m.Line(3.5 * m.LEFT, 3.5 * m.RIGHT, color=DRAAD, stroke_width=STREEP), kaart_l)
        kaart.arrange(m.RIGHT, buff=0).move_to(3.45 * m.UP)
        kaart.add(label("schakelaar", kaart_s, m.LEFT), label("lamp", kaart_l, m.RIGHT))
        uren = m.ValueTracker(0)
        stip = m.Dot(radius=0.09, color=ELEKTRON_KLEUR).add_updater(
            lambda s: s.move_to(kaart[1].point_from_proportion(min(uren.get_value() / 11, 1))))
        hud(kaart, stip)
        self.move_camera(frame_center=volg, zoom=1.4, added_anims=[m.FadeIn(volg), m.FadeIn(ring), m.FadeIn(kaart)],
                         run_time=1.5)
        self.wait(d - 1.5)

        klok = klokje(uren).move_to([1.6, 1.1, 0])  # naast het elektron, dat midden in beeld blijft
        hud(klok)
        self.play(m.FadeIn(klok), run_time=0.5)
        self.play(uren.animate.set_value(10.99), run_time=4, rate_func=m.linear)  # 1 uur… 5 uur… 10 uur…

        # ── Toch brandt de lamp meteen ──
        d = zeg(self, "Toch brandt de lamp binnen een fractie van een seconde.")
        kaart_l[2].set_fill(LICHT, 0.9)
        self.play(m.Flash(kaart_l, color=LICHT, flash_radius=0.5), run_time=0.6)
        self.wait(d - 0.6)

        # ── De vraag, rechtop in de ruimte, met zwevende elektronen erachter ──
        d = zeg(self, "Hoe kan dat?")
        self.stop_ambient_camera_rotation()
        weg = [draad3d, e, volg, ring, kaart, stip, klok]
        self.play(*(m.FadeOut(x) for x in weg), run_time=d * 0.5)
        for x in weg:
            x.clear_updaters()
        self.remove(*weg, zon)
        vraag = tekst("Hoe kan de lamp meteen aan,\nals elektronen zo traag zijn?", KOP + 4)
        rand = kader(vraag)
        rechtop(m.VGroup(vraag, rand))
        diepte = m.Group(*(m.Sphere(radius=0.05, resolution=(8, 4)).set_fill(ELEKTRON_KLEUR, 0.6).set_stroke(width=0)
                           .move_to([rng.uniform(-9, 9), rng.uniform(2, 10), rng.uniform(-5, 5)]) for _ in range(80)))
        diepte.add_updater(lambda g, dt: g.shift(0.04 * dt * m.RIGHT))
        self.set_camera_orientation(phi=86 * m.DEGREES, theta=-96 * m.DEGREES, zoom=1, frame_center=m.ORIGIN)
        self.play(m.FadeIn(vraag, shift=0.3 * m.OUT), m.FadeIn(diepte), run_time=d * 0.5)
        self.move_camera(theta=-92 * m.DEGREES, added_anims=[m.Create(rand)], run_time=SNEL, rate_func=m.linear)

        d = zeg(self, "Als je het antwoord al denkt te weten: pauzeer even en probeer het voor jezelf te formuleren.")
        self.move_camera(theta=-86 * m.DEGREES, run_time=d, rate_func=m.linear)
        d = zeg(self, "Zo niet, geen probleem. Dat is precies waar we naartoe werken.")
        self.move_camera(theta=-82 * m.DEGREES, run_time=d, rate_func=m.linear)

        # ── Stroomschema op een tafel, routekaart van de reeks op het scherm ──
        d = zeg(self, "In deze reeks bouwen we elektriciteit op vanaf de grond.")
        self.play(m.FadeOut(vraag), m.FadeOut(rand), m.FadeOut(diepte), run_time=SNEL)
        diepte.clear_updaters()
        self.remove(diepte, vraag, rand)
        self.set_camera_orientation(phi=0, theta=-90 * m.DEGREES, zoom=1, frame_center=m.ORIGIN)
        tafel = mat(m.Prism(dimensions=[30, 30, 0.1]), 1, ZWART, 0.6).move_to([0, 0, -0.08])
        tafellicht = m.PointLight([SCHAKELING[0] + 2.2, SCHAKELING[1], 0.6], GEEL, intensity=0, radius=4)
        self.add(tafel, tafellicht)
        lb, rb, ro, lo = (SCHAKELING + np.array(v) for v in ([-2.2, 1.5, 0], [2.2, 1.5, 0], [2.2, -1.5, 0], [-2.2, -1.5, 0]))
        kring = m.VGroup(tak(lb, lo, bron()), tak(lb, rb, schakelaar()), tak(rb, ro, lamp()), m.VGroup(draad(ro, lo)))
        self.move_camera(phi=50 * m.DEGREES, theta=-80 * m.DEGREES, frame_center=[-0.6, 0.6, 0],
                         added_anims=[m.LaggedStart(*(m.Create(t) for t in kring), lag_ratio=0.4)], run_time=d - SNEL)

        onderwerpen = [("lading", Q_KLEUR), ("stroom", I_KLEUR), ("spanning", U_KLEUR), ("weerstand", R_KLEUR),
                       ("schakelingen", TEKST), ("sensoren", TEKST), ("energie", E_KLEUR), ("de stroomkring thuis", TEKST)]
        lijst = m.VGroup(*(m.VGroup(m.Dot(radius=0.08, color=kl), tekst(f"{n}  {s}", LABEL)).arrange(m.RIGHT, buff=0.25)
                           for n, (s, kl) in enumerate(onderwerpen, 1)))
        lijst.arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.28).move_to(4.4 * m.RIGHT + 0.4 * m.UP)

        d = zeg(self, "Eerst lading en stroom, dan spanning en weerstand.")
        hud(*lijst)
        lijst.set_opacity(0)
        self.play(m.LaggedStart(*(r.animate.set_opacity(1) for r in lijst[:4]), lag_ratio=0.5), run_time=d)
        d = zeg(self, "Daarna schakelingen, sensoren, energie, en uiteindelijk de stroomkring in je eigen huis.")
        self.play(m.LaggedStart(*(r.animate.set_opacity(1) for r in lijst[4:]), lag_ratio=0.5), run_time=d)

        d = zeg(self, "Aan het eind kun je elke schakeling op het vwo-examen ontleden,")
        self.play(m.Transform(kring[1][1], plaats(schakelaar(open=False), lb, rb)), run_time=SNEL)
        i = pijltjes_langs([lo, lb, rb, ro, lo])
        kring[2][1][2].set_fill(LICHT, 0.9)
        tafellicht.intensity = 3
        self.add(i)
        self.move_camera(theta=-72 * m.DEGREES, run_time=d - SNEL, rate_func=m.linear)
        d = zeg(self, "en je snapt ook waarom het werkt.")
        self.move_camera(theta=-66 * m.DEGREES, added_anims=[m.Indicate(kring[2][1], color=LICHT)], run_time=d,
                         rate_func=m.linear)

        # ── Logo: gekleurde balken schuiven de ruimte in ──
        zeg(self, "")
        self.play(m.FadeOut(m.Group(kring, i, tafel, lijst)), run_time=SNEL)
        i.clear_updaters()
        self.remove(kring, i, tafel, lijst, tafellicht)
        formules, strepen, naam = nabla_logo()
        self.add(m.SunLight([-4, -6, 5], intensity=3))
        self.set_camera_orientation(phi=84 * m.DEGREES, theta=-100 * m.DEGREES, zoom=1, frame_center=m.ORIGIN)
        self.play(m.FadeIn(formules), run_time=SNEL)
        for s in strepen:
            s.shift(9 * m.LEFT)
        self.move_camera(theta=-90 * m.DEGREES, phi=88 * m.DEGREES, added_anims=[
            m.LaggedStart(*(s.animate.shift(9 * m.RIGHT) for s in strepen), lag_ratio=0.12), m.Write(naam)], run_time=2)
        self.wait(2)
