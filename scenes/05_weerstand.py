"""Weerstand en de wet van Ohm, in de hoogte-kring uit 04_spanning.py.

Begint waar 04_spanning.py eindigt. Waarom zakt de stroom over de lamp? Weerstand. Alles heeft een beetje weerstand,
maar bij draden is die te verwaarlozen. Wat weerstand is (R, ohm); waar de weerstand van een draad van afhangt
(R = ρ·ℓ/A, soortelijke weerstand), geleiders en isolatoren; wat een weerstand (onderdeel) doet, met de
zigzag als symbool. Dan de wet van Ohm, visueel: spanning ×2 → hogere batterij én pijltjes 2× zo snel;
weerstand ×2 → pijltjes half zo snel. U = I · R geldt altijd; bij een lamp verandert R zelf wel (geen ohmse weerstand).

Run vanuit de repo-root:  python -m manimgx render scenes/05_weerstand.py -o videos/Weerstand.mp4
"""
import numpy as np
import manimgx as m
from bouwstenen import *


MASKER_WEERSTAND = interval((RECHTS, -0.37), (RECHTS, 0.37))


def in_3d(p, h, stijf):
    """Als kring.hoogte_vorm, maar met instelbare hoogte h (spanning van de batterij), en
    stijf: 1 = het onderdeel rechts kantelt als stijf geheel (lamp blijft rond), 0 = het rekt mee over de helling
           (een zigzag mag rekken; zo kan de helling ook hoger dan het symbool lang is)."""
    x, y, z = p
    L, R, half = LINKS, RECHTS, LENGTE / 2
    lz, rz = L + 0.6, R - 0.6
    if x < lz:  # batterij: stijgt tussen de platen
        return np.array([x, y, z + h * np.clip((y + 0.1) / 0.2, 0, 1)])
    if x > rz:  # onderdeel rechts: zakt van h naar 0
        boven, onder = h, 0.0
        if abs(y) <= half:
            y_s, z_s = y, onder + (boven - onder) * (y + half) / LENGTE
        else:
            y_s, z_s = y, (boven if y > 0 else onder)
        sin = min((boven - onder) / LENGTE, 1.0)
        cos = np.sqrt(1 - sin ** 2)
        if abs(y) <= half:
            y_r, z_r = y * cos, (boven + onder) / 2 + y * sin
        else:
            krimp = half * (1 - cos) * np.clip(1 - (abs(y) - half) / OVERGANG, 0, 1)
            y_r, z_r = y - np.sign(y) * krimp, (boven if y > 0 else onder)
        return np.array([x, stijf * y_r + (1 - stijf) * y_s, z + stijf * z_r + (1 - stijf) * z_s])
    return np.array([x, y, z + (h if y > 0 else 0)])  # draden: vlak, achter boven en voor onder


def draadje(lengte, dikte, kleur=ORANJE):
    """Getekend stukje draad (2D, voor op het doek): koper is oranje."""
    return m.RoundedRectangle(width=lengte, height=dikte, corner_radius=dikte / 2).set_stroke(width=0).set_fill(kleur, 1)


def ohm_regels(U, I, R):
    return [waarde("U", U, "V"), waarde("I", I, "A"), waarde("R", R, r"\Omega", decimalen=0)]


