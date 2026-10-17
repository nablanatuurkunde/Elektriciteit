"""Waarom brandt de lamp pas als de kring gesloten is? Elektronen als water: lamp = waterrad, batterij = pomp.

Didactiek: voorspellen → waarnemen → verklaren (POE), daarna een analogie met expliciete vertaaltabel,
twee misconcepties ("de lamp verbruikt elektronen", "elektronen moeten eerst helemaal rondreizen"),
terug naar de echte kring en een samenvatting.
Zelfde 3D-opstelling als kring_3d_naar_2d.py: liggende batterij links, tafellamp rechts, draden plat op tafel.

Run vanuit de repo-root:  python -m manimgx render scenes/waterkring.py -o videos/Waterkring.mp4
"""
import numpy as np
import manimgx as m
from stijl import *
import kring_3d_naar_2d as kr  # als module: anders telt deze file twee scènes

# Elektronen verlaten de − pool (voorkant, -y), gaan door de lamp en komen bij de + pool (achterkant) terug.
PAD = [(kr.LINKS, -kr.BAT_HALF), (kr.LINKS, -kr.HALF), (kr.RECHTS, -kr.HALF), (kr.RECHTS, -kr.VOET),
       (kr.RECHTS, kr.VOET), (kr.RECHTS, kr.HALF), (kr.LINKS, kr.HALF), (kr.LINKS, kr.BAT_HALF)]


def mat(mob, opacity=0.35):
    """Witte, doorschijnende, belichte vorm in de stijl van de lamp en batterij."""
    return mob.set_fill(WIT, opacity).set_stroke(width=0).set_material(m.Material(roughness=0.5))


class Rondgang:
    """De gesloten kring als lus (ook door batterij/pomp heen), geparametriseerd naar afgelegde afstand:
    alles wat hierover beweegt, gaat overal even snel (point_from_proportion doet dat per segment, niet per lengte)."""

    def __init__(self):
        self.p = np.array([[x, y, kr.Z] for x, y in PAD + PAD[:1]], float)
        self.seg = np.linalg.norm(np.diff(self.p, axis=0), axis=1)
        self.cum = np.concatenate([[0], np.cumsum(self.seg)])
        self.lengte = self.cum[-1]

    def punt(self, s):
        s %= self.lengte
        i = min(np.searchsorted(self.cum, s, side="right") - 1, len(self.seg) - 1)
        return self.p[i] + (s - self.cum[i]) / self.seg[i] * (self.p[i + 1] - self.p[i])

    def stuk(self, s, l, k=10):
        """Punten van afstand s tot s + l, ook om hoeken heen."""
        return [self.punt(s + l * j / k) for j in range(k + 1)]


LUS = Rondgang()
assert np.isclose(np.linalg.norm(LUS.punt(0.1) - LUS.punt(0.0)), 0.1)  # gelijke stap = gelijke afstand


def stromer(groep, tempo, zet, richting=1):
    """Laat groep met snelheid tempo (eenheden/s) rond de lus schuiven; zet(lid, s) plaatst een lid op afstand s.
    richting 1 = zoals PAD (elektronen: − → lamp → +), -1 = andersom (stroom en water: + → lamp → −)."""
    groep.s = 0.0
    n = len(groep)

    def schuif(g, dt):
        g.s += richting * dt * tempo.get_value()
        for i, lid in enumerate(g):
            zet(lid, g.s + i * LUS.lengte / n)
    groep.add_updater(schuif)
    schuif(groep, 0)
    return groep


def deeltjes(kleur, tempo, richting, afstand=0.3):
    """Kleine bolletjes (onzichtbaar bij de start), gelijkmatig over de hele kring, met snelheid tempo (ValueTracker)."""
    g = m.Group(*(m.Sphere(radius=0.03, resolution=(8, 4)).set_fill(kleur, 0).set_stroke(width=0)
                  for _ in range(int(LUS.lengte / afstand))))
    return stromer(g, tempo, lambda bol, s: bol.move_to(LUS.punt(s)), richting)


def elektronen_in_kring(tempo, afstand=0.3):
    """Gele elektronen: van de − pool door de lamp naar de + pool."""
    return deeltjes(GEEL, tempo, 1, afstand)


