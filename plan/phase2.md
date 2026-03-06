# 📄 TÀI LIỆU ĐẶC TẢ KỸ THUẬT: GIAI ĐOẠN 2 (REVISED)
**Tên dự án:** Stickman AI Video Factory
**Giai đoạn:** 2 - Audio Pipeline & Script Management (Mock-First)
**Mục tiêu:** Xây dựng quy trình xử lý âm thanh hàng loạt, đồng bộ thời gian thực tế, và quản lý kịch bản ở chế độ Mock (không cần LLM ngay).

---

## 1. CHIẾN LƯỢC "MOCK-FIRST"
*   **Chế độ mặc định:** Hệ thống đọc kịch bản từ file `sample_project.json` có sẵn.
*   **Chế độ tương lai:** Khi có API Key, chỉ cần sửa `config.json` (`llm.enabled: true`), hệ thống sẽ tự gọi API thay vì đọc file mẫu.
*   **Lợi ích:** Bạn có thể test toàn bộ quy trình Audio -> Video ngay lập tức mà không bị phụ thuộc vào bên thứ 3.

---

## 2. CẤU TRÚC THƯ MỤC BỔ SUNG
Thêm vào cấu trúc Phase 1:

```text
StickmanFactory/
├── src/
│   ├── script/
│   │   ├── generator.py          # Logic chọn Mock hoặc API
│   │   ├── mock_data.py          # Chứa logic load file mẫu
│   │   └── api_connector.py      # (Reserved) Cho Groq/API sau này
│   ├── audio/
│   │   ├── batch_processor.py    # Sinh audio hàng loạt từ JSON
│   │   ├── normalizer.py         # Chuẩn hóa âm lượng (FFmpeg)
│   │   └── sync_checker.py       # So sánh duration thực tế vs dự kiến
│   └── pipeline/
│       └── orchestrator.py       # Chạy toàn bộ quy trình Phase 2
├── data/
│   └── sample_project.json       # Kịch bản mẫu (Bạn sẽ dùng file tôi cung cấp bên dưới)
└── storage/
    └── cache/
        ├── audio/                # Chứa file wav đã sinh
        └── json/                 # Chứa JSON đã cập nhật duration thực tế
```

---

## 3. NHIỆM VỤ CHI TIẾT (TASKS FOR AI AGENT)

### TASK 2.1: Cập nhật `config.json` (Chế độ Mock)
**Yêu cầu:**
1.  Thêm trường `llm` vào config:
    ```json
    "llm": {
      "enabled": false,
      "mode": "mock",
      "mock_file_path": "./data/sample_project.json"
    }
    ```
2.  Nếu `enabled: false`, hệ thống bỏ qua bước gọi AI và đọc thẳng từ `mock_file_path`.

### TASK 2.2: Module Sinh Kịch bản (`src/script/generator.py`)
**Yêu cầu:**
1.  **Hàm `get_script(topic=None)`:**
    *   Kiểm tra `config['llm']['enabled']`.
    *   Nếu `False`: Load file từ `mock_file_path`. Validate schema (dùng Phase 1 validator).
    *   Nếu `True`: (Để trống hoặc raise Error "API not configured yet").
2.  **Xử lý đường dẫn:** Đảm bảo đường dẫn file JSON là tương đối hoặc tuyệt đối chính xác.

### TASK 2.3: Bộ xử lý Audio Hàng loạt (`src/audio/batch_processor.py`)
**Yêu cầu:**
1.  **Hàm `generate_all_audio(scenes, output_dir)`:**
    *   Duyệt qua từng scene trong list `scenes`.
    *   Gọi `kokoro_wrapper.generate_audio` (từ Phase 1).
    *   **Tên file:** `audio_{scene_id:03d}.wav` (ví dụ: `audio_001.wav`).
    *   **Lưu path:** Cập nhật đường dẫn file vào object scene.
