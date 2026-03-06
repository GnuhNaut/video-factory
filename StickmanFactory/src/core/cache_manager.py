"""
cache_manager.py - Quản lý Cache thông minh cho Pipeline

Hash-based caching: không sinh lại Audio/Image nếu nội dung không đổi.
Lưu hash tại storage/cache/hashes.json.
"""

import os
import sys
import json
import hashlib

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from src.core.config_loader import load_config, get_nested

HASH_FILE = os.path.join(PROJECT_ROOT, "storage", "cache", "hashes.json")


def _load_hashes() -> dict:
    """Đọc file hashes.json. Trả về dict rỗng nếu chưa tồn tại."""
    if os.path.exists(HASH_FILE):
        try:
            with open(HASH_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def _save_hashes(hashes: dict):
    """Lưu dict hashes ra file."""
    os.makedirs(os.path.dirname(HASH_FILE), exist_ok=True)
    with open(HASH_FILE, "w", encoding="utf-8") as f:
        json.dump(hashes, f, indent=2, ensure_ascii=False)


def calculate_hash(scene_data: dict, hash_type: str = "audio") -> str:
    """
    Tính hash cho 1 scene dựa trên nội dung liên quan.

    Args:
        scene_data: Dict chứa thông tin scene.
        hash_type: "audio" hoặc "image".

    Returns:
        MD5 hash string.
    """
    if hash_type == "audio":
        # Hash dựa trên text + voice_id + speed
        content = json.dumps({
            "text": scene_data.get("text", ""),
            "voice_id": scene_data.get("voice_id", "af_bella"),
            "speed": scene_data.get("speed", 1.0),
        }, sort_keys=True, ensure_ascii=False)
    elif hash_type == "image":
        # Hash dựa trên bg_prompt + bg_seed
        content = json.dumps({
            "bg_prompt": scene_data.get("bg_prompt", ""),
            "bg_seed": scene_data.get("bg_seed", 42),
        }, sort_keys=True, ensure_ascii=False)
    else:
        content = json.dumps(scene_data, sort_keys=True, ensure_ascii=False)

    return hashlib.md5(content.encode("utf-8")).hexdigest()


def check_cache(scene_id: int, current_hash: str, hash_type: str = "audio", output_path: str = None) -> bool:
    """
    Kiểm tra xem scene này đã được cache chưa.

    Args:
        scene_id: ID của scene.
        current_hash: Hash hiện tại cần so sánh.
        hash_type: "audio" hoặc "image".
        output_path: Đường dẫn file output (kiểm tra tồn tại).

    Returns:
        True nếu hash trùng VÀ file output tồn tại → có thể skip.
    """
    hashes = _load_hashes()
    key = f"{hash_type}_{scene_id:03d}"
    stored_hash = hashes.get(key, "")

    if stored_hash != current_hash:
        return False

    # Hash trùng, kiểm tra file có tồn tại không
    if output_path and not os.path.exists(output_path):
        return False

    return True


def update_cache(scene_id: int, current_hash: str, hash_type: str = "audio"):
    """
    Cập nhật hash sau khi sinh thành công.

    Args:
        scene_id: ID của scene.
        current_hash: Hash mới.
        hash_type: "audio" hoặc "image".
    """
    hashes = _load_hashes()
    key = f"{hash_type}_{scene_id:03d}"
    hashes[key] = current_hash
    _save_hashes(hashes)


def clear_cache():
    """Xóa toàn bộ cache hashes."""
    if os.path.exists(HASH_FILE):
        os.remove(HASH_FILE)
        print("  [Cache] Cleared all hashes.")


def get_cache_stats() -> dict:
    """Trả về thống kê cache."""
    hashes = _load_hashes()
    audio_count = sum(1 for k in hashes if k.startswith("audio_"))
    image_count = sum(1 for k in hashes if k.startswith("image_"))
    return {
        "total": len(hashes),
        "audio": audio_count,
        "image": image_count,
    }


if __name__ == "__main__":
    # Test
    test_scene = {
        "scene_id": 1,
        "text": "Hello world",
        "bg_prompt": "A sunny park",
        "bg_seed": 42,
    }

    audio_hash = calculate_hash(test_scene, "audio")
    image_hash = calculate_hash(test_scene, "image")

    print(f"Audio hash: {audio_hash}")
    print(f"Image hash: {image_hash}")

    # Test cache flow
    print(f"Cache hit (before): {check_cache(1, audio_hash, 'audio')}")
    update_cache(1, audio_hash, "audio")
    print(f"Cache hit (after): {check_cache(1, audio_hash, 'audio')}")

    stats = get_cache_stats()
    print(f"Stats: {stats}")
