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

    Ưu tiên: config.visual.provider (mới) > config.image_provider.mode (cũ).

    Args:
        config: Dict cấu hình. Nếu None, tự load.

    Returns:
        Instance của PlaceholderProvider hoặc LocalAIProvider.
    """
    if config is None:
        config = load_config()

    # Ưu tiên config mới: visual.provider
    provider_type = get_nested(config, "visual", "provider", default=None)

    # Fallback: config cũ image_provider.mode
    if provider_type is None:
        provider_type = get_nested(config, "image_provider", "mode", default="placeholder")

    if provider_type == "local_ai":
        from src.visual.providers.local_ai import LocalAIProvider
        return LocalAIProvider(config)
    else:
        return PlaceholderProvider(config)


if __name__ == "__main__":
    provider = get_image_provider()
    print(f"Active provider: {provider.get_name()}")
    print(f"Health check: {provider.check_health()}")
