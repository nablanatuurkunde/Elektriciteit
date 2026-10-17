"""Serie en parallel: stroom (2D) en spanning (3D, hoogte = spanning).

Twee lampen in serie (naast elkaar, achter elkaar in één lus: volts verdelen, één kapot = alles uit), daarna
dezelfde twee parallel (vertakking: ampères splitsen, volts niet; één kapot = de rest blijft aan, zoals
stopcontacten). 2D voor wegen en stroom, 3D (de hoogte-kring uit spanning.py) voor spanning.
Batterij 6 V, lampen 4 Ω (als constant aangenomen).

Stroompijltjes: alle even snel; de stroom zit in hun dichtheid. Ze worden met een vast ritme bij de + uitgezonden
(sneller bij meer stroom) en verdwijnen bij de −. Op een splitsing gaat elk pijltje één tak in, verdeeld naar
I = U / R van de takken (vooraf uitgerekend, gelijkmatig gespreid): in elke tak loopt zo precies zijn deel.

Run vanuit de repo-root:  python -m manimgx render scenes/serie_parallel.py -o videos/SerieParallel.mp4
"""
import re

import numpy as np
import manimgx as m
from stijl import *
import kring_3d_naar_2d as kr
import stroom as st  # als modules: anders telt deze file meer dan één scène

Z = kr.Z
U_BRON, R_LAMP = 6.0, 4.0
K = 1 / U_BRON          # hoogte per volt: 6 V = 1 eenheid (past bij de gekantelde lamp, zie spanning.py)
V_PIJL = 0.9            # snelheid van elk pijltje (eenheden/s)
Q_PIJL = 1.0            # lading per pijltje (A·s): bij I ampère komt er elke Q_PIJL / I seconde een pijltje bij
P_MAX = U_BRON ** 2 / R_LAMP  # vermogen van één lamp op de volle 6 V: helderheid 1
XL, XR, YT, YB = -3.0, 3.0, 1.8, -1.8  # buitenrand van de kringen


def xy(x, y):
    return np.array([x, y, Z], float)


def onderdeel(soort, P, Q, Vp, Vq, naam=None, maak=None, extra=()):
    """Onderdeel van P naar Q (LENGTE lang), met spanning Vp bij P en Vq bij Q. Bij de batterij is P de +.
    maak: eigen symboolfunctie (anders volgt het symbool uit soort); extra: ValueTrackers waar dat symbool van
    afhangt (bijvoorbeeld de stand van een schakelaar), zodat de kring opnieuw tekent als ze veranderen.
    zicht: eigen zichtbaarheid, zodat twee onderdelen op dezelfde plek in elkaar kunnen overvloeien."""
    return dict(soort=soort, P=xy(*P), Q=xy(*Q), Vp=Vp, Vq=Vq, naam=naam, maak=maak, extra=list(extra),
                helder=m.ValueTracker(0), kapot=m.ValueTracker(0), zicht=m.ValueTracker(1))


def vervaag(mob, f):
    """Maak elk deel van mob f keer zo zichtbaar. Per deel (family=False): op een groep zou set_stroke de
    doorzichtigheid van álle kinderen gelijkzetten, en zo verborgen delen weer zichtbaar maken."""
    for deel in mob.get_family():
        if hasattr(deel, "get_stroke_opacity"):
            deel.set_stroke(opacity=deel.get_stroke_opacity() * f, family=False)
            deel.set_fill(opacity=deel.get_fill_opacity() * f, family=False)
    return mob


def helderheid(U):
    """Helderheid 0…1 uit het vermogen P = U²/R, vergeleken met één lamp op de volle 6 V.
    Wortel: zo oogt een kwart van het vermogen als 'zwakker', niet als 'uit'."""
    return np.sqrt((U ** 2 / R_LAMP) / P_MAX)


