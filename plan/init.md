# 📄 TÀI LIỆU ĐẶC TẢ KỸ THUẬT: GIAI ĐOẠN 1 (PHASE 1)
**Tên dự án:** Stickman AI Video Factory
**Giai đoạn:** 1 - Core Infrastructure & Data Structure
**Mục tiêu:** Xây dựng nền tảng code, cấu trúc dữ liệu JSON, và các module lõi (Thời gian, Audio, Nhân vật) để đảm bảo video đầu ra chuẩn xác 10-12 phút.

---

## 1. YÊU CẦU HỆ THỐNG (SYSTEM REQUIREMENTS)
*   **Ngôn ngữ lập trình:** Python 3.9+, Node.js 18+ (cho Remotion).
*   **Mô hình AI:** Kokoro (Local path), Stable Diffusion/Flux (Local hoặc API).
*   **Công cụ xử lý:** FFmpeg (System Path).
*   **Ngôn ngữ nội dung:** Tiếng Anh (en-us).
*   **Độ dài video mục tiêu:** 10 - 12 phút (600 - 720 giây).
*   **Tốc độ đọc trung bình:** 150 words/phút (WPM).
*   **Nhân vật:** Stickman sinh bằng Code (SVG/Canvas) để đảm bảo đồng bộ 100%.
*   **Bối cảnh:** Sinh bằng AI với Seed cố định để đảm bảo phong cách.

---

## 2. CẤU TRÚC THƯ MỤC (DIRECTORY STRUCTURE)
AI Agent cần tạo chính xác cấu trúc thư mục sau tại thư mục gốc `StickmanFactory/`:

```text
StickmanFactory/
├── .env                        # Biến môi trường (nếu cần)
├── config.json                 # Cấu hình toàn cục (Path model, tham số thời gian)
├── requirements.txt            # Python dependencies
├── package.json                # Node.js dependencies (Remotion)
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── config_loader.py    # Đọc và validate config.json
│   │   ├── json_schema.py      # Định nghĩa schema cho kịch bản
│   │   └── validator.py        # Validate dữ liệu đầu vào/ra
│   ├── timekeeper/
│   │   └── calculator.py       # Tính toán số từ, thời lượng, tốc độ đọc
│   ├── audio/
│   │   └── kokoro_wrapper.py   # Wrapper gọi model Kokoro local
│   ├── visual/
│   │   ├── stickman_gen.py     # Sinh nhân vật Stickman (SVG/PNG)
│   │   └── bg_prompt.py        # Tạo prompt cho background
│   ├── script/
│   │   └── generator.py        # (Reserved for Phase 2)
│   └── main.py                 # Entry point
├── assets/
│   ├── fonts/                  # Font chữ cho subtitle
│   ├── sfx/                    # Sound effects (pop, click, whoosh)
│   └── bgm/                    # Background Music
├── models/                     # (Optional) Nếu cần copy model vào đây, иначе trỏ path ngoài
├── storage/
│   ├── cache/                  # Lưu audio, ảnh đã sinh để tái sử dụng
│   ├── drafts/                 # Video nháp
│   └── renders/                # Video hoàn chỉnh
└── logs/                       # Log hệ thống
```

---

## 3. NHIỆM VỤ CHI TIẾT (TASKS FOR AI AGENT)

### TASK 1.1: Cấu hình Toàn cục (`config.json`)
**Mục tiêu:** Quản lý đường dẫn model và tham số thời gian.
**Yêu cầu:**
1.  Tạo file `config.json` với nội dung mẫu sau (AI cần đảm bảo structure này):
    ```json
    {
      "project": {
        "language": "en-us",
        "target_duration_min": 11,
        "tolerance_sec": 30,
        "wpm": 150,
        "resolution": "1920x1080",
        "fps": 30
      },
      "models": {
        "kokoro_path": "D:/AI_Models/kokoro/models",
        "kokoro_voice": "af_bella",
        "sd_checkpoint": "D:/AI_Models/Flux/flux1-dev.safetensors"
      },
      "character": {
        "type": "svg_vector",
        "base_color": "#000000",
        "accent_color": "#3498db",
        "line_width": 3
      },
      "paths": {
        "ffmpeg": "C:/ffmpeg/bin/ffmpeg.exe",
        "output_root": "./storage/renders"
      }
    }
    ```
2.  Viết module `src/core/config_loader.py` để đọc file này và biến thành object Python. Xử lý lỗi nếu file không tồn tại.

### TASK 1.2: Bộ tính toán Thời gian & Số từ (`src/timekeeper/calculator.py`)
**Mục tiêu:** Đảm bảo video dài chính xác 10-12 phút.
**Logic yêu cầu:**
1.  **Hàm `calculate_target_words(duration_min, wpm)`:**
    *   Input: Thời gian mục tiêu (ví dụ 11), WPM (ví dụ 150).
    *   Output: Tổng số từ cần thiết (ví dụ 1650 words).
2.  **Hàm `estimate_duration(text, wpm)`:**
    *   Input: Văn bản kịch bản.
    *   Output: Thời lượng dự kiến (giây).
3.  **Hàm `validate_script_length(text, target_words, tolerance=0.05)`:**
    *   Kiểm tra xem số từ thực tế có nằm trong khoảng ±5% so với mục tiêu không.
    *   Return: `True/False` và số từ hiện tại.
4.  **Hàm `adjust_speed_factor(actual_duration, target_duration)`:**
    *   Tính toán hệ số tốc độ (speed factor) để truyền vào Kokoro nếu thời lượng lệch quá nhiều (ví dụ: cần đọc nhanh hơn 1.05x).

