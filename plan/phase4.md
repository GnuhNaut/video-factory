# 📄 TÀI LIỆU ĐẶC TẢ KỸ THUẬT: GIAI ĐOẠN 4 (REVISED)
**Tên dự án:** Stickman AI Video Factory
**Giai đoạn:** 4 - System Optimization & Architecture Prep (No AI Image Yet)
**Mục tiêu:** Tối ưu tốc độ xử lý (Audio/Render), xây dựng cơ chế Cache thông minh, sinh Thumbnail chuyên nghiệp và chuẩn hóa kiến trúc để sẵn sàng tích hợp AI Local sau này.

---

## 1. CHIẾN LƯỢC "OPTIMIZE-FIRST"

| Thành phần | Giải pháp hiện tại (Phase 4) | Chuẩn bị cho tương lai |
| :--- | :--- | :--- |
| **Hình ảnh** | Placeholder (Code) | Interface `ImageProvider` đã sẵn sàng |
| **Âm thanh** | **Parallel Processing (Kokoro)** | Giữ nguyên |
| **Cache** | **Hash-based (Audio & Render)** | Mở rộng cho AI Image |
| **Thumbnail** | Remotion (High Quality) | Giữ nguyên |
| **Render** | **Optimized Flags (Concurrency)** | Giữ nguyên |

**Trọng tâm:** Làm cho quy trình hiện tại chạy nhanh nhất có thể, không lãng phí tài nguyên sinh lại những gì đã có.

---

## 2. CẤU TRÚC THƯ MỤC BỔ SUNG

```text
StickmanFactory/
├── src/
│   ├── visual/
│   │   ├── image_provider.py     # (MỚI) Interface chuẩn
│   │   ├── providers/
│   │   │   ├── base.py           # Abstract Base Class
│   │   │   └── placeholder.py    # Implement hiện tại
│   │   └── thumbnail_gen.py      # (MỚI) Sinh thumbnail bằng Remotion
│   ├── core/
│   │   ├── cache_manager.py      # (MỚI) Quản lý hash & skip
│   │   └── logger.py             # (MỚI) Logging chuẩn
│   ├── utils/
│   │   └── parallel.py           # (MỚI) Pool xử lý audio
│   └── pipeline/
│       └── orchestrator.py       # (Cập nhật) Logic tối ưu
├── config.json                   # (Cập nhật) Cache & Render config
└── storage/
    └── cache/
        ├── hashes/               # Lưu hash kiểm tra thay đổi
        └── thumbnails/           # Ảnh thumbnail
```

---

## 3. NHIỆM VỤ CHI TIẾT (TASKS FOR AI AGENT)

### TASK 4.1: Cập nhật `config.json` (Tối ưu & Cache)
**Yêu cầu:** Thêm cấu hình cho cache, song song hóa và render.
```json
{
  "optimization": {
    "cache_enabled": true,
    "audio_parallel_workers": 4,
    "render_concurrency": 2,
    "skip_render_if_exists": true
  },
  "image_provider": {
    "mode": "placeholder",
    "ready_for_ai": true 
  },
  "thumbnail": {
    "enabled": true,
    "resolution": "1280x720",
    "style": "high_contrast"
  },
  "render": {
    "codec": "h264",
    "crf": 23,
    "threads": 0 
  }
}
```

### TASK 4.2: Interface Image Provider (`src/visual/image_provider.py`)
**Mục tiêu:** Chuẩn hóa kiến trúc để sau này chỉ cần viết thêm class mới.
**Yêu cầu:**
1.  **Abstract Base Class `BaseImageProvider`:**
    ```python
    from abc import ABC, abstractmethod
    class BaseImageProvider(ABC):
        @abstractmethod
        def generate(self, prompt, seed, output_path): pass
        @abstractmethod
        def check_health(self): pass
    ```
2.  **Factory:** Hàm `get_provider(mode)` trả về đối tượng `PlaceholderProvider`.
3.  **Lợi ích:** Khi bạn cài AI Local sau này, chỉ cần tạo `LocalAIProvider(BaseImageProvider)` và sửa config, không cần đụng vào logic pipeline.

### TASK 4.3: Quản lý Cache Thông minh (`src/core/cache_manager.py`)
**Mục tiêu:** Không sinh lại Audio/Ảnh nếu nội dung không đổi.
**Yêu cầu:**
1.  **Hàm `calculate_hash(scene_data)`:**
    *   Hash dựa trên `text`, `prompt`, `seed`, `voice_id`.
2.  **Hàm `check_cache(scene_id, current_hash)`:**
    *   Đọc file `storage/cache/hashes.json`.
    *   So sánh hash. Nếu trùng và file tồn tại -> Return `True` (Skip).
