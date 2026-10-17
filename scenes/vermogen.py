"""Vermogen: wat betekent het getal in watt? P = U · I, de watt (joule per seconde), P = E / t en de kilowattuur.

Eén doorlopend voorbeeld: een lamp van 4 Ω op 6 V (1,5 A, 9 W), met de kring en stroompijltjes uit serie_parallel.py.
Opbouw: haakvraag → energie per lading (3D: hoogte, 6 J per coulomb) → lading per seconde (pijltjes, 1,5 C/s)
→ samen P = U · I → watt zichtbaar: uit de lamp komen lichtbolletjes, één per joule, 9 per seconde, gelijk met
een joule-teller → E = P · t → één toetsvraag (de serielamp) → waarom de kWh bestaat (waterkoker) → terug naar de
haakvraag en een samenvattingskaart.

Run vanuit de repo-root:  python -m manimgx render scenes/vermogen.py -o videos/Vermogen.mp4
"""
import numpy as np
import manimgx as m
from stijl import *
import kring_3d_naar_2d as kr
import stroom as st
import serie_parallel as sp  # als modules: anders telt deze file meer dan één scène

Z = kr.Z
U, R = sp.U_BRON, sp.R_LAMP   # 6 V, 4 Ω
I = U / R                     # 1,5 A
P = U * I                     # 9 W
GULDEN_HOEK = np.pi * (3 - np.sqrt(5))  # bolletjes gelijkmatig rondom, zonder patroon


def kring():
    """Batterij links, één lamp rechts (zoals tak B van de parallelschakeling)."""
    XL, XR, YT, YB = sp.XL, sp.XR, sp.YT, sp.YB
    L = sp.onderdeel("lamp", (XR, 0.6), (XR, -0.6), U, 0)
    sch = sp.Schakeling([sp.batterij(), L],
                        [([(XL, 0.6), (XL, YT), (XR, YT), (XR, 0.6)], U),
                         ([(XR, -0.6), (XR, YB), (XL, YB), (XL, -0.6)], 0)], [])
    route = sp.Route([((XL, 0.6), U), ((XL, YT), U), ((XR, YT), U), ((XR, 0.6), None), ((XR, -0.6), 0),
                      ((XR, YB), 0), ((XL, YB), 0), ((XL, -0.6), None)])
    return sch, L, route


def waterkoker_kring():
    """Stopcontact (wisselspanning, 230 V) met het verwarmingselement van een waterkoker (weerstand).
    Geen stroompijltjes: bij wisselspanning keert de stroom 50 keer per seconde om."""
    XL, XR, YT, YB = sp.XL, sp.XR, sp.YT, sp.YB
    bron_w = sp.onderdeel("wissel", (XL, 0.6), (XL, -0.6), 0, 0, "230 V")
    koker = sp.onderdeel("weerstand", (XR, 0.6), (XR, -0.6), 0, 0, "waterkoker")
    sch = sp.Schakeling([bron_w, koker], [([(XL, 0.6), (XL, YT), (XR, YT), (XR, 0.6)], 0),
                                          ([(XR, -0.6), (XR, YB), (XL, YB), (XL, -0.6)], 0)], [])
    return sch, koker


U_ACCU, Q_ACCU, I_TEL = 3.7, 4.0, 0.4  # telefoonaccu: 3,7 V, 4000 mAh; telefoon gebruikt gemiddeld 0,4 A


def accu_kring():
    """Accu (gelijkspanning) met een telefoon als verbruiker (weerstand); geeft (kring, route voor de pijltjes)."""
    XL, XR, YT, YB = sp.XL, sp.XR, sp.YT, sp.YB
    accu = sp.onderdeel("bron", (XL, 0.6), (XL, -0.6), U_ACCU, 0, "accu")
    telefoon = sp.onderdeel("weerstand", (XR, 0.6), (XR, -0.6), U_ACCU, 0, "telefoon")
    sch = sp.Schakeling([accu, telefoon], [([(XL, 0.6), (XL, YT), (XR, YT), (XR, 0.6)], U_ACCU),
                                           ([(XR, -0.6), (XR, YB), (XL, YB), (XL, -0.6)], 0)], [])
    route = sp.Route([((XL, 0.6), U_ACCU), ((XL, YT), U_ACCU), ((XR, YT), U_ACCU), ((XR, 0.6), None),
                      ((XR, -0.6), 0), ((XR, YB), 0), ((XL, YB), 0), ((XL, -0.6), None)])
    return sch, route


