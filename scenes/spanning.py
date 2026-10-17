"""Spanning als hoogte: het schema uit stroom.py wordt 3D; de hoogte van elk punt laat zien hoe 'hoog' de stroom daar zit.

De batterij tilt omhoog (− onder, + boven), de draden zijn vlak, de lamp is een helling naar beneden (weerstand).
De stroompijltjes lopen overal even snel: de stroomsterkte verandert niet. Een spanningsmeter staat parallel
en meet het hoogteverschil tussen twee punten: 1,5 V over de lamp, 0 V over een stuk draad.

Run vanuit de repo-root:  python -m manimgx render scenes/spanning.py -o videos/Spanning.mp4
"""
import numpy as np
import manimgx as m
from stijl import *
import kring_3d_naar_2d as kr
import waterkring as wk
import stroom as st  # als modules: anders telt deze file meer dan één scène

Z, LUS, H = kr.Z, wk.LUS, 1.0   # H: hoogte die de batterij geeft (1,5 V)
BRON_HALF = 0.1                 # de batterij stijgt tussen de platen (y = −0,1 … 0,1)
LINKS_ZONE, RECHTS_ZONE = kr.LINKS + 0.6, kr.RECHTS - 0.6
# De lamp (symbool van LENGTE lang, y = −0,6 … 0,6) kantelt als stijf geheel: hoek α met sin α = H / LENGTE,
# zodat zijn polen precies op hoogte H en 0 uitkomen. Zo blijft de cirkel rond in plaats van uitgerekt.
SIN_A = H / LENGTE
COS_A = np.sqrt(1 - SIN_A ** 2)
OVERGANG = 0.4  # draadstuk buiten de lamp waarover de kanteling geleidelijk overgaat (draden en pijltjes sluiten aan)


def in_3d(p):
    """Waar een punt van het platte schema in de 3D-kring komt: de hoogte = hoe 'hoog' de stroom daar zit."""
    x, y, z = p
    if x < LINKS_ZONE:   # linkerzijde met de batterij: stijgt tussen de platen, − onder, + boven
        return np.array([x, y, z + H * np.clip((y + BRON_HALF) / (2 * BRON_HALF), 0, 1)])
    if x > RECHTS_ZONE:  # rechterzijde met de lamp: gekantelde helling naar beneden
        half = LENGTE / 2
        if abs(y) <= half:
            return np.array([x, y * COS_A, z + H / 2 + y * SIN_A])
        krimp = half * (1 - COS_A) * np.clip(1 - (abs(y) - half) / OVERGANG, 0, 1)
        return np.array([x, y - np.sign(y) * krimp, z + (H if y > 0 else 0)])
    return np.array([x, y, z + (H if y > 0 else 0)])  # achterste draad boven, voorste (met stroommeter) onder


def til(p, t):
    p = np.asarray(p, float)
    return p + t * (in_3d(p) - p)


def stroompijlen3d(tempo, naar_3d, afstand=0.6):
    """Witte driehoekjes (+ → lamp → −) die de hoogte volgen: op de helling kantelen ze mee.
    naar_3d(punt) zet een punt van het platte schema op zijn plek in 3D."""
    pijlen = m.VGroup(*(m.VMobject().set_fill(WIT, 0).set_stroke(width=0) for _ in range(int(LUS.lengte / afstand))))

    def zet(p, s):
        a, b = LUS.punt(s), LUS.punt(s - 1e-3)  # op weg naar kleinere s
        d = (b - a) / np.linalg.norm(b - a)
        n = np.array([-d[1], d[0], 0])
        hoeken = [a + 0.08 * d, a - 0.05 * d + 0.06 * n, a - 0.05 * d - 0.06 * n]
        p.set_points_as_corners([naar_3d(q) for q in hoeken + hoeken[:1]])
    return wk.stromer(pijlen, tempo, zet, richting=-1)


def maatlat(x, y, tekst_, kleur=U_KLEUR, links=False):
    """Verticale lat van hoogte 0 tot H met streepjes en een staand label: het hoogteverschil U."""
    lat = m.VGroup(m.Line([x, y, Z], [x, y, Z + H]),
                   *(m.Line([x - 0.1, y, z], [x + 0.1, y, z]) for z in (Z, Z + H))).set_stroke(kleur, 4)
    lbl = tekst(tekst_, LABEL, kleur).rotate(m.PI / 2, m.RIGHT)  # rechtop, naar de camera (−y)
    lbl.move_to([x + (-0.35 if links else 0.35), y, Z + H / 2])
    return m.VGroup(lat, lbl)


