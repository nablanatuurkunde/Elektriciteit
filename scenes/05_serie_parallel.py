"""Serie en parallel: stroom (2D) en spanning (3D, hoogte = spanning).

Twee lampen in serie (naast elkaar, achter elkaar in één lus: volts verdelen, één kapot = alles uit), daarna
dezelfde twee parallel (vertakking: ampères splitsen, volts niet; één kapot = de rest blijft aan, zoals
stopcontacten). 2D voor wegen en stroom, 3D (hoogte = spanning, zie bouwstenen/schakeling.py) voor spanning.
Batterij 6 V, lampen 4 Ω (als constant aangenomen).

Stroompijltjes: alle even snel; de stroom zit in hun dichtheid. Ze worden met een vast ritme bij de + uitgezonden
(sneller bij meer stroom) en verdwijnen bij de −. Op een splitsing gaat elk pijltje één tak in, verdeeld naar
I = U / R van de takken (vooraf uitgerekend, gelijkmatig gespreid): in elke tak loopt zo precies zijn deel.

Run vanuit de repo-root:  python -m manimgx render scenes/05_serie_parallel.py -o videos/SerieParallel.mp4
"""
import numpy as np
import manimgx as m
from bouwstenen import *


class SerieParallel(Les):
    def construct(self):
        self.add(*zon_en_schemer())
        def boven():  # 2D: recht van boven, zonder perspectief
            return dict(phi=0, theta=-90 * m.DEGREES, zoom=1.0, frame_center=[0, 0, Z], focal_distance=400)

        def schuin():  # 3D: hoogte = spanning
            return dict(phi=62 * m.DEGREES, theta=-62 * m.DEGREES, zoom=0.95, frame_center=[0, 0, 0.5],
                        focal_distance=20)

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
        d = zeg(self, "In serie verdelen de volts zich over de lampen. Daarom branden ze zwakker dan één lamp alleen.")
        self.wait(d)

        d = zeg(self, "En als er één lamp kapotgaat? Dan is de lus onderbroken: er kan nergens meer stroom lopen. "
                      "Alles gaat uit.")
        self.play(*(m.FadeOut(x) for x in (lat_a, lat_b, lat_bat)), run_time=SNEL)
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
                      "helft door lamp B. Door elke lamp gaat 1,5 ampère, samen 3 ampère door de batterij.")
        self.doe(d, *(a.animate.set_value(1) for a in aan_p), A2["helder"].animate.set_value(helderheid(6)),
            B2["helder"].animate.set_value(helderheid(6)), *self.toon(i_par))

        lat_a2 = maatlat(A2, "6 V", kant=1)   # rechts van A: lege binnenruimte
        lat_b2 = maatlat(B2, "6 V", kant=1)   # rechts van B: buiten de kring
        d = zeg(self, "En de spanning? Elke tak begint bovenaan en eindigt onderaan. Over elke lamp staat dus de volle "
                      "6 volt. De ampères splitsen, de volts niet.")
        self.play(m.FadeOut(i_par), run_time=SNEL)
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
        zeg(self, "")
        self.wait(2)
