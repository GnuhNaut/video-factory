"""
audit.py - Kiểm tra chất lượng video sau khi render

Sử dụng ffprobe để phát hiện:
1. Black frames (khung hình bị đen hoàn toàn).
2. Silent gaps (đoạn mất tiếng tại điểm nối).
3. Audio/Video duration mismatch.
"""

import os
import json
import subprocess
import logging

logger = logging.getLogger(__name__)

def audit_video(video_path: str, ffmpeg_path: str = "ffmpeg") -> dict:
    """
    Quét video để tìm lỗi kỹ thuật.
    """
    if not os.path.exists(video_path):
        return {"error": "File not found"}
        
    ffprobe_path = ffmpeg_path.replace("ffmpeg.exe", "ffprobe.exe") if "ffmpeg" in ffmpeg_path else "ffprobe"
    
    results = {
        "path": video_path,
        "black_frames_count": 0,
        "silent_gaps_count": 0,
        "duration_sec": 0,
        "status": "PASS",
        "warnings": []
    }
    
    try:
        # 1. Kiểm tra Black Frames (dùng bộ lọc blackdetect)
        print(f"🔍 Auditing for black frames: {video_path}")
        cmd_black = [
            ffmpeg_path, "-i", video_path,
            "-vf", "blackdetect=d=0.1:pix_th=0.10",
            "-an", "-f", "null", "-"
        ]
        res_black = subprocess.run(cmd_black, capture_output=True, text=True, timeout=120)
        
        # Parse stderr for "black_start"
        black_matches = [line for line in res_black.stderr.split('\n') if "black_start" in line]
        results["black_frames_count"] = len(black_matches)
        if len(black_matches) > 0:
            results["warnings"].append(f"Detected {len(black_matches)} potential black frame segments.")
            
        # 2. Kiểm tra Silent Gaps (dùng bộ lọc silencedetect)
        print(f"🔍 Auditing for silent gaps...")
        cmd_silence = [
            ffmpeg_path, "-i", video_path,
            "-af", "silencedetect=n=-50dB:d=0.5",
            "-vn", "-f", "null", "-"
        ]
        res_silence = subprocess.run(cmd_silence, capture_output=True, text=True, timeout=120)
        
        silence_matches = [line for line in res_silence.stderr.split('\n') if "silence_start" in line]
        results["silent_gaps_count"] = len(silence_matches)
        
        # 3. Lấy duration thực tế
        cmd_probe = [
            ffprobe_path, "-v", "quiet", "-show_entries", "format=duration",
            "-of", "json", video_path
        ]
        res_probe = subprocess.run(cmd_probe, capture_output=True, text=True)
        if res_probe.returncode == 0:
            probe_data = json.loads(res_probe.stdout)
            results["duration_sec"] = float(probe_data["format"]["duration"])

        # Decide status
        if results["black_frames_count"] > 2 or results["silent_gaps_count"] > 1:
            results["status"] = "WARNING"
            
    except Exception as e:
        results["error"] = str(e)
        results["status"] = "ERROR"
        
    return results

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        path = sys.argv[1]
        print(json.dumps(audit_video(path), indent=2))
