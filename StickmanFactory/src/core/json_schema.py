"""
json_schema.py - Định nghĩa schema cho kịch bản video

Sử dụng jsonschema để validate cấu trúc JSON project files.
Mỗi project chứa danh sách scenes với các trường bắt buộc.
"""
# Schema cho một frame / sự kiện hình ảnh trên dòng thời gian (thay thế cho character_state/actions tĩnh)
VISUAL_TIMELINE_SCHEMA = {
    "type": "object",
    "required": ["time_offset", "action", "bg_prompt"],
    "properties": {
        "time_offset": {
            "type": "number",
            "minimum": 0,
            "description": "Start time of the visual event relative to scene start (in seconds)"
        },
        "bg_prompt": {
            "type": "string",
            "minLength": 1,
            "description": "Background prompt for this timeline segment"
        },
        "action": {
            "type": "string",
            "description": "Stickman character pose or camera action"
        },
        "b_roll": {
            "type": "string",
            "description": "Optional B-roll description to show at this timeline segment"
        },
        "emotion_icon": {
            "type": "string",
            "description": "Optional emotion icon to appear"
        }
    },
    "additionalProperties": False
}

# Schema cho một scene trong project
SCENE_SCHEMA = {
    "type": "object",
    "required": [
        "scene_id",
        "text",
        "word_count",
        "expected_duration",
        "audio_path",
        "visual_timeline"
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
        "actual_duration": {
            "type": "number",
            "minimum": 0.1,
            "description": "Actual audio duration of this scene in seconds"
        },
        "audio_path": {
            "type": "string",
            "description": "Path to the generated audio file"
        },
        "bg_seed": {
            "type": "integer",
            "minimum": 0,
            "description": "Seed for background generation (ensures style consistency)"
        },
        "visual_timeline": {
            "type": "array",
            "minItems": 1,
            "items": VISUAL_TIMELINE_SCHEMA,
            "description": "List of visual timeline events in this scene"
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
