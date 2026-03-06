"""
bg_generator.py - Sinh ảnh background placeholder bằng PIL

Tạo ảnh nền gradient + text từ bg_prompt mà không cần AI.
Dùng seed cố định để đảm bảo đồng bộ phong cách.
"""

import os
import sys
import random
import math

# Force UTF-8 stdout cho Windows cp1252 terminal
if sys.platform == "nt":
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    Image = None

# Kích thước chuẩn
WIDTH = 1920
HEIGHT = 1080


def _seed_colors(seed: int):
    """Sinh 2 màu gradient dựa trên seed."""
    rng = random.Random(seed)
    # Tạo màu đậm phía trên, nhạt hơn phía dưới
    c1 = (rng.randint(10, 80), rng.randint(10, 80), rng.randint(80, 180))
    c2 = (rng.randint(5, 40), rng.randint(5, 40), rng.randint(40, 120))
    return c1, c2


def _draw_gradient(img: Image.Image, c1: tuple, c2: tuple):
    """Vẽ gradient dọc từ c1 (trên) đến c2 (dưới)."""
    draw = ImageDraw.Draw(img)
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(c1[0] + (c2[0] - c1[0]) * t)
        g = int(c1[1] + (c2[1] - c1[1]) * t)
        b = int(c1[2] + (c2[2] - c1[2]) * t)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def _draw_decorative_shapes(img: Image.Image, seed: int):
    """Vẽ hình trang trí nhẹ (circles, lines) dựa trên seed."""
    draw = ImageDraw.Draw(img)
    rng = random.Random(seed + 100)

    # Vẽ vài hình tròn mờ
    for _ in range(rng.randint(3, 7)):
        cx = rng.randint(100, WIDTH - 100)
        cy = rng.randint(100, HEIGHT - 100)
        radius = rng.randint(50, 200)
        alpha = rng.randint(15, 40)
        color = (255, 255, 255, alpha)

        # Vẽ hình tròn mờ bằng overlay
        overlay = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.ellipse(
            [cx - radius, cy - radius, cx + radius, cy + radius],
            fill=color
        )
        img.paste(Image.alpha_composite(
            img.convert('RGBA'), overlay
        ).convert('RGB'))


def _get_font(size: int):
    """Lấy font, fallback nếu không có system font."""
    font_names = ["arial.ttf", "Arial.ttf", "DejaVuSans.ttf", "FreeSans.ttf"]
    for name in font_names:
        try:
            return ImageFont.truetype(name, size)
        except (OSError, IOError):
            continue

    # Thử load từ assets/fonts/
    fonts_dir = os.path.join(PROJECT_ROOT, "assets", "fonts")
    if os.path.isdir(fonts_dir):
        for f in os.listdir(fonts_dir):
            if f.endswith(('.ttf', '.otf')):
                try:
                    return ImageFont.truetype(os.path.join(fonts_dir, f), size)
                except (OSError, IOError):
                    continue

    # Fallback
    return ImageFont.load_default()


def _draw_text_with_outline(draw, position, text, font, fill='white',
                            outline='black', outline_width=2):
    """Vẽ text có viền đen để dễ đọc trên mọi nền."""
    x, y = position
    # Vẽ viền
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, fill=outline, font=font)
    # Vẽ text chính
    draw.text((x, y), text, fill=fill, font=font)


def _wrap_text(text: str, font, max_width: int, draw) -> list:
    """Ngắt dòng text để vừa khung."""
    words = text.split()
    lines = []
    current = ""

    for word in words:
        test = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)
    return lines


