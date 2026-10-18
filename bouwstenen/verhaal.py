"""Vertellen: ondertitels (zeg), panelen en kaarten vast in beeld, en Les: de basis voor elke video.

Een video is een Les; daarin:
    d = zeg(self, "zin")          ondertitel tonen; d = spreektijd in seconden
    self.doe(d, *animaties)       animatie van een seconde, daarna stilstaan tot de zin klaar is
    self.play(*self.toon(paneel)) iets vast in beeld zetten en laten invagen
"""
import textwrap

import manimgx as m

from .stijl import *

# ── Ondertitels ────────────────────────────────────────────────────────────
ONDERTITEL_IN_BEELD = True  # False: alleen de .srt naast de video (voor YouTube-ondertitels)
WOORDEN_PER_SEC = 2.6       # spreektempo; stem af op je eigen voice-over


def zeg(scene, s, duur=None):
    """Toon s als ondertitel (in beeld en in de .srt) en geef de spreektijd terug.
    Vul die tijd daarna met animaties of wait(). zeg(scene, "") haalt de ondertitel weg."""
    if getattr(scene, "_ondertitel", None) is not None:
        scene.remove(scene._ondertitel)
        scene._ondertitel = None
    if not s:
        return 0
    duur = duur or max(1.2, len(s.split()) / WOORDEN_PER_SEC)
    scene.add_subcaption(s, duration=duur)
    if ONDERTITEL_IN_BEELD:
        t = tekst("\n".join(textwrap.wrap(s, 64)), KLEIN + 4).to_edge(m.DOWN, buff=0.3)
        achter = m.BackgroundRectangle(t, color=BG, fill_opacity=0.8, buff=0.12)
        scene._ondertitel = m.VGroup(achter, t).set_z_index(10)
        if isinstance(scene, m.ThreeDScene):
            scene.add_fixed_in_frame_mobjects(scene._ondertitel)
        else:
            scene.add(scene._ondertitel)
    return duur


# ── Panelen en kaarten (vast in beeld) ─────────────────────────────────────
def paneel(*inhoud, hoek=m.UL):
    """Inhoud op een (bijna) dekkend vlak met rand, vast in beeld: leesbaar, ook boven de kring.
    paneel[0] is het vlak, paneel[1] de regels: zo kunnen ze apart verschijnen."""
    groep = m.VGroup(*inhoud).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.25)
    vlak = m.SurroundingRectangle(groep, buff=0.25, corner_radius=0.12).set_stroke(GEDEMPT, 2).set_fill(BG, PANEEL_DEKKING)
    return m.VGroup(vlak, groep).to_corner(hoek, buff=0.5)  # vlak eerst: tekst ligt erbovenop


def kaart(*regels, hoek=m.UL, size=LABEL):
    """Tekstkaart vast in beeld (links boven), met kader. Een regel mag ook al een tekst-mobject zijn."""
    tekst_ = m.VGroup(*(tekst(r, size) if isinstance(r, str) else r for r in regels)).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.2)
    return m.VGroup(tekst_, kader(tekst_, kleur=GEDEMPT)).to_corner(hoek, buff=0.5)


# ── De basis voor elke video ───────────────────────────────────────────────
class Les(m.ThreeDScene):
    def hud(self, *mobs):
        """Vast in beeld zetten (blijft op zijn plek, wat de camera ook doet)."""
        self.add_fixed_in_frame_mobjects(*mobs)

    def toon(self, *mobs):
        """Vast in beeld zetten en laten invagen: self.play(*self.toon(a, b))."""
        self.hud(*mobs)
        return [m.FadeIn(x) for x in mobs]

    def doe(self, d, *anims, duur=NORMAAL):
        """Animatie van `duur` seconden, daarna stilstaan tot de zin (d seconden) klaar is: geen trage fades."""
        self.play(*anims, run_time=min(duur, d))
        self.wait(max(d - duur, 0))


def paneel_delen(*regels, hoek=m.UR):
    """Paneel waarvan vlak en regels apart kunnen verschijnen: geeft (paneel, vlak, regels)."""
    pnl = paneel(*regels, hoek=hoek)
    return pnl, pnl[0], pnl[1]
