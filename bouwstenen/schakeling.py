"""Schakelingen met meerdere onderdelen en vertakkingen (video 5 t/m 7): plat (2D) of opgetild (3D, hoogte = spanning).

Een Schakeling is een lijst onderdelen (elk met spanning aan beide polen), draden en knooppunten. Stroompijltjes
gaan allemaal even snel; de stroom zit in hun dichtheid. Ze worden met een vast ritme bij de + uitgezonden
(sneller bij meer stroom) en verdwijnen bij de −. Op een splitsing gaat elk pijltje één tak in, verdeeld naar
I = U / R van de takken: in elke tak loopt zo precies zijn deel.
"""
import numpy as np
import manimgx as m

from .stijl import *
from .symbolen import *
from .kring import Z

U_BRON, R_LAMP = 6.0, 4.0
K = 1 / U_BRON          # hoogte per volt: 6 V = 1 eenheid (past bij de gekantelde lamp, zie kring.hoogte_vorm)
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


def stroompijltjes(sch, routes, aandelen, I, aan):
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


# ── Vaste kringen ──────────────────────────────────────────────────────────
def batterij():
    return onderdeel("bron", (XL, 0.6), (XL, -0.6), U_BRON, 0)  # + boven


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