class Weerstand(Les):
    def construct(self):
        self.add(*zon_en_schemer())
        h, stijf = m.ValueTracker(H), m.ValueTracker(1)
        stap = LUS.lengte / int(LUS.lengte / 0.3)
        tempo = m.ValueTracker(2 * stap)  # zelfde tempo als in 03_stroom.py en 04_spanning.py
        naar_3d = lambda p: in_3d(p, h.get_value(), stijf.get_value())

        def til_op(mob, zicht=None):
            """mob volgt voortaan de 3D-vorm van zijn platte versie (h en stijf kunnen veranderen).
            Omdat hij elk beeld opnieuw uit die platte versie ontstaat, gaat in- en uitfaden via zicht (ValueTracker)."""
            plat = mob.copy()

            vorige = [None]

            def volg(x):
                stand = (h.get_value(), stijf.get_value(), zicht.get_value() if zicht else 1)
                if stand == vorige[0]:
                    return  # niets veranderd: niet opnieuw bouwen (scheelt het meeste rekenwerk)
                vorige[0] = stand
                x.become(plat.copy().apply_function(naar_3d))
                if zicht is not None and zicht.get_value() < 1:
                    for deel in x.get_family():  # per deel: op een groep zou het alle kinderen gelijkzetten
                        deel.set_stroke(opacity=deel.get_stroke_opacity() * zicht.get_value(), family=False)
                        deel.set_fill(opacity=deel.get_fill_opacity() * zicht.get_value(), family=False)
            mob.add_updater(volg)
            mob.update()
            return mob

        def licht_op(mob, kleur, duur):
            """Indicate op een stilstaande kopie: het origineel wordt elk beeld herberekend en zou het overschrijven."""
            kopie = mob.copy()
            kopie.clear_updaters()
            self.play(m.Indicate(kopie, color=kleur, scale_factor=1.1), run_time=duur)
            self.remove(kopie)

        # ── Begin: zoals 04_spanning.py eindigt ──
        self.set_camera_orientation(phi=65 * m.DEGREES, theta=-62 * m.DEGREES, zoom=1.25, frame_center=[0.6, 0, 0.8],
                                    focal_distance=20)
        sch = schema()
        bron_s, lamp_s = sch["symbolen"]
        zicht_lamp, zicht_zz, zicht_zz2 = m.ValueTracker(1), m.ValueTracker(0), m.ValueTracker(0)
        for mob in (bron_s, sch["min_"], sch["plus"]):
            til_op(mob)
        til_op(lamp_s, zicht_lamp)
        maskers = [MASKER_BRON, MASKER_LAMP]
        pijlen = maskeer(lus_pijltjes(tempo, naar_3d), maskers, m.ValueTracker(1))
        yv = -HALF - 0.55
        vm_plat = plaats(meter("V"), [0.3, yv, Z], [1.1, yv, Z]).scale(0.7)
        a, b = [pool_a(vm_plat)[0], -HALF, Z], [pool_b(vm_plat)[0], -HALF, Z]
        meting = m.VGroup(vm_plat, draad(pool_a(vm_plat), a),
                          draad(pool_b(vm_plat), b), knoop(a), knoop(b))
        aflezing = paneel(waarde("U", 0, "V", decimalen=0), hoek=m.UR)
        self.hud(aflezing)
        self.add(bron_s, lamp_s, sch["min_"], sch["plus"], pijlen, meting)

        # ── Waarom zakt de stroom over de lamp? ──
        d = zeg(self, "Maar waarom verandert de lamp de spanning in de stroomkring?")
        self.move_camera(theta=-75 * m.DEGREES, frame_center=[RECHTS - 0.2, 0, 0.6], zoom=1.6,
                         added_anims=[m.FadeOut(meting), m.FadeOut(aflezing)], run_time=d)
        d = zeg(self, "De lamp heeft weerstand. In het dunne gloeidraadje botsen de elektronen steeds tegen de atomen. "
                      "Daarbij geven ze energie af: het draadje wordt heet en geeft licht.")
        licht_op(lamp_s, LICHT, min(d, 2))
        self.wait(max(d - 2, 0))
        d = zeg(self, "Die energie komt van de batterij. Daarom zakt de stroom over de lamp naar beneden.")
        self.wait(d)

        # ── Alles heeft een beetje weerstand ──
        d = zeg(self, "Eigenlijk heeft elk onderdeel stiekem een beetje weerstand, ook de draden. Maar bij een goede "
                      "koperdraad is die zo klein, dat we hem bijna altijd mogen verwaarlozen.")
        self.move_camera(theta=-55 * m.DEGREES, frame_center=[-0.4, 0, 0.6], zoom=1.1, run_time=d)

        # ── Wat is weerstand? R in ohm ──
        eenheid = paneel(tekst("weerstand R, in ohm (Ω)", LABEL), formule(r"1\ \Omega = 1\ \mathrm{V/A}"), hoek=m.UR)
        d = zeg(self, "Weerstand zegt hoe moeilijk de stroom ergens doorheen komt. Hoe groter de weerstand, "
                      "hoe meer spanning er nodig is om er een bepaalde stroom door te sturen.")
        self.wait(d)
        d = zeg(self, "We geven weerstand aan met R, en meten hem in ohm, met het teken omega. "
                      "Eén ohm betekent: je hebt één volt nodig voor één ampère.")
        self.hud(eenheid)
        self.play(m.FadeIn(eenheid), run_time=d)

        # ── Weerstand van een draad: lengte, doorsnede, materiaal → R = ρ·ℓ/A (op een doek, de kring erachter) ──
        doek = m.FullScreenRectangle(fill_color=BG, fill_opacity=0.94, stroke_width=0)

        def rij(uitleg, dr, uitkomst, y):
            """Eén regel: uitleg rechts uitgelijnd op x = -2, het draadje vanaf x = -1,6, de uitkomst op x = 3,4."""
            t = tekst(uitleg, LABEL).move_to([-2.0, y, 0], aligned_edge=m.RIGHT)
            dr.move_to([-1.6, y, 0], aligned_edge=m.LEFT)
            return m.VGroup(t, dr, formule(uitkomst).move_to([3.4, y, 0], aligned_edge=m.LEFT))

        rijen = [rij("lengte ℓ, doorsnede A", draadje(2.0, 0.22), r"R", 2.6),
                 rij("twee keer zo lang", draadje(4.0, 0.22), r"2R", 1.7),
                 rij("dubbele doorsnede", draadje(2.0, 0.31), r"\frac{1}{2} R", 0.8),  # 2× oppervlak: √2× zo dik
                 rij("ander materiaal", draadje(2.0, 0.22, GEDEMPT), r"\rho", -0.1)]
        rho = formule(r"R = \rho \cdot \frac{\ell}{A}", size=FORMULE + 6).move_to([0, -1.3, 0])
        d = zeg(self, "Waar hangt de weerstand van een draad eigenlijk van af? Van drie dingen: "
                      "de lengte, de dikte en het materiaal.")
        self.play(m.FadeOut(eenheid), *self.toon(doek), run_time=SNEL)
        self.doe(d - SNEL, *self.toon(rijen[0]))
        d = zeg(self, "Maak je de draad twee keer zo lang, dan moeten de elektronen een twee keer zo lange weg vol "
                      "botsingen afleggen: twee keer zoveel weerstand.")
        self.doe(d, *self.toon(rijen[1]))
        d = zeg(self, "Maak je de doorsnede twee keer zo groot, dan zijn er twee keer zoveel wegen naast elkaar: "
                      "de weerstand halveert.")
        self.doe(d, *self.toon(rijen[2]))
        d = zeg(self, "En het materiaal telt mee. Dat zit in de soortelijke weerstand, met de Griekse letter rho. "
                      "Die zoek je op in Binas.")
        self.doe(d, *self.toon(rijen[3]))
        d = zeg(self, "Samen: de weerstand is rho maal de lengte, gedeeld door de doorsnede. "
                      "De lengte in meter, de doorsnede in vierkante meter.")
        self.doe(d, *self.toon(rho))

        voorbeeld = m.VGroup(
            m.VGroup(tekst("koperdraad in huis:", LABEL), formule(komma(r"\ell = 1\ \mathrm{m},\quad A = 1,5\ \mathrm{mm^2}")))
            .arrange(m.RIGHT, buff=0.3),
            formule(komma(r"\rho_{koper} = 17 \cdot 10^{-9}\ \Omega\,\mathrm{m}")),
            formule(komma(r"R = 17 \cdot 10^{-9} \cdot \frac{1}{1,5 \cdot 10^{-6}} \approx 0,011\ \Omega")),
        ).arrange(m.DOWN, buff=0.45).move_to([0, 1.3, 0])
        d = zeg(self, "Een koperdraad in huis: 1 meter lang, met een doorsnede van 1,5 vierkante millimeter. "
                      "Koper heeft een soortelijke weerstand van 17 maal 10 tot de min 9 ohm meter.")
        self.play(*(m.FadeOut(x) for x in (*rijen, rho)), run_time=SNEL)
        self.doe(d - SNEL, *self.toon(voorbeeld[0], voorbeeld[1]))
        d = zeg(self, "Dat geeft maar 0,011 ohm: ongeveer een honderdste ohm. "
                      "Daarom mogen we de weerstand van draden bijna altijd verwaarlozen.")
        self.doe(d, *self.toon(voorbeeld[2]))

        # geleider en isolator: een kabel met een koperen kern in een plastic mantel
        mantel = draadje(6.0, 0.9, GEDEMPT).set_fill(opacity=0.45)
        kabel = m.VGroup(mantel, draadje(6.4, 0.3).move_to(mantel)).move_to([0.5, 0.6, 0])
        kabel_labels = m.VGroup(
            tekst("geleider: koper", LABEL, ORANJE).next_to(kabel, m.UP, buff=0.35).align_to(kabel, m.LEFT),
            tekst("isolator: plastic", LABEL).next_to(kabel, m.DOWN, buff=0.35).align_to(kabel, m.LEFT))
        d = zeg(self, "Metalen zoals koper hebben een heel kleine soortelijke weerstand. Ze hebben veel vrije "
                      "elektronen, en laten de stroom makkelijk door: dat zijn geleiders.")
        self.play(m.FadeOut(voorbeeld), run_time=SNEL)
        self.doe(d - SNEL, *self.toon(kabel[1], kabel_labels[0]))
        d = zeg(self, "Stoffen als plastic, glas en rubber hebben een soortelijke weerstand die miljarden keren groter "
                      "is. Er loopt vrijwel geen stroom doorheen: dat zijn isolatoren. Daarom zit er om elke koperdraad "
                      "een laagje plastic.")
        self.doe(d, *self.toon(kabel[0], kabel_labels[1]))

        # ── Het onderdeel 'weerstand', met zigzag ──
        zigzag = til_op(plaats(weerstand_zigzag(), [RECHTS, -LENGTE / 2, Z], [RECHTS, LENGTE / 2, Z]), zicht_zz)
        d = zeg(self, "Soms wil je met opzet weerstand in een kring, bijvoorbeeld om de stroom klein te houden "
                      "zodat een LED niet kapotgaat. Dan gebruik je een weerstand: een onderdeel met een vaste weerstand.")
        maskers.remove(MASKER_LAMP)
        maskers.append(MASKER_WEERSTAND)
        self.add(zigzag)
        self.move_camera(theta=-70 * m.DEGREES, frame_center=[RECHTS - 0.2, 0, 0.6], zoom=1.6, added_anims=[
            *(m.FadeOut(x) for x in (doek, kabel, kabel_labels)), zicht_lamp.animate.set_value(0), zicht_zz.animate.set_value(1),
            stijf.animate.set_value(0)],
            run_time=d)
        self.remove(lamp_s)
        d = zeg(self, "In een schema tekenen we hem hier als een zigzaglijn. Deze weerstand heeft 3 ohm.")
        licht_op(zigzag, R_KLEUR, d)

        # ── De wet van Ohm, visueel ──
        ohm = paneel(*ohm_regels(1.5, 0.5, 3), hoek=m.UR)
        rijen = ohm[1]

        def naar(U, I, R):
            return [m.Transform(oud, nieuw.move_to(oud, aligned_edge=m.LEFT))
                    for oud, nieuw in zip(rijen, ohm_regels(U, I, R))]

        d = zeg(self, "Met 1,5 volt over 3 ohm loopt er een stroom van 0,5 ampère.")
        self.hud(ohm)
        self.move_camera(theta=-55 * m.DEGREES, frame_center=[-0.4, 0, 1.0], zoom=1.0,
                         added_anims=[m.FadeIn(ohm)], run_time=d)
        d = zeg(self, "Wat gebeurt er als we de spanning twee keer zo groot maken? De batterij tilt de stroom twee keer "
                      "zo hoog, en de stroom gaat twee keer zo hard: 1 ampère.")
        self.play(h.animate.set_value(2 * H), tempo.animate.set_value(4 * stap), *naar(3.0, 1.0, 3),
                  run_time=min(d, 3))
        self.wait(max(d - 3, 0))

        zigzag2 = til_op(plaats(weerstand_zigzag(tanden=12), [RECHTS, -LENGTE / 2, Z], [RECHTS, LENGTE / 2, Z]),
                         zicht_zz2)
        self.add(zigzag2)
        d = zeg(self, "En als we de weerstand twee keer zo groot maken, 6 ohm? Dan komt de stroom moeilijker door "
                      "de weerstand: hij wordt half zo groot, weer 0,5 ampère.")
        self.play(zicht_zz.animate.set_value(0), zicht_zz2.animate.set_value(1), tempo.animate.set_value(2 * stap),
                  *naar(3.0, 0.5, 6), run_time=min(d, 3))
        self.remove(zigzag)
        self.wait(max(d - 3, 0))

        wet = paneel(formule(r"U = I \cdot R", size=FORMULE + 8), formule(r"3{,}0 = 0{,}5 \cdot 6"), hoek=m.UL)
        d = zeg(self, "Dit is de wet van Ohm: de spanning over een onderdeel is de stroom erdoor, maal de weerstand. "
                      "U is I maal R.")
        self.hud(wet)
        self.play(m.FadeIn(wet), run_time=d)
        d = zeg(self, "Deze formule geldt altijd en voor elk onderdeel: de weerstand is gewoon de spanning gedeeld "
                      "door de stroom.")
        self.play(m.Indicate(wet[1][0], color=U_KLEUR), run_time=d)
        d = zeg(self, "Let wel op: R zelf kan veranderen. Een lamp krijgt meer weerstand als hij heet wordt. "
                      "Een gewone weerstand houdt steeds dezelfde R.")
        self.wait(d)
        d = zeg(self, "Zo'n onderdeel, waarvan de weerstand altijd hetzelfde blijft, heet een ohmse weerstand. "
                      "Een lamp is dus géén ohmse weerstand.")
        self.wait(d)
        zeg(self, "")
        self.wait(2)
