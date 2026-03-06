"""
generator.py - Logic chọn chế độ Mock hoặc API cho kịch bản

Kiểm tra config để quyết định load kịch bản từ file mẫu (Mock)
hoặc gọi LLM API để sinh kịch bản tự động.
"""

import os
import sys

if sys.platform == "nt":
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from src.core.config_loader import load_config, get_nested


from src.core.json_schema import PROJECT_SCHEMA
import json

def get_llm_prompt_template(topic: str) -> str:
    """
    Trả về prompt template để gửi cho LLM (OpenAI/Gemini).
    Yêu cầu LLM sinh kịch bản video tuân thủ chuẩn JSON Schema mới.
    """
    schema_str = json.dumps(PROJECT_SCHEMA, indent=2)
    return f"""Bạn là một chuyên gia viết kịch bản video ngắn (Shorts/Reels) về chủ đề: {topic}.
Nhiệm vụ của bạn là trả về DUY NHẤT một chuỗi JSON hợp lệ theo đúng cấu trúc sau. KHÔNG giải thích thêm.

YÊU CẦU QUAN TRỌNG VỀ KỊCH BẢN:
1. Mỗi video có từ 5-10 scenes. Độ dài câu chữ phải tự nhiên, không quá dài mỗi scene.
2. TÓM TẮT MỖI 2-3 CÂU THOẠI (1 phân cảnh - scene):
   Trong mỗi scene, kịch bản có thể dài, việc đứng yên một tư thế sẽ gây nhàm chán.
   Do đó, bạn PHẢI định nghĩa mảng `actions` cho mỗi scene. 
   - Thay đổi pose / thêm action (như point, explain, walk, happy, etc.) tại các mốc thời gian (time_start) khác nhau trong scene. Ví dụ: bắt đầu ở 0s, chuyển tư thế ở 2.5s, 5.0s.
   - Thêm "b_roll" (hình ảnh minh hoạ chèn vào clip) ở một số keyframe để làm sinh động.
   - Thêm "emotion_icon" (sweat, question, bulb, etc.) tại những lúc phù hợp.

CẤU TRÚC JSON SCHEMA BẮT BUỘC:
{schema_str}
"""

def get_script(topic: str = None, config: dict = None) -> dict:
    """
    Lấy kịch bản video — tự động chọn Mock hoặc API.

    Args:
        topic: Chủ đề video (chỉ dùng cho chế độ API).
        config: Dict cấu hình. Nếu None, tự load.

    Returns:
        Dict chứa dữ liệu project (bao gồm scenes).

    Raises:
        NotImplementedError: Nếu chế độ API được bật nhưng chưa triển khai.
    """
    if config is None:
        config = load_config()

    llm_enabled = get_nested(config, "llm", "enabled", default=False)

    if llm_enabled:
        # Chế độ API — chưa triển khai
        print("🔌 LLM mode: API (not implemented yet)")
        raise NotImplementedError(
            "LLM API chưa được triển khai.\n"
            "Đặt config.llm.enabled = false để dùng chế độ Mock.\n"
            "Hoặc triển khai src/script/api_connector.py trong phase tương lai."
        )
    else:
        # Chế độ Mock — load từ file mẫu
        print("📦 LLM mode: Mock (loading from file)")
        from src.script.mock_data import load_mock_script
        return load_mock_script(config=config)


if __name__ == "__main__":
    script = get_script()
    scenes = script.get("scenes", [])
    total_words = sum(s.get("word_count", 0) for s in scenes)
    title = script.get("meta", {}).get("title", script.get("project_name", "N/A"))

    print(f"\n📺 Title: {title}")
    print(f"📊 Scenes: {len(scenes)}")
    print(f"📝 Total words: {total_words}")
    print(f"⏱️  Est. duration: {total_words / 150 * 60:.0f}s ({total_words / 150:.1f} min)")