class Schakeling:
    """Een kring die van plat (t = 0) naar 3D (t = 1) kan: de hoogte van elk punt is zijn spanning × K.
    Lampen kantelen als stijf geheel (blijven rond); de batterij is een trap (aansluitingen vlak, stijgt tussen de
    platen); draden zijn vlak en haken aan de polen."""

    def __init__(self, onderdelen, draden, knopen):
        self.onderdelen, self.draden, self.knopen = onderdelen, draden, knopen  # draden: (punten, V); knopen: (punt, V)
        self.t, self.zicht = m.ValueTracker(0), m.ValueTracker(0)
        self.geheel = m.Group()
        self.vorige = None
        self.geheel.add_updater(self._volg)
        self._volg(self.geheel)

    def vorm(self, p, c, t):
        """Waar punt p van onderdeel c komt bij optilstand t."""
        C, a = (c["P"] + c["Q"]) / 2, (c["Q"] - c["P"]) / LENGTE
        d = np.asarray(p, float) - C
        u = d @ a
        if c["soort"] == "bron":  # trap: vlak tot de platen (u = ±0,1), daartussen van Vp naar Vq
            V = c["Vp"] + (c["Vq"] - c["Vp"]) * np.clip((u + 0.1) / 0.2, 0, 1)
            return np.asarray(p, float) + [0, 0, t * K * V]
        sin = np.clip(t * K * (c["Vq"] - c["Vp"]) / LENGTE, -1, 1)  # lamp: stijf kantelen
        cos = np.sqrt(1 - sin ** 2)
        return C + u * cos * a + (d - u * a) + [0, 0, t * K * (c["Vp"] + c["Vq"]) / 2 + u * sin]

    def in_3d(self, p, V, t):
        """Draadpunt: op een pool van een onderdeel volgt het dat onderdeel, anders gewoon op hoogte V."""
        for c in self.onderdelen:
            for pool in (c["P"], c["Q"]):
                if np.linalg.norm(np.asarray(p)[:2] - pool[:2]) < 1e-6:
                    return self.vorm(pool, c, t)
        return np.array([p[0], p[1], Z + t * K * V])

    def bouw(self):
        t = self.t.get_value()
        delen = []
        for c in self.onderdelen:
            if c["zicht"].get_value() <= 0:
                continue  # onzichtbaar onderdeel (bijvoorbeeld een wachtend onderdeel op dezelfde plek): niet bouwen
            maak = c["maak"] or {"bron": bron, "lamp": lamp, "weerstand": weerstand, "wissel": wisselbron}[c["soort"]]
            sym = plaats(maak(), c["P"], c["Q"])
            groep = m.Group()
            C, a = (c["P"] + c["Q"]) / 2, (c["Q"] - c["P"]) / LENGTE
            if c["soort"] == "lamp":
                hl = c["helder"].get_value()
                kleur = 0.55 * min(hl / 0.2, 1) + 0.45 * hl  # brandt hij, dan duidelijk geel; vloeiend vanaf 0 (geen sprong)
                sym[2].set_fill(m.interpolate_color(m.ManimColor(BG), m.ManimColor(LICHT), kleur), 1)
                if hl > 0 and t < 1:  # zachte gloed om een brandende lamp, alleen in 2D (eronder getekend)
                    groep.add(m.VGroup(*(m.Circle(radius=r, stroke_width=0).set_fill(LICHT, 0.08 * (1 - i / 8) * hl * (1 - t))
                                         for i, r in enumerate(np.linspace(0.35, 0.95, 8)))).move_to(C - [0, 0, 0.005]))
            groep.add(sym)
            if c["soort"] == "lamp":
                if c["kapot"].get_value() > 0:
                    k = 0.3
                    kruis = m.VGroup(m.Line(C + [-k, k, 0], C + [k, -k, 0]), m.Line(C + [-k, -k, 0], C + [k, k, 0]))
                    groep.add(kruis.set_stroke(ACCENT, 7, c["kapot"].get_value()))
            if c["soort"] == "weerstand":  # verwarmingselement: gloeit oranje als hij aan staat
                sym[2].set_fill(m.interpolate_color(m.ManimColor(BG), m.ManimColor(ORANJE), c["helder"].get_value()), 1)
            if c["naam"] and t < 1:  # label alleen in 2D: gekanteld wordt het scheef en onleesbaar
                opzij = np.array([a[1], -a[0], 0])  # loodrecht op het onderdeel
                # naast het hele symbool (met zijn pijltjes, −t° enz.), niet naast het midden: geen overlap
                groep.add(tekst(c["naam"], LABEL).next_to(sym, opzij, buff=0.15).set_opacity(1 - t))
            zc = c["zicht"].get_value()
            if zc < 1:  # dit onderdeel vervaagt (of komt op)
                vervaag(groep, zc)
            delen.append(groep.apply_function(lambda p, c=c: self.vorm(p, c, t)))
        for punten, V in self.draden:
            delen.append(draad(*(self.in_3d(xy(*q), V, t) for q in punten)).set_stroke(WIT, 3))
        for q, V in self.knopen:
            delen.append(knoop(self.in_3d(xy(*q), V, t)))
        geheel = m.Group(*delen)
        z = self.zicht.get_value()
        if z < 1:
            vervaag(geheel, z)
        return geheel

    def _volg(self, g):
        stand = (self.t.get_value(), self.zicht.get_value(),
                 *(c["helder"].get_value() for c in self.onderdelen), *(c["kapot"].get_value() for c in self.onderdelen),
                 *(c["zicht"].get_value() for c in self.onderdelen),
                 *(x.get_value() for c in self.onderdelen for x in c["extra"]))
        if stand != self.vorige:  # alleen opnieuw bouwen als er iets veranderd is
            self.vorige = stand
            g.become(self.bouw())


