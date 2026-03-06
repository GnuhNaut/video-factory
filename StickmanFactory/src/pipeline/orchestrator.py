"""
orchestrator.py - Bo dieu phoi toan bo quy trinh Pipeline

Chay pipeline: Load Script -> Cache Check -> Parallel Audio -> Normalize
              -> Sync Duration -> Render Video -> Thumbnail -> Done.

Phase 4: Tich hop cache, parallel audio, thumbnail, error recovery.
"""

import os
import sys
import json
import time
from datetime import datetime

# Force UTF-8 stdout cho Windows cp1252 terminal
if sys.platform == "nt":
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from src.core.config_loader import load_config, get_nested
from src.core.logger import setup_logger, get_logger, SceneErrorTracker
from src.core.cache_manager import calculate_hash, check_cache, update_cache, get_cache_stats
from src.script.generator import get_script
from src.audio.normalizer import normalize_scenes
from src.audio.sync_checker import update_durations
from src.visual.image_provider import get_image_provider
from src.pipeline.renderer import render_video
from src.visual.thumbnail_gen import generate_thumbnail

logger = get_logger("orchestrator")


def run_pipeline(config: dict = None, output_json: str = None) -> dict:
    """
    Chay toan bo pipeline (Phase 4 optimized).

    1: Load script
    2: Generate Backgrounds (with cache)
    3: Generate Audio (parallel + cache)
    4: Normalize audio
    5: Sync duration & Save JSON
    6: Render Video (with skip logic)
    7: Generate Thumbnail
    """
    pipeline_start = time.time()
    error_tracker = SceneErrorTracker()

    if config is None:
        config = load_config()

    cache_enabled = get_nested(config, "optimization", "cache_enabled", default=False)

    print("=" * 60)
    print("  [STICKMAN FACTORY - Pipeline v4]")
    print("=" * 60)
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Cache: {'ON' if cache_enabled else 'OFF'}")
    print()

    # ========================================
    # STEP 1: Load Script
    # ========================================
    step_start = time.time()
    print("=" * 60)
    print("  STEP 1/7: Loading Script")
    print("=" * 60)

    data = get_script(config=config)
    scenes = data.get("scenes", [])
    title = data.get("meta", {}).get("title", data.get("project_name", "Untitled"))

    print(f"  Title: {title}")
    print(f"  Scenes: {len(scenes)}")
    print(f"  Time: {time.time() - step_start:.1f}s")
    print()
    logger.info(f"Loaded script: {title} ({len(scenes)} scenes)")

    # ========================================
    # STEP 2: Generate Backgrounds (with cache)
    # ========================================
    step_start = time.time()
    print("=" * 60)
    print("  STEP 2/7: Generating Backgrounds")
    print("=" * 60)

    image_provider = get_image_provider(config)
    img_dir = os.path.join(PROJECT_ROOT, "storage", "cache", "images")

    img_generated = 0
    img_cached = 0

    for scene in scenes:
        scene_id = scene.get("scene_id", 0)
        try:
            if cache_enabled:
                img_hash = calculate_hash(scene, "image")
                output_path = os.path.join(img_dir, f"bg_{scene_id:03d}.png")
                if check_cache(scene_id, img_hash, "image", output_path):
                    scene["bg_image_path"] = output_path
                    img_cached += 1
                    continue

            # Generate
            path = image_provider.generate(
                prompt=scene.get("bg_prompt", ""),
                seed=scene.get("bg_seed", 42),
                output_path=os.path.join(img_dir, f"bg_{scene_id:03d}.png")
            )
            scene["bg_image_path"] = path
            img_generated += 1

            if cache_enabled:
                img_hash = calculate_hash(scene, "image")
                update_cache(scene_id, img_hash, "image")

        except Exception as e:
            error_tracker.log_error(scene_id, "image", e)
            scene["bg_image_path"] = ""

    print(f"  Generated: {img_generated} | Cached: {img_cached}")
    print(f"  Time: {time.time() - step_start:.1f}s")
    print()
    logger.info(f"Backgrounds: {img_generated} generated, {img_cached} cached")

    # ========================================
    # STEP 3: Generate Audio (Parallel + Cache)
    # ========================================
    step_start = time.time()
    print("=" * 60)
    print("  STEP 3/7: Generating Audio (Parallel)")
    print("=" * 60)

    audio_dir = os.path.join(PROJECT_ROOT, "storage", "cache", "audio")
    voice_id = data.get("meta", {}).get("voice_model", None)

    # Use parallel audio generation
    from src.utils.parallel import generate_audio_parallel
    scenes = generate_audio_parallel(
        scenes=scenes,
        output_dir=audio_dir,
        config=config,
        voice_id=voice_id,
    )

    print(f"  Time: {time.time() - step_start:.1f}s")
    print()
    logger.info(f"Audio generation completed in {time.time() - step_start:.1f}s")

    # ========================================
    # STEP 4: Normalize Audio
    # ========================================
    step_start = time.time()
    print("=" * 60)
    print("  STEP 4/7: Normalizing Audio (-16 LUFS)")
    print("=" * 60)

    try:
        scenes = normalize_scenes(scenes, config=config)
    except Exception as e:
        logger.error(f"Audio normalization failed: {e}")
        print(f"  [WARNING] Normalization failed: {e}")

    print(f"  Time: {time.time() - step_start:.1f}s")
    print()

    # ========================================
    # STEP 5: Sync Durations & Save JSON
    # ========================================
    step_start = time.time()
    print("=" * 60)
    print("  STEP 5/7: Syncing Durations & Saving JSON")
    print("=" * 60)

    sync_result = update_durations(scenes, config=config)
    scenes = sync_result["scenes"]

    if output_json is None:
        json_dir = os.path.join(PROJECT_ROOT, "storage", "cache", "json")
        os.makedirs(json_dir, exist_ok=True)
        output_json = os.path.join(json_dir, "project_ready.json")

    data["scenes"] = scenes
    data["pipeline_result"] = {
        "total_actual_duration": sync_result["total_actual"],
        "total_expected_duration": sync_result["total_expected"],
        "drift_percent": sync_result["drift_percent"],
        "audio_dir": audio_dir,
        "image_dir": img_dir,
        "generated_at": datetime.now().isoformat(),
        "warnings": sync_result["warnings"],
        "cache_stats": get_cache_stats() if cache_enabled else None,
    }

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  Saved: {output_json}")
    print(f"  Time: {time.time() - step_start:.1f}s")
    print()

    # ========================================
    # STEP 6: Render Video (Remotion)
    # ========================================
    step_start = time.time()
    print("=" * 60)
    print("  STEP 6/7: Rendering Video")
    print("=" * 60)

    video_path = render_video(
        project_json_path=output_json,
        config=config
    )

    print(f"  Time: {time.time() - step_start:.1f}s")
    print()
    logger.info(f"Video render completed in {time.time() - step_start:.1f}s")

    # ========================================
    # STEP 7: Generate Thumbnail
    # ========================================
    step_start = time.time()
    print("=" * 60)
    print("  STEP 7/7: Generating Thumbnail")
    print("=" * 60)

    thumbnail_path = None
    try:
        thumbnail_path = generate_thumbnail(title=title, config=config)
    except Exception as e:
        logger.error(f"Thumbnail generation failed: {e}")
        print(f"  [WARNING] Thumbnail failed: {e}")

    print(f"  Time: {time.time() - step_start:.1f}s")
    print()

    # ========================================
    # SUMMARY
    # ========================================
    elapsed = time.time() - pipeline_start
    total_dur = sync_result["total_actual"]

    print("=" * 60)
    print("  [FULL PIPELINE COMPLETE]")
    print("=" * 60)
    print(f"  Title: {title}")
    print(f"  Scenes: {len(scenes)}")
    print(f"  Total Video Duration: {int(total_dur//60)}m {int(total_dur%60)}s")
    print(f"  Pipeline Time: {elapsed:.1f}s")
    print(f"  Final Video: {video_path}")
    print(f"  Thumbnail: {thumbnail_path}")
    print(f"  Output JSON: {output_json}")

    if cache_enabled:
        stats = get_cache_stats()
        print(f"  Cache: {stats['audio']} audio, {stats['image']} image hashes stored")

    # Error summary
    error_tracker.print_summary()

    if sync_result["warnings"]:
        print(f"\n  [WARNING] {len(sync_result['warnings'])} warning(s) -- see output JSON")

    print("=" * 60)

    logger.info(f"Pipeline complete: {elapsed:.1f}s total")

    return {
        "data": data,
        "output_json": output_json,
        "video_path": video_path,
        "thumbnail_path": thumbnail_path,
        "sync_result": sync_result,
        "elapsed": elapsed,
        "errors": error_tracker.errors,
    }


if __name__ == "__main__":
    setup_logger()
    result = run_pipeline()
