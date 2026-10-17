"""Stroom: richting (afspraak, andersom dan de elektronen), stroomsterkte met de waterleiding, en de stroommeter.

Begint met het schema waarop waterkring_schema.py eindigt. Stroom = witte pijltjes die door de kring trekken;
de symbolen maskeren ze (een pijltje vervaagt waar het onder een symbool door gaat). Daarna 3D: een vlak dwars
op de leiding telt het water dat erdoor gaat (I = water per seconde), dan de stroommeter in 3D en als symbool.
Water en stroom gaan dezelfde kant op: van + door de lamp naar −; de elektronen andersom.

Run vanuit de repo-root:  python -m manimgx render scenes/stroom.py -o videos/Stroom.mp4
"""
import numpy as np
import manimgx as m
from stijl import *
import kring_3d_naar_2d as kr
import waterkring as wk  # als modules: anders telt deze file meer dan één scène

Z, LUS = kr.Z, wk.LUS
METER_X = -0.5  # plek van het telvlak en later de stroommeter, op de voorste draad

_s_raster = np.linspace(0, LUS.lengte, 16001)
_p_raster = np.array([LUS.punt(s) for s in _s_raster])


def s_op(x, y):
    """Afstand langs de lus van het punt (x, y) op de kring."""
    return _s_raster[np.argmin(np.linalg.norm(_p_raster[:, :2] - [x, y], axis=1))]


def interval(p, q):
    a, b = s_op(*p), s_op(*q)
    return min(a, b), max(a, b)


MASKER_BRON = interval((kr.LINKS, 0.13), (kr.LINKS, -0.13))   # tussen de platen van de bron
MASKER_LAMP = interval((kr.RECHTS, -0.3), (kr.RECHTS, 0.3))   # binnen de cirkel van de lamp
MASKER_METER = interval((METER_X - 0.32, -kr.HALF), (METER_X + 0.32, -kr.HALF))


def maskeer(groep, maskers, zicht, rand=0.05):
    """Zichtbaarheid per lid: zicht (ValueTracker) maal 0 onder een symbool, met een zachte rand van `rand`.
    maskers is een lijst van (s_begin, s_eind); later toevoegen kan (de stroommeter)."""
    n = len(groep)

    def bijwerken(g):
        for i, lid in enumerate(g):
            s = (g.s + i * LUS.lengte / n) % LUS.lengte
            f = 1.0
            for a, b in maskers:
                d = 0.0 if a <= s <= b else min(abs(s - a), abs(s - b))
                f = min(f, np.clip(d / rand, 0, 1))
            lid.set_fill(opacity=zicht.get_value() * f)
    groep.add_updater(bijwerken)
    bijwerken(groep)
    return groep


def stroompijlen(tempo, afstand=0.6):
    """Witte driehoekjes die van + door de lamp naar − trekken (andersom dan de elektronen)."""
    pijlen = m.VGroup(*(m.Triangle(fill_color=WIT, fill_opacity=0, stroke_width=0).scale(0.09).rotate(-m.PI / 2)
                        for _ in range(int(LUS.lengte / afstand))))  # Triangle wijst omhoog; nu naar rechts
    for p in pijlen:
        p.hoek = 0.0

    def zet(p, s):
        a, b = LUS.punt(s), LUS.punt(s - 1e-3)  # richting -1: op weg naar kleinere s
        h = m.angle_of_vector(b - a)
        p.rotate(h - p.hoek)
        p.hoek = h
        p.move_to(a)
    return wk.stromer(pijlen, tempo, zet, richting=-1)


