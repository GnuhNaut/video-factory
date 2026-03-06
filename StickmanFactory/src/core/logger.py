"""
logger.py - Hệ thống logging chuẩn cho Stickman Factory

Format: [TIME] [LEVEL] [MODULE] Message
File log: logs/pipeline_{date}.log
Error Recovery: log lỗi scene nhưng tiếp tục pipeline.
"""

import os
import sys
import logging
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
os.makedirs(LOG_DIR, exist_ok=True)


def setup_logger(
    name: str = "stickman_factory",
    level: int = logging.DEBUG,
    console_level: int = logging.INFO,
    log_file: str = None,
) -> logging.Logger:
    """
    Thiết lập logger chuẩn cho toàn bộ pipeline.

    Args:
        name: Tên logger.
        level: Level tối thiểu ghi log (file).
        console_level: Level hiển thị trên console.
        log_file: Đường dẫn file log. Mặc định: logs/pipeline_{date}.log.

    Returns:
        Logger đã cấu hình.
    """
    logger = logging.getLogger(name)

    # Tránh thêm handler trùng khi gọi nhiều lần
    if logger.handlers:
        return logger

    logger.setLevel(level)

    # Format chuẩn
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)-7s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler (INFO+)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (DEBUG+)
    if log_file is None:
        date_str = datetime.now().strftime("%Y%m%d")
        log_file = os.path.join(LOG_DIR, f"pipeline_{date_str}.log")

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def get_logger(module_name: str) -> logging.Logger:
    """
    Lấy child logger cho từng module.

    Usage:
        from src.core.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Hello from module X")

    Args:
        module_name: Thường là __name__.

    Returns:
        Child logger kế thừa config từ root.
    """
    # Đảm bảo root logger đã setup
    root = logging.getLogger("stickman_factory")
    if not root.handlers:
        setup_logger()

    return logging.getLogger(f"stickman_factory.{module_name}")


class SceneErrorTracker:
    """
    Theo dõi lỗi từng scene để pipeline không dừng khi 1 scene fail.

    Usage:
        tracker = SceneErrorTracker()
        try:
            process_scene(scene)
        except Exception as e:
            tracker.log_error(scene_id, "audio", e)

        # Cuối pipeline
        tracker.print_summary()
    """

    def __init__(self):
        self.errors = []
        self.logger = get_logger("error_tracker")

    def log_error(self, scene_id: int, step: str, error: Exception):
        """Ghi nhận lỗi của 1 scene tại 1 bước."""
        entry = {
            "scene_id": scene_id,
            "step": step,
            "error": str(error),
            "timestamp": datetime.now().isoformat(),
        }
        self.errors.append(entry)
        self.logger.error(
            f"Scene {scene_id} failed at [{step}]: {error}"
        )

    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def get_failed_scenes(self) -> list:
        return list(set(e["scene_id"] for e in self.errors))

    def print_summary(self):
        """In tóm tắt lỗi cuối pipeline."""
        if not self.errors:
            print("  [OK] No scene errors during pipeline.")
            return

        print(f"\n  [ERRORS] {len(self.errors)} error(s) in {len(self.get_failed_scenes())} scene(s):")
        for e in self.errors:
            print(f"    - Scene {e['scene_id']} [{e['step']}]: {e['error']}")


if __name__ == "__main__":
    logger = setup_logger()
    logger.info("Logger initialized successfully")
    logger.debug("Debug message (only in file)")
    logger.warning("Warning message")

    child = get_logger("test_module")
    child.info("Child logger working")

    tracker = SceneErrorTracker()
    tracker.log_error(3, "audio", ValueError("Test error"))
    tracker.print_summary()

    print(f"\nLog file: {LOG_DIR}")
