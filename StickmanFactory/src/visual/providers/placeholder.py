"""
placeholder.py - Placeholder Image Provider

Sinh ảnh placeholder bằng PIL (gradient + text).
Implement chuẩn BaseImageProvider, không cần AI.
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, PROJECT_ROOT)

from src.visual.providers.base import BaseImageProvider
from src.core.config_loader import load_config, get_nested


class PlaceholderProvider(BaseImageProvider):
    """Sinh ảnh placeholder bằng PIL (gradient + text). Không cần AI."""

    def __init__(self, config: dict = None):
        if config is None:
            config = load_config()
        self.config = config
        self.show_text = get_nested(config, "image_provider", "placeholder",
                                    "show_prompt_text", default=True)

    def generate(self, prompt: str, seed: int, output_path: str) -> str:
        """Sinh 1 ảnh placeholder."""
        from src.visual.bg_generator import generate_placeholder

        # Lấy scene_id từ filename
        basename = os.path.basename(output_path)
        try:
            scene_id = int(basename.replace("bg_", "").replace(".png", ""))
        except ValueError:
            scene_id = 1

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        generate_placeholder(
            prompt=prompt,
            seed=seed,
            scene_id=scene_id,
            output_path=output_path,
            show_text=self.show_text
        )

        return output_path

    def generate_batch(self, scenes: list, output_dir: str) -> list:
        """Sinh ảnh placeholder cho tất cả scenes."""
        from src.visual.bg_generator import generate_batch
        return generate_batch(scenes, output_dir=output_dir, config=self.config)

    def check_health(self) -> bool:
        """Placeholder luôn sẵn sàng (chỉ cần PIL)."""
        try:
            from PIL import Image
            return True
        except ImportError:
            return False
