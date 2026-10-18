"""Serie en parallel: stroom (2D) en spanning (3D, hoogte = spanning).

Twee lampen in serie (naast elkaar, achter elkaar in één lus: volts verdelen, één kapot = alles uit), daarna
dezelfde twee parallel (vertakking: ampères splitsen, volts niet; één kapot = de rest blijft aan, zoals
stopcontacten). Telkens ook de vervangingsweerstand (serie: optellen, parallel: omgekeerden optellen) en de
vakbegrippen spanningsdeling en stroomdeling. Daarna een gemengde schakeling, rustig stap voor stap, en tot slot
kortsluiting. 2D voor wegen en stroom, 3D (hoogte = spanning, zie bouwstenen/schakeling.py) voor spanning.
Batterij 6 V, lampen 4 Ω (als constant aangenomen).

Stroompijltjes: alle even snel; de stroom zit in hun dichtheid. Ze worden met een vast ritme bij de + uitgezonden
(sneller bij meer stroom) en verdwijnen bij de −. Op een splitsing gaat elk pijltje één tak in, verdeeld naar
I = U / R van de takken (vooraf uitgerekend, gelijkmatig gespreid): in elke tak loopt zo precies zijn deel.

Run vanuit de repo-root:  python -m manimgx render scenes/06_serie_parallel.py -o videos/SerieParallel.mp4
"""
import numpy as np
import manimgx as m
from bouwstenen import *


def gemengd():
    """A in serie met B ∥ C (alle 4 Ω, batterij 6 V): R_BC = 2 Ω, R_tot = 6 Ω, I = 1 A, U_A = 4 V, U_BC = 2 V."""
    xb = 0.8  # tak B; tak C ligt op XR
    A = onderdeel("lamp", (-2.2, YT), (-1.0, YT), 6, 2, "A")
    B = onderdeel("lamp", (xb, 0.6), (xb, -0.6), 2, 0, "B")
    C = onderdeel("lamp", (XR, 0.6), (XR, -0.6), 2, 0, "C")
    sch = Schakeling([batterij(), A, B, C],
                     [([(XL, 0.6), (XL, YT), (-2.2, YT)], 6), ([(-1.0, YT), (XR, YT), (XR, 0.6)], 2),
                      ([(xb, YT), (xb, 0.6)], 2), ([(xb, -0.6), (xb, YB)], 0),
                      ([(XR, -0.6), (XR, YB), (XL, YB), (XL, -0.6)], 0)],
                     [((xb, YT), 2), ((xb, YB), 0)])
    begin = [((XL, 0.6), 6), ((XL, YT), 6), ((-2.2, YT), None), ((-1.0, YT), 2)]
    eind = [((XL, YB), 0), ((XL, -0.6), None)]
    route_b = Route(begin + [((xb, YT), 2), ((xb, 0.6), None), ((xb, -0.6), 0), ((xb, YB), 0)] + eind)
    route_c = Route(begin + [((XR, YT), 2), ((XR, 0.6), None), ((XR, -0.6), 0), ((XR, YB), 0)] + eind)
    return sch, A, B, C, [route_b, route_c]


def enkele_lamp():
    """Batterij met één lamp rechts, en de route van de stroom door de lamp en (bij kortsluiting) door x = 0."""
    L = onderdeel("lamp", (XR, 0.6), (XR, -0.6), 6, 0)
    sch = Schakeling([batterij(), L], [([(XL, 0.6), (XL, YT), (XR, YT), (XR, 0.6)], 6),
                                       ([(XR, -0.6), (XR, YB), (XL, YB), (XL, -0.6)], 0)], [])
    via_lamp = Route([((XL, 0.6), 6), ((XL, YT), 6), ((XR, YT), 6), ((XR, 0.6), None), ((XR, -0.6), 0),
                      ((XR, YB), 0), ((XL, YB), 0), ((XL, -0.6), None)])
    via_draad = Route([((XL, 0.6), 6), ((XL, YT), 6), ((0, YT), 6), ((0, YB), 0), ((XL, YB), 0), ((XL, -0.6), None)])
    return sch, L, via_lamp, via_draad


