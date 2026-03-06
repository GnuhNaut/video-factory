# 📄 TÀI LIỆU ĐẶC TẢ KỸ THUẬT: GIAI ĐOẠN 3 (REVISED)
**Tên dự án:** Stickman AI Video Factory
**Giai đoạn:** 3 - Remotion Composition & Rendering (Placeholder-First)
**Mục tiêu:** Ghép nối Audio, Stickman (Code), Placeholder (Code), Subtitle và Xuất video MP4. Sẵn sàng để tích hợp AI Image Gen sau này.

---

## 1. CHIẾN LƯỢC "PLACEHOLDER-FIRST"

Thay vì chờ AI sinh ảnh, chúng ta sẽ dùng **Python/PIL** để sinh ảnh nền dựa trên `bg_prompt` (dưới dạng text trên ảnh màu gradient).

| Thành phần | Giải pháp hiện tại (Phase 3) | Giải pháp tương lai (Phase 4+) |
| :--- | :--- | :--- |
| **Nhân vật** | Code SVG (Remotion) | Code SVG (Giữ nguyên) |
| **Background** | **Python PIL (Gradient + Text)** | **AI Model (Flux/SD/API)** |
| **Kiến trúc** | Interface `ImageProvider` | Implement `AIImageProvider` |
| **Chi phí** | $0 | Tùy API/Điện năng |

**Lợi ích:**
1.  **Chạy ngay:** Không cần GPU mạnh, không cần API Key.
2.  **Đồng bộ:** Ảnh sinh bằng code nên luôn đúng kích thước 1920x1080.
3.  **Dễ thay thế:** Cùng một đường dẫn file, chỉ khác nguồn sinh.

---

## 2. CẤU TRÚC THƯ MỤC BỔ SUNG

```text
StickmanFactory/
├── remotion/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Stickman.tsx          # Nhân vật (SVG)
│   │   │   ├── Background.tsx        # Nền (Ảnh/Video)
│   │   │   ├── Subtitle.tsx          # Phụ đề
│   │   │   ├── Scene.tsx             # 1 cảnh hoàn chỉnh
│   │   │   └── VideoRoot.tsx         # Toàn bộ video
│   │   └── index.ts
│   └── package.json
├── src/
│   ├── visual/
│   │   ├── stickman_gen.py           # (Phase 1)
│   │   ├── bg_generator.py           # (MỚI) Sinh ảnh Placeholder
│   │   └── image_provider.py         # (MỚI) Interface chọn nguồn ảnh
│   └── pipeline/
│       ├── orchestrator.py           # (Phase 2)
│       └── renderer.py               # (MỚI) Gọi Remotion render
├── config.json                       # Thêm cấu hình image_provider
└── storage/
    └── cache/
        ├── audio/                    # (Phase 2)
        ├── images/                   # (MỚI) Ảnh background
        └── json/                     # (Phase 2)
```

---

## 3. NHIỆM VỤ CHI TIẾT (TASKS FOR AI AGENT)

### TASK 3.1: Cập nhật `config.json` (Chế độ ảnh)
**Yêu cầu:** Thêm cấu hình linh hoạt cho nguồn ảnh.
```json
{
  "image_provider": {
    "enabled": false,
    "mode": "placeholder",
    "api_key": "",
    "model": "flux-dev",
    "placeholder": {
      "use_gradient": true,
      "show_prompt_text": true,
      "base_color": "#3498db"
    }
  },
  "video": {
    "resolution": "1920x1080",
    "fps": 30
  }
}
```
*   `"enabled": false`: Dùng Placeholder (Gradient + Text).
*   `"enabled": true`: Dùng AI Model/API (khi có).

### TASK 3.2: Module sinh ảnh Placeholder (`src/visual/bg_generator.py`)
**Mục tiêu:** Sinh ảnh nền đẹp mắt mà không cần AI.
**Yêu cầu:**
1.  Sử dụng thư viện `Pillow` (PIL).
2.  **Hàm `generate_placeholder(prompt, seed, output_path)`:**
    *   Tạo ảnh 1920x1080.
    *   Vẽ nền gradient (2 màu ngẫu nhiên dựa trên `seed` để đồng bộ).
    *   Vẽ text ngắn gọn từ `prompt` ở giữa (font đậm, màu trắng, có viền đen).
    *   Vẽ `scene_id` góc trên để dễ kiểm tra.
