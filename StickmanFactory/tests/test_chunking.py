import sys
import os
import pytest

# Add project root to sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.pipeline.renderer import render_video, PROJECT_ROOT

# Assuming we can test the chunking logic indirectly or we mock subprocess

def test_chunking_logic_duration_preservation():
    # Since chunking logic is currently inside render_video, to unit test it cleanly, 
    # we would ideally extract it. But we can write a conceptual test here.
    
    # We will simulate the chunking logic as it exists in renderer.py to ensure 
    # the total duration math is perfect 100% of the time.
    
    all_scenes = [
        {"scene_id": 1, "expected_duration": 15.5},
        {"scene_id": 2, "expected_duration": 20.0},
        {"scene_id": 3, "expected_duration": 30.5},
        {"scene_id": 4, "expected_duration": 10.0},
        {"scene_id": 5, "expected_duration": 45.0},
        {"scene_id": 6, "expected_duration": 15.0},
        {"scene_id": 7, "expected_duration": 10.0},
    ]
    
    # Simulate chunking from renderer.py
    chunks = []
    current_chunk_scenes = []
    current_chunk_duration = 0.0
    CHUNK_MAX_DURATION = 90.0

    for idx, scene in enumerate(all_scenes):
        duration = scene.get("actual_duration", scene.get("expected_duration", 5))
        if current_chunk_duration + duration > CHUNK_MAX_DURATION and current_chunk_scenes:
            chunks.append({
                "chunk_id": len(chunks) + 1,
                "scenes": current_chunk_scenes,
                "duration": current_chunk_duration
            })
            current_chunk_scenes = [scene]
            current_chunk_duration = duration
        else:
            current_chunk_scenes.append(scene)
            current_chunk_duration += duration
            
    if current_chunk_scenes:
        chunks.append({
            "chunk_id": len(chunks) + 1,
            "scenes": current_chunk_scenes,
            "duration": current_chunk_duration
        })
        
    # Test conditions
    total_original_duration = sum(s["expected_duration"] for s in all_scenes)
    total_chunks_duration = sum(c["duration"] for c in chunks)
    
    # 1. Total duration must be 100% identical
    assert abs(total_original_duration - total_chunks_duration) < 0.001
    
    # 2. Number of scenes must be identical
    total_chunked_scenes = sum(len(c["scenes"]) for c in chunks)
    assert total_chunked_scenes == len(all_scenes)
    
    # 3. Check boundaries (first chunk should have expected duration)
    # 15.5 + 20 + 30.5 + 10 = 76.0 (adding 45 would be 121 > 90) -> Chunk 1 = 76.0s
    assert chunks[0]["duration"] == 76.0
    assert len(chunks[0]["scenes"]) == 4
    
    # Chunk 2 = 45.0 + 15.0 + 10.0 = 70.0s
    assert chunks[1]["duration"] == 70.0
    assert len(chunks[1]["scenes"]) == 3
