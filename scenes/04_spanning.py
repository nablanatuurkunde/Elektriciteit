"""Spanning als hoogte: het schema uit 03_stroom.py wordt 3D; de hoogte van elk punt laat zien hoe 'hoog' de stroom daar zit.

De batterij tilt omhoog (− onder, + boven), de draden zijn vlak, de lamp is een helling naar beneden (weerstand).
De stroompijltjes lopen overal even snel: de stroomsterkte verandert niet. Een spanningsmeter staat parallel
en meet het hoogteverschil tussen twee punten: 1,5 V over de lamp, 0 V over een stuk draad.

Run vanuit de repo-root:  python -m manimgx render scenes/04_spanning.py -o videos/Spanning.mp4
"""
import numpy as np
import manimgx as m
from bouwstenen import *


class Spanning(Les):
    def construct(self):
        self.add(*zon_en_schemer())
        opgetild = m.ValueTracker(0)
        tempo = m.ValueTracker(2 * LUS.lengte / int(LUS.lengte / 0.3))  # zelfde tempo als in 03_stroom.py

        # ── Begin: het schema waarop 03_stroom.py eindigt (bovenaanzicht zonder perspectief) ──
        self.set_camera_orientation(phi=0, theta=-90 * m.DEGREES, zoom=1.4, frame_center=[-0.5, 0, Z],
                                    focal_distance=400)
        sch = schema(met_meter=True)
        bron_s, lamp_s, meter_s = sch["symbolen"]
        maskers = [MASKER_BRON, MASKER_LAMP, MASKER_METER]
        pijlen = maskeer(lus_pijltjes(tempo, lambda q: til(q, opgetild.get_value())), maskers, m.ValueTracker(1))
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
        self.move_camera(theta=-35 * m.DEGREES, frame_center=[LINKS + 0.5, 0, 0.8], zoom=1.5,
                         added_anims=[m.Indicate(bron_s, color=U_KLEUR)], run_time=d)
        d = zeg(self, "Daarna loopt de stroom over een vlakke draad naar de lamp. Daar gaat het omlaag: "
                      "de lamp is een helling, omdat hij weerstand heeft.")
        self.move_camera(theta=-70 * m.DEGREES, frame_center=[RECHTS - 0.3, 0, 0.8], zoom=1.5,
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
        dicht = draad([METER_X - LENGTE / 2, -HALF, Z], [METER_X + LENGTE / 2, -HALF, Z])
        maskers.remove(MASKER_METER)
        self.play(m.FadeOut(meter_s), m.FadeIn(dicht), run_time=NORMAAL)

        # ── Spanning = hoogteverschil ──
        lat_bron = hoogte_maatlat(LINKS - 0.6, 0, "U", links=True)
        d = zeg(self, "Hoe hoog de batterij de stroom optilt, noemen we de spanning U. "
                      "Die meet je in volt, V. Een AA-batterij geeft 1,5 volt.")
        aflezing = paneel(waarde("U", 1.5, "V"), hoek=m.UR)
        self.hud(aflezing)
        self.play(m.Create(lat_bron), m.FadeIn(aflezing), run_time=d)

        # ── De spanningsmeter: parallel, tikt twee punten aan ──
        x_m = RECHTS + 1.3
        vm = staand(plaats(meter("V"), [0, LENGTE / 2, 0], [0, -LENGTE / 2, 0])).scale(0.7).move_to([x_m, 0, Z + H / 2])
        boven, onder = til([RECHTS, 0.8, Z], 1), til([RECHTS, -0.8, Z], 1)  # net voor en net na de lamp
        draad_boven = draad(pool_a(vm), [x_m, 0, Z + H], [x_m, boven[1], Z + H], boven)
        draad_onder = draad(pool_b(vm), [x_m, 0, Z], [x_m, onder[1], Z], onder)
        contacten = m.VGroup(knoop(boven), knoop(onder))
        lat_lamp = hoogte_maatlat(RECHTS + 0.55, 0, "U")

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
        yv = -HALF - 0.55
        vm_plat = plaats(meter("V"), [0.3, yv, Z], [1.1, yv, Z]).scale(0.7)  # horizontaal, V leesbaar van boven
        a, b = [pool_a(vm_plat)[0], -HALF, Z], [pool_b(vm_plat)[0], -HALF, Z]  # recht boven de polen
        draadjes = m.VGroup(draad(pool_a(vm_plat), a), draad(pool_b(vm_plat), b))
        stuk = m.Line(a, b).set_stroke(U_KLEUR, 6)
        nul = staand(tekst("U = 0 V", LABEL, U_KLEUR)).move_to([(a[0] + b[0]) / 2, -HALF + 0.1, Z + 0.35])
        d = zeg(self, "Meet je tussen twee punten op dezelfde draad, dan is er geen hoogteverschil: "
                      "de spanningsmeter geeft 0 volt.")
        # overvloeien in plaats van vervormen: oude plek weg, nieuwe plek erbij
        self.move_camera(theta=-72 * m.DEGREES, frame_center=[0.7, -HALF - 0.3, 0.3], zoom=1.6, added_anims=[
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
