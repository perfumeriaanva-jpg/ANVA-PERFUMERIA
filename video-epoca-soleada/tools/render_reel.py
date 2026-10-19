"""Edita el Reel "Perfumes para época soleada" a partir del video en crudo.

Uso: python3 render_reel.py <crudo.mov> <dir_fuentes> <dir_fotos> <musica.wav> <dir_salida>
  dir_fuentes: JosefinSans.ttf y Arimo.ttf (variables) + static/ con las instancias para libass.

Todos los tiempos de abajo están en segundos del video en crudo y salen de la transcripción.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

import make_cards as mc

FPS = 30
END_CARD = 2.0

# Tramos que se conservan. Se quita el "Hola, ¿cómo están?" y se acortan las pausas entre frases.
# zoom alterna el encuadre en cada corte para que los saltos no se noten.
SEGMENTS = [
    (0.97, 7.22, 1.00),
    (7.52, 16.62, 1.07),
    (16.80, 19.86, 1.00),
    (20.22, 23.16, 1.07),
    (23.38, 24.40, 1.00),
    (24.72, 33.42, 1.07),
    (33.80, 37.92, 1.00),
    (38.12, 41.50, 1.07),
]

# {C}…{/C} = concepto destacado (champagne), {N}…{/N} = nombre de perfume o marca.
SUBS = [
    (0.98, 2.78, "Les voy a recomendar rápidamente"),
    (2.80, 5.56, "mis dos perfumes favoritos árabes"),
    (5.60, 7.20, "para esta temporada de {C}calor{/C}"),
    (7.56, 9.02, "El número uno es el"),
    (9.04, 11.10, "{N}Al Haramain Aqua Dubai{/N},"),
    (11.32, 14.05, "que es un perfume que dupea"),
    (14.07, 15.66, "a la perfección el {N}Imagination{/N}"),
    (15.68, 16.58, "de Louis Vuitton."),
    (16.86, 18.62, "Vas a oler prácticamente"),
    (18.70, 19.84, "{C}fresco y jabonoso{/C}"),
    (20.28, 20.95, "todo el día,"),
    (20.96, 21.90, "{C}dura bastante{/C},"),
    (21.92, 23.14, "tiene muy buena calidad,"),
    (23.44, 24.38, "es espectacular."),
    (24.78, 26.40, "Y el número dos es el"),
    (26.42, 28.10, "{N}Hawas Ice{/N} de Rasasi,"),
    (28.32, 29.68, "que también es muy {C}fresco{/C},"),
    (29.70, 31.68, "también es muy para el día a día,"),
    (31.95, 33.40, "pero es un poquito más {C}dulzón{/C}."),
    (33.86, 35.02, "Son espectaculares."),
    (35.04, 36.50, "Ambos son muy buenas opciones"),
    (36.52, 37.90, "para esta temporada de {C}calor{/C}"),
    (38.16, 39.60, "y los tenemos disponibles"),
    (39.62, 41.48, "aquí en {N}Perfumería ANVA{/N}."),
]

AQUA = {"slug": "amber-oud-aqua-dubai", "casa": "AL HARAMAIN", "nombre": "AMBER OUD AQUA DUBAI", "glow": (70, 165, 215)}
IMAG = {"slug": "imagination", "casa": "LOUIS VUITTON", "nombre": "IMAGINATION", "glow": (130, 190, 180)}
HAWAS = {"slug": "hawas-ice", "casa": "RASASI", "nombre": "HAWAS ICE", "glow": (120, 150, 205)}

# Insertos a pantalla completa (la voz sigue sonando debajo): (inicio, fin, escena) en tiempo crudo.
INSERTS = [
    (9.00, 11.80, "hero-aqua"),
    (14.05, 16.62, "comparacion"),
    (26.38, 29.10, "hero-hawas"),
]

BONE_ASS = "&H00E3EBEF&"
CHAMP_ASS = "&H0096B8C9&"


def out_time(t):
    """Convierte un tiempo del crudo al tiempo del video editado."""
    acc = 0.0
    for s0, s1, _ in SEGMENTS:
        if t < s0:
            return acc
        if t <= s1:
            return acc + t - s0
        acc += s1 - s0
    return acc


EDIT_LEN = sum(s1 - s0 for s0, s1, _ in SEGMENTS)
TOTAL = EDIT_LEN + END_CARD


# ---------- escenas de producto ----------

def label(layer, text, y, size, fonts, color=mc.CHAMPAGNE, tracking=0.32, weight=400, which=1, cx=mc.W / 2):
    d = ImageDraw.Draw(layer)
    mc.draw_tracked(d, cx, y, text, mc.font(fonts[which], size, weight), color, tracking=tracking)


def scene(name, fotos, fonts):
    """Devuelve (fondo, [(frasco, cx, cy)], capa_texto) de cada escena."""
    txt = Image.new("RGBA", (mc.W, mc.H), (0, 0, 0, 0))
    if name in ("hero-aqua", "hero-hawas"):
        p, num = (AQUA, "N.º 1") if name == "hero-aqua" else (HAWAS, "N.º 2")
        bg = mc.background(p["glow"], cy=690)
        bottles = [(mc.bottle(fotos / f"{p['slug']}.png", 690), mc.W // 2, 680)]
        label(txt, num, 1068, 30, fonts, tracking=0.25, weight=700, which=0)
        mc.text_layer(p, fonts, y=1122, size=68, layer=txt)
    elif name == "comparacion":
        bg = mc.background((95, 178, 200), cy=690)
        bottles = [
            (mc.bottle(fotos / f"{AQUA['slug']}.png", 600), 300, 720),
            (mc.bottle(fotos / f"{IMAG['slug']}.png", 650), 780, 700),
        ]
        mc.text_layer(AQUA, fonts, y=1100, size=40, max_w=430, cx=300, layer=txt)
        mc.text_layer(IMAG, fonts, y=1100, size=40, max_w=430, cx=780, layer=txt)
    else:  # cierre
        bg = mc.background((100, 160, 210), cy=740)
        bottles = [
            (mc.bottle(fotos / f"{AQUA['slug']}.png", 520), 330, 740),
            (mc.bottle(fotos / f"{HAWAS['slug']}.png", 540), 760, 730),
        ]
        label(txt, "¿CON CUÁL TE QUEDAS?", 1150, 62, fonts, color=mc.HUESO, tracking=mc.TRACKING, weight=700, which=0)
        label(txt, "ANVA PERFUMERÍA", 1262, 26, fonts, tracking=0.42)
    return bg, bottles, txt


def render_scene(name, dur, fotos, fonts, out):
    bg, bottles, txt = scene(name, fotos, fonts)
    with tempfile.TemporaryDirectory() as tmp:
        for i in range(round(dur * FPS)):
            t = i / FPS
            frame = bg.convert("RGBA")
            for b, cx, cy in bottles:
                frame.alpha_composite(mc.bottle_layer(b, 1.0 + 0.03 * t / dur, cy, cx=cx))
            a = mc.ease((t - 0.25) / 0.45)
            if a > 0:
                moved = Image.new("RGBA", (mc.W, mc.H), (0, 0, 0, 0))
                moved.alpha_composite(txt, (0, round(10 * (1 - a))))
                moved.putalpha(moved.getchannel("A").point(lambda v: int(v * a)))
                frame.alpha_composite(moved)
            frame.convert("RGB").save(f"{tmp}/{i:04d}.png")
        run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{tmp}/%04d.png",
             "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-pix_fmt", "yuv420p", str(out)])


def gradients(out_dir):
    """Degradado inferior permanente (legibilidad de subtítulos) y superior para el gancho."""
    for name, top in (("grad-bottom.png", False), ("grad-top.png", True)):
        g = Image.new("L", (1, mc.H), 0)
        for y in range(mc.H):
            if top:
                v = max(0.0, 1 - y / 900) ** 1.3 * 0.82
            else:
                v = max(0.0, (y - 1180) / (mc.H - 1180)) ** 1.4 * 0.62
            g.putpixel((0, y), int(255 * v))
        im = Image.new("RGBA", (mc.W, mc.H), mc.NEGRO + (0,))
        im.putalpha(g.resize((mc.W, mc.H)))
        im.save(out_dir / name)


# ---------- subtítulos ----------

def ass_time(t):
    cs = round(t * 100)
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def markup(text):
    def kw(tag, color):
        nonlocal text
        while "{" + tag + "}" in text:
            a = text.index("{" + tag + "}")
            b = text.index("{/" + tag + "}")
            word = text[a + 3 : b].upper()
            text = (text[:a] + r"{\fnJosefin Sans\b1\fs66\fsp3\c" + color + "}" + word + r"{\r}" + text[b + 4 :])
    kw("C", CHAMP_ASS)
    kw("N", BONE_ASS)
    return text


def write_ass(path):
    lines = [
        "[Script Info]", "ScriptType: v4.00+", "PlayResX: 1080", "PlayResY: 1920",
        "WrapStyle: 0", "ScaledBorderAndShadow: yes", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
        "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, "
        "MarginL, MarginR, MarginV, Encoding",
        f"Style: Sub,Arimo,62,{BONE_ASS},{BONE_ASS},&H70000000,&H00000000,0,0,0,0,100,100,1,0,1,3,0,2,110,110,440,1",
        f"Style: Hook,Josefin Sans,84,{BONE_ASS},{BONE_ASS},&H78000000,&H00000000,1,0,0,0,100,100,5,0,1,3,0,8,80,80,300,1",
        "", "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    # Gancho: título breve con lo que se dice en la primera frase.
    lines.append(
        f"Dialogue: 0,{ass_time(0.25)},{ass_time(4.4)},Hook,,0,0,0,,"
        r"{\blur10\fad(350,400)}{\fnArimo\b0\fs38\fsp9\c" + CHAMP_ASS + r"}TEMPORADA DE CALOR\N{\r\blur10}2 PERFUMES ÁRABES"
    )
    for s0, s1, text in SUBS:
        a, b = out_time(s0), out_time(s1)
        lines.append(f"Dialogue: 0,{ass_time(a)},{ass_time(b)},Sub,,0,0,0,,{{\\blur8\\fad(70,50)}}{markup(text)}")
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------- render ----------

def run(cmd):
    subprocess.run(cmd, check=True)


def main(raw, font_dir, fotos, music, out_dir):
    font_dir, fotos, out_dir = Path(font_dir), Path(fotos), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    work = out_dir / "work"
    work.mkdir(exist_ok=True)
    fonts = (font_dir / "JosefinSans.ttf", font_dir / "Arimo.ttf")

    scenes = []
    for s0, s1, name in INSERTS:
        a, b = out_time(s0), out_time(s1)
        scenes.append((a, b - a, work / f"{name}.mp4"))
        render_scene(name, b - a, fotos, fonts, scenes[-1][2])
    scenes.append((EDIT_LEN, END_CARD, work / "cierre.mp4"))
    render_scene("cierre", END_CARD, fotos, fonts, scenes[-1][2])
    gradients(work)
    write_ass(work / "subs.ass")

    inputs, fc = [], []
    for s0, s1, _ in SEGMENTS:
        inputs += ["-ss", f"{s0:.3f}", "-t", f"{s1 - s0:.3f}", "-i", str(raw)]
    n = len(SEGMENTS)
    for i, (s0, s1, z) in enumerate(SEGMENTS):
        w, h = round(1080 * z / 2) * 2, round(1920 * z / 2) * 2
        fc.append(f"[{i}:v]fps={FPS},scale={w}:{h}:flags=lanczos,crop=1080:1920:(iw-1080)/2:(ih-1920)*0.42,"
                  f"setsar=1,setpts=PTS-STARTPTS[v{i}]")
        d = s1 - s0
        fc.append(f"[{i}:a:0]aresample=48000,afade=t=in:d=0.012,afade=t=out:st={d - 0.018:.3f}:d=0.018,"
                  f"asetpts=PTS-STARTPTS[a{i}]")
    fc.append("".join(f"[v{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[vcat]")
    fc.append("".join(f"[a{i}]" for i in range(n)) + f"concat=n={n}:v=0:a=1[acat]")
    # Corrección de color: contraste elegante, altas luces contenidas, saturación algo más baja, piel natural.
    fc.append("[vcat]eq=contrast=1.06:brightness=-0.025:saturation=0.92,"
              "curves=all='0/0 0.18/0.15 0.5/0.49 0.85/0.82 1/0.95',"
              "colorbalance=rm=0.012:bm=-0.012,vignette=angle=0.42,"
              f"tpad=stop_mode=add:stop_duration={END_CARD}:color=0x111111[vg]")

    k = n
    inputs += ["-loop", "1", "-t", f"{TOTAL:.3f}", "-i", str(work / "grad-bottom.png")]
    fc.append(f"[vg][{k}:v]overlay=0:0:shortest=1[vb]")
    k += 1
    inputs += ["-loop", "1", "-t", "4.8", "-i", str(work / "grad-top.png")]
    fc.append(f"[{k}:v]format=rgba,fade=t=in:st=0:d=0.3:alpha=1,fade=t=out:st=4.1:d=0.5:alpha=1[gt]")
    fc.append("[vb][gt]overlay=0:0:eof_action=pass[last]")
    k += 1
    for j, (t0, d, path) in enumerate(scenes):
        inputs += ["-i", str(path)]
        fade_out = "" if path.name == "cierre.mp4" else f",fade=t=out:st={d - 0.22:.3f}:d=0.22:alpha=1"
        fc.append(f"[{k}:v]format=yuva420p,fade=t=in:st=0:d=0.28:alpha=1{fade_out},setpts=PTS-STARTPTS+{t0:.3f}/TB[s{j}]")
        fc.append(f"[last][s{j}]overlay=0:0:eof_action=pass[o{j}]")
        fc.append(f"[o{j}]null[last]")
        k += 1
    subs = str(work / "subs.ass").replace(":", r"\:")
    fc.append(f"[last]subtitles='{subs}':fontsdir='{font_dir / 'static'}',format=yuv420p,split=2[vout][vout2]")

    # Voz: limpieza suave, compresión ligera y normalización a -15 LUFS.
    fc.append("[acat]highpass=f=80,afftdn=nr=8:nf=-42,"
              "acompressor=threshold=-21dB:ratio=2.5:attack=8:release=120:makeup=1.5,"
              "loudnorm=I=-15:TP=-1.5:LRA=8,aresample=48000,"
              f"apad=whole_dur={TOTAL:.3f},asplit=3[voz][key][vozsola]")
    inputs += ["-i", str(music)]
    fc.append(f"[{k}:a]aresample=48000,volume=-12dB,atrim=0:{TOTAL:.3f}[mus]")
    fc.append("[mus][key]sidechaincompress=threshold=0.03:ratio=4:attack=25:release=400[duck]")
    fc.append("[voz][duck]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.89[amix]")
    fc.append("[vozsola]alimiter=limit=0.89[asola]")

    common = ["-c:v", "libx264", "-preset", "slow", "-crf", "17", "-profile:v", "high", "-pix_fmt", "yuv420p",
              "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart"]
    (work / "filter.txt").write_text(";\n".join(fc))
    run(["ffmpeg", "-y", "-loglevel", "error", "-stats", *inputs, "-filter_complex_script", str(work / "filter.txt"),
         "-map", "[vout]", "-map", "[amix]", *common, str(out_dir / "anva-epoca-soleada.mp4"),
         "-map", "[vout2]", "-map", "[asola]", *common, str(out_dir / "anva-epoca-soleada-sin-musica.mp4")])


if __name__ == "__main__":
    main(*sys.argv[1:6])
