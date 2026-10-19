"""Onderdelen die de stroom regelen: schakelaar, LDR, NTC, PTC, diode en LED.

Eén kring: batterij (6 V) links, lamp (4 Ω) rechts, en bovenin een vrije plek waar de onderdelen één voor één
in- en uitvloeien. Het beeld volgt de tekst: steeds staat het besproken onderdeel in de kring, met een zon
(licht) of thermometer (temperatuur) erbij, en een paneel met de weerstand en de stroom die daaruit volgt
(I = U / (R + R_lamp)). Stroompijltjes: vaste snelheid, dichtheid = stroom (zoals in 06_serie_parallel.py);
bij geen stroom staan ze stil en vervagen ze. Voor de LED komt er een weerstand op de plek van de lamp; de LED
geeft alleen licht als er stroom loopt, en wisselt daarna van kleur (LED's bestaan in allerlei kleuren).

Run vanuit de repo-root:  python -m manimgx render scenes/08_sensoren.py -o videos/Sensoren.mp4
"""
import numpy as np
import manimgx as m
from bouwstenen import *


U = U_BRON                                # 6 V; de lamp heeft R_LAMP = 4 Ω
PLEK = ((-0.6, YT), (0.6, YT))            # de vrije plek bovenin, stroom loopt van links naar rechts
LED_KLEUREN = [ROOD, ORANJE, GEEL, GROEN, BLAUW, WIT]

# Weerstand als functie van licht (0 donker … 1 vol licht) en temperatuur (0 koud … 1 warm), in ohm
R_LDR = lambda licht: 20 * 0.1 ** licht           # donker 20 Ω, vol licht 2 Ω
R_NTC = lambda warm: 20 * 0.1 ** warm             # koud 20 Ω, warm 2 Ω
R_PTC = lambda warm: 2 * 10 ** warm               # koud 2 Ω, warm 20 Ω


def stroom_variabel(sch, route, I, zicht, I_max=1.5):
    """Pijltjes van + naar −, vaste snelheid, dichtheid = stroom I (ValueTracker, mag veranderen).
    De hele kring zit al vol met een vaste rij pijltjes (dichtheid bij I_max); daarvan is een gelijkmatig gespreid
    deel I / I_max zichtbaar. Gaat de stroom aan, dan lopen ze dus meteen overal, niet vanaf de batterij.
    Bij (bijna) geen stroom staan ze stil en vervagen ze."""
    n = int(route.L / (V_PIJL * Q_PIJL / I_max))  # zoveel pijltjes passen er bij de grootste stroom
    pijlen = m.VGroup(*(m.VMobject().set_fill(PIJL_KLEUR, 0).set_stroke(width=0) for _ in range(n)))
    pijlen.s = 0.0
    # Elk pijltje een vaste drempel (van-der-Corputreeks: 0, ½, ¼, ¾, …). Bij stroom I zijn de pijltjes met
    # drempel < I / I_max zichtbaar: altijd gelijkmatig gespreid, en bij minder stroom verdwijnen ze één voor één
    # (zacht), in plaats van dat het hele patroon elk beeld verspringt.
    drempel = [float(sum(((k >> b) & 1) / 2 ** (b + 1) for b in range(16))) for k in range(n)]

    def schuif(g, dt):
        i = I.get_value()
        g.s += dt * V_PIJL * np.clip(i / 0.05, 0, 1)   # bij geen stroom: stilstaan
        deel = np.clip(i / I_max, 0, 1)
        for k, p in enumerate(g):
            aan = np.clip((deel - drempel[k]) * n, 0, 1)  # het randpijltje vaagt zacht in of uit
            if aan <= 0:
                p.set_fill(opacity=0)
                continue
            plek, r, _, z = route.plek((g.s + k * route.L / n) % route.L)
            hoeken = pijlhoeken(plek, r)
            p.set_points_as_corners(hoeken + hoeken[:1])
            p.set_fill(opacity=aan * z * zicht.get_value() * sch.zicht.get_value() * np.clip(i / 0.05, 0, 1))
    pijlen.add_updater(schuif)
    schuif(pijlen, 0)
    return pijlen