class SerieParallel(Les):
    def construct(self):
        self.add(*zon_en_schemer())
        def boven():  # 2D: recht van boven, zonder perspectief
            return dict(phi=0, theta=-90 * m.DEGREES, zoom=1.0, frame_center=[0, 0, Z], focal_distance=400)

        def schuin():  # 3D: hoogte = spanning
            return dict(phi=62 * m.DEGREES, theta=-62 * m.DEGREES, zoom=0.95, frame_center=[0, 0, 0.5],
                        focal_distance=20)

        def boven_links():  # 2D, kring links in beeld: rechts ruimte voor een rekenpaneel
            return dict(phi=0, theta=-90 * m.DEGREES, zoom=0.85, frame_center=[2.6, 0, Z], focal_distance=400)

        def rij(tex):
            return formule(komma(tex), size=FORMULE - 6)

        self.set_camera_orientation(**boven())

        # ═══ Serie ═══
        sch, A, B, routes = serie()
        I_s = U_BRON / (2 * R_LAMP)                      # 0,75 A
        stroom_s, aan_s = m.ValueTracker(I_s), [m.ValueTracker(1)]
        pijlen = stroompijltjes(sch, routes, [1.0], stroom_s, aan_s)
        self.add(sch.geheel, pijlen)
        A["helder"].set_value(helderheid(3))  # de stroom loopt vanaf het begin, dus de lampen branden ook meteen
        B["helder"].set_value(helderheid(3))
        d = zeg(self, "Tot nu toe had onze kring één lamp. Wat gebeurt er als we er twee aansluiten?")
        self.doe(d, sch.zicht.animate.set_value(1))
        d = zeg(self, "Hier staan de lampen in serie: achter elkaar, in één lus. "
                      "Alle stroom gaat eerst door lamp A en daarna door lamp B.")
        self.wait(d)
        i_serie = paneel(formule(komma(r"I = 0,75\ \mathrm{A}")), tekst("overal even groot", LABEL), hoek=m.UR)
        d = zeg(self, "Er is maar één weg, dus de stroomsterkte is overal in de kring even groot: 0,75 ampère.")
        self.doe(d, *self.toon(i_serie), duur=SNEL)

        lat_a, lat_b = maatlat(A, "3 V", kant=-1), maatlat(B, "3 V", kant=-1)  # in de lege binnenruimte
        lat_bat = maatlat(sch.onderdelen[0], "6 V", kant=-1)                    # buiten, links van de batterij
        d = zeg(self, "Kijk nu naar de hoogte. De batterij tilt de stroom 6 volt omhoog. Onderweg zakt hij over twee "
                      "lampen. Elke lamp krijgt dus maar een deel: 3 volt per lamp.")
        self.play(m.FadeOut(i_serie), run_time=SNEL)
        self.move_camera(**schuin(), added_anims=[sch.t.animate.set_value(1)], run_time=3)
        self.play(m.Create(lat_bat), run_time=SNEL)
        self.doe(d - SNEL - 3 - SNEL, m.Create(lat_a), m.Create(lat_b))
        d = zeg(self, "In serie verdelen de volts zich over de lampen: dat heet spanningsdeling. "
                      "Daarom branden ze zwakker dan één lamp alleen.")
        self.wait(d)
        r_serie = paneel(rij(r"R_{tot} = R_A + R_B = 4 + 4 = 8\ \Omega"),
                         rij(r"I = \frac{U}{R_{tot}} = \frac{6}{8} = 0,75\ \mathrm{A}"), hoek=m.UR)
        d = zeg(self, "Waarom 0,75 ampère? De stroom moet door allebei de lampen, dus in serie tellen de weerstanden "
                      "op: R totaal is 4 plus 4 is 8 ohm. En 6 volt gedeeld door 8 ohm is 0,75 ampère.")
        self.doe(d, *self.toon(r_serie))

        d = zeg(self, "En als er één lamp kapotgaat? Dan is de lus onderbroken: er kan nergens meer stroom lopen. "
                      "Alles gaat uit.")
        self.play(*(m.FadeOut(x) for x in (lat_a, lat_b, lat_bat, r_serie)), run_time=SNEL)
        self.move_camera(**boven(), added_anims=[sch.t.animate.set_value(0)], run_time=2.5)
        self.play(A["kapot"].animate.set_value(1), run_time=SNEL)
        self.doe(d - SNEL - 2.5 - SNEL, A["helder"].animate.set_value(0), B["helder"].animate.set_value(0),
            aan_s[0].animate.set_value(0), stroom_s.animate.set_value(0))
        d = zeg(self, "Dat was het probleem van ouderwetse kerstboomverlichting: één lampje stuk, en de hele slinger "
                      "bleef donker.")
        self.wait(d)

        # ═══ Parallel ═══
        sch2, A2, B2, routes2 = parallel()
        I_a, I_b = U_BRON / R_LAMP, U_BRON / R_LAMP    # elke tak krijgt de volle 6 V: 1,5 A per tak
        stroom_p, aan_p = m.ValueTracker(I_a + I_b), [m.ValueTracker(0), m.ValueTracker(0)]
        pijlen2 = stroompijltjes(sch2, routes2, [I_a / (I_a + I_b), I_b / (I_a + I_b)], stroom_p, aan_p)
        self.add(sch2.geheel, pijlen2)
        d = zeg(self, "Nu sluiten we dezelfde twee lampen anders aan: parallel. Elke lamp krijgt zijn eigen tak.")
        self.play(sch.zicht.animate.set_value(0), run_time=SNEL)
        self.remove(sch.geheel, pijlen)
        self.doe(d - SNEL, sch2.zicht.animate.set_value(1))
        i_par = paneel(formule(komma(r"I_A = I_B = 1,5\ \mathrm{A}")),
                          formule(komma(r"I_{totaal} = 3,0\ \mathrm{A}")), hoek=m.UR)
        d = zeg(self, "Bij de vertakking splitst de stroom zich: de ene helft van de pijltjes gaat door lamp A, de andere "
                      "helft door lamp B. Door elke lamp gaat 1,5 ampère, samen 3 ampère door de batterij. "
                      "Dat heet stroomdeling.")
        self.doe(d, *(a.animate.set_value(1) for a in aan_p), A2["helder"].animate.set_value(helderheid(6)),
            B2["helder"].animate.set_value(helderheid(6)), *self.toon(i_par))
        r_par = paneel(rij(r"\frac{1}{R_{tot}} = \frac{1}{4} + \frac{1}{4} = \frac{1}{2}"),
                       rij(r"R_{tot} = 2\ \Omega"), rij(r"I = \frac{6}{2} = 3,0\ \mathrm{A}"), hoek=m.UR)
        d = zeg(self, "Wat is nu de totale weerstand? Met twee wegen naast elkaar komt de stroom makkelijker door: "
                      "de totale weerstand is kleiner dan die van elke lamp apart.")
        self.doe(d, m.FadeOut(i_par), *self.toon(r_par[0], r_par[1][0]))
        d = zeg(self, "Bij parallel tel je de omgekeerden op: 1 gedeeld door R totaal is een kwart plus een kwart, "
                      "is een half. Dus R totaal is 2 ohm. Controle: 6 volt gedeeld door 2 ohm is inderdaad 3 ampère.")
        self.play(*self.toon(r_par[1][1]), run_time=SNEL)
        self.doe(d - SNEL, *self.toon(r_par[1][2]))

        lat_a2 = maatlat(A2, "6 V", kant=1)   # rechts van A: lege binnenruimte
        lat_b2 = maatlat(B2, "6 V", kant=1)   # rechts van B: buiten de kring
        d = zeg(self, "En de spanning? Elke tak begint bovenaan en eindigt onderaan. Over elke lamp staat dus de volle "
                      "6 volt. De ampères splitsen, de volts niet.")
        self.play(m.FadeOut(r_par), run_time=SNEL)
        self.move_camera(**schuin(), added_anims=[sch2.t.animate.set_value(1)], run_time=3)
        self.doe(d - SNEL - 3, m.Create(lat_a2), m.Create(lat_b2))
        d = zeg(self, "Daarom branden parallelle lampen fel: elke lamp krijgt de volledige spanning van de batterij.")
        self.wait(d)

        # ── Eén lamp kapot: B houdt zijn 1,5 A, alleen de batterij levert minder (veelgemaakte denkfout) ──
        def rij(tex):
            return formule(komma(tex), size=FORMULE - 6)

        tabel = paneel(rij(r"I_A = 1,5\ \mathrm{A}"), rij(r"I_B = 1,5\ \mathrm{A}"),
                          rij(r"I_{totaal} = 3,0\ \mathrm{A}"), hoek=m.UR)
        r_a, r_b, r_tot = tabel[1]

        def wordt(oud, tex):
            return m.Transform(oud, rij(tex).move_to(oud, aligned_edge=m.LEFT))

        d = zeg(self, "Gaat er nu één lamp kapot, dan stopt de stroom in die tak. De andere lamp blijft branden.")
        self.play(m.FadeOut(lat_a2), m.FadeOut(lat_b2), run_time=SNEL)
        self.move_camera(**boven(), added_anims=[sch2.t.animate.set_value(0), *self.toon(tabel)], run_time=2.5)
        self.play(A2["kapot"].animate.set_value(1), run_time=SNEL)
        self.doe(d - SNEL - 2.5 - SNEL, A2["helder"].animate.set_value(0), aan_p[0].animate.set_value(0),
            wordt(r_a, r"I_A = 0\ \mathrm{A}"))

        d = zeg(self, "Je zou misschien denken: alle stroom moet nu door lamp B, dus B krijgt de stroom van A erbij. "
                      "Maar dat klopt niet!")
        self.wait(d)
        d = zeg(self, "Over lamp B staat nog steeds 6 volt, en B heeft nog steeds 4 ohm. Dus gaat er nog steeds "
                      "6 gedeeld door 4 is 1,5 ampère door B. Lamp B merkt er niets van.")
        self.doe(d, wordt(r_b, r"I_B = \frac{6}{4} = 1,5\ \mathrm{A}"))
        d = zeg(self, "Wél gaat nu alle stroom door B. Maar dat is minder dan eerst: "
                      "de batterij levert nu 1,5 ampère in plaats van 3. Kijk maar: de pijltjes op de hoofddraad "
                      "staan nu half zo dicht.")
        self.doe(d, wordt(r_tot, r"I_{totaal} = 1,5\ \mathrm{A}"))
        d = zeg(self, "De batterij levert dus geen vaste hoeveelheid stroom, maar een vaste spanning. "
                      "Elke tak neemt zelf de stroom die bij zijn weerstand hoort.")
        self.wait(d)
        d = zeg(self, "Vergelijk het met twee kranen aan dezelfde waterleiding: draai je de ene dicht, dan stroomt "
                      "er uit de andere niet ineens twee keer zoveel. Er gaat alleen minder door de hoofdleiding.")
        self.wait(d)
        d = zeg(self, "Zo zijn de stopcontacten in je huis geschakeld: zet je een lamp uit, "
                      "dan blijft de koelkast gewoon aan.")
        self.doe(d, m.FadeOut(tabel), duur=SNEL)

        # ═══ Gemengde schakeling: rustig, stap voor stap ═══
        sch3, A3, B3, C3, routes3 = gemengd()
        stroom_g, aan_g = m.ValueTracker(1.0), [m.ValueTracker(0), m.ValueTracker(0)]
        pijlen3 = stroompijltjes(sch3, routes3, [0.5, 0.5], stroom_g, aan_g)
        self.add(sch3.geheel, pijlen3)
        d = zeg(self, "Nu een gemengde schakeling. Lamp A staat in serie met twee lampen B en C, die parallel aan "
                      "elkaar staan. Alle lampen hebben 4 ohm, de batterij geeft 6 volt.")
        self.play(sch2.zicht.animate.set_value(0), run_time=SNEL)
        self.remove(sch2.geheel, pijlen2)
        self.move_camera(**boven_links(), added_anims=[sch3.zicht.animate.set_value(1)], run_time=NORMAAL)
        self.wait(max(d - SNEL - NORMAAL, 0))
        d = zeg(self, "Hoeveel stroom levert de batterij? Pauzeer de video en probeer het eerst zelf.")
        self.wait(d + 2)  # tijd om te pauzeren

        weer = paneel(rij(r"\frac{1}{R_{BC}} = \frac{1}{4} + \frac{1}{4} = \frac{1}{2}"),
                      rij(r"R_{BC} = 2\ \Omega,\quad R_{tot} = 4 + 2 = 6\ \Omega"),
                      rij(r"I = \frac{U}{R_{tot}} = \frac{6}{6} = 1\ \mathrm{A}"), hoek=m.UR)
        d = zeg(self, "Pak het stap voor stap aan. Begin met het parallelle deel: B en C samen. 1 gedeeld door R B C "
                      "is een kwart plus een kwart, is een half. Dus B en C samen hebben 2 ohm.")
        self.doe(d, *self.toon(weer[0], weer[1][0]))
        d = zeg(self, "Dat deel werkt als één weerstand van 2 ohm, in serie met lamp A. "
                      "De totale weerstand is dus 4 plus 2 is 6 ohm.")
        self.doe(d, *self.toon(weer[1][1]))
        d = zeg(self, "De stroom uit de batterij is 6 gedeeld door 6 is 1 ampère. Die stroom gaat helemaal door lamp A.")
        self.doe(d, *self.toon(weer[1][2]), *(a.animate.set_value(1) for a in aan_g),
                 A3["helder"].animate.set_value(helderheid(4)), B3["helder"].animate.set_value(helderheid(2)),
                 C3["helder"].animate.set_value(helderheid(2)))

        lat_a3, lat_b3, lat_c3 = maatlat(A3, "4 V", kant=1), maatlat(B3, "2 V", kant=-1), maatlat(C3, "2 V", kant=1)
        d = zeg(self, "Kijk weer naar de hoogte. Over A staat I maal R is 1 maal 4 is 4 volt. Er blijft 6 min 4 is "
                      "2 volt over, en die staat over B én over C, want die staan parallel.")
        self.play(m.FadeOut(weer), run_time=SNEL)
        self.move_camera(**schuin(), added_anims=[sch3.t.animate.set_value(1)], run_time=3)
        self.doe(d - SNEL - 3, m.Create(lat_a3), m.Create(lat_b3), m.Create(lat_c3))

        span = paneel(rij(r"U_A = I \cdot R_A = 1 \cdot 4 = 4\ \mathrm{V}"), rij(r"U_{BC} = 6 - 4 = 2\ \mathrm{V}"),
                      rij(r"I_B = I_C = \frac{2}{4} = 0,5\ \mathrm{A}"), hoek=m.UR)
        d = zeg(self, "Door B en door C gaat dus 2 gedeeld door 4 is 0,5 ampère. Samen weer 1 ampère: "
                      "de stroom deelt zich, en komt daarna weer samen.")
        self.play(*(m.FadeOut(x) for x in (lat_a3, lat_b3, lat_c3)), run_time=SNEL)
        self.move_camera(**boven_links(), added_anims=[sch3.t.animate.set_value(0), *self.toon(span)], run_time=2.5)
        self.wait(max(d - SNEL - 2.5, 0))
        d = zeg(self, "Daarom brandt A het felst: over A staat de meeste spanning, en door A loopt de meeste stroom.")
        self.wait(d)

        # ═══ Kortsluiting ═══
        sch4, L4, via_lamp, via_draad = enkele_lamp()
        L4["helder"].set_value(helderheid(6))
        stroom_l, aan_l = m.ValueTracker(1.5), [m.ValueTracker(1)]
        stroom_k, aan_k = m.ValueTracker(8.0), [m.ValueTracker(0)]  # 'heel groot': de pijltjes liggen dicht opeen
        pijl_lamp = stroompijltjes(sch4, [via_lamp], [1.0], stroom_l, aan_l)
        pijl_kort = stroompijltjes(sch4, [via_draad], [1.0], stroom_k, aan_k)
        kortsluitdraad = m.VGroup(draad([0, YT, Z], [0, YB, Z]).set_stroke(ACCENT, DRAAD_DIKTE + 1),
                                  knoop([0, YT, Z]), knoop([0, YB, Z]))
        uitleg = paneel(rij(r"I = \frac{U}{R} \quad \mathrm{met} \quad R \approx 0"),
                        tekst("dus de stroom wordt heel groot", LABEL), hoek=m.UR)
        self.add(sch4.geheel, pijl_lamp, pijl_kort)
        d = zeg(self, "Tot slot iets wat je juist níet wilt. Hier is weer één lamp op de batterij.")
        self.play(m.FadeOut(span), sch3.zicht.animate.set_value(0), run_time=SNEL)
        self.remove(sch3.geheel, pijlen3)
        self.doe(d - SNEL, sch4.zicht.animate.set_value(1))
        d = zeg(self, "Stel dat er per ongeluk een draad zonder weerstand parallel aan de lamp komt te zitten. "
                      "Over die draad staat vrijwel geen spanning, en dus ook niet over de lamp: de lamp gaat uit.")
        self.doe(d, m.Create(kortsluitdraad), L4["helder"].animate.set_value(0), aan_l[0].animate.set_value(0),
                 aan_k[0].animate.set_value(1))
        d = zeg(self, "En omdat de weerstand bijna nul is, wordt de stroom enorm groot. Dit heet kortsluiting.")
        self.doe(d, *self.toon(uitleg))
        d = zeg(self, "De draden en de batterij worden dan heet, en er kan brand ontstaan. Daarom zitten er in huis "
                      "zekeringen. Daarover meer in de video over elektriciteit thuis.")
        self.doe(d, m.Indicate(kortsluitdraad, color=ACCENT))
        zeg(self, "")
        self.wait(2)
