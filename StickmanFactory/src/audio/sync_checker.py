"""
sync_checker.py - Đồng bộ thời gian thực tế với dự kiến

So sánh actual_duration (từ audio) với expected_duration (từ WPM),
cập nhật total_duration, và cảnh báo nếu lệch quá 10%.
"""

import os
import sys
import json
import subprocess
import logging

if sys.platform == "nt":
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from src.core.config_loader import load_config, get_nested

logger = logging.getLogger(__name__)


def get_audio_duration(audio_path: str, ffmpeg_path: str = None) -> float:
    """
    Đo duration chính xác của file audio bằng ffprobe.

    Args:
        audio_path: Đường dẫn file audio.
        ffmpeg_path: Đường dẫn ffmpeg (dùng để suy ra ffprobe).

    Returns:
        Duration (giây). Trả về 0.0 nếu lỗi.
    """
    if not os.path.exists(audio_path):
        return 0.0

    # Thử ffprobe
    try:
        if ffmpeg_path:
            ffprobe_path = ffmpeg_path.replace("ffmpeg.exe", "ffprobe.exe")
        else:
            ffprobe_path = "ffprobe"

        cmd = [
            ffprobe_path,
            "-v", "quiet",
            "-show_entries", "format=duration",
            "-of", "json",
            audio_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return float(data["format"]["duration"])
    except Exception:
        pass

    # Fallback: soundfile
    try:
        import soundfile as sf
        data, sr = sf.read(audio_path)
        return len(data) / float(sr)
    except Exception:
        pass

    return 0.0


def update_durations(scenes: list, config: dict = None) -> dict:
    """
    Cập nhật actual_duration cho từng scene từ file audio thực tế.

    Args:
        scenes: List các scene dict (phải có 'audio_path').
        config: Dict cấu hình.

    Returns:
        Dict với:
            - scenes: List scenes đã cập nhật
            - total_actual: Tổng thời lượng thực tế (giây)
            - total_expected: Tổng thời lượng dự kiến (giây)
            - drift_percent: % lệch giữa thực tế và dự kiến
            - warnings: List cảnh báo
    """
    if config is None:
        config = load_config()

    ffmpeg_path = get_nested(config, "paths", "ffmpeg")
    target_min = get_nested(config, "project", "target_duration_min", default=11)
    target_sec = target_min * 60

    warnings = []
    total_actual = 0.0
    total_expected = 0.0

    print("🔄 Syncing durations...")

    for scene in scenes:
        audio_path = scene.get("audio_path", "")
        expected = scene.get("expected_duration", 0)
        total_expected += expected

        if audio_path and os.path.exists(audio_path):
            actual = get_audio_duration(audio_path, ffmpeg_path)
            scene["actual_duration"] = round(actual, 2)
            total_actual += actual

            # Cảnh báo nếu scene lệch > 30%
            if expected > 0:
                scene_drift = abs(actual - expected) / expected
                if scene_drift > 0.30:
                    msg = (f"Scene {scene['scene_id']}: "
                           f"expected {expected:.1f}s, actual {actual:.1f}s "
                           f"(drift {scene_drift:.0%})")
                    warnings.append(msg)
                    logger.warning(msg)
        else:
            scene["actual_duration"] = 0

    # Tính drift tổng
    if target_sec > 0:
        drift_percent = ((total_actual - target_sec) / target_sec) * 100
    else:
        drift_percent = 0

    # Cảnh báo nếu tổng lệch > 10%
    target_min_sec = 600  # 10 phút
    target_max_sec = 720  # 12 phút

    if total_actual > 0 and (total_actual < target_min_sec or total_actual > target_max_sec):
        msg = (f"⚠️  Total duration {total_actual:.0f}s ({total_actual/60:.1f} min) "
               f"is outside target range 10-12 min!")
        warnings.append(msg)

    # In báo cáo
    print(f"\n{'=' * 55}")
    print(f"  Duration Sync Report")
    print(f"{'=' * 55}")
    print(f"  📊 Total expected:  {total_expected:.1f}s ({total_expected/60:.1f} min)")
    print(f"  📊 Total actual:    {total_actual:.1f}s ({total_actual/60:.1f} min)")
    print(f"  📊 Target:          {target_sec:.0f}s ({target_min:.0f} min)")
    print(f"  📊 Drift from target: {drift_percent:+.1f}%")

    if warnings:
        print(f"\n  ⚠️  Warnings ({len(warnings)}):")
        for w in warnings:
            print(f"     • {w}")
    else:
        print(f"\n  ✅ All durations within acceptable range")

    print(f"{'=' * 55}")

    return {
        "scenes": scenes,
        "total_actual": round(total_actual, 2),
        "total_expected": round(total_expected, 2),
        "drift_percent": round(drift_percent, 2),
        "warnings": warnings,
    }


def apply_timeline_scaling(scenes: list) -> list:
    """
    Adjust visual_timeline offsets based on actual audio duration.
    If actual duration differs from expected, we scale the timeline to match.
    """
    print("⏳ Scaling visual timelines to match audio...")
    
    for scene in scenes:
        actual = scene.get("actual_duration", 0)
        expected = scene.get("expected_duration", 0)
        timeline = scene.get("visual_timeline", [])
        
        if not timeline or actual <= 0 or expected <= 0:
            continue
            
        ratio = actual / expected
        
        # Only scale if drift is > 2% to avoid noise
        if abs(1.0 - ratio) < 0.02:
            continue
            
        logger.info(f"Scaling scene {scene.get('scene_id')} timeline by {ratio:.3f}x")
        
        for item in timeline:
            if "time_offset" in item:
                # Scale offset
                new_offset = round(item["time_offset"] * ratio, 3)
                # Ensure it doesn't exceed actual duration
                item["time_offset"] = min(new_offset, actual - 0.1)
                
    return scenes


if __name__ == "__main__":
    print("Usage: Gọi update_durations(scenes) sau khi sinh audio.")
    print("Module này thường được gọi từ orchestrator.py.")
