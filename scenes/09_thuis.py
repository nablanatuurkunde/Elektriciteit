"""Video 9 – Elektriciteit in huis: groepen en zekering, aardlekschakelaar, motor en rendement, lampen vergelijken
en energie besparen, de kWh-meter en de opwekking van elektriciteit.

Haak: je zet de waterkoker, de magnetron en de föhn tegelijk aan en het is ineens donker. Stopcontacten zijn parallel
geschakeld (video 6): de stromen tellen op, I = P / U per apparaat; boven 16 A brandt de zekering door. De zekering
beschermt de draden, de aardlekschakelaar beschermt jou (verschil heen/terug > 30 mA). Daarna rendement
(η = P_nuttig / P_in, elektromotor), gloeilamp/spaarlamp/LED met evenveel licht, besparen in kWh en euro, de
kWh-meter, en waar de elektrische energie vandaan komt. Wisselspanning: geen stroompijltjes (de stroom keert om).

Run vanuit de repo-root:  python -m manimgx render scenes/09_thuis.py -o videos/Thuis.mp4
"""
import numpy as np
import manimgx as m
from bouwstenen import *


WX, YT, YB = -5.0, 0.6, -2.0       # bron links op x = -5; boven- en onderdraad
P_BOVEN, P_ONDER = 0.0, -1.2       # een staand onderdeel loopt van y = 0 naar y = -1,2
TAKKEN = (-1.8, 1.0, 3.8)          # x van de drie apparaten in de groep
PRIJS = 0.30                       # euro per kWh (afgerond)


def verticaal(soort, x, naam=None, maak=None, Vp=0, Vq=0):
    return onderdeel(soort, (x, P_BOVEN), (x, P_ONDER), Vp, Vq, naam, maak=maak)


def groep():
    """Stopcontact met een zekering en drie apparaten parallel (waterkoker, magnetron, föhn)."""
    bron_w = verticaal("wissel", WX, "230 V")
    heel = onderdeel("anders", (-4.2, YT), (-3.0, YT), 0, 0, "zekering 16 A", maak=zekering)
    door = onderdeel("anders", (-4.2, YT), (-3.0, YT), 0, 0, "zekering 16 A", maak=lambda: zekering(True))
    door["zicht"].set_value(0)
    apparaten = [verticaal("weerstand", x, n) for x, n in zip(TAKKEN, ("waterkoker", "magnetron", "föhn"))]
    x1, x2, x3 = TAKKEN
    draden = [([(WX, P_BOVEN), (WX, YT), (-4.2, YT)], 0), ([(-3.0, YT), (x3, YT), (x3, P_BOVEN)], 0),
              ([(x1, YT), (x1, P_BOVEN)], 0), ([(x2, YT), (x2, P_BOVEN)], 0),
              ([(x1, P_ONDER), (x1, YB)], 0), ([(x2, P_ONDER), (x2, YB)], 0),
              ([(x3, P_ONDER), (x3, YB), (WX, YB), (WX, P_ONDER)], 0)]
    knopen = [((x, y), 0) for x in (x1, x2) for y in (YT, YB)]
    return Schakeling([bron_w, heel, door, *apparaten], draden, knopen), heel, door, apparaten


def enkel(soort, naam, maak=None, bron_soort="wissel", U=0):
    """Bron links met één verbruiker rechts; geeft (schakeling, verbruiker, route)."""
    x = TAKKEN[-1]
    b = verticaal(bron_soort, WX, None if bron_soort == "bron" else "230 V", Vp=U)
    v = verticaal(soort, x, naam, maak=maak, Vp=U)
    sch = Schakeling([b, v], [([(WX, P_BOVEN), (WX, YT), (x, YT), (x, P_BOVEN)], U),
                              ([(x, P_ONDER), (x, YB), (WX, YB), (WX, P_ONDER)], 0)], [])
    route = Route([((WX, P_BOVEN), U), ((WX, YT), U), ((x, YT), U), ((x, P_BOVEN), None), ((x, P_ONDER), 0),
                   ((x, YB), 0), ((WX, YB), 0), ((WX, P_ONDER), None)])
    return sch, v, route


