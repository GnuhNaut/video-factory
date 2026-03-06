"""
batch_processor.py - Sinh audio hàng loạt từ JSON scenes

Duyệt qua từng scene, gọi Kokoro TTS để sinh file WAV,
cập nhật audio_path vào scene object.
"""

import os
import sys
import logging
from datetime import datetime

if sys.platform == "nt":
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from src.audio.kokoro_wrapper import KokoroWrapper
from src.core.config_loader import load_config, get_nested

logger = logging.getLogger(__name__)


def generate_all_audio(
    scenes: list,
    output_dir: str = None,
    config: dict = None,
    voice_id: str = None,
    speed: float = 1.0
) -> list:
    """
    Sinh audio cho tất cả scenes.

    Args:
        scenes: List các scene dict (phải có 'scene_id' và 'text').
        output_dir: Thư mục lưu file WAV. Mặc định: storage/cache/audio/.
        config: Dict cấu hình. Nếu None, tự load.
        voice_id: ID giọng đọc. Mặc định từ config.
        speed: Tốc độ đọc (1.0 = bình thường).

    Returns:
        List scenes đã cập nhật audio_path và actual_duration.
    """
    if config is None:
        config = load_config()

    if output_dir is None:
        output_dir = os.path.join(PROJECT_ROOT, "storage", "cache", "audio")
    os.makedirs(output_dir, exist_ok=True)

    # Lấy voice từ config nếu không chỉ định
    if voice_id is None:
        voice_id = get_nested(config, "models", "kokoro_voice", default="af_bella")
        # Hoặc từ meta trong data
        meta_voice = None
        # voice_id đã có từ config, giữ nguyên

    # Khởi tạo Kokoro wrapper (load model 1 lần)
    tts = KokoroWrapper(config=config)

    total = len(scenes)
    success = 0
    failed = 0

    # Thử import tqdm cho progress bar
    try:
        from tqdm import tqdm
        scene_iter = tqdm(scenes, desc="Generating audio", unit="scene")
    except ImportError:
        print("[TIP] Install tqdm for progress bar: pip install tqdm")
        scene_iter = scenes

    for i, scene in enumerate(scene_iter):
        scene_id = scene.get("scene_id", i + 1)
        text = scene.get("text", "")

        if not text.strip():
            logger.warning(f"Scene {scene_id}: Empty text, skipping")
            continue

        # Tên file: audio_001.wav, audio_002.wav, ...
        filename = f"audio_{scene_id:03d}.wav"
        output_path = os.path.join(output_dir, filename)

        try:
            # Sinh audio
            duration = tts.generate_audio(
                text=text,
                output_path=output_path,
                voice_id=voice_id,
                speed=speed
            )

            # Cập nhật scene
            scene["audio_path"] = output_path
            scene["actual_duration"] = round(duration, 2)
            success += 1

            # Progress info (nếu không có tqdm)
            if not hasattr(scene_iter, 'set_postfix'):
                print(f"  [{success}/{total}] Scene {scene_id}: {duration:.2f}s")

        except Exception as e:
            logger.error(f"Scene {scene_id} failed: {e}")
            print(f"  [FAIL] Scene {scene_id} failed: {e}")
            scene["audio_path"] = ""
            scene["actual_duration"] = 0
            failed += 1

    # Summary
    print(f"\n{'=' * 50}")
    print(f"  Audio Generation Complete")
    print(f"  Success: {success}/{total}")
    if failed > 0:
        print(f"  Failed: {failed}/{total}")
    total_duration = sum(s.get("actual_duration", 0) for s in scenes)
    print(f"  Total duration: {total_duration:.1f}s ({total_duration/60:.1f} min)")
    print(f"  Output: {output_dir}")
    print(f"{'=' * 50}")

    return scenes


if __name__ == "__main__":
    import json

    print("Loading sample project...")
    from src.script.generator import get_script

    data = get_script()
    scenes = data["scenes"]

    print(f"\nGenerating audio for {len(scenes)} scenes...")
    updated_scenes = generate_all_audio(scenes)

    # Hiện kết quả
    for s in updated_scenes:
        print(f"  Scene {s['scene_id']}: {s.get('actual_duration', 0):.2f}s - {s.get('audio_path', 'N/A')}")
