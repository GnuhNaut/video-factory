"""
validator.py - Validate dữ liệu JSON project files

Sử dụng jsonschema để kiểm tra file JSON project có đúng
cấu trúc schema đã định nghĩa hay không.
"""

import json
import sys
import os

# Thêm project root vào path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from jsonschema import validate, ValidationError, Draft7Validator
from src.core.json_schema import PROJECT_SCHEMA


def validate_project_json(json_data: dict) -> tuple:
    """
    Validate dữ liệu JSON project theo schema.

    Args:
        json_data: Dict chứa dữ liệu project.

    Returns:
        Tuple (is_valid: bool, errors: list)
        - is_valid: True nếu dữ liệu hợp lệ.
        - errors: Danh sách lỗi (rỗng nếu hợp lệ).
    """
    validator = Draft7Validator(PROJECT_SCHEMA)
    errors = []

    for error in sorted(validator.iter_errors(json_data), key=lambda e: list(e.path)):
        path = " → ".join(str(p) for p in error.absolute_path) if error.absolute_path else "(root)"
        errors.append({
            "path": path,
            "message": error.message,
            "validator": error.validator,
        })

    is_valid = len(errors) == 0
    if not is_valid:
        return False, errors
    
    # Custom validation cho visual_timeline
    for i, scene in enumerate(json_data.get("scenes", [])):
        scene_id = scene.get("scene_id", i + 1)
        duration = scene.get("actual_duration", scene.get("expected_duration", 0))
        
        timeline = scene.get("visual_timeline", [])
        for j, event in enumerate(timeline):
            time_offset = event.get("time_offset", 0)
            if time_offset > duration:
                errors.append({
                    "path": f"scenes[{i}] → visual_timeline[{j}] → time_offset",
                    "message": f"time_offset ({time_offset}) exceeds scene duration ({duration})",
                    "validator": "custom"
                })
                is_valid = False

    return is_valid, errors


def validate_project_file(file_path: str) -> tuple:
    """
    Validate file JSON project từ đường dẫn.

    Args:
        file_path: Đường dẫn tới file JSON.

    Returns:
        Tuple (is_valid: bool, errors: list)
    """
    if not os.path.exists(file_path):
        return False, [{"path": "(file)", "message": f"File not found: {file_path}",
                        "validator": "file"}]

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return False, [{"path": "(file)", "message": f"Invalid JSON: {e}",
                        "validator": "json"}]

    return validate_project_json(data)


def print_validation_result(is_valid: bool, errors: list):
    """In kết quả validation ra console."""
    if is_valid:
        print("✅ Valid")
    else:
        print(f"❌ Invalid - {len(errors)} error(s) found:")
        for i, err in enumerate(errors, 1):
            print(f"   {i}. [{err['path']}] {err['message']}")


if __name__ == "__main__":
    if "--check" in sys.argv:
        # Tìm file path sau --check
        idx = sys.argv.index("--check")
        if idx + 1 >= len(sys.argv):
            print("Usage: python src/core/validator.py --check <file.json>")
            sys.exit(1)

        file_path = sys.argv[idx + 1]

        # Nếu path tương đối, resolve từ project root
        if not os.path.isabs(file_path):
            project_root = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            file_path = os.path.join(project_root, file_path)

        print("=" * 60)
        print("  JSON VALIDATOR - Check Result")
        print("=" * 60)
        print(f"  File: {file_path}")
        print("-" * 60)

        is_valid, errors = validate_project_file(file_path)
        print_validation_result(is_valid, errors)

        print("=" * 60)
        sys.exit(0 if is_valid else 1)
    else:
        print("Usage: python src/core/validator.py --check <file.json>")
        print("  Validates a project JSON file against the schema.")