def waterdeeltjes(tempo, afstand=0.3):
    """Blauw water: stroomt andersom dan de elektronen, net als de (conventionele) stroom: + → lamp → −."""
    return deeltjes(BLAUW, tempo, -1, afstand)


def waterrad(tempo):
    """Rad met schoepen, as langs x, op de plek van de lamp; draait mee met het water (tempo)."""
    straal, c = 0.45, np.array([kr.RECHTS, 0, kr.Z + 0.45])
    schoepen = m.Group(*(mat(m.Prism(dimensions=[0.3, 0.03, 0.2])).move_to(c + [0, 0, straal - 0.1])
                         .rotate(k * m.TAU / 8, m.RIGHT, about_point=c) for k in range(8)))
    as_ = mat(m.Cylinder(radius=0.04, height=0.5, direction=m.RIGHT)).move_to(c)
    randen = m.VGroup(*(m.Circle(radius=straal).rotate(m.PI / 2, m.UP).move_to(c + [dx, 0, 0])
                        for dx in (-0.15, 0.15))).set_stroke(WIT, 2)
    rad = m.Group(schoepen, as_, randen)
    # water langs de rechterkant stroomt naar -y; de onderkant van het rad gaat mee (draaien om +x duwt die naar +y)
    rad.add_updater(lambda r, dt: r.rotate(-2.5 * tempo.get_value() * dt, m.RIGHT, about_point=c))
    return rad


def pomp(tempo):
    """Pomp in lijn met de draad, op de plek van de batterij: doorzichtig huis met een draaiende schroef (helix).

    Het blad ligt op hoek a = k·y rond de as (y). Draaien over φ om +y (rechterhand) geeft a = k·y − φ:
    de schroefdraad schuift met ω/k langs de as. In de pomp stroomt het water van − naar + (het komt er aan de
    + kant uit), dus naar +y; met ω = k·tempo schuift de draad precies even snel mee als het water."""
    c = np.array([kr.LINKS, 0, kr.Z])
    huis = mat(m.Cylinder(radius=0.2, height=0.5, direction=m.UP), opacity=0.2).move_to(c)
    randen = m.VGroup(*(m.Circle(radius=0.2).rotate(m.PI / 2, m.RIGHT).move_to(c + [0, dy, 0])
                        for dy in (-0.25, 0.25))).set_stroke(WIT, 2)
    lengte, slagen = 0.44, 1.5
    k = m.TAU * slagen / lengte
    blad = m.Surface(lambda r, y: c + [r * np.cos(k * y), y, r * np.sin(k * y)],
                     u_range=(0.03, 0.17), v_range=(-lengte / 2, lengte / 2), resolution=(4, 48))
    as_ = m.Cylinder(radius=0.03, height=lengte, direction=m.UP).move_to(c)
    schroef = m.Group(mat(blad, 0.6), mat(as_, 0.6))
    schroef.add_updater(lambda s, dt: s.rotate(k * tempo.get_value() * dt, m.UP, about_point=c))
    return m.Group(huis, randen, schroef)


def plat_label(s, x, y, kleur=TEKST):
    """Tekst plat op tafel, leesbaar van schuin boven."""
    return tekst(s, KOP, kleur).move_to([x, y, kr.Z + 0.01])


def kaart(*regels, hoek=m.UL, size=LABEL):
    """Tekstkaart vast in beeld (links boven), met kader. Een regel mag ook al een tekst-mobject zijn."""
    tekst_ = m.VGroup(*(tekst(r, size) if isinstance(r, str) else r for r in regels)).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.2)
    return m.VGroup(tekst_, kader(tekst_, kleur=GEDEMPT)).to_corner(hoek, buff=0.5)