3.  **Output:** File PNG lưu vào `storage/cache/images/bg_{scene_id}.png`.

```python
# Ví dụ logic
from PIL import Image, ImageDraw, ImageFont

def generate_placeholder(prompt, seed, output_path):
    width, height = 1920, 1080
    # Tạo gradient dựa trên seed để màu sắc đồng bộ
    img = Image.new('RGB', (width, height), color=(50, 50, 50))
    draw = ImageDraw.Draw(img)
    # ... code vẽ gradient và text ...
    img.save(output_path)
```

### TASK 3.3: Interface Nguồn ảnh (`src/visual/image_provider.py`)
**Mục tiêu:** Chuẩn hóa việc gọi sinh ảnh để dễ thay thế sau này.
**Yêu cầu:**
1.  **Class `ImageProvider`:**
    *   Method `generate(scene_data, output_dir)`.
2.  **Class `PlaceholderProvider(ImageProvider)`:**
    *   Gọi `bg_generator.generate_placeholder`.
3.  **Class `AIProvider(ImageProvider)`:** (Để trống cho tương lai)
    *   Sẽ gọi Stable Diffusion/API sau này.
4.  **Factory:** Dựa vào `config.json` để chọn class nào được khởi tạo.

### TASK 3.4: Component Remotion - Stickman (`remotion/src/components/Stickman.tsx`)
**Mục tiêu:** Hiển thị nhân vật vector.
**Yêu cầu:**
1.  Dùng SVG inline trong React.
2.  Nhận props: `action` (wave, point, idle).
3.  Dùng `useCurrentFrame()` và `interpolate()` để tạo animation đơn giản (tay chuyển động).
4.  **Quan trọng:** Giữ nguyên tỷ lệ, nền trong suốt.

### TASK 3.5: Component Remotion - Background (`remotion/src/components/Background.tsx`)
**Mục tiêu:** Hiển thị ảnh nền từ cache.
**Yêu cầu:**
1.  Nhận props: `imagePath`, `effect` (zoom_in, pan, none).
2.  Dùng `Img` component của Remotion.
3.  Áp dụng CSS transform cho hiệu ứng camera (Ken Burns effect).
    ```typescript
    const scale = interpolate(frame, [0, duration], [1, 1.1]);
    ```

### TASK 3.6: Component Remotion - Subtitle (`remotion/src/components/Subtitle.tsx`)
**Mục tiêu:** Hiển thị lời thoại.
**Yêu cầu:**
1.  Nhận props: `text`, `duration`.
2.  Style: Font chữ lớn (Arial Bold), màu trắng, viền đen (`textStroke`), nền đen mờ phía sau nếu cần.
3.  Vị trí: Bottom 15%, căn giữa.
4.  **An toàn:** Cắt text nếu quá dài (truncate) để không tràn màn hình.

### TASK 3.7: Component Remotion - Scene & Root (`Scene.tsx`, `VideoRoot.tsx`)
**Mục tiêu:** Ghép nối tất cả.
**Yêu cầu:**
1.  **Scene.tsx:** Nhận `sceneData`, tính `durationInFrames`, render Background + Stickman + Subtitle + Audio.
2.  **VideoRoot.tsx:** Dùng `Sequence` để xếp các cảnh nối tiếp nhau.
    ```typescript
    {scenes.map((scene, i) => (
      <Sequence key={scene.id} from={fromFrame(i)}>
        <Scene data={scene} />
      </Sequence>
    ))}
    ```
3.  **Audio:** Load file từ `audio_path` trong JSON.

### TASK 3.8: Script Render (`src/pipeline/renderer.py`)
**Mục tiêu:** Gọi Remotion xuất video.
**Yêu cầu:**
1.  **Hàm `render_video(project_json_path, output_path)`:**
    *   Đọc JSON, chuyển thành string để truyền vào Remotion props.
    *   Gọi lệnh:
        ```bash
        npx remotion render remotion/src/index.tsx VideoRoot output.mp4 --props="..."
        ```
2.  **Codec:** Sử dụng H.264 (mp4) để tương thích YouTube.
3.  **Progress:** Hiển thị tiến độ render ra console.

---

## 4. QUY TRÌNH KIỂM THỬ (TESTING PROTOCOL)

