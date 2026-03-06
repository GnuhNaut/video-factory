"""
renderer.py - Goi Remotion de render video MP4

Doc project_ready.json, truyen props vao Remotion, xuat video.
Toi uu: concurrency, CRF, skip logic.
"""

import os
import sys
import json
import shutil
import subprocess
import time
import logging

# Force UTF-8 stdout cho Windows cp1252 terminal
if sys.platform == "nt":
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from src.core.config_loader import load_config, get_nested

logger = logging.getLogger(__name__)

REMOTION_DIR = os.path.join(PROJECT_ROOT, "remotion")


def render_video(
    project_json_path: str = None,
    output_path: str = None,
    config: dict = None
) -> str:
    """
    Goi Remotion render video MP4 tu project JSON.

    Args:
        project_json_path: Duong dan file JSON (project_ready.json).
        output_path: Duong dan file MP4 output.
        config: Dict cau hinh.

    Returns:
        Duong dan file MP4 da render.
    """
    if config is None:
        config = load_config()

    if project_json_path is None:
        project_json_path = os.path.join(
            PROJECT_ROOT, "storage", "cache", "json", "project_ready.json"
        )

    if not os.path.exists(project_json_path):
        raise FileNotFoundError(f"Project JSON not found: {project_json_path}")

    # Doc project data
    with open(project_json_path, "r", encoding="utf-8") as f:
        project_data = json.load(f)

    # Output path
    if output_path is None:
        output_dir = os.path.join(PROJECT_ROOT, "storage", "renders")
        os.makedirs(output_dir, exist_ok=True)
        title = project_data.get("meta", {}).get("title", "output")
        safe_title = "".join(c if c.isalnum() or c in "_ -" else "_" for c in title)
        output_path = os.path.join(output_dir, f"{safe_title}.mp4")

    # Skip render if exists
    skip_if_exists = get_nested(config, "optimization", "skip_render_if_exists", default=False)
    if skip_if_exists and os.path.exists(output_path):
        file_size = os.path.getsize(output_path)
        if file_size > 0:
            print(f"  [Renderer] SKIP: Output already exists ({file_size / 1024 / 1024:.1f} MB)")
            print(f"  [Renderer] Path: {output_path}")
            logger.info(f"Skipped render - output exists: {output_path}")
            return output_path

    # Chuan bi props cho Remotion
    # Copy cac file sang thu muc public cua remotion de tranh loi security cua Chrome
    public_cache_dir = os.path.join(REMOTION_DIR, "public", "cache")
    os.makedirs(os.path.join(public_cache_dir, "audio"), exist_ok=True)
    os.makedirs(os.path.join(public_cache_dir, "images"), exist_ok=True)

    for scene in project_data.get("scenes", []):
        for key in ["audio_path", "bg_image_path"]:
            path = scene.get(key, "")
            if path:
                if not os.path.isabs(path):
                    src_abs = os.path.abspath(os.path.join(PROJECT_ROOT, path))
                else:
                    src_abs = path

                dest_sub = "audio" if src_abs.endswith(('.wav', '.mp3')) else "images"
                filename = os.path.basename(src_abs)
                dest_abs = os.path.join(public_cache_dir, dest_sub, filename)

                if os.path.exists(src_abs):
                    shutil.copy2(src_abs, dest_abs)

                # Truyen path tuong doi cho Remotion staticFile()
                scene[key] = f"cache/{dest_sub}/{filename}"

    # Luu props tam
    props_path = os.path.join(REMOTION_DIR, "props.json")
    with open(props_path, "w", encoding="utf-8") as f:
        json.dump(project_data, f, ensure_ascii=False)

    # Tinh tong frames
    fps = get_nested(config, "video", "fps",
                     default=get_nested(config, "project", "fps", default=30))
    total_duration = sum(
        s.get("actual_duration", s.get("expected_duration", 5))
        for s in project_data.get("scenes", [])
    )
    total_frames = int(total_duration * fps)

    # Render config
    codec = get_nested(config, "render", "codec", default="h264")
    crf = get_nested(config, "render", "crf", default=23)
    concurrency = get_nested(config, "optimization", "render_concurrency", default=2)

    print("=" * 60)
    print("  [REMOTION RENDERER]")
    print("=" * 60)
    print(f"  Input: {project_json_path}")
    print(f"  Output: {output_path}")
    print(f"  Scenes: {len(project_data.get('scenes', []))}")
    print(f"  Duration: {total_duration:.1f}s ({total_duration/60:.1f} min)")
    print(f"  Frames: {total_frames} @ {fps}fps")
    print(f"  Codec: {codec} | CRF: {crf} | Concurrency: {concurrency}")
    print()

    start_time = time.time()

    # Chay Remotion render
    npx_cmd = "npx.cmd" if os.name == "nt" else "npx"
    cmd = [
        npx_cmd, "remotion", "render",
        "src/index.ts",
        "VideoRoot",
        output_path,
        f"--props={props_path}",
        f"--fps={fps}",
        f"--codec={codec}",
        f"--crf={crf}",
        f"--concurrency={concurrency}",
        "--log=verbose",
    ]

    print(f"  Command: {' '.join(cmd[:6])}...")
    print()

    try:
        result = subprocess.run(
            cmd,
            cwd=REMOTION_DIR,
            capture_output=False,
            text=True,
            timeout=3600,  # 1 hour max
        )

        elapsed = time.time() - start_time

        if result.returncode == 0:
            file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
            print(f"\n{'=' * 60}")
            print(f"  [RENDER COMPLETE]")
            print(f"  Output: {output_path}")
            print(f"  Size: {file_size / 1024 / 1024:.1f} MB")
            print(f"  Render time: {elapsed:.1f}s")
            print(f"{'=' * 60}")
            logger.info(f"Render complete: {output_path} ({file_size/1024/1024:.1f} MB, {elapsed:.1f}s)")
            return output_path
        else:
            print(f"\n[ERROR] Render failed (exit code: {result.returncode})")
            logger.error(f"Remotion render failed: exit code {result.returncode}")
            return None

    except FileNotFoundError:
        print("\n[ERROR] npx/remotion not found. Please run:")
        print("   cd remotion && npm install")
        logger.error("npx or remotion not found")
        return None
    except subprocess.TimeoutExpired:
        print("\n[ERROR] Render timed out (> 1 hour)")
        logger.error("Render timed out")
        return None
    except Exception as e:
        print(f"\n[ERROR] Render error: {e}")
        logger.error(f"Render error: {e}")
        return None


if __name__ == "__main__":
    render_video()