def zon(midden, licht, zicht):
    """Zon die feller wordt met licht (0…1)."""
    z = m.VGroup()
    z.vorige = None

    def bij(mob):
        if (licht.get_value(), zicht.get_value()) == mob.vorige:
            return
        mob.vorige = (licht.get_value(), zicht.get_value())
        a = zicht.get_value()
        hart = m.Circle(radius=0.22).set_stroke(width=0).set_fill(GEEL, a * (0.25 + 0.75 * licht.get_value()))
        stralen = m.VGroup(*(m.Line(0.32 * np.array([np.cos(h), np.sin(h), 0]), 0.5 * np.array([np.cos(h), np.sin(h), 0]))
                             for h in np.linspace(0, m.TAU, 9)[:-1])).set_stroke(GEEL, 3, a * licht.get_value())
        mob.become(m.VGroup(hart, stralen).move_to(midden))
    z.add_updater(bij)
    bij(z)
    return z


def thermometer(midden, warm, zicht):
    """Thermometer waarvan de rode kolom stijgt met warm (0…1)."""
    t = m.VGroup()
    t.vorige = None

    def bij(mob):
        if (warm.get_value(), zicht.get_value()) == mob.vorige:
            return
        mob.vorige = (warm.get_value(), zicht.get_value())
        a = zicht.get_value()
        buis = m.RoundedRectangle(width=0.18, height=0.9, corner_radius=0.09).set_stroke(WIT, 2, a)
        bol = m.Circle(radius=0.14).set_stroke(WIT, 2, a).set_fill(ROOD, a).next_to(buis, m.DOWN, buff=-0.06)
        hoogte = 0.1 + 0.7 * warm.get_value()
        kolom = m.Rectangle(width=0.08, height=hoogte).set_stroke(width=0).set_fill(ROOD, a)
        kolom.move_to(bol.get_center() + [0, hoogte / 2, 0])
        mob.become(m.VGroup(buis, kolom, bol).move_to(midden))
    t.add_updater(bij)
    bij(t)
    return t


