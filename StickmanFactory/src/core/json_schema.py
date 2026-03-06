"""
json_schema.py - Định nghĩa schema cho kịch bản video

Sử dụng jsonschema để validate cấu trúc JSON project files.
Mỗi project chứa danh sách scenes với các trường bắt buộc.
"""

# Schema cho một scene trong project
SCENE_SCHEMA = {
    "type": "object",
    "required": [
        "scene_id",
        "text",
        "word_count",
        "expected_duration",
        "audio_path",
        "bg_prompt",
        "bg_seed",
        "character_state"
    ],
    "properties": {
        "scene_id": {
            "type": "integer",
            "minimum": 1,
            "description": "Unique identifier for the scene (1-indexed)"
        },
        "text": {
            "type": "string",
            "minLength": 1,
            "description": "Narration text in English"
        },
        "word_count": {
            "type": "integer",
            "minimum": 1,
            "description": "Number of words in the text"
        },
        "expected_duration": {
            "type": "number",
            "minimum": 0.1,
            "description": "Expected duration of this scene in seconds"
        },
        "audio_path": {
            "type": "string",
            "description": "Path to the generated audio file"
        },
        "bg_prompt": {
            "type": "string",
            "minLength": 1,
            "description": "Prompt for AI background generation"
        },
        "bg_seed": {
            "type": "integer",
            "minimum": 0,
            "description": "Seed for background generation (ensures style consistency)"
        },
        "character_state": {
            "type": "string",
            "enum": ["idle", "wave", "point", "walk", "sad", "happy"],
            "description": "Stickman character state for this scene"
        }
    },
    "additionalProperties": False
}

# Schema cho toàn bộ project
PROJECT_SCHEMA = {
    "type": "object",
    "required": ["project_name", "language", "scenes"],
    "properties": {
        "project_name": {
            "type": "string",
            "minLength": 1,
            "description": "Name of the video project"
        },
        "language": {
            "type": "string",
            "description": "Language code (e.g., 'en-us')"
        },
        "target_duration_min": {
            "type": "number",
            "minimum": 0.1,
            "description": "Target video duration in minutes"
        },
        "total_words": {
            "type": "integer",
            "minimum": 0,
            "description": "Total word count across all scenes"
        },
        "scenes": {
            "type": "array",
            "minItems": 1,
            "items": SCENE_SCHEMA,
            "description": "List of scenes in the video"
        }
    },
    "additionalProperties": True
}
