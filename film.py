"""Maakt de hele film: rendert elk deel (alleen als het veranderd is) en plakt ze achter elkaar, met ondertitels.

Gebruik, vanuit de repo-root:
    python film.py             gewijzigde delen opnieuw renderen, dan samenvoegen
    python film.py --opnieuw   alles opnieuw renderen

Resultaat: videos/Elektriciteit.mp4 en videos/Elektriciteit.srt. De losse delen blijven ook in videos/ staan.
Een deel geldt als veranderd als zijn scènebestand of iets in bouwstenen/ anders is dan bij de vorige render.
"""
import hashlib
import re
import subprocess
import sys
from pathlib import Path

import av
import imageio_ffmpeg

DELEN = [  # (scènebestand, scèneklasse) in de volgorde van de film; scèneklasse None = kant-en-klaar filmpje
    ("scenes/00_intro.py", "Intro"),
    ("assets/Intro.mov", None),  # Nabla-logo, met geluid
    ("scenes/01_lading.py", "Lading"),
    ("scenes/02_waterkring.py", "Waterkring"),
    ("scenes/03_stroom.py", "Stroom"),
    ("scenes/04_spanning.py", "Spanning"),
    ("scenes/05_weerstand.py", "Weerstand"),
    ("scenes/06_serie_parallel.py", "SerieParallel"),
    ("scenes/07_vermogen.py", "Vermogen"),
    ("scenes/08_sensoren.py", "Sensoren"),
    ("scenes/09_thuis.py", "Thuis"),
]
VIDEOS = Path("videos")
FILM = "Elektriciteit"


def vingerafdruk(scene):
    """Hash van het scènebestand plus alle bouwstenen: verandert er iets, dan moet dit deel opnieuw."""
    h = hashlib.sha256()
    for f in [Path(scene), *sorted(Path("bouwstenen").glob("*.py"))]:
        h.update(f.read_bytes())
    return h.hexdigest()


def render(scene, naam, opnieuw):
    mp4, hashbestand = VIDEOS / f"{naam}.mp4", VIDEOS / f"{naam}.hash"
    nieuw = vingerafdruk(scene)
    if not opnieuw and mp4.exists() and hashbestand.exists() and hashbestand.read_text() == nieuw:
        print(f"{naam}: ongewijzigd, wordt niet opnieuw gerenderd")
        return
    print(f"{naam}: renderen…", flush=True)
    subprocess.run([sys.executable, "-m", "manimgx", "render", scene, naam, "-o", str(mp4)], check=True)
    hashbestand.write_text(nieuw)


def duur(mp4):
    with av.open(str(mp4)) as v:
        return v.duration / av.time_base


def tijd(s):
    u, mi, rest = s.split(":")
    sec, ms = rest.split(",")
    return int(u) * 3600 + int(mi) * 60 + int(sec) + int(ms) / 1000


def srt_tijd(t):
    ms = round(t * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def verschuif(srt, offset):
    """Ondertitelblokken (zonder nummer) met alle tijden offset seconden later."""
    blokken = []
    for blok in re.split(r"\n\s*\n", srt.strip()):
        regels = blok.splitlines()
        i = next(k for k, r in enumerate(regels) if "-->" in r)
        a, b = (x.strip() for x in regels[i].split("-->"))
        blokken.append([f"{srt_tijd(tijd(a) + offset)} --> {srt_tijd(tijd(b) + offset)}", *regels[i + 1:]])
    return blokken


assert verschuif("1\n00:00:01,500 --> 00:00:03,000\nHallo\n", 61.25) == [["00:01:02,750 --> 00:01:04,250", "Hallo"]]


def bestand(scene, naam):
    """Het videobestand van een deel: de render, of het kant-en-klare filmpje zelf."""
    return Path(scene) if naam is None else VIDEOS / f"{naam}.mp4"


def heeft_geluid(pad):
    with av.open(str(pad)) as v:
        return any(s.type == "audio" for s in v.streams)


def plak():
    film = VIDEOS / f"{FILM}.mp4"
    bronnen = [bestand(s, n) for s, n in DELEN]
    duren = [duur(b) for b in bronnen]
    # Eén keer hercoderen naar vaste 60 beelden/s (crf 16: nauwelijks te zien). Per deel: het laatste beeld vasthouden
    # (tpad) en exact afknippen op zijn duur (trim), want manimgx schrijft een stilstand als één lang beeld, en dat
    # raakt bij het plakken anders zoek. Delen zonder geluid (de renders) krijgen stilte, zodat het logo zijn geluid
    # houdt.
    filters, invoer = [], []
    for i, (b, d) in enumerate(zip(bronnen, duren)):
        invoer += ["-i", str(b)]
        filters.append(f"[{i}:v]fps=60,scale=1920:1080,setsar=1,format=yuv420p,"
                       f"tpad=stop_mode=clone:stop_duration=10,trim=duration={d:.4f},setpts=PTS-STARTPTS[v{i}]")
        filters.append(f"[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo,apad,atrim=duration={d:.4f},"
                       f"asetpts=PTS-STARTPTS[a{i}]" if heeft_geluid(b) else
                       f"anullsrc=r=48000:cl=stereo,atrim=duration={d:.4f}[a{i}]")
    filters.append("".join(f"[v{i}][a{i}]" for i in range(len(bronnen))) + f"concat=n={len(bronnen)}:v=1:a=1[v][a]")
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", *invoer,
                    "-filter_complex", ";".join(filters), "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-crf", "16", "-preset", "fast", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", str(film)], check=True)

    blokken, offset = [], 0.0
    for (_, naam), d in zip(DELEN, duren):
        srt = VIDEOS / f"{naam}.srt"
        if naam and srt.exists():
            blokken += verschuif(srt.read_text(encoding="utf8"), offset)
        offset += d
    (VIDEOS / f"{FILM}.srt").write_text(
        "\n".join(f"{n}\n" + "\n".join(b) + "\n" for n, b in enumerate(blokken, 1)), encoding="utf8")
    print(f"Klaar: {film} ({offset / 60:.1f} minuten) en {FILM}.srt")


if __name__ == "__main__":
    VIDEOS.mkdir(exist_ok=True)
    for scene, naam in DELEN:
        if naam:  # kant-en-klare filmpjes hoeven niet gerenderd te worden
            render(scene, naam, "--opnieuw" in sys.argv)
    plak()