### TASK 1.3: Wrapper Kokoro Local (`src/audio/kokoro_wrapper.py`)
**Mục tiêu:** Gọi model Kokoro từ đường dẫn cũ trên máy.
**Yêu cầu kỹ thuật:**
1.  Không cài đặt lại qua pip nếu không cần thiết. Sử dụng đường dẫn `models.kokoro_path` từ `config.json`.
2.  **Hàm `generate_audio(text, output_path, voice_id, speed=1.0)`:**
    *   Load model từ path.
    *   Sinh file `.wav`.
    *   Trả về `duration` chính xác của file audio vừa sinh (dùng thư viện `wave` hoặc `ffmpeg probe`).
3.  **Xử lý lỗi:** Nếu model không load được, phải log lỗi rõ ràng vào `logs/error.log`.
4.  **Chuẩn hóa:** Tự động gọi FFmpeg để normalize audio về -16 LUFS (chuẩn YouTube) sau khi sinh.

### TASK 1.4: Bộ sinh nhân vật Stickman (`src/visual/stickman_gen.py`)
**Mục tiêu:** Sinh nhân vật đồng bộ 100% bằng code (không dùng AI image gen cho nhân vật).
**Yêu cầu kỹ thuật:**
1.  Sử dụng thư viện `svgwrite` hoặc vẽ trực tiếp ra file `.svg`.
2.  **Class `Stickman`:**
    *   Tham số khởi tạo: `color`, `line_width`, `scale`.
    *   **Method `generate_state(state)`:**
        *   `idle`: Đứng yên, tay buông.
        *   `wave`: Tay phải gi lên vẫy.
        *   `point`: Tay phải chỉ ngang.
        *   `walk`: Chân tách rộng (dùng cho ảnh tĩnh thể hiện đang đi).
        *   `sad/happy`: Thay đổi độ cong miệng (nếu có mặt) hoặc góc độ thân người.
    *   **Output:** File SVG hoặc PNG trong suốt (transparent background).
3.  **Đảm bảo:** Tọa độ các khớp (head, body, limbs) phải cố định để khi ghép vào Remotion không bị giật.

### TASK 1.5: Schema & Validator (`src/core/json_schema.py`)
**Mục tiêu:** Định nghĩa cấu trúc JSON kịch bản chuẩn.
**Yêu cầu:**
1.  Định nghĩa `PROJECT_SCHEMA` sử dụng thư viện `jsonschema`.
2.  Các trường bắt buộc trong mỗi `scene`:
    *   `scene_id` (int)
    *   `text` (string, English)
    *   `word_count` (int)
    *   `expected_duration` (float)
    *   `audio_path` (string)
    *   `bg_prompt` (string)
    *   `bg_seed` (int) - *Quan trọng để đồng bộ style ảnh*
    *   `character_state` (string)
3.  **Hàm `validate_project_json(json_data)`:**
    *   Return `True` nếu đúng schema.
    *   Return `False` và danh sách lỗi nếu sai.

### TASK 1.6: File mẫu (`sample_project.json`)
**Mục tiêu:** Cung cấp dữ liệu mẫu để test hệ thống.
**Yêu cầu:**
1.  Tạo file `sample_project.json` chứa 3 scenes mẫu.
2.  Đảm bảo tổng thời lượng 3 scenes này khoảng 15-20 giây để test nhanh.
3.  Nội dung tiếng Anh, đúng schema đã định nghĩa ở Task 1.5.

---

## 4. QUY TRÌNH KIỂM THỬ (TESTING PROTOCOL)
AI Agent cần viết script test hoặc hướng dẫn user chạy các lệnh sau để xác nhận hoàn thành Phase 1:

1.  **Test Config:**
    *   Chạy `python src/main.py --test-config`
    *   Kết quả mong đợi: In ra console các tham số đã load từ `config.json` không lỗi.
2.  **Test Time Calculator:**
    *   Chạy `python src/timekeeper/calculator.py --test`
    *   Kết quả mong đợi: In ra số từ mục tiêu cho 11 phút (khoảng 1650 từ).
3.  **Test Kokoro:**
    *   Chạy `python src/audio/kokoro_wrapper.py --test "Hello world"`
    *   Kết quả mong đợi: Sinh file `test.wav` trong `storage/cache/`, có âm thanh, độ dài > 0 giây.
4.  **Test Stickman:**
    *   Chạy `python src/visual/stickman_gen.py --test`
    *   Kết quả mong đợi: Sinh file `stickman_idle.svg` và `stickman_wave.svg` trong `assets/characters/`.
5.  **Test JSON Validator:**
    *   Chạy `python src/core/validator.py --check sample_project.json`
    *   Kết quả mong đợi: Trả về `Valid`.

---

## 5. TIÊU CHÍ HOÀN THÀNH (DEFINITION OF DONE)
Phase 1 chỉ được coi là hoàn thành khi:
1.  [ ] Cấu trúc thư mục tồn tại đầy đủ.
2.  [ ] File `config.json` đúng đường dẫn model Kokoro trên máy user.
3.  [ ] Script test Kokoro sinh được âm thanh tiếng Anh rõ ràng.
4.  [ ] Script sinh Stickman tạo được file ảnh trong suốt, nét đều.
5.  [ ] Module tính toán thời gian trả về kết quả chính xác (sai số < 1%).
6.  [ ] File JSON mẫu vượt qua validator.

