"""Genera las tarjetas de producto ANVA (PNG 1080x1920) y los insertos animados (MP4).

Uso: python3 make_cards.py <dir_fuentes> <dir_imagenes> <dir_salida>
  dir_fuentes  : JosefinSans.ttf y Arimo.ttf (variables, Google Fonts)
  dir_imagenes : hawas-ice.png, imagination.png, amber-oud-aqua-dubai.png
"""
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
FPS = 30
DURATION = 3.2

NEGRO = (17, 17, 17)          # #111111
HUESO = (239, 235, 227)       # blanco hueso
CHAMPAGNE = (201, 184, 150)   # acento champagne sutil
TRACKING = 0.095              # interletrado de referencia (0.95 en CapCut ≈ 0.095 em)

# Nombre y casa tal como aparecen en la etiqueta del frasco; sin concentraciones inventadas.
PERFUMES = [
    {"slug": "hawas-ice", "casa": "RASASI", "nombre": "HAWAS ICE", "glow": (120, 150, 205)},
    {"slug": "imagination", "casa": "LOUIS VUITTON", "nombre": "IMAGINATION", "glow": (130, 190, 180)},
    {"slug": "amber-oud-aqua-dubai", "casa": "AL HARAMAIN", "nombre": "AMBER OUD AQUA DUBAI", "glow": (70, 165, 215)},
]


def font(path, size, weight):
    f = ImageFont.truetype(str(path), size)
    f.set_variation_by_axes([weight])
    return f


def tracked_width(draw, text, f, tracking):
    extra = f.size * tracking
    return sum(draw.textlength(c, font=f) for c in text) + extra * (len(text) - 1)


def draw_tracked(draw, cx, y, text, f, fill, tracking=TRACKING):
    x = cx - tracked_width(draw, text, f, tracking) / 2
    for c in text:
        draw.text((x, y), c, font=f, fill=fill)
        x += draw.textlength(c, font=f) + f.size * tracking


def fit_size(draw, text, path, weight, start, max_w):
    size = start
    while size > 30 and tracked_width(draw, text, font(path, size, weight), TRACKING) > max_w:
        size -= 2
    return size


def background(glow, cy=780):
    """Negro absoluto con un halo de luz muy suave del color de la fragancia."""
    bg = Image.new("RGB", (W, H), NEGRO)
    halo = Image.new("L", (W, H), 0)
    ImageDraw.Draw(halo).ellipse((W / 2 - 430, cy - 400, W / 2 + 430, cy + 400), fill=255)
    halo = halo.filter(ImageFilter.GaussianBlur(170))
    tint = Image.new("RGB", (W, H), glow)
    return Image.composite(tint, bg, halo.point(lambda v: int(v * 0.16)))


def bottle(src, target_h):
    im = Image.open(src).convert("RGBA")
    # recorta al contenido visible (el PNG ya trae el fondo transparente)
    im = im.crop(im.getchannel("A").point(lambda v: 255 if v > 20 else 0).getbbox())
    scale = target_h / im.height
    return im.resize((round(im.width * scale), target_h), Image.LANCZOS)


def bottle_layer(b, scale, cy, cx=W // 2):
    """Frasco + sombra de contacto + reflejo tenue, centrados en el lienzo."""
    if scale != 1:
        b = b.resize((round(b.width * scale), round(b.height * scale)), Image.LANCZOS)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    x, y = cx - b.width // 2, cy - b.height // 2
    base = y + b.height

    shadow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(shadow).ellipse((cx - b.width * 0.42, base - 18, cx + b.width * 0.42, base + 22), fill=150)
    shadow = shadow.filter(ImageFilter.GaussianBlur(22))
    layer = Image.composite(Image.new("RGBA", (W, H), (0, 0, 0, 255)), layer, shadow)

    refl = b.transpose(Image.FLIP_TOP_BOTTOM)
    refl = refl.crop((0, 0, refl.width, round(refl.height * 0.2)))
    fade = Image.linear_gradient("L").resize(refl.size).point(lambda v: int(55 * (1 - v / 255) ** 2))
    refl.putalpha(ImageChops.multiply(refl.getchannel("A"), fade))
    layer.alpha_composite(refl, (x, base + 4))
    layer.alpha_composite(b, (x, y))
    return layer


def text_layer(p, fonts, y=1352, max_w=W - 2 * 110, cx=W / 2, size=76, layer=None):
    layer = layer or Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    josefin, arimo = fonts
    size = fit_size(d, p["nombre"], josefin, 700, size, max_w)
    casa = font(arimo, round(size * 0.4), 400)
    draw_tracked(d, cx, y, p["casa"], casa, CHAMPAGNE, tracking=0.32)
    d.line((cx - 36, y + size * 0.74, cx + 36, y + size * 0.74), fill=CHAMPAGNE, width=2)
    draw_tracked(d, cx, y + size * 1.11, p["nombre"], font(josefin, size, 700), HUESO)
    return layer


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def main(font_dir, img_dir, out_dir):
    font_dir, img_dir, out_dir = Path(font_dir), Path(img_dir), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    fonts = (font_dir / "JosefinSans.ttf", font_dir / "Arimo.ttf")
    for p in PERFUMES:
        bg = background(p["glow"])
        b = bottle(img_dir / f"{p['slug']}.png", 760)
        txt = text_layer(p, fonts)

        card = bg.convert("RGBA")
        card.alpha_composite(bottle_layer(b, 1.0, 820))
        card.alpha_composite(txt)
        card.convert("RGB").save(out_dir / f"tarjeta-{p['slug']}.png")

        # Inserto animado: fundido desde negro, empuje lento del frasco y texto que asciende 12 px.
        with tempfile.TemporaryDirectory() as tmp:
            n = round(DURATION * FPS)
            for i in range(n):
                t = i / FPS
                frame = bg.convert("RGBA")
                frame.alpha_composite(bottle_layer(b, 1.0 + 0.035 * (t / DURATION), 820))
                a = ease((t - 0.35) / 0.5)
                if a > 0:
                    moved = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                    moved.alpha_composite(txt, (0, round(12 * (1 - a))))
                    moved.putalpha(moved.getchannel("A").point(lambda v: int(v * a)))
                    frame.alpha_composite(moved)
                fade = min(ease(t / 0.3), ease((DURATION - t) / 0.3))
                frame = Image.blend(Image.new("RGB", (W, H), NEGRO), frame.convert("RGB"), fade)
                frame.save(f"{tmp}/{i:04d}.png")
            subprocess.run(
                ["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{tmp}/%04d.png",
                 "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p",
                 "-movflags", "+faststart", str(out_dir / f"inserto-{p['slug']}.mp4")],
                check=True,
            )
        print("ok", p["slug"])


if __name__ == "__main__":
    main(*sys.argv[1:4])