def accumeter(vol):
    """Batterijbalkje dat leegloopt: vol (ValueTracker 1 → 0); toont de resterende lading en de verstreken uren."""
    meter = m.VGroup()

    def bij(mob):
        fr = vol.get_value()
        rand = m.RoundedRectangle(width=2.6, height=0.5, corner_radius=0.08).set_stroke(WIT, 2)
        vulling = m.Rectangle(width=max(2.5 * fr, 1e-3), height=0.4).set_stroke(width=0).set_fill(GROEN, 1)
        vulling.move_to(rand.get_left() + [0.05 + 1.25 * fr, 0, 0])
        regel = f"Q = {Q_ACCU * fr:.1f} Ah     t = {Q_ACCU * (1 - fr) / I_TEL:.0f} h".replace(".", ",")
        groep = m.VGroup(rand, vulling, tekst(regel, LABEL).next_to(rand, m.UP, buff=0.15))
        mob.become(groep.to_corner(m.DR, buff=0.5).shift(1.1 * m.UP))  # boven de ondertitels
    meter.add_updater(bij)
    bij(meter)
    return meter


def f(tex, size=FORMULE - 6):
    return formule(sp.komma(tex), size=size)


def lichtbolletjes(midden, per_seconde, zicht, leeftijd=1.0):
    """Gele bolletjes die uit de lamp naar buiten vliegen en vervagen: elk bolletje = 1 joule.
    Precies `per_seconde` per seconde, dus gelijk op met een joule-teller die P per seconde optelt."""
    n = int(np.ceil(per_seconde * leeftijd)) + 1
    g = m.VGroup(*(m.Dot(radius=0.05, color=LICHT) for _ in range(n)))
    g.T = 0.0

    def vlieg(groep, dt):
        groep.T += dt
        laatste = int(np.floor(groep.T * per_seconde))
        for k, bol in enumerate(groep):
            i = laatste - k                      # het k-de jongste bolletje
            leeft = groep.T - i / per_seconde
            if i < 0 or not 0 <= leeft < leeftijd:
                bol.set_opacity(0)
                continue
            hoek = i * GULDEN_HOEK
            bol.move_to(midden + (0.35 + 0.9 * leeft / leeftijd) * np.array([np.cos(hoek), np.sin(hoek), 0]))
            bol.set_opacity(zicht.get_value() * (1 - leeft / leeftijd))
    g.add_updater(vlieg)
    vlieg(g, 0)
    return g