def balk(delen, x0, y, schaal, hoogte=0.32):
    """Liggende balk uit stukken (waarde, kleur), links beginnend op x0."""
    stukken, x = [], x0
    for waarde, kleur in delen:
        b = m.Rectangle(width=max(waarde * schaal, 1e-3), height=hoogte).set_stroke(width=0).set_fill(kleur, 1)
        stukken.append(b.move_to([x + waarde * schaal / 2, y, Z]))
        x += waarde * schaal
    return m.VGroup(*stukken)


def rijlabel(s, y, x=-1.4):
    return tekst(s, LABEL).move_to([x, y, Z], aligned_edge=m.RIGHT)


class Thuis(Les):
    def construct(self):
        self.add(*zon_en_schemer())
        self.set_camera_orientation(phi=0, theta=-90 * m.DEGREES, zoom=0.8, frame_center=[0, -0.4, Z],
                                    focal_distance=400)

        def rij(tex):
            return formule(komma(tex), size=FORMULE - 6)

        # ═══ Haak + groep met zekering ═══
        sch, heel, door, (koker, magn, fohn) = groep()
        self.add(sch.geheel)
        d = zeg(self, "Je zet de waterkoker aan, dan de magnetron, en dan de föhn. En ineens is het donker. "
                      "Wat is er gebeurd?")
        self.doe(d, sch.zicht.animate.set_value(1))
        d = zeg(self, "De stopcontacten in een kamer zitten samen in één groep, en zijn parallel geschakeld. "
                      "Elk apparaat krijgt dus 230 volt, en neemt zijn eigen stroom.")
        self.wait(d)

        def stroompaneel(tex):
            return paneel(rij(r"I = \frac{P}{U}"), rij(tex), hoek=m.UR)

        stroom = stroompaneel(r"I_{tot} = 0\ \mathrm{A}")

        def tot(tex):  # het hele paneel, zodat het kader meegroeit met de som
            return m.Transform(stroom, stroompaneel(tex))

        d = zeg(self, "Hoeveel stroom? Vermogen is spanning maal stroom, dus de stroom is het vermogen gedeeld door de "
                      "spanning. De waterkoker van 2000 watt neemt 2000 gedeeld door 230 is 8,7 ampère.")
        self.play(*self.toon(stroom), run_time=SNEL)
        self.doe(d - SNEL, koker["helder"].animate.set_value(1), tot(r"I_{tot} = 8,7\ \mathrm{A}"))
        d = zeg(self, "De magnetron van 1000 watt neemt er 4,3 ampère bij. Bij parallel tellen de stromen op: "
                      "samen 13 ampère.")
        self.doe(d, magn["helder"].animate.set_value(1), tot(r"I_{tot} = 8,7 + 4,3 = 13,0\ \mathrm{A}"))
        d = zeg(self, "En de föhn van 1500 watt nog eens 6,5 ampère. Samen bijna 20 ampère, door dezelfde draden.")
        self.doe(d, fohn["helder"].animate.set_value(1), tot(r"I_{tot} = 13,0 + 6,5 = 19,6\ \mathrm{A}"))
        d = zeg(self, "Dat is te veel: de draden zouden te heet worden. De zekering van deze groep laat maximaal "
                      "16 ampère door. Daarboven brandt hij door, of schakelt hij uit, en is de groep stroomloos.")
        self.play(heel["zicht"].animate.set_value(0), door["zicht"].animate.set_value(1), run_time=SNEL)
        self.doe(d - SNEL, *(a["helder"].animate.set_value(0) for a in (koker, magn, fohn)),
                 tot(r"I_{tot} = 0\ \mathrm{A}"))
        d = zeg(self, "Ook bij kortsluiting, die je eerder zag, wordt de stroom te groot en grijpt de zekering in. "
                      "De zekering staat in serie met de hele groep: alle stroom gaat erdoorheen.")
        self.doe(d, m.Indicate(stroom, color=ACCENT))
        d = zeg(self, "Een zekering beschermt dus de draden, tegen te veel stroom. Maar wie beschermt jou?")
        self.wait(d)

        # ═══ Aardlekschakelaar ═══
        sch_a, machine, _ = enkel("weerstand", "wasmachine")
        machine["helder"].set_value(1)
        xa = -3.6
        doos = m.VGroup(m.Rectangle(width=0.9, height=YT - YB + 0.6).move_to([xa, (YT + YB) / 2, Z]).set_stroke(TEKST, 3),
                        tekst("aardlek", LABEL).move_to([xa, YT + 0.65, Z]))
        xm = TAKKEN[-1]
        lek = m.VGroup(m.DashedLine([xm + 0.45, -0.6, Z], [xm + 1.2, -0.6, Z]).set_stroke(ACCENT, 3),
                       m.DashedLine([xm + 1.2, -0.6, Z], [xm + 1.2, -2.2, Z]).set_stroke(ACCENT, 3),
                       aarde([xm + 1.2, -2.2, Z]), tekst("via jou", LABEL, ACCENT).move_to([xm + 2.1, -1.3, Z]))
        def meetpaneel(terug):
            return paneel(rij(r"I_{heen} = 10,000\ \mathrm{A}"), rij(rf"I_{{terug}} = {terug}\ \mathrm{{A}}"), hoek=m.UR)

        meting = meetpaneel("10,000")
        self.add(sch_a.geheel)
        d = zeg(self, "Daarvoor is er de aardlekschakelaar. Die vergelijkt de stroom die het huis in gaat met de stroom "
                      "die terugkomt.")
        self.play(m.FadeOut(stroom), sch.zicht.animate.set_value(0), run_time=SNEL)
        self.remove(sch.geheel)
        self.doe(d - SNEL, sch_a.zicht.animate.set_value(1), m.Create(doos))
        d = zeg(self, "Normaal is dat precies evenveel: net als bij de waterkring raakt er onderweg niets op.")
        self.doe(d, *self.toon(meting))
        d = zeg(self, "Maar stel dat er in de wasmachine een draad loszit en jij het metaal aanraakt. Dan stroomt er "
                      "een beetje stroom via jouw lichaam naar de aarde. Die komt dus niet terug.")
        self.doe(d, m.Create(lek), m.Transform(meting, meetpaneel("9,970")))
        d = zeg(self, "Is het verschil 30 milliampère of meer, dan schakelt de aardlekschakelaar alles uit, binnen een "
                      "fractie van een seconde. De zekering beschermt de draden; de aardlekschakelaar beschermt jou.")
        self.doe(d, machine["helder"].animate.set_value(0), m.Indicate(doos, color=ACCENT))

        # ═══ Rendement: de elektromotor ═══
        sch_m, de_motor, route_m = enkel("anders", "motor", maak=motor, bron_soort="bron", U=6)
        aan_m = [m.ValueTracker(1)]
        pijlen_m = stroompijltjes(sch_m, [route_m], [1.0], m.ValueTracker(1.5), aan_m)
        self.add(sch_m.geheel, pijlen_m)
        rend = paneel(rij(r"P_{in} = U \cdot I = 6 \cdot 1,5 = 9,0\ \mathrm{W}"), rij(r"P_{nuttig} = 6,3\ \mathrm{W}"),
                      rij(r"\eta = \frac{P_{nuttig}}{P_{in}} = \frac{6,3}{9,0} = 0,70 = 70\%"), hoek=m.UR)
        stroomdiagram = m.VGroup(balk([(6.3, P_KLEUR), (2.7, ACCENT)], -7.0, 2.2, 0.75),
                                 tekst("beweging 6,3 W", KLEIN + 2, P_KLEUR).move_to([-4.6, 2.75, Z]),
                                 tekst("warmte 2,7 W", KLEIN + 2, ACCENT).move_to([-1.3, 2.75, Z]))
        d = zeg(self, "Apparaten zetten elektrische energie om in iets nuttigs, maar nooit helemaal. "
                      "Neem een elektromotor op een batterij van 6 volt, met een stroom van 1,5 ampère.")
        self.play(m.FadeOut(meting), m.FadeOut(doos), m.FadeOut(lek), sch_a.zicht.animate.set_value(0), run_time=SNEL)
        self.remove(sch_a.geheel)
        self.doe(d - SNEL, sch_m.zicht.animate.set_value(1))
        d = zeg(self, "Er gaat 6 maal 1,5 is 9 watt in. Daarvan wordt 6,3 watt beweging. De rest, 2,7 watt, wordt "
                      "warmte: de motor wordt warm.")
        self.doe(d, *self.toon(rend[0], rend[1][0], rend[1][1]), m.FadeIn(stroomdiagram))
        d = zeg(self, "Het rendement, eta, is het nuttige deel gedeeld door wat erin gaat. Hier 6,3 gedeeld door 9: "
                      "0,70, oftewel 70 procent. Met energie in plaats van vermogen werkt het precies zo.")
        self.doe(d, *self.toon(rend[1][2]))

        # ═══ Lampen vergelijken en energie besparen ═══
        lampen = [("gloeilamp", 60, lamp), ("spaarlamp", 12, lamp), ("LED", 8, led)]
        schaal = 0.09
        rijen = m.VGroup(*(m.VGroup(rijlabel(f"{naam}  {P} W", y), plaats(maak(), [-1.0, y, Z], [0.0, y, Z]).scale(0.6),
                                    balk([(3, LICHT), (P - 3, ACCENT)], 0.4, y, schaal))
                           for (naam, P, maak), y in zip(lampen, (2.0, 0.9, -0.2))))
        legenda_l = m.VGroup(tekst("licht", KLEIN + 2, LICHT).move_to([0.8, 2.65, Z]),
                             tekst("warmte", KLEIN + 2, ACCENT).move_to([2.6, 2.65, Z]))
        d = zeg(self, "Bij lampen zie je het verschil in rendement heel goed. Deze drie lampen geven evenveel licht.")
        aan_m[0].set_value(0)
        self.play(m.FadeOut(rend), m.FadeOut(stroomdiagram), sch_m.zicht.animate.set_value(0), run_time=SNEL)
        self.remove(sch_m.geheel, pijlen_m)
        self.doe(d - SNEL, m.FadeIn(rijen[0][:2]), m.FadeIn(rijen[1][:2]), m.FadeIn(rijen[2][:2]))
        d = zeg(self, "Een gloeilamp gebruikt 60 watt, waarvan maar ongeveer 3 watt licht wordt: een rendement van "
                      "5 procent. De rest is warmte.")
        self.doe(d, m.FadeIn(rijen[0][2]), m.FadeIn(legenda_l))
        d = zeg(self, "Een spaarlamp geeft hetzelfde licht met 12 watt: een rendement van 25 procent. "
                      "En een LED met 8 watt: bijna 40 procent.")
        self.play(m.FadeIn(rijen[1][2]), run_time=NORMAAL)
        self.doe(d - NORMAAL, m.FadeIn(rijen[2][2]))

        besparen = paneel(rij(r"E = 52\ \mathrm{W} \cdot 3\ \mathrm{h} \cdot 365 = 57\ \mathrm{kWh}"),
                          rij(r"57 \cdot 0,30 \approx 17\ \text{euro per jaar}"), hoek=m.DR).shift(1.2 * m.UP)
        d = zeg(self, "Vervang je een gloeilamp door een LED die 3 uur per dag brandt, dan bespaar je 52 watt, "
                      "elke dag 3 uur lang: per jaar zo'n 57 kilowattuur.")
        self.doe(d, *self.toon(besparen[0], besparen[1][0]))
        d = zeg(self, "Bij 30 cent per kilowattuur is dat ongeveer 17 euro per jaar. Per lamp.")
        self.doe(d, *self.toon(besparen[1][1]))

        # ═══ De kWh-meter ═══
        stand = m.ValueTracker(12345)
        kast = m.VGroup(m.RoundedRectangle(width=4.2, height=2.6, corner_radius=0.15).set_stroke(TEKST, 3),
                        tekst("kWh-meter", LABEL).move_to([0, 0.8, Z]),
                        m.Rectangle(width=3.2, height=0.8).set_stroke(TEKST, 2).move_to([0, -0.2, Z])).move_to([0, 0.3, Z])
        teller = m.VGroup()
        teller.add_updater(lambda t: t.become(tekst(f"{int(stand.get_value()):,} kWh".replace(",", "."), KOP).move_to([0, 0.1, Z])))
        teller.update()
        rekening = paneel(rij(r"15.095 - 12.345 = 2750\ \mathrm{kWh}"), rij(r"2750 \cdot 0,30 = 825\ \text{euro}"),
                          hoek=m.UR)
        d = zeg(self, "Hoeveel energie je thuis gebruikt, meet de kWh-meter in de meterkast. Hij telt het aantal "
                      "kilowattuur dat door het huis is gegaan.")
        self.play(*(m.FadeOut(x) for x in (rijen, legenda_l, besparen)), run_time=SNEL)
        self.doe(d - SNEL, m.FadeIn(kast), m.FadeIn(teller))
        d = zeg(self, "Begin van het jaar staat hij op 12.345. Een jaar later op 15.095. "
                      "Er is dus 2750 kilowattuur gebruikt: bij 30 cent per kilowattuur zo'n 825 euro.")
        self.play(stand.animate.set_value(15095), run_time=3, rate_func=m.linear)
        self.doe(d - 3, *self.toon(rekening))

        # ═══ Opwekking ═══
        teller.clear_updaters()
        bronnen = [("gascentrale", 50, "chemisch"), ("windturbine", 40, "beweging van wind"),
                   ("zonnepaneel", 20, "zonlicht")]
        rijen_o = m.VGroup(*(m.VGroup(rijlabel(naam, y), balk([(r, P_KLEUR), (100 - r, ACCENT)], -1.0, y, 0.06),
                                      tekst(f"{r}%", KLEIN + 2, P_KLEUR).move_to([-1.0 + r * 0.06 / 2, y + 0.42, Z]))
                             for (naam, r, _), y in zip(bronnen, (2.0, 0.9, -0.2))))
        legenda_o = m.VGroup(tekst("elektrische energie", KLEIN + 2, P_KLEUR).move_to([0.6, 2.75, Z]),
                             tekst("verloren als warmte", KLEIN + 2, ACCENT).move_to([3.7, 2.75, Z]))
        d = zeg(self, "Waar komt die elektrische energie eigenlijk vandaan? In een gascentrale verbrandt gas. Daarmee "
                      "draaien turbines, en een generator maakt er elektrische energie van.")
        self.play(m.FadeOut(kast), m.FadeOut(teller), m.FadeOut(rekening), run_time=SNEL)
        self.doe(d - SNEL, m.FadeIn(rijen_o[0]), m.FadeIn(legenda_o))
        d = zeg(self, "Maar ook hier gaat veel verloren: maar ongeveer de helft van de chemische energie wordt "
                      "elektrische energie. De rest verdwijnt als warmte.")
        self.wait(d)
        d = zeg(self, "Een windturbine zet de bewegingsenergie van de wind om, een zonnepaneel de energie van zonlicht: "
                      "daarvan wordt ongeveer 20 procent elektrische energie. Die bronnen raken niet op.")
        self.play(m.FadeIn(rijen_o[1]), run_time=NORMAAL)
        self.doe(d - NORMAAL, m.FadeIn(rijen_o[2]))

        # ═══ Samenvatting ═══
        samen = paneel(tekst("zekering: beschermt de draden tegen te veel stroom", LABEL),
                       tekst("aardlekschakelaar: beschermt jou (verschil > 30 mA)", LABEL),
                       rij(r"\eta = \frac{E_{nuttig}}{E_{in}} = \frac{P_{nuttig}}{P_{in}}"),
                       tekst("de kWh-meter telt je energieverbruik", LABEL), hoek=m.UL)
        d = zeg(self, "Samengevat:")
        self.play(m.FadeOut(rijen_o), m.FadeOut(legenda_o), run_time=SNEL)
        self.hud(samen[0])
        self.na_elkaar(samen[1], max(d, 4), m.FadeIn(samen[0]))
        zeg(self, "")
        self.wait(3)
