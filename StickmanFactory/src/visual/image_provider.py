"""
image_provider.py - Factory cho Image Provider

Thin factory: import từ providers/ package và trả về đúng provider
dựa trên config. Dễ dàng thêm provider mới trong tương lai.
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from src.core.config_loader import load_config, get_nested
from src.visual.providers.base import BaseImageProvider
from src.visual.providers.placeholder import PlaceholderProvider


def get_image_provider(config: dict = None) -> BaseImageProvider:
    """
    Factory: Tạo ImageProvider dựa trên config.

    Args:
        config: Dict cấu hình. Nếu None, tự load.

    Returns:
        Instance của PlaceholderProvider hoặc AI provider (tương lai).
    """
    if config is None:
        config = load_config()

    mode = get_nested(config, "image_provider", "mode", default="placeholder")

    if mode == "ai":
        enabled = get_nested(config, "image_provider", "enabled", default=False)
        if enabled:
            # Khi có AI provider, import và trả về ở đây
            # from src.visual.providers.local_ai import LocalAIProvider
            # return LocalAIProvider(config)
            raise NotImplementedError(
                "AI Image Provider chua duoc trien khai.\n"
                "Dat config.image_provider.mode = 'placeholder' de dung anh placeholder.\n"
                "Hoac trien khai class LocalAIProvider trong providers/."
            )
        else:
            print("  [ImageProvider] AI mode selected but not enabled. Falling back to placeholder.")
            return PlaceholderProvider(config)
    else:
        return PlaceholderProvider(config)


if __name__ == "__main__":
    provider = get_image_provider()
    print(f"Active provider: {provider.get_name()}")
    print(f"Health check: {provider.check_health()}")
