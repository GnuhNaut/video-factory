"""
normalizer.py - Chuẩn hóa âm lượng hàng loạt

Sử dụng FFmpeg loudnorm để normalize tất cả file audio về -16 LUFS
(chuẩn YouTube), đảm bảo cảnh nói nhỏ không thua thiệt cảnh nói to.
"""

import os
import sys
import subprocess
import logging

if sys.platform == "nt":
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from src.core.config_loader import load_config, get_nested

logger = logging.getLogger(__name__)

# Chuẩn YouTube
TARGET_LUFS = -16
TARGET_TP = -1.5
TARGET_LRA = 11
SAMPLE_RATE = 24000


def normalize_single(audio_path: str, ffmpeg_path: str,
                     replace: bool = True) -> bool:
    """
    Normalize 1 file audio về -16 LUFS.

    Args:
        audio_path: Đường dẫn file audio.
        ffmpeg_path: Đường dẫn FFmpeg.
        replace: Nếu True, ghi đè file gốc. Nếu False, tạo file _norm.wav.

    Returns:
        True nếu thành công.
    """
    if not os.path.exists(audio_path):
        logger.warning(f"File not found: {audio_path}")
        return False

    if replace:
        temp_path = audio_path + ".tmp_norm.wav"
    else:
        base, ext = os.path.splitext(audio_path)
        temp_path = f"{base}_norm{ext}"

    cmd = [
        ffmpeg_path,
        "-y",
        "-i", audio_path,
        "-af", f"loudnorm=I={TARGET_LUFS}:TP={TARGET_TP}:LRA={TARGET_LRA}",
        "-ar", str(SAMPLE_RATE),
        temp_path
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode == 0:
            if replace:
                os.replace(temp_path, audio_path)
            return True
        else:
            logger.error(f"FFmpeg normalize failed for {audio_path}: {result.stderr[:200]}")
            if replace and os.path.exists(temp_path):
                os.remove(temp_path)
            return False

    except FileNotFoundError:
        logger.error(f"FFmpeg not found at: {ffmpeg_path}")
        return False
    except Exception as e:
        logger.error(f"Normalize error for {audio_path}: {e}")
        if replace and os.path.exists(temp_path):
            os.remove(temp_path)
        return False


def normalize_batch(audio_files: list, config: dict = None,
                    replace: bool = True) -> dict:
    """
    Normalize hàng loạt file audio về -16 LUFS.

    Args:
        audio_files: List đường dẫn file audio.
        config: Dict cấu hình.
        replace: Ghi đè file gốc hay tạo file mới.

    Returns:
        Dict: {success: int, failed: int, skipped: int, total: int}
    """
    if config is None:
        config = load_config()

    ffmpeg_path = get_nested(config, "paths", "ffmpeg", default="ffmpeg")
    total = len(audio_files)
    success = 0
    failed = 0
    skipped = 0

    print(f"🔊 Normalizing {total} audio files to {TARGET_LUFS} LUFS...")

    # Thử import tqdm
    try:
        from tqdm import tqdm
        file_iter = tqdm(audio_files, desc="🔊 Normalizing", unit="file")
    except ImportError:
        file_iter = audio_files

    for audio_path in file_iter:
        if not audio_path or not os.path.exists(audio_path):
            skipped += 1
            continue

        ok = normalize_single(audio_path, ffmpeg_path, replace=replace)
        if ok:
            success += 1
        else:
            failed += 1

    # Summary
    print(f"\n  🔊 Normalization: {success} OK, {failed} failed, {skipped} skipped / {total} total")

    return {
        "success": success,
        "failed": failed,
        "skipped": skipped,
        "total": total,
    }


def normalize_scenes(scenes: list, config: dict = None) -> list:
    """
    Normalize audio từ danh sách scenes.

    Args:
        scenes: List scenes có trường 'audio_path'.
        config: Dict cấu hình.

    Returns:
        List scenes (không thay đổi, chỉ normalize file trên disk).
    """
    audio_files = [s.get("audio_path", "") for s in scenes if s.get("audio_path")]
    normalize_batch(audio_files, config=config)
    return scenes


if __name__ == "__main__":
    print("Usage: Gọi normalize_batch(files) hoặc normalize_scenes(scenes).")
    print("Module này thường được gọi từ orchestrator.py.")
