```markdown
# 🎯 KẾ HOẠCH NÂNG CẤP STICKMAN FACTORY (BẢN CHUẨN)

**Ngữ cảnh:** Dự án cần render video dài bằng cách chia nhỏ thành các Chunk để chống tràn RAM, và yêu cầu nhân vật đổi dáng mượt mà nhiều lần trong cùng một Scene.

---

## 🛠️ TASK 1: Xử lý Chunking Render nội bộ trong `renderer.py`
**Mục tiêu:** Tự động chia nhỏ video khi render và nối lại bằng FFmpeg. KHÔNG sửa đổi file `orchestrator.py`, giữ nguyên input của `render_video`.

**Yêu cầu cập nhật `src/pipeline/renderer.py`:**
1. Trong hàm `render_video`, sau khi đã chuẩn bị xong biến `project_data` (và copy assets sang public cache), hãy viết logic chia mảng `project_data["scenes"]` thành các nhóm nhỏ (chunks).
   - Thuật toán: Cộng dồn `actual_duration` (hoặc `expected_duration`). Khi tổng thời gian của chunk hiện tại >= 60 giây, ngắt sang chunk mới.
2. Chạy vòng lặp `for i, chunk_scenes in enumerate(chunks)`:
   - Tạo biến `chunk_data = project_data.copy()` và gán `chunk_data["scenes"] = chunk_scenes`.
   - Ghi dữ liệu này ra các file tạm như `props_chunk_0.json`, `props_chunk_1.json`.
   - Gọi `subprocess.run` thực thi Remotion CLI để render từng file: `output_part_{i}.mp4`.
3. **Ghép nối FFmpeg (Concat) an toàn:**
   - Tạo file `list.txt` nằm CÙNG THƯ MỤC với các file `output_part`.
   - Ghi nội dung theo chuẩn: `file 'output_part_0.mp4'` (Dùng tên file tương đối, KHÔNG dùng đường dẫn tuyệt đối để tránh lỗi dấu gạch chéo trên Windows).
   - Gọi lệnh hệ thống: `ffmpeg -f concat -safe 0 -i list.txt -c copy final_video.mp4`
   - Dọn rác: Xóa file `list.txt`, các file `props_chunk` và `output_part_{i}`. Trả về đường dẫn video cuối cùng.

---

## 🎭 TASK 2: Nâng cấp Hoạt ảnh (Animation) theo mốc thời gian

**Bước 2.1: Sửa JSON Schema (`src/core/json_schema.py`)**
- Xóa `"character_state"` khỏi phần `properties`. Thay bằng cấu trúc sau:
  ```python
  "actions": {
      "type": "array",
      "items": {
          "type": "object",
          "properties": {
              "time_start": { "type": "number", "description": "Thời gian bắt đầu đổi dáng (giây)" },
              "action": { "type": "string", "enum": ["idle", "wave", "point", "walk", "sad", "happy"] }
          },
          "required": ["time_start", "action"]
      }
  }

```

* **QUAN TRỌNG:** Trong mảng `"required"` của biến `SCENE_SCHEMA`, bắt buộc phải xóa string `"character_state"` và thêm string `"actions"` vào để Validator không báo lỗi.
* Mở file `src/script/mock_data.py` và sửa dữ liệu mẫu (mock data) sao cho phù hợp với schema mới này.

**Bước 2.2: Tính toán Frame tương đối trong `Scene.tsx**`

* Trong component `<Scene />`:
* Lấy `const frame = useCurrentFrame();` và `const { fps } = useVideoConfig();`.
* Tính thời gian hiện tại của cảnh: `const currentTime = frame / fps;`.
* Duyệt mảng `data.actions` để tìm action hiện hành (action có `time_start <= currentTime` gần nhất).
* Tính **Frame tương đối (Relative Frame)** để reset hiệu ứng nẩy:
`const actionStartFrame = Math.round(currentAction.time_start * fps);`
`const relativeFrame = frame - actionStartFrame;`
* Truyền cả 2 props xuống Stickman: `<Stickman action={currentAction.action} actionFrame={relativeFrame} ... />`



**Bước 2.3: Kích hoạt lại Spring Bounce trong `Stickman.tsx**`

* Thêm `actionFrame?: number` vào interface `StickmanProps`.
* Sửa lại tính toán hiệu ứng nẩy (`spring`):
```tsx
const activeFrame = actionFrame !== undefined ? actionFrame : frame;

const bounce = spring({
    frame: activeFrame, // Sử dụng activeFrame để Stickman nẩy lên mỗi khi đổi dáng
    fps,
    config: { damping: 10, mass: 0.5, stiffness: 100 },
});

```
