"""De transformator: eerst een 3D-model in een kring (stopcontact → transformator → lampje), dan het schema.

Opzet zoals extra/kring_3d_naar_2d.py: het 3D-model ligt zo op tafel dat het van boven al het schema is (stopcontact
links, transformator in het midden met zijn spoelen langs y, lampje rechts). De camera gaat naar het bovenaanzicht
en de 3D-onderdelen vloeien ter plekke over in hun symbolen. Daarna U_p / U_s = N_p / N_s met een voorbeeld
(1150 en 60 windingen: 230 V → 12 V) en vermogen: P_p = P_s (ideale transformator), dus hogere spanning = lagere
stroom. Het magnetisme blijft bij één zin: de wisselstroom maakt in de kern een wisselend veld (de kern 'pulseert').

Run vanuit de repo-root:  python -m manimgx render scenes/extra/transformator.py -o videos/Transformator.mp4
"""
import numpy as np
import manimgx as m
from bouwstenen import *


BEEN_X, BEEN_Y, DIK = 0.65, 0.85, 0.3   # kern: benen op x = ±0,65, jukken op y = ±0,85, balken 0,3 dik
KERN_Z = DIK / 2                         # kern ligt op tafel
SPOEL_R, SPOEL_Y = 0.25, 0.6             # spoelen: straal 0,25, van y = −0,6 tot 0,6
POOL_X = BEEN_X + SPOEL_R                # spoeluiteinden (aansluitingen) op x = ±0,9, y = ±0,6
N_P, N_S, U_P = 1150, 60, 230            # voorbeeld: 230 V → 12 V


def kern():
    """IJzeren kern: rechthoekig raam van vier balken, plat op tafel."""
    balken = [m.Prism(dimensions=[DIK, 2 * BEEN_Y + DIK, DIK]).move_to([x, 0, KERN_Z]) for x in (-BEEN_X, BEEN_X)]
    balken += [m.Prism(dimensions=[2 * BEEN_X - DIK, DIK, DIK]).move_to([0, y, KERN_Z]) for y in (-BEEN_Y, BEEN_Y)]
    return m.Group(*(mat(b, 0.45).set_fill(GEDEMPT, 0.45) for b in balken))


def spoel(x, windingen, start):
    """Koperen spoel om het been op x (as langs y). start: hoek waar de draad begint, zodat de uiteinden naar buiten
    wijzen (π: naar links, 0: naar rechts)."""
    hoek_eind = start + 2 * np.pi * windingen
    return m.ParametricFunction(
        lambda u: np.array([x + SPOEL_R * np.cos(start + (hoek_eind - start) * u), -SPOEL_Y + 2 * SPOEL_Y * u,
                            KERN_Z + SPOEL_R * np.sin(start + (hoek_eind - start) * u)]),
        t_range=[0, 1, 1 / (60 * windingen)]).set_stroke(ORANJE, 4)


def stopcontact():
    """Stopcontact links: blokje met twee gaatjes en het label 230 V plat op tafel."""
    blok = mat(m.Prism(dimensions=[0.6, 1.5, 0.3])).move_to([LINKS, 0, 0.15])
    gaten = m.Group(*(m.Cylinder(radius=0.06, height=0.02, direction=m.OUT).set_fill(BG, 1).set_stroke(width=0)
                      .move_to([LINKS, y, 0.31]) for y in (-0.25, 0.25)))
    label = tekst("230 V", LABEL).move_to([LINKS - 0.75, 0, Z + 0.01])
    return m.Group(blok, gaten, label)


def lampje_3d():
    """Fitting met peer (uit bouwstenen/modellen.py, op schaal 1 eenheid = 10 cm), rechtop rechts op tafel."""
    fitting = Draaivorm([(0, 27), (1.8, 27), (1.8, 31), (0, 31)], (30, 0, -27))
    peer = Draaivorm(peerprofiel(), (30, 0, -27), randen=[0])
    peer.vlak.set_material(None)  # geeft straks zelf licht
    return [fitting, peer]


def transformator_symbool(bulten_p=6, bulten_s=3):
    """Schemasymbool: twee spoelen (boogjes) met twee streepjes ertussen (de ijzeren kern). Aansluitingen op
    (±0,9, ±0,6), net als de spoeluiteinden van het 3D-model."""
    def spoel2d(x_draad, x_boog, bulten, kant):
        h = 2 * SPOEL_Y / bulten
        boogjes = [m.Arc(radius=h / 2, start_angle=m.PI / 2, angle=-kant * m.PI).move_to(
                   [x_boog + kant * h / 4, SPOEL_Y - h * (k + 0.5), Z]) for k in range(bulten)]
        aansluiting = [m.Line([x_draad, y, Z], [x_boog, y, Z]) for y in (SPOEL_Y, -SPOEL_Y)]
        return m.VGroup(*aansluiting, *boogjes)
    kernlijnen = m.VGroup(*(m.Line([x, -SPOEL_Y - 0.1, Z], [x, SPOEL_Y + 0.1, Z]) for x in (-0.06, 0.06)))
    return m.VGroup(spoel2d(-POOL_X, -0.45, bulten_p, 1), kernlijnen,
                    spoel2d(POOL_X, 0.45, bulten_s, -1)).set_stroke(TEKST, STREEP)


