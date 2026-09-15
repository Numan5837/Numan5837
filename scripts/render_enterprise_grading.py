from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "enterprise-grading.gif"
WIDTH, HEIGHT = 1100, 310
FPS, SECONDS = 8, 8
FRAME_COUNT = FPS * SECONDS


def load_font(name: str, size: int) -> ImageFont.FreeTypeFont:
    for path in (Path("C:/Windows/Fonts") / name, Path("/usr/share/fonts/truetype/dejavu") / name):
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


TITLE = load_font("segoeuib.ttf", 32)
SUBTITLE = load_font("segoeui.ttf", 18)
MONO = load_font("consola.ttf", 15)
MONO_BOLD = load_font("consolab.ttf", 15)
MONO_SMALL = load_font("consola.ttf", 12)

TEAL = (85, 230, 204)
BLUE = (101, 167, 255)
VIOLET = (176, 140, 255)
GREEN = (85, 230, 165)
TEXT = (224, 234, 244)
MUTED = (127, 154, 180)


def mix(a: tuple[int, int, int], b: tuple[int, int, int], ratio: float) -> tuple[int, int, int]:
    return tuple(round(x + (y - x) * ratio) for x, y in zip(a, b))


def base_image() -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT))
    pixels = image.load()
    for x in range(WIDTH):
        ratio = x / (WIDTH - 1)
        color = mix((5, 15, 28), (17, 35, 57), ratio)
        for y in range(HEIGHT):
            shade = 1 - 0.06 * y / HEIGHT
            pixels[x, y] = tuple(round(channel * shade) for channel in color)

    image = image.convert("RGBA")
    draw = ImageDraw.Draw(image, "RGBA")
    for x in range(0, WIDTH, 34):
        draw.line((x, 0, x, HEIGHT), fill=(136, 172, 207, 15))
    for y in range(0, HEIGHT, 34):
        draw.line((0, y, WIDTH, y), fill=(136, 172, 207, 15))
    draw.ellipse((880, -130, 1190, 180), fill=(18, 29, 67, 255))
    draw.ellipse((-120, 215, 180, 515), fill=(7, 35, 40, 255))
    draw.rounded_rectangle((1, 1, WIDTH - 2, HEIGHT - 2), radius=22, outline=(44, 70, 97, 230), width=2)

    draw.text((40, 26), "INFINITY MEGATRON", font=MONO_BOLD, fill=TEAL)
    draw.text((40, 49), "Enterprise grading pipeline", font=TITLE, fill=(244, 248, 253))
    draw.text((40, 90), "PRIVATE R&D · AI-AGENT EVALUATION", font=SUBTITLE, fill=(174, 195, 215))
    infinity_path = []
    for path_index in range(97):
        angle = path_index / 96 * math.tau
        infinity_path.append((960 + 70 * math.cos(angle), 82 + 27 * math.sin(2 * angle)))
    draw.line(infinity_path, fill=(67, 81, 139, 210), width=2, joint="curve")
    draw.text((960, 114), "GRADING CORE", font=MONO_SMALL, anchor="ma", fill=(103, 119, 169))
    draw.rounded_rectangle((40, 119, 1060, 122), radius=2, fill=(50, 76, 101))

    # Pipeline rail and labels.
    node_x = [78, 230, 382, 534, 686, 838, 990]
    draw.line((node_x[0], 167, node_x[-1], 167), fill=(47, 77, 104), width=4)
    labels = ["INGEST", "AUDIT", "CALIBRATE", "GRADE", "TRIALS", "REPORT", "EVIDENCE"]
    for x, label in zip(node_x, labels):
        draw.ellipse((x - 21, 146, x + 21, 188), fill=(10, 30, 48), outline=(55, 84, 109), width=2)
        box = draw.textbbox((0, 0), label, font=MONO_SMALL)
        draw.text((x - (box[2] - box[0]) / 2, 196), label, font=MONO_SMALL, fill=MUTED)

    cards = [
        (40, 228, 350, "VERIFIER AUDIT", "rubric and implementation review", TEAL),
        (395, 228, 705, "PASS@K TRIALS", "on-demand model panels", BLUE),
        (750, 228, 1060, "CALIBRATION", "oracle · no-op · mutation", VIOLET),
    ]
    for x1, y1, x2, heading, caption, color in cards:
        draw.rounded_rectangle((x1, y1, x2, 294), radius=13, fill=(9, 28, 45), outline=(45, 72, 96))
        draw.text((x1 + 17, y1 + 10), heading, font=MONO_BOLD, fill=color)
        draw.text((x1 + 17, y1 + 30), caption, font=MONO_SMALL, fill=(115, 142, 166))
    return image


def glow(image: Image.Image, x: int, y: int, color: tuple[int, int, int], radius: int = 5) -> None:
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")
    draw.ellipse((x - radius * 3, y - radius * 3, x + radius * 3, y + radius * 3), fill=(*color, 85))
    image.alpha_composite(layer.filter(ImageFilter.GaussianBlur(radius * 1.8)))
    draw = ImageDraw.Draw(image, "RGBA")
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*color, 255))


def ease(value: float) -> float:
    value = max(0.0, min(1.0, value))
    return value * value * (3 - 2 * value)