def schema(met_meter=False):
    """Het schakelschema: bron, brandende lamp met gloed, draden en labels; eventueel met stroommeter in de voorste draad."""
    bron_s, lamp_s = kr.schema_symbolen()
    lamp_s[2].set_fill(LICHT, 1)
    L, R, H = kr.LINKS, kr.RECHTS, kr.HALF
    plus_s = draad(pool_b(lamp_s), [R, H, Z], [L, H, Z], pool_a(bron_s))  # zelfde looprichting als de 3D-draden
    labels = [label("spanningsbron", bron_s, m.LEFT, size=LABEL, kleur=TEKST),
              label("lamp", lamp_s, m.RIGHT, size=LABEL, kleur=TEKST)]
    if met_meter:
        meter_s = plaats(meter("A"), [METER_X - LENGTE / 2, -H, Z], [METER_X + LENGTE / 2, -H, Z])
        min_s = m.VGroup(draad(pool_b(bron_s), [L, -H, Z], pool_a(meter_s)),
                         draad(pool_b(meter_s), [R, -H, Z], pool_a(lamp_s)))
        labels.append(label("stroommeter", meter_s, m.DOWN, size=LABEL, kleur=TEKST))
        symbolen = m.VGroup(bron_s, lamp_s, meter_s)
    else:
        min_s = draad(pool_b(bron_s), [L, -H, Z], [R, -H, Z], pool_a(lamp_s))
        symbolen = m.VGroup(bron_s, lamp_s)
    for x in (min_s, plus_s):
        x.set_stroke(WIT, 3)
    return dict(symbolen=symbolen, gloed=kr.schemagloed(lamp_s), labels=m.VGroup(*labels), min_=min_s, plus=plus_s)


def paneel(*inhoud, hoek=m.UL):
    """Inhoud op een (bijna) dekkend vlak met rand, vast in beeld: leesbaar, ook boven de kring."""
    groep = m.VGroup(*inhoud).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.25)
    vlak = m.SurroundingRectangle(groep, buff=0.25, corner_radius=0.12).set_stroke(GEDEMPT, 2).set_fill(BG, 0.9)
    return m.VGroup(vlak, groep).to_corner(hoek, buff=0.5)  # vlak eerst: tekst ligt erbovenop


def stroommeter3d():
    """Kastje in de voorste leiding, met een wijzerplaat en een A erop."""
    c = np.array([METER_X, -kr.HALF, 0.1])
    kast = wk.mat(m.Prism(dimensions=[0.5, 0.32, 0.2])).move_to(c)
    plaat = m.Circle(radius=0.11).set_stroke(WIT, 2).move_to(c + [0, 0, 0.101])
    letter = tekst("A", LABEL).scale(0.6).move_to(c + [0, 0, 0.102])
    return m.Group(kast, plaat, letter)


def telvlak():
    """Denkbeeldig vlak dwars op de voorste leiding (normaal langs x); flitst als er een deeltje doorheen gaat."""
    v = m.Square(side_length=0.45).set_fill(WIT, 0.12).set_stroke(WIT, 2)
    v.rotate(m.PI / 2, m.UP).move_to([METER_X, -kr.HALF, Z])
    v.flits = 0.0

    def dim(mob, dt):
        mob.flits = max(0.0, mob.flits - 3 * dt)
        mob.set_fill(opacity=0.12 + 0.45 * mob.flits)
    v.add_updater(dim)
    return v