def generate_placeholder(
    prompt: str,
    seed: int,
    scene_id: int,
    output_path: str,
    show_text: bool = True,
    show_id: bool = True
) -> str:
    """
    Sinh ảnh background placeholder dạng gradient + text.

    Args:
        prompt: Mô tả scene (bg_prompt).
        seed: Seed để đồng bộ màu sắc.
        scene_id: ID scene (hiện ở góc trên).
        output_path: Đường dẫn file PNG đầu ra.
        show_text: Hiện prompt text lên ảnh.
        show_id: Hiện scene ID góc trên.

    Returns:
        Đường dẫn file đã sinh.
    """
    if Image is None:
        raise ImportError("Pillow is required. Install: pip install Pillow")

    # Tạo ảnh
    img = Image.new('RGB', (WIDTH, HEIGHT))

    # Vẽ gradient
    c1, c2 = _seed_colors(seed)
    _draw_gradient(img, c1, c2)

    draw = ImageDraw.Draw(img)

    # Vẽ prompt text ở giữa
    if show_text and prompt:
        font_main = _get_font(36)
        max_text_width = WIDTH - 200

        lines = _wrap_text(prompt, font_main, max_text_width, draw)

        # Tính tổng chiều cao
        line_height = 50
        total_height = len(lines) * line_height
        start_y = (HEIGHT - total_height) // 2

        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font_main)
            text_w = bbox[2] - bbox[0]
            x = (WIDTH - text_w) // 2
            y = start_y + i * line_height
            _draw_text_with_outline(draw, (x, y), line, font_main)

    # Vẽ Scene ID góc trên trái
    if show_id:
        font_id = _get_font(28)
        _draw_text_with_outline(draw, (30, 25), f"Scene {scene_id}", font_id,
                                fill='#FFFFFF80', outline='black', outline_width=1)

    # Vẽ khung mỏng
    draw.rectangle([0, 0, WIDTH - 1, HEIGHT - 1], outline=(255, 255, 255, 40), width=1)

    # Lưu
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    img.save(output_path, "PNG")

    return output_path


def generate_batch(scenes: list, output_dir: str = None, config: dict = None) -> list:
    """
    Sinh placeholder cho tất cả scenes.

    Args:
        scenes: List scene dicts.
        output_dir: Thư mục output. Mặc định: storage/cache/images/.
        config: Dict cấu hình.

    Returns:
        List scenes đã cập nhật bg_image_path.
    """
    if output_dir is None:
        output_dir = os.path.join(PROJECT_ROOT, "storage", "cache", "images")
    os.makedirs(output_dir, exist_ok=True)

    # Đọc config placeholder
    show_text = True
    show_id = True
    if config:
        from src.core.config_loader import get_nested
        show_text = get_nested(config, "image_provider", "placeholder",
                               "show_prompt_text", default=True)

    total = len(scenes)
    for i, scene in enumerate(scenes):
        scene_id = scene.get("scene_id", i + 1)
        prompt = scene.get("bg_prompt", "")
        seed = scene.get("bg_seed", 42)

        filename = f"bg_{scene_id:03d}.png"
        output_path = os.path.join(output_dir, filename)

        generate_placeholder(
            prompt=prompt,
            seed=seed,
            scene_id=scene_id,
            output_path=output_path,
            show_text=show_text,
            show_id=show_id
        )

        scene["bg_image_path"] = output_path
        print(f"  [{i+1}/{total}] bg_{scene_id:03d}.png ✅")

    print(f"\n✅ Generated {total} placeholder images in {output_dir}")
    return scenes


def _run_tests():
    """Test: Sinh ảnh placeholder cho 3 scenes mẫu."""
    print("=" * 60)
    print("  BACKGROUND GENERATOR - Test")
    print("=" * 60)

    test_scenes = [
        {"scene_id": 1, "bg_prompt": "Abstract background with question marks, soft blue tones, minimalist", "bg_seed": 1001},
        {"scene_id": 2, "bg_prompt": "Pattern geometry background, golden ratio spiral, clean style", "bg_seed": 1001},
        {"scene_id": 3, "bg_prompt": "Three pillars illustration, minimalist icons, white background", "bg_seed": 1001},
    ]

    output_dir = os.path.join(PROJECT_ROOT, "storage", "cache", "images")
    scenes = generate_batch(test_scenes, output_dir=output_dir)

    for s in scenes:
        path = s.get("bg_image_path", "")
        if os.path.exists(path):
            size = os.path.getsize(path)
            img = Image.open(path)
            print(f"  Scene {s['scene_id']}: {img.size} ({size:,} bytes)")
        else:
            print(f"  Scene {s['scene_id']}: ❌ File not found")

    print("=" * 60)


if __name__ == "__main__":
    if "--test" in sys.argv:
        _run_tests()
    else:
        print("Usage: python src/visual/bg_generator.py --test")
