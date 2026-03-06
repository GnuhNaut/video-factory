"""
config_loader.py - Đọc và validate config.json

Cung cấp hàm load_config() để đọc cấu hình toàn cục cho dự án
StickmanFactory và trả về dưới dạng Python dict.
"""

import json
import os
import sys
import logging

logger = logging.getLogger(__name__)

# Đường dẫn mặc định tới config.json (nằm ở thư mục gốc project)
DEFAULT_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "config.json"
)


def load_config(config_path: str = None) -> dict:
    """
    Đọc file config.json và trả về dict.

    Args:
        config_path: Đường dẫn tới file config. Nếu None, dùng đường dẫn mặc định.

    Returns:
        dict chứa toàn bộ cấu hình.

    Raises:
        FileNotFoundError: Nếu file config không tồn tại.
        json.JSONDecodeError: Nếu file config không phải JSON hợp lệ.
    """
    path = config_path or DEFAULT_CONFIG_PATH

    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Config file not found: {path}\n"
            f"Please create config.json at the project root."
        )

    try:
        with open(path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Invalid JSON in config file: {path}",
            e.doc, e.pos
        )

    logger.info(f"Config loaded successfully from: {path}")
    return config


def get_nested(config: dict, *keys, default=None):
    """
    Truy cập an toàn vào nested dict.

    Ví dụ:
        get_nested(config, "models", "kokoro_path")
        → config["models"]["kokoro_path"]

    Args:
        config: Dict cấu hình.
        *keys: Danh sách key để truy cập lần lượt.
        default: Giá trị trả về nếu key không tồn tại.

    Returns:
        Giá trị tìm được hoặc default.
    """
    current = config
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def validate_required_keys(config: dict) -> list:
    """
    Kiểm tra các key bắt buộc trong config.

    Returns:
        Danh sách các key bị thiếu. Rỗng nếu đầy đủ.
    """
    required = [
        ("project", "language"),
        ("project", "target_duration_min"),
        ("project", "wpm"),
        ("project", "resolution"),
        ("project", "fps"),
        ("models", "kokoro_path"),
        ("models", "kokoro_voice"),
        ("character", "type"),
        ("character", "base_color"),
        ("paths", "ffmpeg"),
        ("paths", "output_root"),
    ]

    missing = []
    for key_path in required:
        if get_nested(config, *key_path) is None:
            missing.append(".".join(key_path))

    return missing


def print_config(config: dict):
    """In cấu hình ra console dưới dạng formatted JSON."""
    print("=" * 60)
    print("  STICKMAN FACTORY - Configuration")
    print("=" * 60)
    print(json.dumps(config, indent=2, ensure_ascii=False))
    print("=" * 60)

    missing = validate_required_keys(config)
    if missing:
        print(f"\n⚠️  Missing required keys: {', '.join(missing)}")
    else:
        print("\n✅ All required configuration keys present.")


if __name__ == "__main__":
    """Quick test: python src/core/config_loader.py"""
    try:
        cfg = load_config()
        print_config(cfg)
    except Exception as e:
        print(f"❌ Error loading config: {e}", file=sys.stderr)
        sys.exit(1)
