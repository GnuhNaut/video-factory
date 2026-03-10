
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.audio.sync_checker import apply_timeline_scaling

def test_scaling():
    scenes = [
        {
            "scene_id": 1,
            "expected_duration": 10.0,
            "actual_duration": 12.0, # 20% slower
            "visual_timeline": [
                {"time_offset": 0, "action": "idle"},
                {"time_offset": 5.0, "action": "wave"}
            ]
        }
    ]
    
    print("Before scaling:", scenes[0]["visual_timeline"])
    scaled_scenes = apply_timeline_scaling(scenes)
    print("After scaling:", scaled_scenes[0]["visual_timeline"])
    
    # Expected: 5.0 * 1.2 = 6.0
    assert scaled_scenes[0]["visual_timeline"][1]["time_offset"] == 6.0
    print("Test passed!")

if __name__ == "__main__":
    test_scaling()