class Vermogen(m.ThreeDScene):
    def construct(self):
        self.add(*kr.zon_en_schemer())
        hud = self.add_fixed_in_frame_mobjects

        def boven():  # 2D: recht van boven, zonder perspectief; kring naar links voor de panelen
            return dict(phi=0, theta=-90 * m.DEGREES, zoom=0.85, frame_center=[3.4, 0, Z], focal_distance=400)

        def schuin():  # 3D: hoogte = spanning
            return dict(phi=62 * m.DEGREES, theta=-62 * m.DEGREES, zoom=0.95, frame_center=[0.6, 0, 0.5],
                        focal_distance=20)

        def toon(*mobs):
            hud(*mobs)
            return [m.FadeIn(x) for x in mobs]

        def doe(d, *anims, duur=NORMAAL):
            """Animatie van `duur` seconden, daarna stilstaan tot de zin (d seconden) klaar is."""
            self.play(*anims, run_time=min(duur, d))
            self.wait(max(d - duur, 0))

        def paneel(*regels, hoek=m.UR):
            """Paneel waarvan achtergrond en regels apart kunnen verschijnen: (paneel, achtergrond, regels)."""
            pnl = st.paneel(*regels, hoek=hoek)
            return pnl, pnl[0], pnl[1]

        self.set_camera_orientation(**boven())
        sch, lampje, route = kring()
        lampje["helder"].set_value(sp.helderheid(U))
        pijlen = sp.stroom(sch, [route], [1.0], m.ValueTracker(I), [m.ValueTracker(1)])
        licht_zicht = m.ValueTracker(0)
        licht = lichtbolletjes((lampje["P"] + lampje["Q"]) / 2, P, licht_zicht)
        self.add(sch.geheel, pijlen, licht)

        # ── Haakvraag ──
        d = zeg(self, "Op elke lamp en elk apparaat staat een getal in watt. Wat betekent dat getal eigenlijk?")
        doe(d, sch.zicht.animate.set_value(1))
        d = zeg(self, "Een lamp zet elektrische energie om in licht en warmte. Hoe snel hij dat doet, "
                      "noemen we zijn vermogen.")
        doe(d, licht_zicht.animate.set_value(1))

        # ── Energie per lading: de hoogte ──
        lat = sp.maatlat(lampje, "6 V", kant=1)
        volt, _, _ = paneel(f(r"1\ \mathrm{V} = 1\ \mathrm{J/C}"))
        d = zeg(self, "Waar komt die energie vandaan? Kijk weer naar de hoogte. Elke lading die de helling van de lamp "
                      "afgaat, geeft energie af. 6 volt betekent: 6 joule voor elke coulomb.")
        self.play(licht_zicht.animate.set_value(0), run_time=SNEL)
        self.move_camera(**schuin(), added_anims=[sch.t.animate.set_value(1)], run_time=3)
        doe(d - SNEL - 3, m.Create(lat), *toon(volt))

        # ── Lading per seconde: de pijltjes ──
        amp, _, _ = paneel(f(r"1\ \mathrm{V} = 1\ \mathrm{J/C}"), f(r"1\ \mathrm{A} = 1\ \mathrm{C/s}"))
        d = zeg(self, "Hoeveel lading komt er langs? Dat zegt de stroom: 1,5 ampère is 1,5 coulomb per seconde.")
        doe(d, m.FadeOut(volt), *toon(amp), duur=SNEL)

        # ── Samen: P = U · I ──
        d = zeg(self, "Elke seconde komen er dus 1,5 coulomb langs, en elke coulomb geeft 6 joule af. "
                      "Samen: 6 maal 1,5 is 9 joule per seconde.")
        self.wait(d)
        form, achter, (r_p, r_eenh, r_getal) = paneel(
            f(r"P = U \cdot I", size=FORMULE + 4),
            f(r"\frac{\mathrm{J}}{\mathrm{C}} \cdot \frac{\mathrm{C}}{\mathrm{s}} = \frac{\mathrm{J}}{\mathrm{s}} = \mathrm{W}"),
            f(r"P = 6 \cdot 1,5 = 9\ \mathrm{W}"))
        d = zeg(self, "Dat is de formule voor vermogen: P is U maal I. Joule per coulomb maal coulomb per seconde "
                      "geeft joule per seconde, en dat noemen we watt.")
        self.play(m.FadeOut(amp), run_time=SNEL)
        hud(achter)
        self.play(m.FadeIn(achter), *toon(r_p), run_time=SNEL)
        doe(d - 2 * SNEL, *toon(r_eenh))

        # ── De watt zichtbaar: 9 bolletjes (joules) per seconde, met een teller ──
        d = zeg(self, "Deze lamp heeft dus een vermogen van 9 watt.")
        self.play(m.FadeOut(lat), run_time=SNEL)
        self.move_camera(**boven(), added_anims=[sch.t.animate.set_value(0), *toon(r_getal)], run_time=2.5)
        self.wait(max(d - SNEL - 2.5, 0))

        teller = m.VGroup()
        teller.t, teller.sec = 0.0, -1

        def tel(mob, dt):
            mob.t += dt
            if int(mob.t) != mob.sec:  # alleen op hele seconden bijwerken
                mob.sec = int(mob.t)
                mob.become(st.paneel(tekst(f"t = {mob.sec} s", LABEL), f(rf"E = {int(P * mob.sec)}\ \mathrm{{J}}"),
                                     hoek=m.DR))
        tel(teller, 0)
        d = zeg(self, "Stel dat elk geel bolletje één joule is. Uit de lamp komen er dan precies 9 per seconde. "
                      "Na 1 seconde is er 9 joule omgezet, na 2 seconden 18, enzovoort.")
        licht.T = 0.0  # bolletjes en teller starten tegelijk: ze lopen precies gelijk op
        teller.add_updater(tel)
        hud(teller)
        self.play(licht_zicht.animate.set_value(1), m.FadeIn(teller), run_time=SNEL)
        self.wait(max(d - SNEL, 5.2))

        # ── E = P · t ──
        teller.clear_updaters()
        et, achter_e, (r_ept, r_min, r_pet) = paneel(
            f(r"E = P \cdot t", size=FORMULE + 4), f(r"E = 9 \cdot 60 = 540\ \mathrm{J}"), f(r"P = \frac{E}{t}"))
        d = zeg(self, "De energie is dus vermogen maal tijd: E is P maal t.")
        self.play(m.FadeOut(teller), m.FadeOut(form), run_time=SNEL)
        hud(achter_e)
        doe(d - SNEL, m.FadeIn(achter_e), *toon(r_ept))
        d = zeg(self, "Brandt de lamp een minuut, dan zet hij 9 maal 60 is 540 joule om.")
        doe(d, *toon(r_min))
        d = zeg(self, "Andersom geldt: vermogen is energie gedeeld door tijd. Precies wat watt betekent: "
                      "joule per seconde.")
        doe(d, *toon(r_pet))

        # ── Toetsvraag: de serielamp (de kring wordt even de serieschakeling uit de vorige video) ──
        sch_s, A_s, B_s, routes_s = sp.serie()
        for lamp_s in (A_s, B_s):
            lamp_s["helder"].set_value(sp.helderheid(3))
        pijlen_s = sp.stroom(sch_s, routes_s, [1.0], m.ValueTracker(3 / R), [m.ValueTracker(1)])
        licht_s_zicht = m.ValueTracker(0)
        licht_s = [lichtbolletjes((c["P"] + c["Q"]) / 2, 3 * 3 / R, licht_s_zicht) for c in (A_s, B_s)]  # 2,25 J/s
        self.add(sch_s.geheel, pijlen_s, *licht_s)
        vraag, achter_v, (v_vraag, v_antw) = paneel(
            tekst("Lamp in serie: 3 V en 0,75 A. Vermogen?", LABEL), f(r"P = 3 \cdot 0,75 = 2,25\ \mathrm{W}"))
        d = zeg(self, "Test jezelf. In de serieschakeling had elke lamp 3 volt en 0,75 ampère. "
                      "Wat is zijn vermogen? Pauzeer de video en reken het uit.")
        self.play(m.FadeOut(et), sch.zicht.animate.set_value(0), licht_zicht.animate.set_value(0), run_time=SNEL)
        hud(achter_v)
        doe(d - SNEL + 2, sch_s.zicht.animate.set_value(1), m.FadeIn(achter_v), *toon(v_vraag))  # 2 s om te pauzeren
        d = zeg(self, "3 maal 0,75 is 2,25 watt: maar een kwart van 9 watt. Kijk: uit elke lamp komen nu maar "
                      "2,25 bolletjes per seconde. Daarom brandden die lampen zoveel zwakker.")
        doe(d, *toon(v_antw), licht_s_zicht.animate.set_value(1))

        # ── Waarom de kilowattuur ──
        kwh, achter_k, (k_groot, k_def, k_koker) = paneel(
            f(r"2000\ \mathrm{W} \cdot 180\ \mathrm{s} = 360\ 000\ \mathrm{J}"),
            f(r"1\ \mathrm{kWh} = 1000\ \mathrm{W} \cdot 3600\ \mathrm{s} = 3,6 \cdot 10^{6}\ \mathrm{J}"),
            f(r"E = 2\ \mathrm{kW} \cdot 0,05\ \mathrm{h} = 0,1\ \mathrm{kWh}"))
        d = zeg(self, "Apparaten in huis zijn veel sterker. Een waterkoker heeft zo'n 2000 watt. "
                      "Kookt hij 3 minuten, dan zet hij al 360 duizend joule om.")
        self.play(m.FadeOut(vraag), sch_s.zicht.animate.set_value(0), licht_s_zicht.animate.set_value(0),
                  run_time=SNEL)
        self.remove(sch_s.geheel, pijlen_s, *licht_s)
        sch_w, koker = waterkoker_kring()  # het beeld volgt de tekst: nu de waterkoker op het stopcontact
        koker["helder"].set_value(1)
        self.add(sch_w.geheel)
        self.play(sch_w.zicht.animate.set_value(1), run_time=SNEL)
        hud(achter_k)
        doe(d - 2 * SNEL, m.FadeIn(achter_k), *toon(k_groot))
        d = zeg(self, "Zulke grote getallen zijn onhandig. Daarom rekent het energiebedrijf in kilowattuur: "
                      "de energie van 1 kilowatt die 1 uur aanstaat. Dat is 3,6 miljoen joule.")
        doe(d, *toon(k_def))
        d = zeg(self, "De waterkoker van 2 kilowatt, 3 minuten lang, is 0,05 uur: samen 0,1 kilowattuur.")
        doe(d, *toon(k_koker))
        d = zeg(self, "Let op: reken óf in watt en seconden, dan krijg je joule, "
                      "óf in kilowatt en uren, dan krijg je kilowattuur.")
        self.wait(d)

        # ── Accu's: mAh is lading, Wh is energie ──
        sch_a, route_a = accu_kring()  # het beeld volgt de tekst: nu een telefoon op een accu
        pijlen_a = sp.stroom(sch_a, [route_a], [1.0], m.ValueTracker(I_TEL), [m.ValueTracker(1)])
        lading, achter_q, (q_def, q_mah, q_duur) = paneel(
            f(r"Q = I \cdot t", size=FORMULE + 4),
            f(r"4000\ \mathrm{mAh} = 4\ \mathrm{A} \cdot 1\ \mathrm{h} = 4\ \mathrm{Ah}"),
            f(r"t = \frac{Q}{I} = \frac{4\ \mathrm{Ah}}{0,4\ \mathrm{A}} = 10\ \mathrm{h}"))
        energie, achter_w, (w_def, w_joule) = paneel(
            f(r"E = Q \cdot U = 4\ \mathrm{Ah} \cdot 3,7\ \mathrm{V} = 14,8\ \mathrm{Wh}"),
            f(r"14,8\ \mathrm{Wh} = 14,8 \cdot 3600\ \mathrm{J} \approx 53\ 000\ \mathrm{J}"))

        d = zeg(self, "Op een telefoonaccu of powerbank staat vaak iets anders: bijvoorbeeld 4000 mAh, "
                      "milliampère-uur. Is dat ook energie? Denk even na.")
        self.play(m.FadeOut(kwh), sch_w.zicht.animate.set_value(0), run_time=SNEL)
        self.remove(sch_w.geheel)
        self.add(sch_a.geheel, pijlen_a)
        doe(d - SNEL + 1.5, sch_a.zicht.animate.set_value(1))  # 1,5 s extra om na te denken
        d = zeg(self, "Nee! Milliampère maal uur is stroom maal tijd, en stroom maal tijd is lading: Q is I maal t. "
                      "4000 milliampère-uur is dus 4 ampère-uur.")
        hud(achter_q)
        self.play(m.FadeIn(achter_q), *toon(q_def), run_time=SNEL)
        doe(d - SNEL, *toon(q_mah))

        vol = m.ValueTracker(1)
        meter_acc = accumeter(vol)
        d = zeg(self, "Een mAh-getal zegt dus hoeveel lading de accu kan leveren. Gebruikt je telefoon gemiddeld "
                      "0,4 ampère, dan is de accu na 4 gedeeld door 0,4 is 10 uur leeg.")
        hud(meter_acc)
        self.play(*toon(q_duur), m.FadeIn(meter_acc), run_time=SNEL)
        self.play(vol.animate.set_value(0), run_time=5, rate_func=m.linear)  # 10 uur in 5 seconden
        self.wait(max(d - SNEL - 5, 0))

        d = zeg(self, "Maar hoeveel energie zit erin? Daarvoor heb je ook de spanning nodig: "
                      "elke coulomb krijgt 3,7 joule mee.")
        meter_acc.clear_updaters()
        self.play(m.FadeOut(lading), m.FadeOut(meter_acc), run_time=SNEL)
        self.wait(max(d - SNEL, 0))
        d = zeg(self, "Energie is lading maal spanning: 4 ampère-uur maal 3,7 volt is 14,8 wattuur. "
                      "Wattuur is, net als kilowattuur, een eenheid van energie.")
        hud(achter_w)
        self.play(m.FadeIn(achter_w), *toon(w_def), run_time=SNEL)
        doe(d - SNEL, *toon(w_joule))
        d = zeg(self, "Dus: mAh zegt hoeveel lading er in een accu zit, Wh hoeveel energie. "
                      "Wil je accu's eerlijk vergelijken, kijk dan naar de wattuur.")
        self.wait(d)

        # ── Terug naar de haakvraag + samenvatting ──
        samen, achter_s, regels = paneel(
            f(r"P = U \cdot I"), f(r"P = \frac{E}{t}"), f(r"1\ \mathrm{W} = 1\ \mathrm{J/s}"),
            f(r"1\ \mathrm{kWh} = 3,6 \cdot 10^{6}\ \mathrm{J}"), tekst("mAh = lading,  Wh = energie", LABEL),
            hoek=m.UR)
        d = zeg(self, "Dus: het getal in watt zegt hoeveel joule een apparaat per seconde omzet. Samengevat:")
        self.play(m.FadeOut(energie), sch_a.zicht.animate.set_value(0), run_time=SNEL)  # terug naar onze lamp
        self.remove(sch_a.geheel, pijlen_a)
        self.play(sch.zicht.animate.set_value(1), run_time=SNEL)
        hud(achter_s)
        self.play(m.FadeIn(achter_s), licht_zicht.animate.set_value(1), run_time=SNEL)
        self.play(m.LaggedStart(*(toon(r)[0] for r in regels), lag_ratio=0.4), run_time=max(d - 3 * SNEL, 1.5))
        zeg(self, "")
        self.wait(3)
