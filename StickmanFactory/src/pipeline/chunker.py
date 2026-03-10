"""
chunker.py - Smart Chunking cho Video
Chia video dài thành các đoạn nhỏ (chunk) xấp xỉ 1 phút.
Đảm bảo không cắt giữa chừng một scene (bảo toàn trọn vẹn scene logic).
"""

import json
import os
import copy
import sys

def create_chunks(project_data: dict, output_dir: str, target_chunk_duration: float = 60.0) -> list:
    """
    Chia project data thành các chunks.

    Args:
        project_data: Nội dung file project JSON.
        output_dir: Thư mục lưu các file chunk JSON.
        target_chunk_duration: Thời lượng mong muốn mỗi chunk (giây). Default: 60s.

    Returns:
        List paths tới các file chunk JSON đã tạo.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    scenes = project_data.get("scenes", [])
    if not scenes:
        return []

    chunks = []
    current_chunk_scenes = []
    current_chunk_duration = 0.0
    chunk_index = 1

    for scene in scenes:
        # Lấy thời lượng thực tế, nếu chưa có lấy expected
        duration = scene.get("actual_duration", scene.get("expected_duration", 0))
        
        # Nếu thêm scene này vào chunk hiện tại mà vượt quá mục tiêu
        # VÀ chunk hiện tại ĐÃ CÓ data (không bị rỗng) thì cắt chunk
        if current_chunk_duration + duration > target_chunk_duration and current_chunk_scenes:
            # Lưu lại chunk
            chunk_data = copy.deepcopy(project_data)
            chunk_data["scenes"] = current_chunk_scenes
            chunk_data["chunk_id"] = chunk_index
            
            chunk_path = os.path.join(output_dir, f"chunk_{chunk_index:03d}.json")
            with open(chunk_path, "w", encoding="utf-8") as f:
                json.dump(chunk_data, f, indent=4, ensure_ascii=False)
            
            chunks.append(chunk_path)
            
            # Reset cho chunk tiếp theo
            chunk_index += 1
            current_chunk_scenes = []
            current_chunk_duration = 0.0

        current_chunk_scenes.append(scene)
        current_chunk_duration += duration

    # Lưu chunk cuối cùng nếu còn
    if current_chunk_scenes:
        chunk_data = copy.deepcopy(project_data)
        chunk_data["scenes"] = current_chunk_scenes
        chunk_data["chunk_id"] = chunk_index
        
        chunk_path = os.path.join(output_dir, f"chunk_{chunk_index:03d}.json")
        with open(chunk_path, "w", encoding="utf-8") as f:
            json.dump(chunk_data, f, indent=4, ensure_ascii=False)
        
        chunks.append(chunk_path)

    return chunks

if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        out_dir = sys.argv[2] if len(sys.argv) > 2 else "storage/renders/chunks"
        
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        chunks = create_chunks(data, out_dir)
        print(f"Created {len(chunks)} chunks in {out_dir}")
        for c in chunks:
            print(" -", c)
"""