def staand(mob):
    """Van het xy-vlak naar het xz-vlak, rechtop naar de camera gericht."""
    return mob.rotate(m.PI / 2, m.RIGHT, about_point=m.ORIGIN)


class Spanning(m.ThreeDScene):
    def construct(self):
        self.add(*kr.zon_en_schemer())
        hud = self.add_fixed_in_frame_mobjects
        opgetild = m.ValueTracker(0)
        tempo = m.ValueTracker(2 * LUS.lengte / int(LUS.lengte / 0.3))  # zelfde tempo als in stroom.py

        # ── Begin: het schema waarop stroom.py eindigt (bovenaanzicht zonder perspectief) ──
        self.set_camera_orientation(phi=0, theta=-90 * m.DEGREES, zoom=1.4, frame_center=[-0.5, 0, Z],
                                    focal_distance=400)
        sch = st.schema(met_meter=True)
        bron_s, lamp_s, meter_s = sch["symbolen"]
        maskers = [st.MASKER_BRON, st.MASKER_LAMP, st.MASKER_METER]
        pijlen = st.maskeer(stroompijlen3d(tempo, lambda q: til(q, opgetild.get_value())), maskers, m.ValueTracker(1))
        self.add(sch["gloed"], *sch["min_"], sch["plus"], sch["symbolen"], sch["labels"], pijlen)

        d = zeg(self, "We gaan verder met onze kring, met de stroommeter erin.")
        self.wait(d)

        # ── De kring krijgt hoogte ──
        schemadelen = [bron_s, lamp_s, meter_s, *sch["min_"], sch["plus"]]
        for mob in schemadelen:
            plat = mob.copy()
            mob.add_updater(lambda x, plat=plat: x.become(plat.copy().apply_function(
                lambda p: til(p, opgetild.get_value()))))
        d = zeg(self, "Tot nu toe lag de kring plat. Nu geven we elk punt van de kring een hoogte.")
        self.play(m.FadeOut(sch["labels"]), m.FadeOut(sch["gloed"]), run_time=SNEL)
        self.move_camera(phi=65 * m.DEGREES, theta=-55 * m.DEGREES, zoom=1.1, frame_center=[-0.4, 0, 0.8],
                         focal_distance=20, added_anims=[opgetild.animate.set_value(1)], run_time=max(d - SNEL, 3))
        for mob in schemadelen:
            mob.clear_updaters()  # opgetild staat op 1: vorm ligt vast

        d = zeg(self, "De batterij tilt de stroom omhoog: de min-kant ligt onderaan, de plus-kant bovenaan.")
        self.move_camera(theta=-35 * m.DEGREES, frame_center=[kr.LINKS + 0.5, 0, 0.8], zoom=1.5,
                         added_anims=[m.Indicate(bron_s, color=U_KLEUR)], run_time=d)
        d = zeg(self, "Daarna loopt de stroom over een vlakke draad naar de lamp. Daar gaat het omlaag: "
                      "de lamp is een helling, omdat hij weerstand heeft.")
        self.move_camera(theta=-70 * m.DEGREES, frame_center=[kr.RECHTS - 0.3, 0, 0.8], zoom=1.5,
                         added_anims=[m.Indicate(lamp_s, color=LICHT)], run_time=d)
        d = zeg(self, "Onderaan loopt de stroom vlak terug naar de batterij, die hem weer omhoog tilt. "
                      "Net als bij het water: de pomp tilt het op, en in het waterrad valt het weer naar beneden.")
        self.move_camera(theta=-55 * m.DEGREES, frame_center=[-0.4, 0, 0.8], zoom=1.1, run_time=d)

        # ── De stroomsterkte verandert niet ──
        d = zeg(self, "Let op: de stroomsterkte verandert nergens. Overal in de kring gaan er per seconde evenveel "
                      "pijltjes langs, ook op de helling. De stroommeter wijst nog steeds hetzelfde aan.")
        self.play(m.Indicate(meter_s, color=I_KLEUR), run_time=min(d, 2))
        self.wait(max(d - 2, 0))
        # punt gemaakt: de stroommeter gaat eruit, de voorste draad wordt weer één stuk
        dicht = draad([st.METER_X - LENGTE / 2, -kr.HALF, Z], [st.METER_X + LENGTE / 2, -kr.HALF, Z]).set_stroke(WIT, 3)
        maskers.remove(st.MASKER_METER)
        self.play(m.FadeOut(meter_s), m.FadeIn(dicht), run_time=NORMAAL)

        # ── Spanning = hoogteverschil ──
        lat_bron = maatlat(kr.LINKS - 0.6, 0, "U", links=True)
        d = zeg(self, "Hoe hoog de batterij de stroom optilt, noemen we de spanning U. "
                      "Die meet je in volt, V. Een AA-batterij geeft 1,5 volt.")
        aflezing = st.paneel(waarde("U", 1.5, "V"), hoek=m.UR)
        hud(aflezing)
        self.play(m.Create(lat_bron), m.FadeIn(aflezing), run_time=d)

        # ── De spanningsmeter: parallel, tikt twee punten aan ──
        x_m = kr.RECHTS + 1.3
        vm = staand(plaats(meter("V"), [0, LENGTE / 2, 0], [0, -LENGTE / 2, 0])).scale(0.7).move_to([x_m, 0, Z + H / 2])
        boven, onder = til([kr.RECHTS, 0.8, Z], 1), til([kr.RECHTS, -0.8, Z], 1)  # net voor en net na de lamp
        draad_boven = draad(pool_a(vm), [x_m, 0, Z + H], [x_m, boven[1], Z + H], boven).set_stroke(WIT, 3)
        draad_onder = draad(pool_b(vm), [x_m, 0, Z], [x_m, onder[1], Z], onder).set_stroke(WIT, 3)
        contacten = m.VGroup(knoop(boven), knoop(onder))
        lat_lamp = maatlat(kr.RECHTS + 0.55, 0, "U")

        d = zeg(self, "Met een spanningsmeter meet je het hoogteverschil tussen twee punten.")
        self.move_camera(theta=-62 * m.DEGREES, frame_center=[0.6, 0, 0.8], zoom=1.25, added_anims=[m.FadeIn(vm)],
                         run_time=d)
        d = zeg(self, "Je zet hem niet ín de kring, maar ernaast: met zijn twee draden tikt hij twee punten aan. "
                      "Hier: net voor en net na de lamp.")
        self.play(m.Create(draad_boven), m.Create(draad_onder), m.FadeIn(contacten), run_time=d)
        d = zeg(self, "Hij meet 1,5 volt: de lamp laat de stroom precies zo ver zakken als de batterij hem optilde.")
        self.play(m.FadeOut(lat_bron), m.Create(lat_lamp), m.Indicate(aflezing, color=U_KLEUR), run_time=d)

        # ── Twee punten op dezelfde draad: geen hoogteverschil ──
        # de spanningsmeter verhuist: plat op tafel vóór de voorste draad, met twee korte draadjes naar die draad
        yv = -kr.HALF - 0.55
        vm_plat = plaats(meter("V"), [0.3, yv, Z], [1.1, yv, Z]).scale(0.7)  # horizontaal, V leesbaar van boven
        a, b = [pool_a(vm_plat)[0], -kr.HALF, Z], [pool_b(vm_plat)[0], -kr.HALF, Z]  # recht boven de polen
        draadjes = m.VGroup(draad(pool_a(vm_plat), a), draad(pool_b(vm_plat), b)).set_stroke(WIT, 3)
        stuk = m.Line(a, b).set_stroke(U_KLEUR, 6)
        nul = staand(tekst("U = 0 V", LABEL, U_KLEUR)).move_to([(a[0] + b[0]) / 2, -kr.HALF + 0.1, Z + 0.35])
        d = zeg(self, "Meet je tussen twee punten op dezelfde draad, dan is er geen hoogteverschil: "
                      "de spanningsmeter geeft 0 volt.")
        # overvloeien in plaats van vervormen: oude plek weg, nieuwe plek erbij
        self.move_camera(theta=-72 * m.DEGREES, frame_center=[0.7, -kr.HALF - 0.3, 0.3], zoom=1.6, added_anims=[
            m.FadeOut(lat_lamp), m.FadeOut(vm), m.FadeOut(draad_boven), m.FadeOut(draad_onder), m.FadeOut(contacten),
            m.FadeIn(vm_plat), m.FadeIn(draadjes), m.FadeIn(m.VGroup(knoop(a), knoop(b)))], run_time=d * 0.6)
        self.play(m.Create(stuk), m.FadeIn(nul),
                  m.Transform(aflezing[1][0], waarde("U", 0, "V", decimalen=0).move_to(aflezing[1][0], aligned_edge=m.LEFT)),
                  run_time=d * 0.4)

        # ── Het symbool ──
        d = zeg(self, "In een schema teken je de spanningsmeter als een cirkel met een V erin.")
        self.move_camera(theta=-62 * m.DEGREES, frame_center=[0.6, 0, 0.8], zoom=1.25,
                         added_anims=[m.FadeOut(stuk), m.FadeOut(nul), m.Indicate(vm_plat, color=U_KLEUR)], run_time=d)
        zeg(self, "")
        self.wait(2)