1.  **Test Placeholder Gen:**
    *   Chạy `python src/visual/bg_generator.py --test`.
    *   Kết quả: Có ảnh PNG 1920x1080 trong `storage/cache/images/`.
2.  **Test Remotion Studio:**
    *   Chạy `npx remotion studio` trong thư mục `remotion/`.
    *   Kết quả: Xem trước video trên trình duyệt, ảnh nền hiển thị đúng, stickman chuyển động.
3.  **Test Render:**
    *   Chạy `python src/pipeline/renderer.py`.
    *   Kết quả: File MP4 xuất ra trong `storage/renders/`.
4.  **Test Quality:**
    *   Mở video, kiểm tra âm thanh khớp hình, subtitle rõ ràng.

---

## 5. TIÊU CHÍ HOÀN THÀNH (DEFINITION OF DONE)
- [ ] Script sinh ảnh placeholder chạy được, tạo ảnh 1920x1080.
- [ ] Remotion Studio xem trước video không lỗi.
- [ ] Stickman hiển thị và chuyển động được.
- [ ] Subtitle đồng bộ với audio.
- [ ] Render ra file MP4 hoàn chỉnh từ command line.
- [ ] Hệ thống ảnh linh hoạt, sẵn sàng để thay bằng AI sau này.

---

## 📄 MODULE MẪU: `src/visual/bg_generator.py`
Đây là code mẫu để bạn hoặc AI Agent dựa vào viết ngay. Nó sinh ảnh gradient đẹp mắt mà không cần AI.

```python
import os
import random
from PIL import Image, ImageDraw, ImageFont

def generate_placeholder(prompt, seed, scene_id, output_path):
    """
    Sinh ảnh background placeholder dạng gradient + text.
    Không cần AI, chạy ngay lập tức.
    """
    width, height = 1920, 1080
    random.seed(seed)
    
    # Tạo 2 màu ngẫu nhiên dựa trên seed để đồng bộ
    color1 = (random.randint(0, 100), random.randint(0, 100), random.randint(100, 200))
    color2 = (random.randint(0, 50), random.randint(0, 50), random.randint(50, 150))
    
    # Tạo ảnh gradient
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)
    
    for y in range(height):
        r = int(color1[0] + (color2[0] - color1[0]) * y / height)
        g = int(color1[1] + (color2[1] - color1[1]) * y / height)
        b = int(color1[2] + (color2[2] - color1[2]) * y / height)
        draw.line((0, y, width, y), fill=(r, g, b))
    
    # Vẽ text prompt (cắt ngắn nếu quá dài)
    short_prompt = prompt[:50] + "..." if len(prompt) > 50 else prompt
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    # Căn giữa text
    text_bbox = draw.textbbox((0, 0), short_prompt, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Vẽ viền đen cho text để dễ đọc
    draw.text((x-2, y-2), short_prompt, fill='black', font=font)
    draw.text((x+2, y+2), short_prompt, fill='black', font=font)
    draw.text((x, y), short_prompt, fill='white', font=font)
    
    # Vẽ Scene ID góc trên
    draw.text((20, 20), f"Scene: {scene_id}", fill='white', font=font)
    
    # Lưu ảnh
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)
    print(f"Generated placeholder: {output_path}")

# Test
if __name__ == "__main__":
    generate_placeholder(
        prompt="Abstract background with question marks, soft blue tones",
        seed=1001,
        scene_id=1,
        output_path="./storage/cache/images/bg_001.png"
    )
```

---

## 💡 LỘ TRÌNH TÍCH HỢP AI IMAGE SAU NÀY

Khi bạn sẵn sàng dùng AI (Local hoặc API), việc tích hợp rất đơn giản:

1.  **Bước 1:** Đăng ký API (Replicate/Leonardo) hoặc cài Stable Diffusion local.
2.  **Bước 2:** Viết class `AIProvider` kế thừa `ImageProvider`.
    ```python
    class AIProvider(ImageProvider):
        def generate(self, scene_data, output_dir):
            # Gọi API hoặc Local Model
            # Lưu ảnh vào cùng đường dẫn
            pass
    ```
3.  **Bước 3:** Sửa `config.json`: `"mode": "ai"`.
4.  **Bước 4:** Chạy lại pipeline. Hệ thống tự động dùng ảnh AI thay vì placeholder.