class Stroom(m.ThreeDScene):
    def construct(self):
        self.add(*kr.zon_en_schemer())
        hud = self.add_fixed_in_frame_mobjects
        tempo = m.ValueTracker(0)
        zicht_e, zicht_p, zicht_w = m.ValueTracker(0), m.ValueTracker(0), m.ValueTracker(0)
        maskers = [MASKER_BRON, MASKER_LAMP]

        # ── Begin: het schema uit de vorige video (bovenaanzicht zonder perspectief) ──
        self.set_camera_orientation(phi=0, theta=-90 * m.DEGREES, zoom=1.4, frame_center=[-0.5, 0, Z],
                                    focal_distance=400)
        sch = schema()
        e = maskeer(wk.elektronen_in_kring(tempo), maskers, zicht_e)
        pijlen = maskeer(stroompijlen(tempo), maskers, zicht_p)
        w = maskeer(wk.waterdeeltjes(tempo), [], zicht_w)
        stap = LUS.lengte / len(w)  # afstand tussen twee waterdeeltjes
        tempo.set_value(2 * stap)   # precies 2 deeltjes per seconde door elk punt: de teller komt exact uit
        self.add(sch["gloed"], sch["min_"], sch["plus"], sch["symbolen"], sch["labels"], e, pijlen, w)

        # ── Stroomrichting: een afspraak, andersom dan de elektronen ──
        d = zeg(self, "Dit is de kring uit de vorige video. In de draden bewegen elektronen: "
                      "van de min-pool, door de lamp, naar de plus-pool.")
        self.play(zicht_e.animate.set_value(1), run_time=d)
        d = zeg(self, "Toch tekenen we de stroom precies de andere kant op: van plus, door de lamp, naar min.")
        self.play(zicht_e.animate.set_value(0), run_time=SNEL)  # nooit elektronen én pijltjes tegelijk
        self.play(zicht_p.animate.set_value(1), run_time=d - SNEL)
        d = zeg(self, "Dat is een afspraak van lang geleden, toen nog niemand wist dat er elektronen bestonden.")
        self.wait(d)
        d = zeg(self, "Er bewegen in de draad dus geen deeltjes van plus naar min. "
                      "De stroomrichting is een afspraak: een handig trucje om mee te rekenen.")
        self.wait(d)
        d = zeg(self, "Voor het rekenen maakt het niet uit: negatieve lading die de ene kant op gaat, "
                      "telt hetzelfde als positieve lading die de andere kant op gaat.")
        self.wait(d)
        d = zeg(self, "Vanaf nu tekenen we daarom alleen de stroom. Dat is ook de richting waarin ons water stroomde.")
        self.wait(d)

        # ── Naar 3D: de waterleiding ──
        rad, pomp = wk.waterrad(tempo), wk.pomp(tempo)
        min_3d, plus_3d = kr.lijn(*wk.PAD[:4]), kr.lijn(*wk.PAD[4:])
        draad_min, draad_plus = sch["min_"], sch["plus"]  # deze objecten blijven; hun vorm verandert
        d = zeg(self, "Maar hoeveel stroom loopt er eigenlijk? Daarvoor gaan we terug naar onze waterleiding.")
        self.move_camera(phi=60 * m.DEGREES, theta=-60 * m.DEGREES, zoom=1.2, frame_center=[-0.5, 0, 0.3],
                         focal_distance=20, added_anims=[
                             m.FadeOut(sch["symbolen"]), m.FadeOut(sch["gloed"]), m.FadeOut(sch["labels"]),
                             m.FadeIn(rad), m.FadeIn(pomp), m.Transform(draad_min, min_3d),
                             m.Transform(draad_plus, plus_3d), zicht_p.animate.set_value(0),
                             zicht_w.animate.set_value(1)], run_time=max(d, 3))

        # ── Stroomsterkte: water door een vlak, per seconde ──
        vlak = telvlak()
        d = zeg(self, "Zet op één plek een denkbeeldig vlak dwars op de leiding, zodat al het water erdoorheen moet.")
        self.move_camera(phi=62 * m.DEGREES, theta=-72 * m.DEGREES, zoom=2.4, frame_center=[METER_X, -kr.HALF, 0.1],
                         added_anims=[m.FadeIn(vlak)], run_time=d)

        p_vlak = s_op(METER_X, -kr.HALF)
        teller = m.VGroup()
        teller.actief, teller.t, teller.s0, teller.N, teller.regels, teller.I = False, 0.0, 0.0, 0, None, None

        def fase():
            """0 → 1 tussen twee deeltjes die door het vlak gaan (0 = er gaat er net een door)."""
            return ((p_vlak - w.s) / stap) % 1  # w.s neemt af: water stroomt naar kleinere s

        def herstart():
            # wacht tot we precies halverwege twee deeltjes zijn: dan gaan ze op t = ¼, ¾, … s door het vlak
            # en staat de teller op elke hele seconde exact op een geheel aantal per seconde
            self.wait(((0.5 - fase()) % 1) * stap / tempo.get_value())
            teller.t, teller.s0, teller.N, teller.I, teller.actief = 0.0, w.s, 0, None, True

        def tel(mob, dt):
            if not mob.actief:
                return
            mob.t += dt
            n = abs(np.floor((w.s - p_vlak) / stap) - np.floor((mob.s0 - p_vlak) / stap))  # deeltjes door het vlak
            if n > mob.N:
                vlak.flits = 1.0
            mob.N = int(n)
            sec = int(mob.t)
            if sec >= 1 and (mob.I is None or mob.I[1] != sec):
                mob.I = (mob.N, sec)  # alleen op hele seconden bijwerken
            regels = [f"geteld: {mob.N} deeltjes", f"tijd: {sec} s"]
            if mob.I:
                n_, s_ = mob.I
                regels.append(f"I = {n_} / {s_} = {n_ / s_:.1f} deeltjes per seconde".replace(".", ","))
            if regels != mob.regels:  # alleen opnieuw zetten als de tekst verandert
                mob.regels = regels
                mob.become(paneel(*(tekst(r, LABEL) for r in regels)))
        teller.add_updater(tel)

        d = zeg(self, "De stroomsterkte I is de hoeveelheid water die per seconde door dat vlak stroomt. Laten we tellen.")
        herstart()
        tel(teller, 0)
        hud(teller)
        self.wait(d + 3)
        d = zeg(self, "Er gaan ongeveer twee deeltjes per seconde door het vlak.")
        self.wait(d)
        d = zeg(self, "Laat de pomp twee keer zo hard draaien: dan gaat er per seconde twee keer zoveel water "
                      "door het vlak. De stroom is groter.")
        teller.actief = False
        self.play(tempo.animate.set_value(4 * stap), run_time=0.5)  # precies 4 per seconde
        herstart()
        self.wait(d + 2.5)

        # ── Van water naar lading: I = Q / t in ampère ──
        teller.actief = False
        formules = paneel(formule(r"I = \frac{Q}{t}"), formule(r"1\ \mathrm{A} = 1\ \mathrm{C/s}", size=FORMULE - 8),
                          hoek=m.UR)
        achter, (i_formule, eenheid) = formules[0], formules[1]
        d = zeg(self, "In een echte draad tellen we geen water, maar lading. "
                      "De stroomsterkte is de lading Q die per seconde langs een punt gaat.")
        hud(achter, i_formule)
        self.play(m.FadeOut(teller), m.FadeIn(achter), m.FadeIn(i_formule), tempo.animate.set_value(2 * stap),
                  run_time=d)
        d = zeg(self, "We meten I in ampère, A. Eén ampère is één coulomb lading per seconde.")
        hud(eenheid)
        self.play(m.FadeIn(eenheid), run_time=d)

        # ── De stroommeter: in 3D, in serie ──
        meter3d = stroommeter3d()
        vlak.clear_updaters()
        d = zeg(self, "Om de stroomsterkte te meten, gebruiken we een stroommeter.")
        self.play(m.FadeOut(vlak), m.FadeIn(meter3d), run_time=d)
        d = zeg(self, "De stroommeter zit ín de leiding: al het water moet erdoorheen. "
                      "We zeggen: de stroommeter staat in serie.")
        self.move_camera(theta=-55 * m.DEGREES, zoom=2.0, run_time=d)

        # ── Terug naar het schema, nu met het symbool van de stroommeter ──
        d = zeg(self, "In een schema tekenen we de stroommeter als een cirkel met een A erin.")
        self.move_camera(phi=0, theta=-90 * m.DEGREES, zoom=1.4, frame_center=[-0.5, 0, Z], focal_distance=400,
                         added_anims=[m.FadeOut(achter), m.FadeOut(i_formule), m.FadeOut(eenheid)], run_time=3)
        nieuw = schema(met_meter=True)
        maskers.append(MASKER_METER)  # de pijltjes gaan nu ook onder de stroommeter door
        for x in (rad, pomp[2]):
            x.clear_updaters()
        self.play(m.FadeOut(rad), m.FadeOut(pomp), m.FadeOut(meter3d),
                  m.FadeIn(nieuw["symbolen"]), m.FadeIn(nieuw["gloed"]), m.FadeIn(nieuw["labels"]),
                  m.FadeOut(draad_min), m.FadeOut(draad_plus), m.FadeIn(nieuw["min_"]), m.FadeIn(nieuw["plus"]),
                  zicht_w.animate.set_value(0), zicht_p.animate.set_value(1), run_time=max(d - 3, 2))
        d = zeg(self, "De stroom gaat dwars door de stroommeter heen. "
                      "Zo zie je in elk schema meteen waar de stroom gemeten wordt.")
        self.wait(d)
        zeg(self, "")
        self.wait(2)
