"""
mock_data.py - Load kịch bản mẫu từ file JSON

Module phục vụ chế độ Mock-First: đọc file JSON mẫu thay vì gọi LLM API.
"""

import json
import os
import sys

if sys.platform == "nt":
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from src.core.config_loader import load_config, get_nested


def load_mock_script(file_path: str = None, config: dict = None) -> dict:
    """
    Load kịch bản mẫu từ file JSON.

    Args:
        file_path: Đường dẫn file JSON. Nếu None, lấy từ config.
        config: Dict cấu hình. Nếu None, tự load.

    Returns:
        Dict chứa dữ liệu project (bao gồm scenes).

    Raises:
        FileNotFoundError: Nếu file không tồn tại.
        json.JSONDecodeError: Nếu file JSON không hợp lệ.
    """
    if config is None:
        config = load_config()

    if file_path is None:
        file_path = get_nested(config, "llm", "mock_file_path",
                               default="./data/sample_project.json")

    # Resolve đường dẫn tương đối từ project root
    if not os.path.isabs(file_path):
        file_path = os.path.join(PROJECT_ROOT, file_path)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Mock data file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Validate cơ bản
    if "scenes" not in data:
        raise ValueError(f"Mock data file missing 'scenes' key: {file_path}")

    scene_count = len(data["scenes"])
    total_words = sum(s.get("word_count", 0) for s in data["scenes"])
    print(f"📄 Loaded mock script: {scene_count} scenes, {total_words} words")

    return data


if __name__ == "__main__":
    data = load_mock_script()
    print(f"Title: {data.get('meta', {}).get('title', data.get('project_name', 'N/A'))}")
    for s in data["scenes"][:3]:
        print(f"  Scene {s['scene_id']}: {s['text'][:60]}...")
