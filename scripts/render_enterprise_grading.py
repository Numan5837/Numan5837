from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "enterprise-grading.gif"
WIDTH, HEIGHT = 1200, 300
FPS, SECONDS = 12, 10
FRAME_COUNT = FPS * SECONDS


def load_font(name: str, size: int) -> ImageFont.FreeTypeFont:
    for path in (
        Path("C:/Windows/Fonts") / name,
        Path("/usr/share/fonts/truetype/dejavu") / name,
    ):
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


TITLE = load_font("segoeuib.ttf", 40)
SUBTITLE = load_font("segoeui.ttf", 20)
MONO_BOLD = load_font("consolab.ttf", 20)
MONO = load_font("consola.ttf", 19)
MONO_SMALL_BOLD = load_font("consolab.ttf", 18)

BACKGROUND_LEFT = (5, 16, 27)
BACKGROUND_RIGHT = (10, 32, 49)
BORDER = (40, 70, 93)
TEAL = (105, 230, 207)
BLUE = (120, 167, 255)
GREEN = (93, 224, 170)
TEXT = (244, 247, 251)
MUTED = (167, 182, 199)
RAIL = BORDER

NODE_X = [105, 352, 600, 848, 1095]
NODE_Y = 182
NODE_RADIUS = 22
STAGES = ["TASK", "AUDIT", "CALIBRATE", "GRADE", "EVIDENCE"]
CAPTIONS = [
    "Load rubric and artifact",
    "Inspect verifier behavior",
    "Run oracle · no-op · mutations",
    "Execute repeatable Pass@k trials",
    "Package scores and failure traces",
]
ARRIVALS = [0.45, 1.85, 3.25, 4.65, 6.05]
TRAVEL_STARTS = [1.35, 2.75, 4.15, 5.55]
COMPLETE_AT = 6.95


def mix(
    a: tuple[int, int, int],
    b: tuple[int, int, int],
    amount: float,
) -> tuple[int, int, int]:
    return tuple(round(x + (y - x) * amount) for x, y in zip(a, b))


def ease(value: float) -> float:
    value = max(0.0, min(1.0, value))
    return value * value * (3.0 - 2.0 * value)


def make_background() -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT))
    pixels = image.load()
    for x in range(WIDTH):
        horizontal = x / (WIDTH - 1)
        color = mix(BACKGROUND_LEFT, BACKGROUND_RIGHT, horizontal)
        for y in range(HEIGHT):
            vertical = 1.0 - 0.055 * (y / HEIGHT)
            pixels[x, y] = tuple(round(channel * vertical) for channel in color)

    draw = ImageDraw.Draw(image, "RGBA")
    draw.ellipse((870, -210, 1330, 250), fill=(66, 126, 190, 13))
    draw.ellipse((-190, 210, 300, 700), fill=(63, 205, 180, 8))
    draw.rounded_rectangle(
        (1, 1, WIDTH - 2, HEIGHT - 2),
        radius=22,
        outline=(*BORDER, 230),
        width=2,
    )
    return image.convert("RGBA")


def draw_infinity_mark(draw: ImageDraw.ImageDraw) -> None:
    points = []
    for point_index in range(97):
        angle = point_index / 96 * math.tau
        points.append(
            (
                1045 + 60 * math.cos(angle),
                70 + 23 * math.sin(2 * angle),
            )
        )
    draw.line(points, fill=(102, 132, 166, 175), width=2, joint="curve")


def draw_centered_text(
    draw: ImageDraw.ImageDraw,
    center_x: int,
    y: int,
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int, int],
) -> None:
    bounds = draw.textbbox((0, 0), text, font=font)
    width = bounds[2] - bounds[0]
    draw.text((center_x - width / 2, y), text, font=font, fill=fill)


