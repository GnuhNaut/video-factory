"""
parallel.py - Xử lý Audio song song bằng ThreadPoolExecutor

Tăng tốc sinh audio bằng cách chạy nhiều worker đồng thời.
Giới hạn max_workers để không quá tải RAM/GPU.
"""

import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from src.core.config_loader import load_config, get_nested
from src.core.cache_manager import calculate_hash, check_cache, update_cache


def _generate_single_audio(args: dict) -> dict:
    """
    Worker function: sinh audio cho 1 scene.

    Args:
        args: Dict chứa scene, tts, output_dir, voice_id, speed.

    Returns:
        Dict kết quả {scene_id, success, duration, output_path, error}.
    """
    scene = args["scene"]
    tts = args["tts"]
    output_dir = args["output_dir"]
    voice_id = args["voice_id"]
    speed = args["speed"]
    cache_enabled = args.get("cache_enabled", False)

    scene_id = scene.get("scene_id", 0)
    text = scene.get("text", "")

    if not text.strip():
        return {"scene_id": scene_id, "success": False, "duration": 0,
                "output_path": "", "error": "Empty text", "skipped": True}

    filename = f"audio_{scene_id:03d}.wav"
    output_path = os.path.join(output_dir, filename)

    # Check cache
    if cache_enabled:
        audio_hash = calculate_hash(scene, "audio")
        if check_cache(scene_id, audio_hash, "audio", output_path):
            # Cache hit - đọc duration từ file đã tồn tại
            try:
                import soundfile as sf
                data, sr = sf.read(output_path)
                duration = len(data) / sr
            except Exception:
                duration = scene.get("actual_duration", 0)

            return {"scene_id": scene_id, "success": True, "duration": duration,
                    "output_path": output_path, "error": None, "skipped": True,
                    "cache_hit": True}

    try:
        duration = tts.generate_audio(
            text=text,
            output_path=output_path,
            voice_id=voice_id,
            speed=speed
        )

        # Update cache
        if cache_enabled:
            audio_hash = calculate_hash(scene, "audio")
            update_cache(scene_id, audio_hash, "audio")

        return {"scene_id": scene_id, "success": True, "duration": duration,
                "output_path": output_path, "error": None, "skipped": False}

    except Exception as e:
        return {"scene_id": scene_id, "success": False, "duration": 0,
                "output_path": "", "error": str(e), "skipped": False}


def generate_audio_parallel(
    scenes: list,
    output_dir: str = None,
    config: dict = None,
    voice_id: str = None,
    speed: float = 1.0,
    max_workers: int = None,
) -> list:
    """
    Sinh audio cho tất cả scenes bằng ThreadPoolExecutor.

    Args:
        scenes: List scene dicts.
        output_dir: Thư mục lưu file WAV.
        config: Dict cấu hình.
        voice_id: ID giọng đọc.
        speed: Tốc độ đọc.
        max_workers: Số worker tối đa. Mặc định từ config.

    Returns:
        List scenes đã cập nhật audio_path và actual_duration.
    """
    from src.audio.kokoro_wrapper import KokoroWrapper

    if config is None:
        config = load_config()

    if output_dir is None:
        output_dir = os.path.join(PROJECT_ROOT, "storage", "cache", "audio")
    os.makedirs(output_dir, exist_ok=True)

    if voice_id is None:
        voice_id = get_nested(config, "models", "kokoro_voice", default="af_bella")

    if max_workers is None:
        max_workers = get_nested(config, "optimization", "audio_parallel_workers", default=4)

    cache_enabled = get_nested(config, "optimization", "cache_enabled", default=False)

    # Load model 1 lần (chia sẻ giữa các worker)
    tts = KokoroWrapper(config=config)

    total = len(scenes)
    success = 0
    skipped = 0
    failed = 0

    # Chuẩn bị args cho workers
    work_items = []
    for scene in scenes:
        work_items.append({
            "scene": scene,
            "tts": tts,
            "output_dir": output_dir,
            "voice_id": voice_id,
            "speed": speed,
            "cache_enabled": cache_enabled,
        })

    print(f"  [Parallel] Workers: {max_workers} | Scenes: {total} | Cache: {'ON' if cache_enabled else 'OFF'}")

    # Progress tracking
    try:
        from tqdm import tqdm
        progress = tqdm(total=total, desc="Generating audio", unit="scene")
    except ImportError:
        progress = None

    results = [None] * total

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_idx = {
            executor.submit(_generate_single_audio, item): i
            for i, item in enumerate(work_items)
        }

        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            try:
                result = future.result()
                results[idx] = result

                if result["success"]:
                    scenes[idx]["audio_path"] = result["output_path"]
                    scenes[idx]["actual_duration"] = round(result["duration"], 2)
                    if result.get("cache_hit"):
                        skipped += 1
                    else:
                        success += 1
                else:
                    scenes[idx]["audio_path"] = ""
                    scenes[idx]["actual_duration"] = 0
                    if not result.get("skipped"):
                        failed += 1

            except Exception as e:
                scenes[idx]["audio_path"] = ""
                scenes[idx]["actual_duration"] = 0
                failed += 1

            if progress:
                progress.update(1)

    if progress:
        progress.close()

    # Summary
    total_duration = sum(s.get("actual_duration", 0) for s in scenes)
    print(f"\n{'=' * 50}")
    print(f"  Audio Generation Complete (Parallel)")
    print(f"  Generated: {success}/{total}")
    if skipped > 0:
        print(f"  Cache hits (skipped): {skipped}/{total}")
    if failed > 0:
        print(f"  Failed: {failed}/{total}")
    print(f"  Total duration: {total_duration:.1f}s ({total_duration/60:.1f} min)")
    print(f"  Output: {output_dir}")
    print(f"{'=' * 50}")

    return scenes


if __name__ == "__main__":
    import time
    from src.script.generator import get_script

    config = load_config()
    data = get_script(config=config)
    scenes = data["scenes"][:4]  # Test 4 scenes

    print(f"Testing parallel audio gen with {len(scenes)} scenes...")
    start = time.time()
    updated = generate_audio_parallel(scenes, config=config, max_workers=2)
    elapsed = time.time() - start

    for s in updated:
        print(f"  Scene {s['scene_id']}: {s.get('actual_duration', 0):.2f}s")
    print(f"\nTotal time: {elapsed:.1f}s")