def render_frame(base: Image.Image, index: int) -> Image.Image:
    elapsed = index / FPS
    image = base.copy()
    draw = ImageDraw.Draw(image, "RGBA")
    node_x = [78, 230, 382, 534, 686, 838, 990]
    colors = [TEAL, TEAL, BLUE, TEAL, BLUE, VIOLET, GREEN]

    # A soft scan across the title rule.
    scan = 40 + int((elapsed / SECONDS) * 1020)
    draw.rounded_rectangle((max(40, scan - 70), 119, min(1060, scan + 70), 122), radius=2, fill=(*BLUE, 220))

    # Two particles orbit a continuous infinity path in opposite phases.
    for offset, color in ((0.0, TEAL), (math.pi, VIOLET)):
        angle = elapsed * math.tau / 4.0 + offset
        orbit_x = round(960 + 70 * math.cos(angle))
        orbit_y = round(82 + 27 * math.sin(2 * angle))
        glow(image, orbit_x, orbit_y, color, 4)

    # One gate completes every 0.62 seconds, with a packet moving to the next gate.
    start, step = 0.45, 0.62
    progress = max(0.0, (elapsed - start) / step)
    completed = min(len(node_x), int(progress))
    segment = min(len(node_x) - 2, max(0, int(progress)))
    within = ease(progress - math.floor(progress))

    for node_index, (x, color) in enumerate(zip(node_x, colors)):
        if node_index < completed:
            draw.ellipse((x - 21, 146, x + 21, 188), fill=(13, 43, 59), outline=(*color, 255), width=3)
            draw.line((x - 8, 167, x - 1, 174, x + 11, 158), fill=(*color, 255), width=3, joint="curve")
        elif node_index == completed and elapsed >= start:
            pulse = 1 + 0.15 * math.sin(elapsed * math.tau * 2)
            radius = round(21 * pulse)
            draw.ellipse((x - radius, 167 - radius, x + radius, 167 + radius), fill=(12, 36, 55), outline=(*color, 230), width=3)

    if elapsed >= start and completed < len(node_x):
        if progress < 1:
            packet_x = node_x[0]
        else:
            packet_x = round(node_x[segment] + (node_x[segment + 1] - node_x[segment]) * within)
        glow(image, packet_x, 167, colors[min(segment + 1, len(colors) - 1)], 5)

    # Three workflow cards pulse independently as the pipeline advances.
    card_ranges = [(40, 228, 350, TEAL, 1.2), (395, 228, 705, BLUE, 2.5), (750, 228, 1060, VIOLET, 3.8)]
    for x1, y1, x2, color, card_start in card_ranges:
        if elapsed >= card_start:
            alpha = round(90 + 55 * (0.5 + 0.5 * math.sin((elapsed - card_start) * math.tau / 2.3)))
            draw.rounded_rectangle((x1, y1, x2, 294), radius=13, outline=(*color, alpha), width=2)

    # Each workflow card has its own motion: audit scan, trial samples, and two calibration lanes.
    if elapsed >= 1.2:
        scan_x = 58 + int(((elapsed - 1.2) * 62) % 274)
        draw.rounded_rectangle((scan_x, 283, min(scan_x + 42, 332), 286), radius=1, fill=(*TEAL, 220))
    if elapsed >= 2.5:
        trial_phase = int((elapsed - 2.5) * 3.2)
        for dot_index in range(5):
            color = BLUE if dot_index <= trial_phase % 6 else (55, 76, 98)
            x = 527 + dot_index * 25
            draw.ellipse((x - 5, 279, x + 5, 289), fill=(*color, 245))
    if elapsed >= 3.8:
        lane_phase = ((elapsed - 3.8) * 0.48) % 1.0
        draw.line((930, 279, 1038, 279), fill=(45, 91, 100), width=2)
        draw.line((930, 288, 1038, 288), fill=(55, 80, 119), width=2)
        glow(image, round(930 + lane_phase * 108), 279, TEAL, 3)
        glow(image, round(1038 - lane_phase * 108), 288, BLUE, 3)

    # Final state is held long enough to read.
    if completed >= len(node_x):
        fade = ease((elapsed - (start + step * len(node_x))) / 0.35)
        draw.rounded_rectangle((811, 25, 1060, 58), radius=16, fill=(15, 50, 49, round(235 * fade)), outline=(*GREEN, round(210 * fade)))
        draw.text((935, 34), "PIPELINE TRACE COMPLETE", font=MONO_BOLD, anchor="ma", fill=(*GREEN, round(255 * fade)))
        draw.text((935, 67), "private R&D platform", font=MONO_SMALL, anchor="ma", fill=(138, 169, 194, round(255 * fade)))

    return image.convert("RGB")


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    base = base_image()
    frames_rgb = [render_frame(base, index) for index in range(FRAME_COUNT)]
    palette = frames_rgb[-8].quantize(colors=64, method=Image.Quantize.MEDIANCUT)
    frames = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames_rgb]
    frames[0].save(
        OUTPUT,
        save_all=True,
        append_images=frames[1:],
        duration=round(1000 / FPS),
        loop=0,
        optimize=True,
        disposal=1,
    )
    print(f"wrote {OUTPUT} ({OUTPUT.stat().st_size / 1024:.1f} KiB, {FRAME_COUNT} frames)")


if __name__ == "__main__":
    main()