def draw_static() -> Image.Image:
    image = make_background()
    draw = ImageDraw.Draw(image, "RGBA")

    draw.text(
        (66, 29),
        "INFINITY MEGATRON · PRIVATE R&D",
        font=MONO_SMALL_BOLD,
        fill=(*TEAL, 255),
    )
    draw.text(
        (66, 53),
        "Enterprise grading",
        font=TITLE,
        fill=(244, 248, 253, 255),
    )
    draw.text(
        (66, 103),
        "Auditable evaluation from task intake to evidence",
        font=SUBTITLE,
        fill=(190, 207, 222, 255),
    )
    draw_infinity_mark(draw)

    draw.rounded_rectangle((66, 135, 1134, 138), radius=2, fill=RAIL)
    draw.line((NODE_X[0], NODE_Y, NODE_X[-1], NODE_Y), fill=RAIL, width=4)

    for center_x, label in zip(NODE_X, STAGES):
        draw.ellipse(
            (
                center_x - NODE_RADIUS,
                NODE_Y - NODE_RADIUS,
                center_x + NODE_RADIUS,
                NODE_Y + NODE_RADIUS,
            ),
            fill=(9, 27, 44, 255),
            outline=(61, 89, 114, 255),
            width=3,
        )
        draw_centered_text(
            draw,
            center_x,
            210,
            label,
            MONO_BOLD,
            (*MUTED, 255),
        )

    draw.rounded_rectangle(
        (66, 240, 1134, 286),
        radius=12,
        fill=(7, 21, 35, 245),
        outline=(48, 75, 103, 255),
        width=2,
    )
    draw.line((286, 249, 286, 277), fill=(48, 75, 103, 255), width=2)
    return image


def glow_dot(
    image: Image.Image,
    center_x: int,
    center_y: int,
    color: tuple[int, int, int],
    opacity: float,
) -> None:
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")
    alpha = round(70 * opacity)
    draw.ellipse(
        (center_x - 12, center_y - 12, center_x + 12, center_y + 12),
        fill=(*color, alpha),
    )
    image.alpha_composite(layer.filter(ImageFilter.GaussianBlur(7)))
    draw = ImageDraw.Draw(image, "RGBA")
    draw.ellipse(
        (center_x - 5, center_y - 5, center_x + 5, center_y + 5),
        fill=(*color, round(245 * opacity)),
    )


def current_stage(elapsed: float) -> int:
    stage_index = 0
    for index, arrival in enumerate(ARRIVALS):
        if elapsed >= arrival:
            stage_index = index
    return stage_index


def packet_position(elapsed: float) -> float:
    if elapsed < TRAVEL_STARTS[0]:
        return float(NODE_X[0])
    for index, travel_start in enumerate(TRAVEL_STARTS):
        travel_end = ARRIVALS[index + 1]
        if elapsed < travel_end:
            progress = ease((elapsed - travel_start) / (travel_end - travel_start))
            return NODE_X[index] + (NODE_X[index + 1] - NODE_X[index]) * progress
        if index + 1 < len(TRAVEL_STARTS) and elapsed < TRAVEL_STARTS[index + 1]:
            return float(NODE_X[index + 1])
    return float(NODE_X[-1])


def detail_alpha(elapsed: float, stage_index: int) -> float:
    fade = ease((elapsed - ARRIVALS[stage_index]) / 0.16)
    if stage_index < len(STAGES) - 1:
        fade *= ease((ARRIVALS[stage_index + 1] - elapsed) / 0.16)
    else:
        fade *= ease((COMPLETE_AT - elapsed) / 0.16)
    return fade


def draw_detail_strip(
    draw: ImageDraw.ImageDraw,
    heading: str,
    caption: str,
    step: str,
    color: tuple[int, int, int],
    opacity: float,
) -> None:
    alpha = round(255 * opacity)
    draw.text((86, 251), heading, font=MONO_BOLD, fill=(*color, alpha))
    draw.text((310, 252), caption, font=MONO, fill=(*TEXT, alpha))
    draw.text(
        (1114, 251),
        step,
        font=MONO_SMALL_BOLD,
        anchor="ra",
        fill=(*MUTED, alpha),
    )