class Route:
    """Een weg van de + naar de − van de batterij. punten: [((x, y), V), …]; V = spanning van het stuk dat daar
    begint, None = door een lamp (daar maskeert het symbool de pijltjes); de V van het laatste punt telt niet."""

    def __init__(self, punten):
        self.P = [xy(*q) for q, _ in punten]
        self.V = [V for _, V in punten[:-1]]
        self.lengtes = np.array([np.linalg.norm(b - a) for a, b in zip(self.P, self.P[1:])])
        self.cum = np.concatenate([[0], np.cumsum(self.lengtes)])
        self.L = self.cum[-1]

    def plek(self, s):
        """(punt, richting, V, zichtbaarheid) op afstand s; zacht vervagen bij lampen en bij de batterijpolen."""
        k = min(np.searchsorted(self.cum, s, side="right") - 1, len(self.lengtes) - 1)
        r = (self.P[k + 1] - self.P[k]) / self.lengtes[k]
        V = self.V[k]
        if V is None:
            return self.P[k] + (s - self.cum[k]) * r, r, 0, 0.0
        d = min(s if k == 0 else (s - self.cum[k]) if self.V[k - 1] is None else 9,
                (self.L - s) if k == len(self.V) - 1 else (self.cum[k + 1] - s) if self.V[k + 1] is None else 9)
        return self.P[k] + (s - self.cum[k]) * r, r, V, float(np.clip(d / 0.12, 0, 1))


def routekeuze(aandelen, i):
    """Welke route pijltje i neemt (twee routes): route 0 krijgt precies zijn aandeel, gelijkmatig gespreid
    (Bresenham: pijltje i gaat naar route 0 als het afgeronde aantal voor route 0 daar oploopt), de rest naar route 1."""
    p = aandelen[0]
    return 0 if np.floor((i + 1) * p + 1e-9) > np.floor(i * p + 1e-9) else len(aandelen) - 1


def stroom(sch, routes, aandelen, I, aan):
    """Pijltjes van + naar −: elke Q_PIJL / I seconde één, verdeeld over de routes volgens aandelen (som 1).
    aan: per route een ValueTracker (0 = die tak stroomt niet meer, bijvoorbeeld een kapotte lamp).
    I: ValueTracker met de stroom uit de batterij; 0 laat alles stilstaan."""
    Lmax = max(r.L for r in routes)
    pool = int(Lmax / V_PIJL * max(I.get_value(), 1e-9) / Q_PIJL) + 4
    pijlen = m.VGroup(*(m.VMobject().set_fill(WIT, 0).set_stroke(width=0) for _ in range(pool)))
    pijlen.T = 0.0
    dt_vast = Q_PIJL / I.get_value()  # uitzendritme ligt vast; stilzetten gaat via de klok (I → 0)

    def schuif(g, dt):
        g.T += dt * I.get_value() / I0
        t = sch.t.get_value()
        eerste = int(np.floor((g.T - Lmax / V_PIJL) / dt_vast))
        for k, p in enumerate(g):
            i = eerste + k
            s = V_PIJL * (g.T - i * dt_vast)
            j = routekeuze(aandelen, i)
            r = routes[j]
            if s < 0 or s > r.L:
                p.set_fill(opacity=0)
                continue
            plek, richting, V, zicht = r.plek(s)
            plek = plek + [0, 0, t * K * V]
            q = np.array([-richting[1], richting[0], 0])
            hoeken = [plek + 0.08 * richting, plek - 0.05 * richting + 0.06 * q, plek - 0.05 * richting - 0.06 * q]
            p.set_points_as_corners(hoeken + hoeken[:1])
            p.set_fill(opacity=zicht * aan[j].get_value() * sch.zicht.get_value())
    I0 = I.get_value()
    pijlen.add_updater(schuif)
    schuif(pijlen, 0)
    return pijlen