class Waterkring(m.ThreeDScene):
    def construct(self):
        self.waterdeel()
        zeg(self, "")
        self.wait(2)

    def waterdeel(self):
        """Het hele waterkring-verhaal; eindigt bij de echte, brandende kring met de samenvatting in beeld.
        Geeft de objecten terug die een vervolg (zoals waterkring_schema.py) nodig heeft."""
        self.add(*kr.zon_en_schemer())
        hud = self.add_fixed_in_frame_mobjects

        def toon(x):
            hud(x)  # vast in beeld, en vanaf onzichtbaar invagen
            return m.FadeIn(x)
        tempo = m.ValueTracker(0)

        def echte_kring():
            lamp3d, beugel, bat = kr.opstelling()
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
        licht, halo = kr.gloeiende_peer(lamp3d, g)
        min_ = kr.lijn(*PAD[:4])   # − → lamp (voorkant)
        plus = kr.lijn(*PAD[4:])   # lamp → + (achterkant): deze komt pas later
        e = elektronen_in_kring(tempo)
        w = waterdeeltjes(tempo)  # aparte deeltjes: water stroomt andersom dan de elektronen
        op_min_draad = [b for b in e if b.get_center()[1] < 0]  # bolletjes op de draad die er al ligt
        self.add(lamp_delen, bat_delen, licht, halo, e, w)

        # ── 1. Voorspellen ──
        d = zeg(self, "We sluiten een lamp met één koperdraad aan op een batterij.")
        self.move_camera(theta=-68 * m.DEGREES, added_anims=[m.Create(min_)], run_time=d)
        vraag = kaart("Voorspel: brandt de lamp?")
        hud(vraag)
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
                      tekst("elektronen  →  water", LABEL, t2c={"elektronen": GEEL, "water": BLAUW}))
        d = zeg(self, "De lamp is een waterrad,")
        halo.clear_updaters()
        self.play(weg(lamp_delen), m.FadeOut(halo), m.FadeIn(rad), toon(tabel[1]), toon(tabel[0][0]), run_time=d)
        licht.intensity = 0
        d = zeg(self, "de batterij is een pomp,")
        self.play(weg(bat_delen), m.FadeIn(p), toon(tabel[0][1]), run_time=d)
        d = zeg(self, "de draden zijn de buizen en de elektronen zijn het water.")
        self.play(toon(tabel[0][2]), run_time=d / 2)
        self.play(toon(tabel[0][3]), run_time=d / 2)
        d = zeg(self, "Eén ding valt op: het water stroomt precies de andere kant op dan de elektronen. "
                      "Waarom we dat zo tekenen, zie je in de volgende video.")
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
        self.move_camera(phi=60 * m.DEGREES, theta=-25 * m.DEGREES, zoom=2.2, frame_center=[kr.RECHTS, 0, 0.4],
                         added_anims=[m.FadeOut(x) for x in (*tabel[0], tabel[1])], run_time=d)

        # ── 7. Wat doet de pomp (batterij) dan wel? ──
        d = zeg(self, "De pomp duwt het water aan de ene kant naar buiten en zuigt het aan de andere kant weer aan.")
        self.move_camera(phi=50 * m.DEGREES, theta=-70 * m.DEGREES, zoom=2.2, frame_center=[kr.LINKS, 0, kr.Z],
                         run_time=d)
        mi = plat_label("−", kr.LINKS - 0.4, -kr.BAT_HALF - 0.15)
        pl = plat_label("+", kr.LINKS - 0.4, kr.BAT_HALF + 0.15)
        d = zeg(self, "Het water komt aan de plus-kant naar buiten. De elektronen doen precies het omgekeerde: "
                      "zij verlaten de batterij aan de min-kant en komen aan de plus-kant weer binnen.")
        self.play(m.FadeIn(mi), run_time=d / 2)
        self.play(m.FadeIn(pl), run_time=d / 2)

        # ── 8. Terug naar de echte kring + samenvatting ──
        d = zeg(self, "Terug naar onze lamp.")
        g.set_value(0)  # nieuwe lamp begint uit en gaat weer aan
        lamp3d, lamp_delen, bat_delen = echte_kring()
        licht2, halo2 = kr.gloeiende_peer(lamp3d, g)
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
        self.play(m.LaggedStart(*(toon(r) for r in samenvatting[0]), toon(samenvatting[1]), lag_ratio=0.3),
                  run_time=d)
        return dict(lamp_delen=lamp_delen, bat_delen=bat_delen, licht=licht2, halo=halo2, elektronen=e,
                    min_=min_, plus=plus, samenvatting=samenvatting, labels=m.VGroup(mi, pl))