def f(tex, size=FORMULE - 6):
    return formule(komma(tex), size=size)


class Transformator(Les):
    def construct(self):
        self.add(*zon_en_schemer())
        # ── 3D: stopcontact – transformator – lampje ──
        de_kern = kern()
        prim, sec = spoel(-BEEN_X, 20, m.PI), spoel(BEEN_X, 5, 0.0)  # veel windingen links, weinig rechts
        contact = stopcontact()
        lamp3d = lampje_3d()
        draden3d = m.VGroup(*(draad([LINKS + 0.3, y, Z], [-POOL_X - 0.3, y, Z], [-POOL_X, y, KERN_Z])
                              for y in (SPOEL_Y, -SPOEL_Y)),  # sluit aan op de spoeluiteinden (op kernhoogte)
                            *(draad([POOL_X, y, KERN_Z], [POOL_X + 0.3, y, Z], [RECHTS, y, Z],
                                    [RECHTS, 0.18 * np.sign(y), Z])
                              for y in (SPOEL_Y, -SPOEL_Y)))
        self.set_camera_orientation(phi=62 * m.DEGREES, theta=-58 * m.DEGREES, zoom=1.15, frame_center=[0, 0, 0.3])
        omtrek = m.always_redraw(lambda: m.VGroup(*(d.omtrek(self.camera.get_theta()) for d in lamp3d)))
        drie_d = [de_kern, prim, sec, contact, draden3d, *(d.vlak for d in lamp3d), *(d.ringen for d in lamp3d)]
        self.add(*drie_d, omtrek)

        # ── Haakvraag ──
        d = zeg(self, "Het stopcontact geeft 230 volt. Maar je telefoon werkt op een paar volt, en dit lampje op 12. "
                      "Hoe krijg je die spanning omlaag?")
        self.move_camera(theta=-68 * m.DEGREES, run_time=d)
        d = zeg(self, "Daarvoor gebruik je een transformator. Die zet een wisselspanning om in een lagere, "
                      "of juist een hogere wisselspanning.")
        self.move_camera(theta=-78 * m.DEGREES, zoom=1.6, frame_center=[0, 0, 0.2], run_time=d)
        d = zeg(self, "Hij heeft twee spoelen om één ijzeren kern. De primaire spoel zit aan het stopcontact en heeft "
                      "veel windingen. De secundaire spoel zit aan het lampje en heeft er minder.")
        self.play(m.Indicate(prim, color=GEEL), run_time=min(d / 2, 2))
        self.play(m.Indicate(sec, color=GEEL), run_time=min(d / 2, 2))
        self.wait(max(d - 4, 0))

        # ── Werking: wisselend veld in de kern (één zin) ──
        puls = m.ValueTracker(0)
        de_kern.T = 0.0

        def pulseer(k, dt):
            k.T += dt
            mix = puls.get_value() * (0.5 + 0.5 * np.sin(2 * np.pi * 1.0 * k.T))  # wisselt heen en weer
            for balk in k:
                balk.set_fill(m.interpolate_color(m.ManimColor(GEDEMPT), m.ManimColor(BLAUW), mix), 0.45 + 0.3 * mix)
        de_kern.add_updater(pulseer)
        d = zeg(self, "De wisselstroom in de primaire spoel maakt in de kern een veld dat steeds wisselt. "
                      "Dat wisselende veld wekt in de secundaire spoel weer een spanning op: het lampje brandt.")
        self.play(puls.animate.set_value(1), run_time=SNEL)
        peer = lamp3d[1].vlak
        self.play(peer.animate.set_fill(LICHT, 1), run_time=SNEL)
        self.wait(max(d - 2 * SNEL, 0))
        d = zeg(self, "Daarom werkt een transformator alleen met wisselspanning: met gelijkspanning wisselt er niets.")
        self.wait(d)

        # ── Naar het schema ──
        d = zeg(self, "In een schema teken je de transformator zo: twee spoelen met twee streepjes ertussen "
                      "voor de ijzeren kern.")
        self.move_camera(phi=0, theta=-90 * m.DEGREES, zoom=1.0, frame_center=[1.8, 0, Z], focal_distance=400,
                         run_time=3)
        bron_s = plaats(wisselbron(), [LINKS, 0.6, Z], [LINKS, -0.6, Z])
        lamp_s = plaats(lamp(), [RECHTS, 0.6, Z], [RECHTS, -0.6, Z])
        lamp_s[2].set_fill(LICHT, 1)
        trafo_s = transformator_symbool()
        draden2d = m.VGroup(*(draad(pool, [-POOL_X, y, Z]) for pool, y in ((pool_a(bron_s), SPOEL_Y),
                                                                            (pool_b(bron_s), -SPOEL_Y))),
                            *(draad([POOL_X, y, Z], pool) for pool, y in ((pool_a(lamp_s), SPOEL_Y),
                                                                          (pool_b(lamp_s), -SPOEL_Y))))
        labels = m.VGroup(label("230 V", bron_s, m.LEFT, size=LABEL, kleur=TEKST),
                          label("primair", trafo_s[0], m.UP, size=LABEL, kleur=TEKST),
                          label("secundair", trafo_s[2], m.UP, size=LABEL, kleur=TEKST))
        omtrek.clear_updaters()
        de_kern.clear_updaters()
        self.play(*(m.FadeOut(x) for x in (*drie_d, omtrek)), m.FadeIn(bron_s), m.FadeIn(lamp_s), m.FadeIn(trafo_s),
                  m.FadeIn(draden2d), m.FadeIn(labels), m.FadeIn(schemagloed(lamp_s)), run_time=2)
        self.wait(max(d - 5, 0))

        # ── U_p / U_s = N_p / N_s ──
        verh, achter_v, (v_form, v_getal, v_reken) = paneel_delen(
            f(r"\frac{U_p}{U_s} = \frac{N_p}{N_s}", size=FORMULE + 4),
            f(rf"N_p = {N_P},\quad N_s = {N_S}"),
            f(rf"U_s = U_p \cdot \frac{{N_s}}{{N_p}} = 230 \cdot \frac{{{N_S}}}{{{N_P}}} = 12\ \mathrm{{V}}"))
        d = zeg(self, "Hoeveel lager wordt de spanning? Dat hangt af van de windingen: de spanning verandert in "
                      "dezelfde verhouding als het aantal windingen.")
        self.hud(achter_v)
        self.doe(d, m.FadeIn(achter_v), *self.toon(v_form))
        d = zeg(self, f"Stel: de primaire spoel heeft {N_P} windingen en de secundaire {N_S}. "
                      "Dan wordt 230 volt maal 60 gedeeld door 1150: precies 12 volt voor het lampje.")
        self.play(*self.toon(v_getal), run_time=SNEL)
        self.doe(d - SNEL, *self.toon(v_reken))

        # ── Vermogen: erin = eruit ──
        verm, achter_p, (p_form, p_lamp, p_prim) = paneel_delen(
            f(r"P_p = P_s \quad\Rightarrow\quad U_p \cdot I_p = U_s \cdot I_s", size=FORMULE - 2),
            f(r"P_s = 12 \cdot 2 = 24\ \mathrm{W}"),
            f(r"I_p = \frac{24}{230} \approx 0,10\ \mathrm{A}"))
        d = zeg(self, "En de stroom? Een ideale transformator verliest geen energie: het vermogen dat erin gaat, "
                      "komt er ook weer uit.")
        self.play(m.FadeOut(verh), run_time=SNEL)
        self.hud(achter_p)
        self.doe(d - SNEL, m.FadeIn(achter_p), *self.toon(p_form))
        d = zeg(self, "Het lampje gebruikt 12 volt en 2 ampère: 24 watt. Aan de primaire kant is dat ook 24 watt, "
                      "maar bij 230 volt: dan loopt daar maar 0,1 ampère.")
        self.play(*self.toon(p_lamp), run_time=SNEL)
        self.doe(d - SNEL, *self.toon(p_prim))
        d = zeg(self, "Lagere spanning betekent dus een hogere stroom, en andersom. "
                      "Een transformator ruilt spanning tegen stroom.")
        self.wait(d)

        # ── Toepassingen + samenvatting ──
        samen, achter_s, regels = paneel_delen(
            tekst("werkt alleen met wisselspanning", LABEL), f(r"\frac{U_p}{U_s} = \frac{N_p}{N_s}"),
            f(r"U_p \cdot I_p = U_s \cdot I_s"), tekst("meer spanning = minder stroom", LABEL))
        d = zeg(self, "Zo maakt de oplader van je telefoon van 230 volt een paar volt. En het elektriciteitsnet doet "
                      "het omgekeerde: met heel hoge spanning en dus kleine stroom gaat er onderweg weinig energie verloren.")
        self.play(m.FadeOut(verm), run_time=SNEL)
        self.wait(max(d - SNEL, 0))
        d = zeg(self, "Samengevat:")
        self.hud(achter_s)
        self.na_elkaar(regels, max(d, 3), m.FadeIn(achter_s))
        zeg(self, "")
        self.wait(3)
