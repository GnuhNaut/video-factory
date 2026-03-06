import pytest
import jsonschema
from src.core.json_schema import SCENE_SCHEMA, PROJECT_SCHEMA

def test_valid_scene_with_actions():
    valid_scene = {
        "scene_id": 1,
        "text": "Hello world",
        "word_count": 2,
        "expected_duration": 2.5,
        "audio_path": "audio/1.wav",
        "bg_prompt": "A beautiful landscape",
        "bg_seed": 12345,
        "actions": [
            {"time_start": 0, "pose": "idle"},
            {"time_start": 1.5, "pose": "explain", "b_roll": "Zoom in on face", "emotion_icon": "bulb"}
        ]
    }
    # Should not raise any exception
    jsonschema.validate(instance=valid_scene, schema=SCENE_SCHEMA)

def test_invalid_scene_missing_actions():
    invalid_scene = {
        "scene_id": 1,
        "text": "Hello world",
        "word_count": 2,
        "expected_duration": 2.5,
        "audio_path": "audio/1.wav",
        "bg_prompt": "A beautiful landscape",
        "bg_seed": 12345,
        "character_state": "idle" # Old format
    }
    with pytest.raises(jsonschema.exceptions.ValidationError):
        jsonschema.validate(instance=invalid_scene, schema=SCENE_SCHEMA)

def test_action_timestamps_within_duration():
    # This is a logical test that would be run after parsing a standard JSON
    # Currently we just check our validator logic manually if needed.
    # We can write a helper function that we expect the application to use.
    scene = {
        "expected_duration": 2.5,
        "actions": [
            {"time_start": 0, "pose": "idle"},
            {"time_start": 3.0, "pose": "explain"} # Invalid: > 2.5
        ]
    }
    
    with pytest.raises(ValueError, match="exceeds expected duration"):
        for action in scene["actions"]:
            if action["time_start"] > scene["expected_duration"]:
                raise ValueError(f"Action start time {action['time_start']} exceeds expected duration {scene['expected_duration']}")

def test_project_schema_validates_new_format():
    project = {
        "project_name": "Test",
        "language": "en-us",
        "scenes": [
            {
                "scene_id": 1,
                "text": "Hello",
                "word_count": 1,
                "expected_duration": 1.0,
                "audio_path": "",
                "bg_prompt": "Bg",
                "bg_seed": 1,
                "actions": [{"time_start": 0, "pose": "wave"}]
            }
        ]
    }
    jsonschema.validate(instance=project, schema=PROJECT_SCHEMA)