2.  **Progress Bar:** Dùng thư viện `tqdm` để hiển thị tiến độ sinh audio (ví dụ: "Generating 1/50...").
3.  **Error Handling:** Nếu sinh lỗi 1 cảnh, log lại và tiếp tục cảnh sau (không dừng toàn bộ).

### TASK 2.4: Đồng bộ Thời gian Thực tế (`src/audio/sync_checker.py`)
**Yêu cầu:**
1.  **Vấn đề:** Thời gian dự kiến (`expected_duration`) tính bằng công thức WPM thường sai lệch so với audio thực tế (`actual_duration`).
2.  **Hàm `update_durations(scenes)`:**
    *   Dùng `ffprobe` hoặc thư viện `wave` để đọc độ dài chính xác của file wav vừa sinh.
    *   Cập nhật trường `actual_duration` vào scene.
    *   Tính toán `total_duration` của toàn bộ video.
3.  **Cảnh báo:** Nếu `total_duration` lệch quá 10% so với mục tiêu (10-12 phút), log cảnh báo để user biết cần điều chỉnh kịch bản.

### TASK 2.5: Chuẩn hóa Âm thanh (`src/audio/normalizer.py`)
**Yêu cầu:**
1.  **Hàm `normalize_batch(audio_files)`:**
    *   Chạy FFmpeg loudnorm cho từng file.
    *   Target: `-16 LUFS` (Chuẩn YouTube).
    *   Replace file gốc hoặc lưu file mới `_norm.wav`.
2.  **Mục đích:** Đảm bảo cảnh nói nhỏ không bị thua thiệt so với cảnh nói to.

### TASK 2.6: Bộ điều phối (`src/pipeline/orchestrator.py`)
**Yêu cầu:**
1.  **Hàm `run_phase2()`:**
    *   Bước 1: Load script (Mock).
    *   Bước 2: Sinh audio hàng loạt.
    *   Bước 3: Chuẩn hóa âm thanh.
    *   Bước 4: Cập nhật duration thực tế vào JSON.
    *   Bước 5: Lưu file JSON mới vào `storage/cache/json/project_ready.json`.
2.  **Output:** In ra tổng thời lượng video cuối cùng (ví dụ: "Total Video Duration: 11m 30s").

---

## 4. QUY TRÌNH KIỂM THỬ (TESTING PROTOCOL)
1.  **Test Mock Load:** Chạy script, đảm bảo load được file `sample_project.json` không lỗi.
2.  **Test Audio Gen:** Đảm bảo sinh đủ file wav cho từng scene.
3.  **Test Duration Sync:** Kiểm tra file JSON cuối cùng, trường `actual_duration` phải khác 0 và hợp lý.
4.  **Test Total Time:** Tổng duration phải nằm trong khoảng 10-12 phút (nếu JSON mẫu đủ dài).

---

## 5. TIÊU CHÍ HOÀN THÀNH
- [ ] Hệ thống chạy được từ JSON mẫu -> Audio Files.
- [ ] Audio files được chuẩn hóa âm lượng.
- [ ] JSON cuối cùng cập nhật đúng thời lượng thực tế của audio.
- [ ] Không cần API Key vẫn chạy được toàn bộ quy trình này.

---

# 📄 FILE MẪU: `data/sample_project.json`
**Chủ đề:** "The Hidden Logic of Success" (Logic Ẩn Giấu Của Thành Công)
**Ngôn ngữ:** Tiếng Anh
**Độ dài:** Thiết kế cho ~10-12 phút (Khoảng 1500-1600 từ).
**Lưu ý:** Đây là file đã được tối ưu schema để chạy ngay với hệ thống của bạn.