class Sensoren(Les):
    def construct(self):
        self.add(*zon_en_schemer())
        self.set_camera_orientation(phi=0, theta=-90 * m.DEGREES, zoom=0.85, frame_center=[2.6, 0, Z],
                                    focal_distance=400)

        # ── De kring met een vrije plek bovenin ──
        hoek = m.ValueTracker(30)
        plek = {naam: onderdeel("anders", *PLEK, U, U, naam, maak=maak, extra=extra)
                for naam, maak, extra in [("schakelaar", lambda: schakelaar_stand(hoek.get_value()), [hoek]),
                                          ("LDR", ldr, []), ("NTC", ntc, []), ("PTC", ptc, []),
                                          ("diode", diode, []), ("LED", led, [])]}
        plek["diode, omgedraaid"] = onderdeel("anders", PLEK[1], PLEK[0], U, U, "diode, omgedraaid", maak=diode)
        plek["LED, omgedraaid"] = onderdeel("anders", PLEK[1], PLEK[0], U, U, "LED, omgedraaid", maak=led)
        for naam, c in plek.items():
            c["zicht"].set_value(1 if naam == "schakelaar" else 0)
        lampje = onderdeel("lamp", (XR, 0.6), (XR, -0.6), U, 0)
        voor = onderdeel("weerstand", (XR, 0.6), (XR, -0.6), U, 0)  # beschermt de LED (stil in beeld)
        voor["zicht"].set_value(0)
        sch = Schakeling([batterij(), lampje, voor, *plek.values()],
                            [([(XL, 0.6), (XL, YT), PLEK[0]], U), ([PLEK[1], (XR, YT), (XR, 0.6)], U),
                             ([(XR, -0.6), (XR, YB), (XL, YB), (XL, -0.6)], 0)], [])
        route = Route([((XL, 0.6), U), ((XL, YT), U), (PLEK[0], None), (PLEK[1], U), ((XR, YT), U),
                          ((XR, 0.6), None), ((XR, -0.6), 0), ((XR, YB), 0), ((XL, YB), 0), ((XL, -0.6), None)])

        # ── Wat er in de kring gebeurt: één regelaar rekent de stroom uit en zet de lamp ──
        licht, warm = m.ValueTracker(1), m.ValueTracker(0)
        stand = {"R": lambda: None}   # weerstand van wat er op de plek staat; None = open kring
        I = m.ValueTracker(0)         # stroom zoals getoond (volgt de echte stroom met een fractie vertraging)
        pijl_zicht = m.ValueTracker(1)
        regelaar = m.VMobject()

        def regel(mob, dt):
            R = stand["R"]()
            doel = 0.0 if R is None else U / (R + R_LAMP)
            nieuw = I.get_value() + (doel - I.get_value()) * min(1, dt / 0.15)  # zacht, geen sprong
            I.set_value(doel if abs(doel - nieuw) < 1e-3 else nieuw)  # en dan echt tot rust: anders bouwt de kring
            # elk beeld opnieuw op, omdat de lamp steeds een fractie van helderheid verandert
            lampje["helder"].set_value(helderheid(I.get_value() * R_LAMP) * lampje["zicht"].get_value())
        regelaar.add_updater(regel)
        pijlen = stroom_variabel(sch, route, I, pijl_zicht)

        def waarden_paneel(naam):
            """Paneel rechtsboven met de weerstand van het onderdeel en de stroom; ververst als de getallen veranderen."""
            p = m.VGroup()
            p.vorige = None

            def bij(mob):
                R = stand["R"]()
                regels = (f"{naam}: R = " + ("oneindig" if R is None else f"{R:.0f} Ω"),
                          f"I = {I.get_value():.2f} A".replace(".", ","))
                if regels != mob.vorige:
                    mob.vorige = regels
                    mob.become(paneel(*(tekst(r, LABEL) for r in regels), hoek=m.UR))
            p.add_updater(bij)
            bij(p)
            return p

        icoon = (0, YT + 1.15)
        zon_zicht, thermo_zicht = m.ValueTracker(0), m.ValueTracker(0)
        de_zon = zon(np.array([*icoon, Z]), licht, zon_zicht)
        de_thermo = thermometer(np.array([*icoon, Z]), warm, thermo_zicht)
        self.add(regelaar, sch.geheel, pijlen, de_zon, de_thermo)

        def wissel(oud, nieuw, R, *extra, duur=NORMAAL):
            """Onderdeel op de plek vervangen; stand["R"] wordt de weerstand van het nieuwe onderdeel."""
            stand["R"] = R
            return [plek[oud]["zicht"].animate.set_value(0), plek[nieuw]["zicht"].animate.set_value(1), *extra]

        # ═══ Haakvraag ═══
        d = zeg(self, "Tot nu toe brandde de lamp gewoon zolang de kring dicht was. Maar hoe zet je hem aan en uit? "
                      "En hoe laat je een kring reageren op licht of warmte?")
        self.doe(d, sch.zicht.animate.set_value(1))

        # ═══ Schakelaar ═══
        d = zeg(self, "Het eenvoudigste onderdeel is de schakelaar. Staat hij open, dan is de kring onderbroken: "
                      "er loopt nergens stroom.")
        self.wait(d)
        stand["R"] = lambda: None if hoek.get_value() > 1 else 0.0
        d = zeg(self, "Klap je hem dicht, dan is de kring gesloten. Meteen loopt overal stroom, en de lamp brandt.")
        self.doe(d, hoek.animate.set_value(0), duur=NORMAAL)  # de arm klapt dicht; pas als hij dicht is loopt er stroom
        d = zeg(self, "Weer open: alles stopt. Een schakelaar zet de stroom dus aan of uit, verder niets.")
        self.doe(d, hoek.animate.set_value(30), duur=NORMAAL)

        # ═══ LDR ═══
        paneel_ldr = waarden_paneel("LDR")
        d = zeg(self, "Nu zetten we op die plek een LDR: een weerstand die gevoelig is voor licht. "
                      "Hoe meer licht erop valt, hoe kleiner zijn weerstand.")
        self.doe(d, *wissel("schakelaar", "LDR", lambda: R_LDR(licht.get_value())), zon_zicht.animate.set_value(1),
            *self.toon(paneel_ldr))
        d = zeg(self, "Voorspel: wat doet de lamp als het donker wordt? Denk even na.")
        self.wait(d + 1.5)
        d = zeg(self, "Het wordt donker: de weerstand van de LDR stijgt, de stroom daalt, en de lamp brandt zwakker.")
        self.doe(d, licht.animate.set_value(0), duur=3)
        d = zeg(self, "Komt er weer licht op, dan zakt de weerstand en wordt de lamp weer feller. "
                      "Het symbool: een weerstand met twee pijltjes van licht erop.")
        self.doe(d, licht.animate.set_value(1), duur=3)
        d = zeg(self, "Zo'n LDR zit bijvoorbeeld in een straatlantaarn die vanzelf aangaat als het donker wordt.")
        self.wait(d)

        # ═══ NTC ═══
        paneel_ntc = waarden_paneel("NTC")
        paneel_ldr.clear_updaters()
        d = zeg(self, "Een NTC reageert niet op licht, maar op temperatuur. Wordt hij warmer, dan daalt zijn "
                      "weerstand. De N staat voor negatief: warmer geeft minder weerstand.")
        self.play(*wissel("LDR", "NTC", lambda: R_NTC(warm.get_value())), zon_zicht.animate.set_value(0),
                  thermo_zicht.animate.set_value(1), m.FadeOut(paneel_ldr), *self.toon(paneel_ntc), run_time=NORMAAL)
        self.doe(d - NORMAAL, warm.animate.set_value(1), duur=3)
        d = zeg(self, "Je vindt een NTC in thermometers en thermostaten: de stroom vertelt hoe warm het is.")
        self.doe(d, warm.animate.set_value(0), duur=3)

        # ═══ PTC ═══
        paneel_ptc = waarden_paneel("PTC")
        paneel_ntc.clear_updaters()
        d = zeg(self, "Een PTC doet precies het omgekeerde. De P staat voor positief: warmer geeft juist méér weerstand.")
        self.play(*wissel("NTC", "PTC", lambda: R_PTC(warm.get_value())), m.FadeOut(paneel_ntc), *self.toon(paneel_ptc),
                  run_time=NORMAAL)
        self.doe(d - NORMAAL, warm.animate.set_value(1), duur=3)
        d = zeg(self, "Handig als beveiliging: wordt een apparaat te heet, dan remt de PTC de stroom vanzelf af.")
        self.doe(d, warm.animate.set_value(0), duur=3)

        # ═══ Diode ═══
        paneel_diode = waarden_paneel("diode")
        paneel_ptc.clear_updaters()
        d = zeg(self, "Een diode laat de stroom maar in één richting door, zoals een terugslagklep in een waterleiding. "
                      "Staat hij in de doorlaatrichting, dan loopt de stroom gewoon.")
        self.play(*wissel("PTC", "diode", lambda: 0.0), thermo_zicht.animate.set_value(0), m.FadeOut(paneel_ptc),
                  *self.toon(paneel_diode), run_time=NORMAAL)
        self.wait(max(d - NORMAAL, 0))
        d = zeg(self, "Het symbool is een pijl met een streep: de pijl wijst de richting waarin de stroom door mag.")
        self.wait(d)
        d = zeg(self, "Draai je de diode om, dan staat hij in sperrichting: er loopt geen stroom meer.")
        self.doe(d, *wissel("diode", "diode, omgedraaid", lambda: None))
        d = zeg(self, "Zo beschermt een diode een apparaat als je de batterijen per ongeluk verkeerd om plaatst.")
        self.wait(d)

        # ═══ LED ═══
        paneel_diode.clear_updaters()
        kleur = m.ValueTracker(0)  # 0 … 5: welke kleur uit LED_KLEUREN (tussenin: vloeiend gemengd)
        led_midden = np.array([0, YT, Z])

        def led_kleur():
            k = kleur.get_value()
            i = min(int(k), len(LED_KLEUREN) - 2)
            return m.interpolate_color(m.ManimColor(LED_KLEUREN[i]), m.ManimColor(LED_KLEUREN[i + 1]), k - i)

        gloed = m.VGroup(*(m.Circle(radius=r, stroke_width=0).set_fill(ROOD, 0)
                           for r in np.linspace(0.25, 0.85, 8))).move_to(led_midden - [0, 0, 0.005])
        for i, ring in enumerate(gloed):  # licht alleen als er stroom door de (goed om staande) LED loopt
            ring.add_updater(lambda r, i=i: r.set_fill(
                led_kleur(), 0.12 * (1 - i / 8) * np.clip(I.get_value() / 0.3, 0, 1) * plek["LED"]["zicht"].get_value()))
        self.add(gloed)

        d = zeg(self, "Een LED is een diode die zelf licht geeft: een Light Emitting Diode. "
                      "Loopt er stroom door, dan geeft hij licht.")
        self.play(*wissel("diode, omgedraaid", "LED", lambda: 8.0), m.FadeOut(paneel_diode),
                  lampje["zicht"].animate.set_value(0), voor["zicht"].animate.set_value(1), run_time=NORMAAL)
        self.wait(max(d - NORMAAL, 0))
        d = zeg(self, "Maar net als een gewone diode laat hij de stroom maar in één richting door. "
                      "Draai je hem om, dan loopt er geen stroom, en blijft hij donker.")
        self.doe(d, *wissel("LED", "LED, omgedraaid", lambda: None))
        d = zeg(self, "De goede kant op: weer stroom, en weer licht.")
        self.doe(d, *wissel("LED, omgedraaid", "LED", lambda: 8.0))

        rij = m.VGroup(*(m.VGroup(*(m.Circle(radius=r, stroke_width=0).set_fill(k, 0.18 * (1 - j / 5))
                                    for j, r in enumerate(np.linspace(0.16, 0.42, 5))),
                                  m.Circle(radius=0.12, stroke_width=0).set_fill(k, 1))
                         for k in LED_KLEUREN)).arrange(m.RIGHT, buff=0.15)
        kleuren = paneel(tekst("LED's in allerlei kleuren", LABEL), rij, hoek=m.UR)
        d = zeg(self, "LED's bestaan in allerlei kleuren: rood, oranje, geel, groen, blauw. "
                      "En met rood, groen en blauw samen maak je zelfs wit licht, zoals in het scherm van je telefoon.")
        self.play(*self.toon(kleuren), run_time=SNEL)
        self.play(kleur.animate.set_value(len(LED_KLEUREN) - 1), run_time=max(d - SNEL, 3), rate_func=m.linear)
        d = zeg(self, "En omdat een LED bijna alle energie omzet in licht, is hij veel zuiniger dan een gloeilamp.")
        self.wait(d)

        # ═══ Samenvatting ═══
        samen = paneel(*(tekst(r, LABEL) for r in (
            "schakelaar: kring open of dicht", "LDR: meer licht → kleinere R", "NTC: warmer → kleinere R",
            "PTC: warmer → grotere R", "diode: stroom maar één kant op", "LED: een diode die licht geeft")),
            hoek=m.UR)
        d = zeg(self, "Samengevat:")
        self.play(m.FadeOut(kleuren), run_time=SNEL)
        self.hud(samen[0])
        self.na_elkaar(samen[1], max(d, 3), m.FadeIn(samen[0]))
        zeg(self, "")
        self.wait(3)
