"""Video 1 – De waterkring: waarom brandt de lamp pas als de kring gesloten is? Daarna: het schakelschema.

Didactiek: voorspellen → waarnemen → verklaren (POE), daarna een analogie met expliciete vertaaltabel
(lamp = waterrad, batterij = pomp, draden = buizen, elektronen = water; het water stroomt andersom dan de
elektronen), twee misconcepties ("de lamp verbruikt elektronen", "elektronen moeten eerst helemaal rondreizen"),
terug naar de echte kring en een samenvatting. Dan de overgang naar het schema: de camera gaat naar het
bovenaanzicht, batterij en lamp vloeien ter plekke over in hun symbool en de draden worden rechte lijnen.

Run vanuit de repo-root:  python -m manimgx render scenes/02_waterkring.py -o videos/Waterkring.mp4
"""
import numpy as np
import manimgx as m
from bouwstenen import *


def plat_label(s, x, y, kleur=TEKST):
    """Tekst plat op tafel, leesbaar van schuin boven."""
    return tekst(s, KOP, kleur).move_to([x, y, Z + 0.01])


class Waterkring(Les):
    def construct(self):
        s = self.waterdeel()
        self.schemadeel(s)

    def waterdeel(self):
        """Het hele waterkring-verhaal; eindigt bij de echte, brandende kring met de samenvatting in beeld.
        Geeft de objecten terug die schemadeel() nodig heeft."""
        self.add(*zon_en_schemer())
        tempo = m.ValueTracker(0)

        def echte_kring():
            lamp3d, beugel, bat = opstelling()
            omtrek_lamp = m.always_redraw(lambda: m.VGroup(*(d.omtrek(self.camera.get_theta()) for d in lamp3d)))
            omtrek_bat = m.always_redraw(lambda: bat.omtrek(self.camera.get_phi(), self.camera.get_theta()))
            lamp_delen = m.Group(*(d.vlak for d in lamp3d), *(d.ringen for d in lamp3d), beugel, omtrek_lamp)
            bat_delen = m.Group(bat.d.vlak, bat.d.ringen, omtrek_bat)
            return lamp3d, lamp_delen, bat_delen

        def weg(groep):
            for x in groep:
                x.clear_updaters()  # always_redraw-omtrek zou anders terugkomen
            return m.FadeOut(groep)

        self.set_camera_orientation(phi=65 * m.DEGREES, theta=-60 * m.DEGREES, zoom=1.1, frame_center=[-0.5, 0, 1.3])
        lamp3d, lamp_delen, bat_delen = echte_kring()
        g = m.ValueTracker(0)
        licht, halo = gloeiende_peer(lamp3d, g)
        min_ = lijn(*PAD[:4])   # − → lamp (voorkant)
        plus = lijn(*PAD[4:])   # lamp → + (achterkant): deze komt pas later
        e = elektronen_in_kring(tempo)
        w = waterdeeltjes(tempo)  # aparte deeltjes: water stroomt andersom dan de elektronen
        op_min_draad = [b for b in e if b.get_center()[1] < 0]  # bolletjes op de draad die er al ligt
        self.add(lamp_delen, bat_delen, licht, halo, e, w)

        # ── 1. Voorspellen ──
        d = zeg(self, "We sluiten een lamp met één koperdraad aan op een batterij.")
        self.move_camera(theta=-68 * m.DEGREES, added_anims=[m.Create(min_)], run_time=d)
        vraag = kaart("Voorspel: brandt de lamp?")
        self.hud(vraag)
        d = zeg(self, "Voorspel eerst zelf: gaat de lamp branden? Pauzeer de video en kies: ja of nee.")
        self.play(m.FadeIn(vraag), run_time=SNEL)
        self.wait(d - SNEL + 2)  # tijd om te pauzeren

        # ── 2. Waarnemen ──
        d = zeg(self, "De lamp blijft uit.")
        self.move_camera(theta=-74 * m.DEGREES, zoom=1.25, frame_center=[0.5, 0, 1.8],
                         added_anims=[m.FadeOut(vraag)], run_time=d)

        # ── 3. Verklaren ──
        d = zeg(self, "In de draad zitten vrije elektronen, maar ze kunnen nergens heen: de weg terug naar de batterij ontbreekt.")
        self.move_camera(theta=-62 * m.DEGREES, zoom=1.4, frame_center=[-0.5, -1, 0.4],
                         added_anims=[b.animate.set_fill(opacity=1) for b in op_min_draad], run_time=d)
        d = zeg(self, "Leggen we een tweede draad, dan is de kring gesloten. Nu kunnen de elektronen rondgaan, en de lamp brandt.")
        self.move_camera(zoom=1.1, frame_center=[-0.5, 0, 1.3], added_anims=[m.Create(plus)], run_time=d * 0.4)
        self.play(*(b.animate.set_fill(opacity=1) for b in e if b not in op_min_draad),
                  tempo.animate.set_value(0.6), g.animate.set_value(1), run_time=d * 0.2)
        self.wait(d * 0.4)

        # ── 4. Analogie: gesloten waterleiding, met vertaaltabel ──
        d = zeg(self, "Vergelijk de kring met een gesloten waterleiding.")
        self.move_camera(phi=55 * m.DEGREES, theta=-55 * m.DEGREES, zoom=1.4, frame_center=[-0.5, 0, 0.6],
                         added_anims=[*(b.animate.set_fill(opacity=0) for b in e),
                                      *(b.animate.set_fill(opacity=1) for b in w)], run_time=d)  # elektronen → water
        rad, p = waterrad(tempo), pomp(tempo)
        tabel = kaart("lamp  →  waterrad", "batterij  →  pomp", "draden  →  buizen",
                      tekst("elektronen  →  water", LABEL, t2c={"elektronen": ELEKTRON_KLEUR, "water": WATER_KLEUR}))
        d = zeg(self, "De lamp is een waterrad,")
        halo.clear_updaters()
        self.play(weg(lamp_delen), m.FadeOut(halo), m.FadeIn(rad), *self.toon(tabel[1], tabel[0][0]), run_time=d)
        licht.intensity = 0
        d = zeg(self, "de batterij is een pomp,")
        self.play(weg(bat_delen), m.FadeIn(p), *self.toon(tabel[0][1]), run_time=d)
        d = zeg(self, "de draden zijn de buizen en de elektronen zijn het water.")
        self.play(*self.toon(tabel[0][2]), run_time=d / 2)
        self.play(*self.toon(tabel[0][3]), run_time=d / 2)
        d = zeg(self, "Eén ding valt op: het water stroomt precies de andere kant op dan de elektronen. "
                      "Waarom we dat zo tekenen, zie je zo meteen.")
        self.wait(d)

        # ── 5. Misconceptie: "eerst moet het water helemaal rondreizen" ──
        d = zeg(self, "Belangrijk: de buizen zitten al vol water. Kijk wat er gebeurt als de pomp stopt…")
        self.play(tempo.animate.set_value(0), run_time=d)
        d = zeg(self, "…en weer aangaat. Hij duwt overal tegelijk: het rad draait meteen, ook al is het water zelf traag.")
        self.play(tempo.animate.set_value(0.6), run_time=0.3)
        self.wait(d - 0.3)

        # ── 6. Misconceptie: "de lamp verbruikt elektronen" ──
        d = zeg(self, "Het water raakt niet op in het rad: er stroomt evenveel uit als erin. "
                      "Zo raken ook de elektronen niet op in de lamp.")
        self.move_camera(phi=60 * m.DEGREES, theta=-25 * m.DEGREES, zoom=2.2, frame_center=[RECHTS, 0, 0.4],
                         added_anims=[m.FadeOut(x) for x in (*tabel[0], tabel[1])], run_time=d)

        # ── 7. Wat doet de pomp (batterij) dan wel? ──
        d = zeg(self, "De pomp duwt het water aan de ene kant naar buiten en zuigt het aan de andere kant weer aan.")
        self.move_camera(phi=50 * m.DEGREES, theta=-70 * m.DEGREES, zoom=2.2, frame_center=[LINKS, 0, Z],
                         run_time=d)
        mi = plat_label("−", LINKS - 0.4, -BAT_HALF - 0.15)
        pl = plat_label("+", LINKS - 0.4, BAT_HALF + 0.15)
        d = zeg(self, "Het water komt aan de plus-kant naar buiten. De elektronen doen precies het omgekeerde: "
                      "zij verlaten de batterij aan de min-kant en komen aan de plus-kant weer binnen.")
        self.play(m.FadeIn(mi), run_time=d / 2)
        self.play(m.FadeIn(pl), run_time=d / 2)

        # ── 8. Terug naar de echte kring + samenvatting ──
        d = zeg(self, "Terug naar onze lamp.")
        g.set_value(0)  # nieuwe lamp begint uit en gaat weer aan
        lamp3d, lamp_delen, bat_delen = echte_kring()
        licht2, halo2 = gloeiende_peer(lamp3d, g)
        rad.clear_updaters()
        p[2].clear_updaters()
        self.move_camera(phi=65 * m.DEGREES, theta=-60 * m.DEGREES, zoom=1.0, frame_center=[-1.6, 0, 1.6], added_anims=[
            m.FadeOut(rad), m.FadeOut(p), m.FadeIn(lamp_delen), m.FadeIn(bat_delen),
            *(b.animate.set_fill(opacity=0) for b in w), *(b.animate.set_fill(opacity=1) for b in e)],
            run_time=d + 1)  # kring naar rechts: ruimte voor kaart
        self.add(licht2, halo2)
        self.play(g.animate.set_value(1), run_time=SNEL)

        samenvatting = kaart("Alleen een gesloten kring geeft stroom.",
                             "De lamp verbruikt geen elektronen.",
                             "Draden zitten al vol: de lamp brandt meteen.", size=KLEIN + 2)
        d = zeg(self, "Samengevat: alleen in een gesloten kring stromen elektronen. De batterij duwt ze rond, "
                      "de lamp verbruikt ze niet, en omdat de draden al vol zitten, brandt de lamp meteen.")
        self.na_elkaar(samenvatting[0], d, *self.toon(samenvatting[1]))
        return dict(lamp_delen=lamp_delen, bat_delen=bat_delen, licht=licht2, halo=halo2, elektronen=e,
                    min_=min_, plus=plus, samenvatting=samenvatting, labels=m.VGroup(mi, pl))

    def schemadeel(self, s):
        """Overgang naar het schakelschema: bovenaanzicht, onderdelen worden symbolen, draden rechte lijnen."""
        # ── Waarom een schema? Eerst naar het bovenaanzicht ──
        d = zeg(self, "Zo'n kring telkens netjes natekenen is veel werk. "
                      "Daarom gebruiken we een schematische weergave: het schakelschema.")
        self.move_camera(phi=0, theta=-90 * m.DEGREES, zoom=1.4, frame_center=[-0.5, 0, Z], focal_distance=400,
                         added_anims=[*(m.FadeOut(x) for x in (*s["samenvatting"][0], s["samenvatting"][1])),
                                      m.FadeOut(s["labels"])], run_time=d)

        # ── Draden worden rechte lijnen, onderdelen worden symbolen ──
        bron_s, lamp_s = schema_symbolen()
        # zelfde looprichting als de 3D-draden (min_: − → lamp, plus: lamp → +), anders zwiept de Transform om
        min_s = draad(pool_b(bron_s), [LINKS, -HALF, Z], [RECHTS, -HALF, Z], pool_a(lamp_s))
        plus_s = draad(pool_b(lamp_s), [RECHTS, HALF, Z], [LINKS, HALF, Z], pool_a(bron_s))
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
        self.play(m.FadeIn(lamp_l), lamp_s[2].animate.set_fill(LICHT, 1), m.FadeIn(schemagloed(lamp_s)),
                  run_time=d)

        d = zeg(self, "Met zulke symbolen teken je elke stroomkring snel en overzichtelijk.")
        self.wait(d)
        zeg(self, "")
        self.wait(2)