```json
{
  "meta": {
    "video_id": "STK_001",
    "title": "The Hidden Logic of Success",
    "theme_color": "#3498db",
    "voice_model": "af_bella",
    "target_duration_sec": 660,
    "language": "en-us"
  },
  "character_config": {
    "seed": 42,
    "style_prompt": "minimalist stickman, black lines, white background, vector style",
    "base_color": "#000000"
  },
  "scenes": [
    {
      "scene_id": 1,
      "text": "Have you ever wondered why some people seem to succeed effortlessly while others struggle forever? We often think success is about luck, or maybe just working harder than everyone else.",
      "word_count": 33,
      "expected_duration": 13.2,
      "actual_duration": 0,
      "audio_path": "",
      "bg_prompt": "Abstract background with question marks, soft blue tones, minimalist",
      "bg_seed": 1001,
      "character_state": "idle",
      "character_action": "wave",
      "camera_effect": "zoom_in_slow"
    },
    {
      "scene_id": 2,
      "text": "But what if I told you there is a hidden logic behind every success story? A pattern that repeats itself across history, business, and even personal relationships.",
      "word_count": 31,
      "expected_duration": 12.4,
      "actual_duration": 0,
      "audio_path": "",
      "bg_prompt": "Pattern geometry background, golden ratio spiral, clean style",
      "bg_seed": 1001,
      "character_state": "happy",
      "character_action": "pointing",
      "camera_effect": "none"
    },
    {
      "scene_id": 3,
      "text": "Today, we are going to decode this logic. We will break it down into three simple pillars that anyone can apply, starting today. No gimmicks, no false promises.",
      "word_count": 32,
      "expected_duration": 12.8,
      "actual_duration": 0,
      "audio_path": "",
      "bg_prompt": "Three pillars illustration, minimalist icons, white background",
      "bg_seed": 1001,
      "character_state": "idle",
      "character_action": "counting",
      "camera_effect": "pan_right"
    },
    {
      "scene_id": 4,
      "text": "The first pillar is Consistency. Not the boring kind of consistency where you do the same thing every day, but the strategic kind. It is about showing up when it matters most.",
      "word_count": 34,
      "expected_duration": 13.6,
      "actual_duration": 0,
      "audio_path": "",
      "bg_prompt": "Calendar timeline, checkmarks, green and white theme",
      "bg_seed": 1001,
      "character_state": "serious",
      "character_action": "writing",
      "camera_effect": "zoom_in"
    },
    {
      "scene_id": 5,
      "text": "Think about a drop of water. One drop does nothing. But thousands of drops falling in the same spot can cut through solid rock. That is the power of consistency.",
      "word_count": 32,
      "expected_duration": 12.8,
      "actual_duration": 0,
      "audio_path": "",
      "bg_prompt": "Water drops hitting rock, cinematic lighting, minimalist",
      "bg_seed": 1001,
      "character_state": "idle",
      "character_action": "none",
      "camera_effect": "none"
    },
    {
      "scene_id": 6,
      "text": "The second pillar is Adaptability. The world changes fast. What worked yesterday might not work tomorrow. Successful people are not stubborn; they are flexible like bamboo.",
      "word_count": 32,
      "expected_duration": 12.8,
      "actual_duration": 0,
      "audio_path": "",
      "bg_prompt": "Bamboo forest swaying in wind, serene atmosphere",
      "bg_seed": 1001,
      "character_state": "happy",
      "character_action": "walking",
      "camera_effect": "pan_left"
    },
    {
      "scene_id": 7,
      "text": "When a storm comes, the oak tree resists and might break. The bamboo bends and survives. You must be willing to pivot your strategy without losing sight of your goal.",
      "word_count": 32,
      "expected_duration": 12.8,
      "actual_duration": 0,
      "audio_path": "",
      "bg_prompt": "Stormy weather vs calm forest, contrast illustration",
      "bg_seed": 1001,
      "character_state": "serious",
      "character_action": "pointing",
      "camera_effect": "zoom_out"
    },
    {
      "scene_id": 8,
      "text": "And now, the third pillar. This is the one most people ignore. It is called Restorative Rest. You cannot pour from an empty cup. Burnout is the enemy of success.",
      "word_count": 33,
      "expected_duration": 13.2,
      "actual_duration": 0,
      "audio_path": "",
      "bg_prompt": "Empty cup being filled with water, simple icons",
      "bg_seed": 1001,
      "character_state": "tired",
      "character_action": "sitting",
      "camera_effect": "none"
    },
    {
      "scene_id": 9,
      "text": "Success is not a sprint; it is a marathon. If you run too hard too fast, you will collapse before the finish line. Rest is part of the work, not a break from it.",
      "word_count": 35,
      "expected_duration": 14.0,
      "actual_duration": 0,
      "audio_path": "",
      "bg_prompt": "Marathon runner resting, finish line in distance",
      "bg_seed": 1001,
      "character_state": "happy",
      "character_action": "walking",
      "camera_effect": "zoom_in_slow"
    },
    {
      "scene_id": 10,
      "text": "So, let us put this together. Consistency builds the foundation. Adaptability keeps you standing when things shake. And Rest ensures you have the energy to keep going.",
      "word_count": 31,
      "expected_duration": 12.4,
      "actual_duration": 0,
      "audio_path": "",
      "bg_prompt": "Three pillars combined, pyramid structure, gold accents",
      "bg_seed": 1001,
      "character_state": "idle",
      "character_action": "wave",
      "camera_effect": "zoom_out"
    },
    {
      "scene_id": 11,
      "text": "Imagine where you could be one year from now if you mastered these three pillars. Small changes compound over time. One percent better every day leads to massive results.",
      "word_count": 32,
      "expected_duration": 12.8,
      "actual_duration": 0,
      "audio_path": "",
      "bg_prompt": "Graph line going up, green arrow, minimalist chart",
      "bg_seed": 1001,
      "character_state": "happy",
      "character_action": "pointing",
      "camera_effect": "pan_up"
    },
    {
      "scene_id": 12,
      "text": "But here is the catch. Knowing this logic is not enough. You must apply it. Knowledge without action is just entertainment. And we do not want to be entertained; we want to win.",
      "word_count": 34,
      "expected_duration": 13.6,
      "actual_duration": 0,
      "audio_path": "",
      "bg_prompt": "Brain with gear inside, action oriented background",
      "bg_seed": 1001,
      "character_state": "serious",
      "character_action": "fist_pump",
      "camera_effect": "zoom_in"
    },
    {
      "scene_id": 13,
      "text": "Start small. Pick one habit today. Maybe it is waking up thirty minutes earlier. Maybe it is reading ten pages of a book. Just start. Momentum is everything.",
      "word_count": 32,
      "expected_duration": 12.8,
      "actual_duration": 0,
      "audio_path": "",
      "bg_prompt": "Dominoes falling, first one being pushed",
      "bg_seed": 1001,
      "character_state": "idle",
      "character_action": "walking",
      "camera_effect": "none"
    },
    {
      "scene_id": 14,
      "text": "Remember, the hidden logic of success is not hidden anymore. It is right here in front of you. The question is, will you use it?",
      "word_count": 28,
      "expected_duration": 11.2,
      "actual_duration": 0,
      "audio_path": "",
      "bg_prompt": "Open door with light shining through, hopeful atmosphere",
      "bg_seed": 1001,
      "character_state": "happy",
      "character_action": "wave",
      "camera_effect": "zoom_out_slow"
    },
    {
      "scene_id": 15,
      "text": "Thank you for watching. If you found value in this video, share it with someone who needs to hear this. Let us build a community of winners together.",
      "word_count": 29,
      "expected_duration": 11.6,
      "actual_duration": 0,
      "audio_path": "",
      "bg_prompt": "Community group icons, connected dots, blue theme",
      "bg_seed": 1001,
      "character_state": "happy",
      "character_action": "wave",
      "camera_effect": "none"
    },
    {
      "scene_id": 16,
      "text": "Subscribe for more insights on mastering your life. We have many more stories to uncover. Until next time, keep moving forward.",
      "word_count": 24,
      "expected_duration": 9.6,
      "actual_duration": 0,
      "audio_path": "",
      "bg_prompt": "Subscribe button animation, clean background",
      "bg_seed": 1001,
      "character_state": "idle",
      "character_action": "pointing",
      "camera_effect": "zoom_in"
    }
  ]
}
