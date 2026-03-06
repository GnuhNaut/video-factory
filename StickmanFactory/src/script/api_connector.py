"""
api_connector.py - (Reserved) Connector cho LLM API

Module dự phòng cho Phase tương lai khi tích hợp LLM API
(Groq, OpenAI, etc.) để tự động sinh kịch bản.
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)


class APIConnector:
    """
    Reserved: Connector cho LLM API.

    Sử dụng khi config['llm']['enabled'] = True.
    Hiện tại raise NotImplementedError.
    """

    def __init__(self, config: dict = None):
        raise NotImplementedError(
            "LLM API chưa được cấu hình.\n"
            "Vui lòng sử dụng chế độ Mock (config.llm.enabled = false).\n"
            "Hoặc triển khai API connector trong phase tương lai."
        )

    def generate_script(self, topic: str, target_words: int) -> dict:
        """Reserved: Sinh kịch bản từ LLM API."""
        raise NotImplementedError("API connector not implemented yet")
