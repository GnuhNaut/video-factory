"""
local_ai.py - Local AI Image Provider (SDXL Turbo)

Sinh ảnh nền bằng SDXL Turbo chạy local trên GPU.
Inference ở 1344x768 (native SDXL 16:9), upscale lên 1920x1080.
Yêu cầu: torch, diffusers, transformers, Pillow.
"""

import os
import sys
import logging

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
sys.path.insert(0, PROJECT_ROOT)

from src.visual.providers.base import BaseImageProvider
from src.core.config_loader import load_config, get_nested

logger = logging.getLogger(__name__)

# Style suffix chuẩn cho background video
STYLE_SUFFIX = (
    ", highly detailed 2D vector art, minimalist, "
    "flat colors, empty background for animation"
)

# Native SDXL Turbo inference resolution (16:9)
INFERENCE_WIDTH = 1344
INFERENCE_HEIGHT = 768


class LocalAIProvider(BaseImageProvider):
    """
    Sinh ảnh background bằng SDXL Turbo local.

    Pipeline:
    1. Load model fp16 lên CUDA.
    2. Inference 1344x768 (2 steps, guidance_scale=0).
    3. Upscale lên target resolution (mặc định 1920x1080) bằng LANCZOS.
    """

    def __init__(self, config: dict = None):
        if config is None:
            config = load_config()
        self.config = config

        self.model_path = get_nested(
            config, "visual", "ai_model_path",
            default="stabilityai/sdxl-turbo"
        )

        # Target resolution từ config
        res_str = get_nested(
            config, "video", "resolution", default="1920x1080"
        )
        parts = res_str.split("x")
        self.target_width = int(parts[0])
        self.target_height = int(parts[1])

        self._pipeline = None
        self._model_loaded = False

    def _load_model(self):
        """Load SDXL Turbo pipeline lên CUDA (fp16)."""
        if self._model_loaded:
            return

        try:
            import torch
            from diffusers import AutoPipelineForText2Image

            print(f"🎨 Đang tải model SDXL Turbo vào VRAM...")
            print(f"   Model: {self.model_path}")
            logger.info(f"Loading SDXL Turbo from: {self.model_path}")

            self._pipeline = AutoPipelineForText2Image.from_pretrained(
                self.model_path,
                torch_dtype=torch.float16,
                variant="fp16",
            )
            self._pipeline.to("cuda")

            self._model_loaded = True
            print("✅ SDXL Turbo loaded successfully on CUDA (fp16)")
            logger.info("SDXL Turbo loaded successfully")

        except ImportError as e:
            error_msg = (
                f"Missing dependency for LocalAIProvider.\n"
                f"Please install: pip install torch diffusers transformers accelerate\n"
                f"Error: {e}"
            )
            logger.error(error_msg)
            raise ImportError(error_msg)

        except Exception as e:
            error_msg = f"Failed to load SDXL Turbo: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def generate(self, prompt: str, seed: int, output_path: str) -> str:
        """
        Sinh 1 ảnh background.

        Args:
            prompt: Mô tả nội dung ảnh.
            seed: Seed cho đồng bộ kết quả.
            output_path: Đường dẫn file output.

        Returns:
            Đường dẫn file ảnh đã sinh.
        """
        import torch
        from PIL import Image

        self._load_model()
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        # Thêm style suffix vào prompt
        styled_prompt = prompt + STYLE_SUFFIX

        # Tạo generator với seed cố định
        generator = torch.Generator(device="cuda").manual_seed(seed)

        try:
            # Inference ở native SDXL resolution
            result = self._pipeline(
                prompt=styled_prompt,
                num_inference_steps=2,
                guidance_scale=0.0,
                width=INFERENCE_WIDTH,
                height=INFERENCE_HEIGHT,
                generator=generator,
            )
            image = result.images[0]

            # Upscale lên target resolution
            if (image.width, image.height) != (self.target_width, self.target_height):
                image = image.resize(
                    (self.target_width, self.target_height),
                    Image.Resampling.LANCZOS,
                )

            image.save(output_path)

            # Giải phóng VRAM sau mỗi lần sinh
            import gc
            gc.collect()
            torch.cuda.empty_cache()

            logger.info(f"Generated: {output_path} ({self.target_width}x{self.target_height})")
            print(f"  🖼️ Generated: {os.path.basename(output_path)}")
            return output_path

        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            raise RuntimeError(f"Image generation failed for prompt '{prompt[:50]}...': {e}")

    def generate_batch(self, scenes: list, output_dir: str) -> list:
        """Sinh ảnh background cho tất cả scenes."""
        os.makedirs(output_dir, exist_ok=True)

        for scene in scenes:
            # Ép kiểu int để tránh lỗi 'Unknown format code 'd' for object of type 'str''
            scene_id = int(scene.get("scene_id", 0))
            prompt = scene.get("bg_prompt", "")
            seed = scene.get("bg_seed", 42)

            if not prompt:
                continue

            output_path = os.path.join(output_dir, f"bg_{scene_id:03d}.png")

            try:
                self.generate(prompt=prompt, seed=seed, output_path=output_path)
                scene["bg_image_path"] = output_path
            except Exception as e:
                logger.error(f"Scene {scene_id} image failed: {e}")
                scene["bg_image_path"] = ""

        return scenes

    def check_health(self) -> bool:
        """Kiểm tra GPU và dependencies có sẵn sàng không."""
        try:
            import torch
            from diffusers import AutoPipelineForText2Image

            if not torch.cuda.is_available():
                print("⚠️ CUDA not available. LocalAIProvider requires GPU.")
                return False

            vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            print(f"  GPU: {torch.cuda.get_device_name(0)} ({vram_gb:.1f} GB VRAM)")

            # Nếu là đường dẫn local, kiểm tra tồn tại
            # Nếu là HuggingFace model ID (vd: stabilityai/sdxl-turbo), bỏ qua kiểm tra
            if os.path.sep in self.model_path or ":" in self.model_path:
                if not os.path.exists(self.model_path):
                    print(f"⚠️ Model path not found: {self.model_path}")
                    return False

            print(f"  Model: {self.model_path}")
            return True

        except ImportError:
            print(
                "⚠️ Missing dependencies. Install:\n"
                "   pip install torch diffusers transformers accelerate"
            )
            return False


if __name__ == "__main__":
    # Quick test
    provider = LocalAIProvider()
    print(f"Provider: {provider.get_name()}")
    print(f"Health: {provider.check_health()}")

    if provider.check_health():
        test_out = os.path.join(PROJECT_ROOT, "storage", "cache", "images", "test_ai.png")
        provider.generate(
            prompt="A beautiful sunset over a calm ocean, warm colors",
            seed=42,
            output_path=test_out,
        )
        print(f"Test image saved to: {test_out}")