def maatlat(c, tekst_, kant):
    """Gele staande lat naast een onderdeel (kant: welke kant van de draad), van zijn lage naar zijn hoge kant (3D).
    Kies kant zo dat de lat buiten de kring of in de lege binnenruimte staat; het label staat nog verder die kant op."""
    C, a = (c["P"] + c["Q"]) / 2, (c["Q"] - c["P"]) / LENGTE
    n = kant * np.array([-a[1], a[0], 0])
    voet = C + 1.0 * n
    z0, z1 = Z + K * min(c["Vp"], c["Vq"]), Z + K * max(c["Vp"], c["Vq"])
    lat = m.VGroup(m.Line([*voet[:2], z0], [*voet[:2], z1]),
                   *(m.Line([*(voet - 0.1 * a)[:2], z], [*(voet + 0.1 * a)[:2], z]) for z in (z0, z1)))
    lbl = tekst(tekst_, LABEL, U_KLEUR).rotate(m.PI / 2, m.RIGHT).move_to([*(voet + 0.5 * n)[:2], (z0 + z1) / 2])
    return m.VGroup(lat.set_stroke(U_KLEUR, 4), lbl)


def batterij():
    return onderdeel("bron", (XL, 0.6), (XL, -0.6), U_BRON, 0)  # + boven


# ── De twee kringen ──
def serie():
    """A en B naast elkaar op de bovenrand: duidelijk achter elkaar."""
    A = onderdeel("lamp", (-1.8, YT), (-0.6, YT), 6, 3, "A")
    B = onderdeel("lamp", (0.6, YT), (1.8, YT), 3, 0, "B")
    sch = Schakeling([batterij(), A, B],
                     [([(XL, 0.6), (XL, YT), (-1.8, YT)], 6), ([(-0.6, YT), (0.6, YT)], 3),
                      ([(1.8, YT), (XR, YT), (XR, YB), (XL, YB), (XL, -0.6)], 0)], [])
    route = Route([((XL, 0.6), 6), ((XL, YT), 6), ((-1.8, YT), None), ((-0.6, YT), 3), ((0.6, YT), None),
                   ((1.8, YT), 0), ((XR, YT), 0), ((XR, YB), 0), ((XL, YB), 0), ((XL, -0.6), None)])
    return sch, A, B, [route]


def parallel():
    A = onderdeel("lamp", (0, 0.6), (0, -0.6), 6, 0, "A")
    B = onderdeel("lamp", (XR, 0.6), (XR, -0.6), 6, 0, "B")
    sch = Schakeling([batterij(), A, B],
                     [([(XL, 0.6), (XL, YT), (XR, YT), (XR, 0.6)], 6), ([(0, YT), (0, 0.6)], 6),
                      ([(XR, -0.6), (XR, YB), (XL, YB), (XL, -0.6)], 0), ([(0, -0.6), (0, YB)], 0)],
                     [((0, YT), 6), ((0, YB), 0)])
    route_a = Route([((XL, 0.6), 6), ((XL, YT), 6), ((0, YT), 6), ((0, 0.6), None), ((0, -0.6), 0), ((0, YB), 0),
                     ((XL, YB), 0), ((XL, -0.6), None)])
    route_b = Route([((XL, 0.6), 6), ((XL, YT), 6), ((XR, YT), 6), ((XR, 0.6), None), ((XR, -0.6), 0), ((XR, YB), 0),
                     ((XL, YB), 0), ((XL, -0.6), None)])
    return sch, A, B, [route_a, route_b]


def komma(s):
    r"""Nederlandse decimale komma zonder spatie erachter; alleen tussen twee cijfers (dus niet in \, of a, b)."""
    return re.sub(r"(?<=\d),(?=\d)", lambda _: r"\mathord{,}", s)


