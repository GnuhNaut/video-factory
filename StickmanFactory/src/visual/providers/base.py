"""
base.py - Abstract Base Class cho Image Provider

Chuẩn hóa kiến trúc: mọi Image Provider đều phải implement interface này.
Khi thêm AI Provider, chỉ cần kế thừa BaseImageProvider.
"""

from abc import ABC, abstractmethod


class BaseImageProvider(ABC):
    """Interface chuẩn cho nguồn sinh ảnh background."""

    @abstractmethod
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
        pass

    @abstractmethod
    def generate_batch(self, scenes: list, output_dir: str) -> list:
        """
        Sinh ảnh background cho tất cả scenes.

        Args:
            scenes: List scene dicts.
            output_dir: Thư mục lưu ảnh.

        Returns:
            List scenes đã cập nhật bg_image_path.
        """
        pass

    @abstractmethod
    def check_health(self) -> bool:
        """
        Kiểm tra provider có sẵn sàng không.

        Returns:
            True nếu provider hoạt động bình thường.
        """
        pass

    def get_name(self) -> str:
        """Trả về tên provider."""
        return self.__class__.__name__
