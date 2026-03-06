"""
json_schema.py - Định nghĩa schema cho kịch bản video

Sử dụng jsonschema để validate cấu trúc JSON project files.
Mỗi project chứa danh sách scenes với các trường bắt buộc.
"""
# Schema cho một action keyframe trong scene (thay thế cho character_state tĩnh tĩnh)
ACTION_KEYFRAME_SCHEMA = {
    "type": "object",
    "required": ["time_start", "pose"],
    "properties": {
        "time_start": {
            "type": "number",
            "minimum": 0,
            "description": "Start time of the action relative to scene start (in seconds)"
        },
        "pose": {
            "type": "string",
            "enum": ["idle", "wave", "point", "walk", "sad", "happy", "explain", "pointing", "counting", "writing", "sitting", "fist_pump"],
            "description": "Stickman character pose/state"
        },
        "b_roll": {
            "type": "string",
            "description": "Optional B-roll description to show at this keyframe"
        },
        "emotion_icon": {
            "type": "string",
            "enum": ["sweat", "question", "bulb", "heart", "anger", "none"],
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
        "bg_prompt",
        "bg_seed",
        "actions"
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
        "actions": {
            "type": "array",
            "minItems": 1,
            "items": ACTION_KEYFRAME_SCHEMA,
            "description": "List of character action keyframes in this scene"
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
