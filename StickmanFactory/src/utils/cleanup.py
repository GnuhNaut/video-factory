"""
cleanup.py - Quản lý dọn dẹp tài nguyên tạm thời

Xóa các file audio/image/json tạm sau khi render xong để giải phóng đĩa và VRAM.
Cung cấp cơ chế "Deep Cleanup" để reset project.
"""

import os
import shutil
import logging

logger = logging.getLogger(__name__)

def cleanup_temp_files(PROJECT_ROOT: str, session_id: str = None, deep: bool = False):
    """
    Dọn dẹp các thư mục tạm.
    
    Args:
        PROJECT_ROOT: Thư mục gốc của project.
        session_id: Nếu có, chỉ dọn dẹp liên quan đến session này (chưa dùng).
        deep: Nếu True, xóa cả cache chính (audio/images).
    """
    temp_dirs = [
        "storage/cache/json/chunks",
        "storage/cache/logs", # Optional: keep logs?
    ]
    
    if deep:
        temp_dirs.extend([
            "storage/cache/images",
            "storage/cache/audio",
            "storage/cache/json",
            "remotion/public/cache/audio",
            "remotion/public/cache/images"
        ])
    
    print(f"🧹 Running cleanup (deep={deep})...")
    
    for relative_path in temp_dirs:
        abs_path = os.path.join(PROJECT_ROOT, relative_path)
        if os.path.exists(abs_path):
            try:
                # Xóa toàn bộ nội dung trong thư mục nhưng giữ lại thư mục gốc
                for filename in os.listdir(abs_path):
                    file_path = os.path.join(abs_path, filename)
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.is_dir(file_path):
                        shutil.rmtree(file_path)
                logger.info(f"Cleaned: {abs_path}")
            except Exception as e:
                logger.error(f"Failed to clean {abs_path}: {e}")
                
    # Xóa file concat_list.txt trong storage/renders nếu còn
    render_dir = os.path.join(PROJECT_ROOT, "storage", "renders")
    if os.path.exists(render_dir):
        for f in ["concat_list.txt"]:
            f_path = os.path.join(render_dir, f)
            if os.path.exists(f_path):
                os.remove(f_path)

if __name__ == "__main__":
    # Test cleanup
    import sys
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    deep = "--deep" in sys.argv
    cleanup_temp_files(ROOT, deep=deep)