def render_frame(base: Image.Image, frame_index: int) -> Image.Image:
    elapsed = frame_index / FPS
    image = base.copy()
    motion = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(motion, "RGBA")

    loop_opacity = min(
        ease(elapsed / 0.45),
        ease((SECONDS - elapsed) / 0.45),
    )
    stage_index = current_stage(elapsed)
    packet_x = packet_position(elapsed)

    # The filled rail and packet are the single continuous motion through the system.
    progress_color = GREEN if elapsed >= COMPLETE_AT else TEAL
    draw.line(
        (NODE_X[0], NODE_Y, round(packet_x), NODE_Y),
        fill=(*progress_color, round(230 * loop_opacity)),
        width=4,
    )

    for index, center_x in enumerate(NODE_X):
        completed_at = TRAVEL_STARTS[index] if index < len(TRAVEL_STARTS) else COMPLETE_AT
        if elapsed >= completed_at:
            draw.ellipse(
                (
                    center_x - NODE_RADIUS,
                    NODE_Y - NODE_RADIUS,
                    center_x + NODE_RADIUS,
                    NODE_Y + NODE_RADIUS,
                ),
                fill=(12, 42, 53, round(255 * loop_opacity)),
                outline=(*GREEN, round(255 * loop_opacity)),
                width=3,
            )
            draw.line(
                (
                    center_x - 9,
                    NODE_Y,
                    center_x - 2,
                    NODE_Y + 7,
                    center_x + 11,
                    NODE_Y - 9,
                ),
                fill=(*GREEN, round(255 * loop_opacity)),
                width=4,
                joint="curve",
            )
        elif index == stage_index:
            arrival = ARRIVALS[index]
            pulse_progress = max(0.0, min(1.0, (elapsed - arrival) / 0.30))
            pulse_radius = NODE_RADIUS + round(5 * math.sin(pulse_progress * math.pi))
            draw.ellipse(
                (
                    center_x - pulse_radius,
                    NODE_Y - pulse_radius,
                    center_x + pulse_radius,
                    NODE_Y + pulse_radius,
                ),
                fill=(10, 34, 51, round(245 * loop_opacity)),
                outline=(*BLUE, round(255 * loop_opacity)),
                width=3,
            )

    if elapsed < COMPLETE_AT:
        glow_dot(
            motion,
            round(packet_x),
            NODE_Y,
            BLUE,
            loop_opacity,
        )

    if elapsed < COMPLETE_AT:
        opacity = detail_alpha(elapsed, stage_index) * loop_opacity
        draw_detail_strip(
            draw,
            STAGES[stage_index],
            CAPTIONS[stage_index],
            f"STEP {stage_index + 1} / 5",
            TEAL,
            opacity,
        )
    else:
        ready_opacity = ease((elapsed - COMPLETE_AT) / 0.16) * loop_opacity
        draw.rounded_rectangle(
            (66, 240, 1134, 286),
            radius=12,
            outline=(*GREEN, round(210 * ready_opacity)),
            width=2,
        )
        draw_detail_strip(
            draw,
            "EVIDENCE READY",
            "scores · traces · audit metadata packaged",
            "5 / 5",
            GREEN,
            ready_opacity,
        )

    image.alpha_composite(motion)
    return image.convert("RGB")


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    base = draw_static()
    raw_frames = [render_frame(base, index) for index in range(FRAME_COUNT)]
    palette = raw_frames[-8].quantize(colors=64, method=Image.Quantize.MEDIANCUT)
    frames = [
        frame.quantize(palette=palette, dither=Image.Dither.NONE)
        for frame in raw_frames
    ]
    frames[0].save(
        OUTPUT,
        save_all=True,
        append_images=frames[1:],
        duration=[80 if index % 3 != 2 else 90 for index in range(FRAME_COUNT)],
        loop=0,
        optimize=True,
        disposal=1,
    )
    print(
        f"wrote {OUTPUT} "
        f"({OUTPUT.stat().st_size / 1024:.1f} KiB, {FRAME_COUNT} frames)"
    )


if __name__ == "__main__":
    main()
