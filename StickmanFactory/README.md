# 🎬 StickmanFactory - Hướng dẫn sử dụng (Phase 3)

## 📋 Mục lục
- [Yêu cầu hệ thống](#-yêu-cầu-hệ-thống)
- [Cài đặt](#-cài-đặt)
- [Cấu hình](#-cấu-hình)
- [Sử dụng từng module](#-sử-dụng-từng-module)
- [Chạy test](#-chạy-test)
- [Cấu trúc thư mục](#-cấu-trúc-thư-mục)
- [API Reference](#-api-reference)

---

## 💻 Yêu cầu hệ thống

| Thành phần | Phiên bản | Ghi chú |
|------------|-----------|---------|
| Python | 3.9+ | Đã test trên 3.11 |
| FFmpeg | 8.0+ | Cần có `ffmpeg.exe` và `ffprobe.exe` |
| Kokoro TTS | 0.9.4 | Source local (không cần pip install) |
| GPU | NVIDIA (optional) | Tăng tốc Kokoro inference |

---

## 🔧 Cài đặt

### 1. Tạo Virtual Environment

```bash
cd StickmanFactory

# Tạo venv
python -m venv venv

# Kích hoạt venv (Windows CMD / PowerShell)
venv\Scripts\activate

# Kích hoạt venv (Git Bash trên Windows)
source venv/Scripts/activate
```

> 💡 Sau khi kích hoạt, bạn sẽ thấy `(venv)` ở đầu dòng terminal.

### 2. Cài dependencies

```bash
# Cài dependencies cơ bản
python -m pip install -r requirements.txt

# Cài Kokoro dependencies (bắt buộc cho TTS)
python -m pip install loguru "misaki[en]" torch transformers huggingface_hub
```

> ⚠️ **Luôn dùng `python -m pip`** thay vì `pip` trực tiếp để tránh lỗi launcher trên Windows.

> 💡 `torch` khá nặng (~2GB). Nếu có GPU NVIDIA, cài phiên bản CUDA:
> ```bash
> python -m pip install torch --index-url https://download.pytorch.org/whl/cu121
> ```

> 💡 Để tải model Kokoro nhanh hơn, set HuggingFace token:
> ```bash
> set HF_TOKEN=hf_your_token_here
> ```

### 3. Kiểm tra cài đặt

```bash
python src/main.py --test-all
```

> ⚠️ Lần đầu chạy Kokoro, model `hexgrad/Kokoro-82M` (~350MB) sẽ được tải tự động từ HuggingFace.

**Kết quả mong đợi:**
```
  TEST SUMMARY
  Config          ✅ PASSED
  Timekeeper      ✅ PASSED
  Stickman        ✅ PASSED
  Validator       ✅ PASSED
  Kokoro          ✅ PASSED

  Total: 5 passed, 0 failed, 0 skipped
```

### 4. Lần sau mở project

Mỗi khi mở terminal mới, cần kích hoạt lại venv trước khi chạy:
```bash
cd StickmanFactory
venv\Scripts\activate
python src/main.py --test-all
```

---

## ⚙️ Cấu hình

File `config.json` ở thư mục gốc project. Chỉnh sửa các đường dẫn phù hợp máy bạn:

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
    "kokoro_path": "D:/Workspace/kokoro_tts/kokoro",  ← Thư mục source Kokoro
    "kokoro_voice": "af_bella",                        ← ID giọng đọc
    "sd_checkpoint": "D:/AI_Models/Flux/flux1-dev.safetensors"
  },
  "paths": {
    "ffmpeg": "D:/Workspace/ffmpeg-8.0.1-full_build/bin/ffmpeg.exe",
    "output_root": "./storage/renders"
  }
}
```

### Giọng đọc Kokoro có sẵn

| Voice ID | Ngôn ngữ | Giới tính |
|----------|-----------|-----------|
| `af_bella` | 🇺🇸 English | Nữ |
| `af_heart` | 🇺🇸 English | Nữ (storytelling) |
| `am_adam` | 🇺🇸 English | Nam |
| `bf_emma` | 🇬🇧 British | Nữ |
| `bm_george` | 🇬🇧 British | Nam |

> 💡 Danh sách đầy đủ: xem README của Kokoro project.

---

## 🚀 Sử dụng từng module

### 1. Config Loader

```python
from src.core.config_loader import load_config, get_nested

# Load toàn bộ config
config = load_config()

# Truy cập nested key an toàn
voice = get_nested(config, "models", "kokoro_voice")         # → "af_bella"
wpm = get_nested(config, "project", "wpm")                   # → 150
missing = get_nested(config, "models", "not_exist", default="N/A")  # → "N/A"
```

### 2. Timekeeper Calculator

```python
from src.timekeeper.calculator import (
    calculate_target_words,
    estimate_duration,
    validate_script_length,
    adjust_speed_factor
)

# Tính số từ cần viết cho video 11 phút
words = calculate_target_words(duration_min=11, wpm=150)
# → 1650 từ

# Ước lượng thời lượng từ kịch bản
script = "Your English script text goes here..."
duration = estimate_duration(script, wpm=150)
# → giây

# Kiểm tra kịch bản có đúng độ dài không (±5%)
is_ok, actual, msg = validate_script_length(script, target_words=1650)
print(msg)  # "✅ Word count 1650 is within ±5% of target 1650"

# Tính hệ số tốc độ nếu audio lệch quá nhiều
speed = adjust_speed_factor(actual_duration=700, target_duration=660)
# → 1.061 (cần đọc nhanh hơn 6%)
```

### 3. Kokoro TTS

```python
from src.audio.kokoro_wrapper import KokoroWrapper

# Khởi tạo (tự load config)
tts = KokoroWrapper()

# Sinh audio
duration = tts.generate_audio(
    text="Hello world. This is a test.",
    output_path="storage/cache/output.wav",
    voice_id="af_bella",    # Tùy chọn, mặc định từ config
    speed=1.0               # 0.95 = chậm hơn (storytelling)
)
print(f"Audio dài: {duration}s")
# → File WAV 24kHz, đã normalize -16 LUFS
```

**Từ command line:**
```bash
python src/audio/kokoro_wrapper.py --test "Once upon a time, in a quiet village"
# → Sinh file storage/cache/test.wav
```

### 4. Stickman Generator

```python
from src.visual.stickman_gen import Stickman

# Tạo nhân vật
character = Stickman(
    color="#000000",        # Màu chính
    line_width=3,           # Độ dày nét
    scale=1.0,              # Tỷ lệ
    accent_color="#3498db"   # Màu phụ
)

# Sinh SVG cho từng trạng thái
character.generate_state("idle")    # Đứng yên
character.generate_state("wave")    # Vẫy tay
character.generate_state("point")   # Chỉ tay
character.generate_state("walk")    # Đang đi
character.generate_state("happy")   # Vui
character.generate_state("sad")     # Buồn

# Chỉ định output path
character.generate_state("idle", output_path="my_stickman.svg")
```

**Từ command line:**
```bash
python src/visual/stickman_gen.py --test
# → Sinh 6 file SVG trong assets/characters/
```

### 5. JSON Validator

```python
from src.core.validator import validate_project_json, validate_project_file

# Validate từ dict
data = {
    "project_name": "My Video",
    "language": "en-us",
    "scenes": [...]
}
is_valid, errors = validate_project_json(data)

# Validate từ file
is_valid, errors = validate_project_file("sample_project.json")
if not is_valid:
    for err in errors:
        print(f"[{err['path']}] {err['message']}")
```

**Từ command line:**
```bash
python src/core/validator.py --check sample_project.json
# → ✅ Valid
```

### 6. Background Prompt

```python
from src.visual.bg_prompt import generate_bg_prompt, generate_bg_negative_prompt

# Tạo prompt cho background
prompt = generate_bg_prompt(
    "A peaceful park with green trees",
    style="cartoon"  # cartoon | realistic | minimalist | watercolor | pixel
)
# → "A peaceful park with green trees, colorful cartoon style, ..."

negative = generate_bg_negative_prompt()
# → "text, watermark, signature, ..."
```

---

## ✅ Chạy test (Phase 1)

| Lệnh | Test |
|-------|------|
| `python src/main.py --test-all` | **Tất cả** module |
| `python src/main.py --test-config` | Config loader |
| `python src/main.py --test-timekeeper` | Bộ tính thời gian |
| `python src/main.py --test-stickman` | Sinh Stickman SVG |
| `python src/main.py --test-validator` | JSON validator |
| `python src/main.py --test-kokoro` | Kokoro TTS |

Hoặc chạy trực tiếp từng module:
```bash
python src/timekeeper/calculator.py --test
python src/visual/stickman_gen.py --test
python src/audio/kokoro_wrapper.py --test "Your text here"
python src/core/validator.py --check sample_project.json
```

---

## 🎬 Phase 2 - Audio Pipeline (Mock-First)

### Chạy pipeline hoàn chỉnh

```bash
python src/pipeline/orchestrator.py
```

Pipeline sẽ thực hiện 5 bước tự động:

```
STEP 1 → Load kịch bản (từ data/sample_project.json)
STEP 2 → Sinh audio cho 16 scenes (Kokoro TTS)
STEP 3 → Normalize âm lượng -16 LUFS (FFmpeg)
STEP 4 → Đồng bộ duration thực tế vs dự kiến
STEP 5 → Lưu project_ready.json (JSON cuối cùng)
```

**Output:**
- `storage/cache/audio/` — 16 file WAV (`audio_001.wav` → `audio_016.wav`)
- `storage/cache/json/project_ready.json` — JSON đã cập nhật `actual_duration`

### Chế độ Mock vs API

Trong `config.json`:
```json
"llm": {
  "enabled": false,     ← false = Mock (đọc file), true = API (reserved)
  "mode": "mock",
  "mock_file_path": "./data/sample_project.json"
}
```

- **Mock (hiện tại):** Đọc kịch bản từ `data/sample_project.json` — không cần LLM API.
- **API (tương lai):** Đặt `enabled: true` + triển khai `src/script/api_connector.py`.

### Sử dụng từng module Phase 2

#### Script Generator
```python
from src.script.generator import get_script

data = get_script()  # Tự chọn Mock hoặc API theo config
scenes = data["scenes"]
```

#### Batch Audio Processor
```python
from src.audio.batch_processor import generate_all_audio

# Sinh audio cho tất cả scenes (có progress bar)
scenes = generate_all_audio(scenes, voice_id="af_bella", speed=0.95)
```

#### Audio Normalizer
```python
from src.audio.normalizer import normalize_scenes

normalize_scenes(scenes)  # Normalize tất cả file về -16 LUFS
```

#### Duration Sync Checker
```python
from src.audio.sync_checker import update_durations

result = update_durations(scenes)
print(f"Total: {result['total_actual']:.0f}s, Drift: {result['drift_percent']:+.1f}%")
```

---

## 📁 Cấu trúc thư mục

```
StickmanFactory/
├── config.json                 # Cấu hình (sửa path tại đây)
├── requirements.txt            # Python dependencies
├── sample_project.json         # Dữ liệu mẫu 3 scenes (Phase 1)
│
├── data/
│   └── sample_project.json     # Kịch bản 16 scenes (Phase 2)
│
├── src/
│   ├── main.py                 # Entry point & CLI
│   ├── core/
│   │   ├── config_loader.py    # load_config(), get_nested()
│   │   ├── json_schema.py      # PROJECT_SCHEMA, SCENE_SCHEMA
│   │   └── validator.py        # validate_project_json()
│   ├── timekeeper/
│   │   └── calculator.py       # Tính toán thời gian & số từ
│   ├── audio/
│   │   ├── kokoro_wrapper.py   # KokoroWrapper class
│   │   ├── batch_processor.py  # Sinh audio hàng loạt
│   │   ├── normalizer.py       # Chuẩn hóa -16 LUFS
│   │   └── sync_checker.py     # Đồng bộ duration
│   ├── visual/
│   │   ├── stickman_gen.py     # Stickman class (SVG)
│   │   └── bg_prompt.py        # Sinh prompt background
│   ├── script/
│   │   ├── generator.py        # Mock/API router
│   │   ├── mock_data.py        # Load file mẫu
│   │   └── api_connector.py    # (Reserved) LLM API
│   └── pipeline/
│       └── orchestrator.py     # Pipeline điều phối Phase 2
│
├── assets/
│   ├── characters/             # SVG stickman sinh ra
│   ├── fonts/                  # Font subtitle
│   ├── sfx/                    # Sound effects
│   └── bgm/                    # Background music
│
├── storage/
│   ├── cache/
│   │   ├── audio/              # File WAV đã sinh
│   │   └── json/               # project_ready.json
│   ├── drafts/                 # Video nháp
│   └── renders/                # Video hoàn chỉnh
│
└── logs/
    └── error.log               # Log lỗi
```

---

## 📖 API Reference

### Scene JSON Schema

Mỗi scene trong project JSON cần có:

```json
{
  "scene_id": 1,                    // int, bắt đầu từ 1
  "text": "English narration...",    // string, nội dung đọc
  "word_count": 18,                  // int, số từ trong text
  "expected_duration": 7.2,          // float, thời lượng dự kiến (giây)
  "actual_duration": 0,              // float, duration thực tế (pipeline cập nhật)
  "audio_path": "",                  // string, path file audio (pipeline cập nhật)
  "bg_prompt": "A sunny park...",    // string, prompt cho background AI
  "bg_seed": 42,                     // int, seed cố định (đồng bộ style)
  "character_state": "wave",         // string: idle|wave|point|walk|sad|happy
  "character_action": "wave",        // string, hành động chi tiết (Phase 3)
  "camera_effect": "zoom_in_slow"    // string, hiệu ứng camera (Phase 3)
}
```

### Workflow tổng quan

```
Phase 1: Cơ sở hạ tầng
  ├── Config → Timekeeper → Kokoro → Stickman → Validator

Phase 2: Audio Pipeline (hiện tại)
  ├── Load Script (Mock) → Batch TTS → Normalize → Sync Duration → Save JSON

Phase 3: Video Rendering
  └── Load project_ready.json → Background (Gradient) → Remotion → Final Video
```

## 🚀 Chạy toàn bộ Pipeline (Phase 3)

Phase 3 cho phép chạy toàn bộ quá trình từ Script -> Audio -> Background -> Video MP4 hoàn chỉnh.

### Cấu hình `config.json`
Để chạy render video, hãy đảm bảo cấu hình `image_provider` và `video`:
```json
"image_provider": {
  "enabled": true,
  "mode": "placeholder"
},
"video": {
  "fps": 30,
  "resolution": "1080p"
}
```

### Lệnh chạy
```bash
# Chạy toàn bộ pipeline Phase 3
python src/pipeline/orchestrator.py
```

### Quá trình thực hiện:
1. Load nội dung kịch bản (`project_demo.json`).
2. Sinh âm thanh (Kokoro)
3. Sinh ảnh nền (Pillow - thư mục `storage/cache/images`)
4. Đồng bộ thời lượng âm thanh và hình ảnh
5. Remotion Render MP4 (thư mục `storage/renders/`)
6. Xuất metadata (`storage/cache/json/project_ready.json`)

---

## 🛠 React / Remotion Component
Trong thư mục `remotion/src/components`:
- `Stickman.tsx`: Component hiển thị nhân vật Stickman SVG, có hiệu ứng thở (`breathing`) và nội suy Animation.
- `Background.tsx`: Component hiển thị ảnh nền với Ken Burns effect (zoom, pan).
- `Subtitle.tsx`: Component hiển thị Subtext.
- `Scene.tsx`: Component ghép tất cả dữ liệu phía trên khớp với Audio.
- `VideoRoot.tsx`: Sequence chạy toàn bộ dự án.

> **💡Lưu ý Windows CP1252 Error:** Các tệp `.py` đã được ép xuất `utf-8` để tương tác với màn hình cmd của Windows mà không bị lỗi Encode ở các ký tự lạ.

---

*[Cập nhật: Phase 3 đã hoàn tất! 🎉]*