class SerieParallel(m.ThreeDScene):
    def construct(self):
        self.add(*kr.zon_en_schemer())
        hud = self.add_fixed_in_frame_mobjects

        def boven():  # 2D: recht van boven, zonder perspectief
            return dict(phi=0, theta=-90 * m.DEGREES, zoom=1.0, frame_center=[0, 0, Z], focal_distance=400)

        def schuin():  # 3D: hoogte = spanning
            return dict(phi=62 * m.DEGREES, theta=-62 * m.DEGREES, zoom=0.95, frame_center=[0, 0, 0.5],
                        focal_distance=20)

        def toon(*mobs):
            hud(*mobs)
            return [m.FadeIn(x) for x in mobs]

        def doe(d, *anims, duur=NORMAAL):
            """Animatie van `duur` seconden, daarna stilstaan tot de zin (d seconden) klaar is: geen trage fades."""
            self.play(*anims, run_time=min(duur, d))
            self.wait(max(d - duur, 0))

        self.set_camera_orientation(**boven())

        # ═══ Serie ═══
        sch, A, B, routes = serie()
        I_s = U_BRON / (2 * R_LAMP)                      # 0,75 A
        stroom_s, aan_s = m.ValueTracker(I_s), [m.ValueTracker(1)]
        pijlen = stroom(sch, routes, [1.0], stroom_s, aan_s)
        self.add(sch.geheel, pijlen)
        A["helder"].set_value(helderheid(3))  # de stroom loopt vanaf het begin, dus de lampen branden ook meteen
        B["helder"].set_value(helderheid(3))
        d = zeg(self, "Tot nu toe had onze kring één lamp. Wat gebeurt er als we er twee aansluiten?")
        doe(d, sch.zicht.animate.set_value(1))
        d = zeg(self, "Hier staan de lampen in serie: achter elkaar, in één lus. "
                      "Alle stroom gaat eerst door lamp A en daarna door lamp B.")
        self.wait(d)
        i_serie = st.paneel(formule(komma(r"I = 0,75\ \mathrm{A}")), tekst("overal even groot", LABEL), hoek=m.UR)
        d = zeg(self, "Er is maar één weg, dus de stroomsterkte is overal in de kring even groot: 0,75 ampère.")
        doe(d, *toon(i_serie), duur=SNEL)

        lat_a, lat_b = maatlat(A, "3 V", kant=-1), maatlat(B, "3 V", kant=-1)  # in de lege binnenruimte
        lat_bat = maatlat(sch.onderdelen[0], "6 V", kant=-1)                    # buiten, links van de batterij
        d = zeg(self, "Kijk nu naar de hoogte. De batterij tilt de stroom 6 volt omhoog. Onderweg zakt hij over twee "
                      "lampen. Elke lamp krijgt dus maar een deel: 3 volt per lamp.")
        self.play(m.FadeOut(i_serie), run_time=SNEL)
        self.move_camera(**schuin(), added_anims=[sch.t.animate.set_value(1)], run_time=3)
        self.play(m.Create(lat_bat), run_time=SNEL)
        doe(d - SNEL - 3 - SNEL, m.Create(lat_a), m.Create(lat_b))
        d = zeg(self, "In serie verdelen de volts zich over de lampen. Daarom branden ze zwakker dan één lamp alleen.")
        self.wait(d)

        d = zeg(self, "En als er één lamp kapotgaat? Dan is de lus onderbroken: er kan nergens meer stroom lopen. "
                      "Alles gaat uit.")
        self.play(*(m.FadeOut(x) for x in (lat_a, lat_b, lat_bat)), run_time=SNEL)
        self.move_camera(**boven(), added_anims=[sch.t.animate.set_value(0)], run_time=2.5)
        self.play(A["kapot"].animate.set_value(1), run_time=SNEL)
        doe(d - SNEL - 2.5 - SNEL, A["helder"].animate.set_value(0), B["helder"].animate.set_value(0),
            aan_s[0].animate.set_value(0), stroom_s.animate.set_value(0))
        d = zeg(self, "Dat was het probleem van ouderwetse kerstboomverlichting: één lampje stuk, en de hele slinger "
                      "bleef donker.")
        self.wait(d)

        # ═══ Parallel ═══
        sch2, A2, B2, routes2 = parallel()
        I_a, I_b = U_BRON / R_LAMP, U_BRON / R_LAMP    # elke tak krijgt de volle 6 V: 1,5 A per tak
        stroom_p, aan_p = m.ValueTracker(I_a + I_b), [m.ValueTracker(0), m.ValueTracker(0)]
        pijlen2 = stroom(sch2, routes2, [I_a / (I_a + I_b), I_b / (I_a + I_b)], stroom_p, aan_p)
        self.add(sch2.geheel, pijlen2)
        d = zeg(self, "Nu sluiten we dezelfde twee lampen anders aan: parallel. Elke lamp krijgt zijn eigen tak.")
        self.play(sch.zicht.animate.set_value(0), run_time=SNEL)
        self.remove(sch.geheel, pijlen)
        doe(d - SNEL, sch2.zicht.animate.set_value(1))
        i_par = st.paneel(formule(komma(r"I_A = I_B = 1,5\ \mathrm{A}")),
                          formule(komma(r"I_{totaal} = 3,0\ \mathrm{A}")), hoek=m.UR)
        d = zeg(self, "Bij de vertakking splitst de stroom zich: de ene helft van de pijltjes gaat door lamp A, de andere "
                      "helft door lamp B. Door elke lamp gaat 1,5 ampère, samen 3 ampère door de batterij.")
        doe(d, *(a.animate.set_value(1) for a in aan_p), A2["helder"].animate.set_value(helderheid(6)),
            B2["helder"].animate.set_value(helderheid(6)), *toon(i_par))

        lat_a2 = maatlat(A2, "6 V", kant=1)   # rechts van A: lege binnenruimte
        lat_b2 = maatlat(B2, "6 V", kant=1)   # rechts van B: buiten de kring
        d = zeg(self, "En de spanning? Elke tak begint bovenaan en eindigt onderaan. Over elke lamp staat dus de volle "
                      "6 volt. De ampères splitsen, de volts niet.")
        self.play(m.FadeOut(i_par), run_time=SNEL)
        self.move_camera(**schuin(), added_anims=[sch2.t.animate.set_value(1)], run_time=3)
        doe(d - SNEL - 3, m.Create(lat_a2), m.Create(lat_b2))
        d = zeg(self, "Daarom branden parallelle lampen fel: elke lamp krijgt de volledige spanning van de batterij.")
        self.wait(d)

        # ── Eén lamp kapot: B houdt zijn 1,5 A, alleen de batterij levert minder (veelgemaakte denkfout) ──
        def rij(tex):
            return formule(komma(tex), size=FORMULE - 6)

        tabel = st.paneel(rij(r"I_A = 1,5\ \mathrm{A}"), rij(r"I_B = 1,5\ \mathrm{A}"),
                          rij(r"I_{totaal} = 3,0\ \mathrm{A}"), hoek=m.UR)
        r_a, r_b, r_tot = tabel[1]

        def wordt(oud, tex):
            return m.Transform(oud, rij(tex).move_to(oud, aligned_edge=m.LEFT))

        d = zeg(self, "Gaat er nu één lamp kapot, dan stopt de stroom in die tak. De andere lamp blijft branden.")
        self.play(m.FadeOut(lat_a2), m.FadeOut(lat_b2), run_time=SNEL)
        self.move_camera(**boven(), added_anims=[sch2.t.animate.set_value(0), *toon(tabel)], run_time=2.5)
        self.play(A2["kapot"].animate.set_value(1), run_time=SNEL)
        doe(d - SNEL - 2.5 - SNEL, A2["helder"].animate.set_value(0), aan_p[0].animate.set_value(0),
            wordt(r_a, r"I_A = 0\ \mathrm{A}"))

        d = zeg(self, "Je zou misschien denken: alle stroom moet nu door lamp B, dus B krijgt de stroom van A erbij. "
                      "Maar dat klopt niet!")
        self.wait(d)
        d = zeg(self, "Over lamp B staat nog steeds 6 volt, en B heeft nog steeds 4 ohm. Dus gaat er nog steeds "
                      "6 gedeeld door 4 is 1,5 ampère door B. Lamp B merkt er niets van.")
        doe(d, wordt(r_b, r"I_B = \frac{6}{4} = 1,5\ \mathrm{A}"))
        d = zeg(self, "Wél gaat nu alle stroom door B. Maar dat is minder dan eerst: "
                      "de batterij levert nu 1,5 ampère in plaats van 3. Kijk maar: de pijltjes op de hoofddraad "
                      "staan nu half zo dicht.")
        doe(d, wordt(r_tot, r"I_{totaal} = 1,5\ \mathrm{A}"))
        d = zeg(self, "De batterij levert dus geen vaste hoeveelheid stroom, maar een vaste spanning. "
                      "Elke tak neemt zelf de stroom die bij zijn weerstand hoort.")
        self.wait(d)
        d = zeg(self, "Vergelijk het met twee kranen aan dezelfde waterleiding: draai je de ene dicht, dan stroomt "
                      "er uit de andere niet ineens twee keer zoveel. Er gaat alleen minder door de hoofdleiding.")
        self.wait(d)
        d = zeg(self, "Zo zijn de stopcontacten in je huis geschakeld: zet je een lamp uit, "
                      "dan blijft de koelkast gewoon aan.")
        doe(d, m.FadeOut(tabel), duur=SNEL)
        zeg(self, "")
        self.wait(2)