3.  **Hàm `update_cache(scene_id, current_hash)`:**
    *   Lưu hash mới sau khi sinh thành công.
4.  **Lưu ý:** Đặc biệt quan trọng với Audio (Kokoro) vì tốn thời gian sinh nhất hiện tại.

### TASK 4.4: Xử lý Audio Song song (`src/utils/parallel.py`)
**Mục tiêu:** Tăng tốc độ sinh audio (Kokoro).
**Yêu cầu:**
1.  Sử dụng `concurrent.futures.ThreadPoolExecutor`.
2.  **Hàm `generate_audio_batch(scenes, max_workers=4)`:**
    *   Chia scenes thành các batch.
    *   Gọi `kokoro_wrapper` song song.
    *   **Quan trọng:** Giới hạn `max_workers` để không quá tải RAM/GPU (Kokoro load model nặng).
3.  **Progress:** Hiển thị thanh tiến độ chung cho toàn bộ batch.

### TASK 4.5: Sinh Thumbnail Tự động (`src/visual/thumbnail_gen.py`)
**Mục tiêu:** Tạo ảnh thumbnail chuẩn YouTube (1280x720) hấp dẫn.
**Yêu cầu:**
1.  **Sử dụng Remotion:** Tạo một `Composition` riêng `ThumbnailComposition`.
    *   Lợi ích: Đồng bộ font, style, nhân vật với video chính.
2.  **Nội dung:**
    *   Background: Gradient màu nổi (Vàng/Đỏ/Đen).
    *   Text: Tiêu đề ngắn gọn (< 5 từ), font cực lớn, viền đậm.
    *   Character: Stickman trạng thái cảm xúc mạnh (Happy/Shock).
3.  **Render:** Chạy lệnh render riêng cho composition này khi kết thúc pipeline.

### TASK 4.6: Tối ưu Render Video (`src/pipeline/renderer.py`)
**Mục tiêu:** Render nhanh nhất có thể với chất lượng chấp nhận được.
**Yêu cầu:**
1.  **Sử dụng Flags:**
    *   `--concurrency=N`: Số luồng render song song (tùy CPU core).
    *   `--codec=h264`: Tương thích YouTube.
    *   `--crf=23`: Cân bằng giữa chất lượng và kích thước.
2.  **Check tồn tại:** Nếu file output đã tồn tại và `skip_render_if_exists: true`, bỏ qua bước render.
3.  **Logging:** Ghi lại thời gian render thực tế để đo lường hiệu suất.

### TASK 4.7: Logging & Error Handling (`src/core/logger.py`)
**Mục tiêu:** Dễ dàng debug khi pipeline chạy dài (10-12 phút).
**Yêu cầu:**
1.  Sử dụng thư viện `logging` của Python.
2.  **Format:** `[TIME] [LEVEL] [MODULE] Message`.
3.  **File Log:** Lưu vào `logs/pipeline_{date}.log`.
4.  **Error Recovery:** Nếu 1 cảnh lỗi (ví dụ: audio fail), log lại và tiếp tục cảnh sau, không dừng toàn bộ pipeline.

---

## 4. QUY TRÌNH KIỂM THỬ (TESTING PROTOCOL)

1.  **Test Cache Logic:**
    *   Chạy pipeline lần 1 -> Ghi nhớ thời gian.
    *   Chạy pipeline lần 2 (không sửa JSON) -> Thời gian phải giảm đáng kể (do skip audio/render).
    *   Sửa 1 chữ trong JSON -> Chỉ cảnh đó phải sinh lại, các cảnh khác vẫn skip.
2.  **Test Parallel Audio:**
    *   Theo dõi CPU/RAM khi chạy. Đảm bảo không bị tràn bộ nhớ.
    *   So sánh thời gian sinh 50 audio file giữa chế độ Single vs Parallel.
3.  **Test Thumbnail:**
    *   Kiểm tra ảnh thumbnail có đúng kích thước 1280x720, chữ rõ ràng không.
4.  **Test Interface:**
    *   Đảm bảo code không bị lỗi khi gọi `ImageProvider` dù chưa có AI thật.

---

## 5. TIÊU CHÍ HOÀN THÀNH (DEFINITION OF DONE)
- [ ] Cơ chế Cache hoạt động chính xác (skip đúng cảnh không đổi).
- [ ] Audio sinh song song nhanh hơn ít nhất 2x so với tuần tự.
- [ ] Thumbnail tự động sinh ra cùng video.
- [ ] Logging rõ ràng, dễ debug.
- [ ] Kiến trúc `ImageProvider` sẵn sàng, chỉ cần viết class mới là có AI.
- [ ] Video render ổn định, không lỗi memory leak khi chạy dài.

