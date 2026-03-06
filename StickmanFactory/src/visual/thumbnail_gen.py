"""
thumbnail_gen.py - Sinh thumbnail chuyên nghiệp cho video

Sử dụng Remotion composition riêng (ThumbnailComposition) để render
ảnh thumbnail 1280x720 chuẩn YouTube.
"""

import os
import sys
import json
import subprocess

# Force UTF-8 stdout cho Windows cp1252 terminal
if sys.platform == "nt":
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from src.core.config_loader import load_config, get_nested

REMOTION_DIR = os.path.join(PROJECT_ROOT, "remotion")


def generate_thumbnail(
    title: str,
    output_path: str = None,
    config: dict = None,
    style: str = None,
) -> str:
    """
    Sinh thumbnail bằng Remotion ThumbnailComposition.

    Args:
        title: Tiêu đề video (hiển thị trên thumbnail).
        output_path: Đường dẫn file output. Mặc định: storage/cache/thumbnails/thumbnail.png.
        config: Dict cấu hình.
        style: Style thumbnail (high_contrast, minimal, vibrant).

    Returns:
        Đường dẫn file thumbnail đã sinh.
    """
    if config is None:
        config = load_config()

    if style is None:
        style = get_nested(config, "thumbnail", "style", default="high_contrast")

    enabled = get_nested(config, "thumbnail", "enabled", default=True)
    if not enabled:
        print("  [Thumbnail] Disabled in config. Skipping.")
        return None

    resolution = get_nested(config, "thumbnail", "resolution", default="1280x720")
    width, height = resolution.split("x")

    if output_path is None:
        thumb_dir = os.path.join(PROJECT_ROOT, "storage", "cache", "thumbnails")
        os.makedirs(thumb_dir, exist_ok=True)
        safe_title = "".join(c if c.isalnum() or c in "_ -" else "_" for c in title)
        output_path = os.path.join(thumb_dir, f"{safe_title}.png")

    # Chuẩn bị props cho Remotion
    # Rút gọn title cho Thumbnail (max 5 từ)
    short_title = " ".join(title.split()[:5])
    if len(title.split()) > 5:
        short_title += "..."

    props = {
        "title": short_title,
        "style": style,
        "width": int(width),
        "height": int(height),
    }

    props_path = os.path.join(REMOTION_DIR, "thumbnail_props.json")
    with open(props_path, "w", encoding="utf-8") as f:
        json.dump(props, f, ensure_ascii=False)

    print(f"  [Thumbnail] Rendering: {short_title}")
    print(f"  [Thumbnail] Size: {width}x{height} | Style: {style}")

    npx_cmd = "npx.cmd" if os.name == "nt" else "npx"
    cmd = [
        npx_cmd, "remotion", "still",
        "src/index.ts",
        "ThumbnailComposition",
        output_path,
        f"--props={props_path}",
        f"--width={width}",
        f"--height={height}",
    ]

    try:
        result = subprocess.run(
            cmd,
            cwd=REMOTION_DIR,
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode == 0 and os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"  [Thumbnail] OK: {output_path} ({file_size / 1024:.0f} KB)")
            return output_path
        else:
            print(f"  [Thumbnail] FAILED (exit code: {result.returncode})")
            if result.stderr:
                print(f"  [Thumbnail] Error: {result.stderr[:200]}")
            return None

    except FileNotFoundError:
        print("  [Thumbnail] npx/remotion not found. Skipping thumbnail.")
        return None
    except subprocess.TimeoutExpired:
        print("  [Thumbnail] Timed out (> 120s). Skipping.")
        return None
    except Exception as e:
        print(f"  [Thumbnail] Error: {e}")
        return None


if __name__ == "__main__":
    result = generate_thumbnail("The Hidden Logic of Success")
    if result:
        print(f"\nThumbnail saved: {result}")
    else:
        print("\nThumbnail generation failed or skipped.")
