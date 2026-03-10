# 🚀 Kế hoạch nâng cấp Stickman AI Video Factory (Chuẩn 95/100)

## 📋 Mục tiêu chiến lược

* **Chất lượng:** Stickman có animation mượt mà (biết thở, biết cử động linh hoạt), đa bối cảnh hình ảnh trong mỗi phân cảnh.
* **Hiệu năng:** Render video 10-12 phút ổn định thông qua cơ chế chia nhỏ (Smart Chunking) và render song song.
* **Tính linh hoạt:** Chấp nhận đầu vào JSON thủ công từ Gemini với cấu trúc phức tạp (`visual_timeline`).
* **Ổn định:** Pre-gen toàn bộ tài nguyên (ảnh/audio) trước khi render để tối ưu VRAM/RAM.

---

## 🏗 1. Thay đổi cấu trúc dữ liệu (Data Architecture)

### 1.1. Cập nhật JSON Schema (`src/core/json_schema.py`)

* **Thay đổi:** Loại bỏ các trường đơn lẻ như `bg_prompt`, `character_state` ở cấp độ scene.
* **Thêm mới:** Cấu trúc `visual_timeline` để hỗ trợ nhiều sự kiện trong một câu thoại.
* **Yêu cầu Agent:** Cập nhật bộ validator để đảm bảo `time_offset` của các sự kiện hình ảnh không vượt quá thời lượng thực tế của audio.

### 1.2. Mẫu JSON đầu vào chuẩn (Gemini Gem)

Hệ thống sẽ tập trung xử lý cấu trúc sau:

```json
{
  "scene_id": 1,
  "text": "The full narration text...",
  "visual_timeline": [
    { "time_offset": 0, "bg_prompt": "City park", "action": "wave" },
    { "time_offset": 4.5, "bg_prompt": "Office desk", "action": "point" }
  ]
}

```

---

## 🎨 2. Nâng cấp Visual Engine (Remotion)

### 2.1. Animation mượt mà cho Stickman (`Stickman.tsx`)

* **Thêm mới:** Sử dụng hook `spring` và `interpolate` của Remotion để tạo chuyển động tự nhiên giữa các tư thế (state).
* **Cải thiện:** Thêm hiệu ứng "Breathing" (thở) tự động bằng hàm `Math.sin(frame)` để nhân vật không bị đứng hình khi ở trạng thái idle.
* **Tính chuẩn xác:** Đảm bảo các khớp nối SVG không bị rời rạc khi co giãn.

### 2.2. Đa bối cảnh & Camera (`Background.tsx`)

* **Thay đổi:** Component nhận mảng `visual_timeline` và hiển thị ảnh tương ứng dựa trên `frame` hiện tại.
* **Thêm mới:** Hiệu ứng chuyển cảnh (Cross-fade) giữa các `bg_prompt` khác nhau trong cùng một Sequence.
* **Font chữ:** Tích hợp `@remotion/google-fonts` để xử lý font English chuyên nghiệp, tránh lỗi hiển thị trên máy render.

---

## ⚙️ 3. Tối ưu hiệu năng & Smart Rendering

### 3.1. Cơ chế Smart Chunking (`src/pipeline/chunker.py`)

* **Nhiệm vụ:** Chia video 10-12 phút thành các đoạn nhỏ ~1 phút.
* **Logic:** Không cắt máy móc tại giây thứ 60; Agent phải tìm điểm kết thúc của Scene gần mốc 1 phút nhất để cắt, đảm bảo không ngắt giữa câu thoại.

### 3.2. Render song song & Ghép nối (`src/pipeline/renderer.py`)

* **Thay đổi:** Chuyển từ render đơn luồng sang render nhiều chunk cùng lúc bằng tham số `--concurrency`.
* **Ghép nối:** Sử dụng FFmpeg với lệnh `concat` (chế độ copy) để ghép các chunk .mp4 lại mà không làm giảm chất lượng hay gây nháy hình tại điểm nối.

### 3.3. Pre-gen Image Provider (`src/visual/image_provider.py`)

* **Thay đổi:** Agent phải quét toàn bộ `visual_timeline` và sinh ảnh từ AI Local trước khi gọi Remotion.
* **Mục tiêu:** Tách biệt quá trình sinh ảnh (nặng VRAM) và render video (nặng CPU) để tránh crash hệ thống.

---

## 🛠 4. Lộ trình thực hiện cho AI Agent (Roadmap)

### Bước 1: Chuẩn bị hạ tầng dữ liệu

1. Cập nhật `json_schema.py` theo cấu trúc `visual_timeline`.
2. Nâng cấp `validator.py` để kiểm tra tính logic của các mốc thời gian hình ảnh.

### Bước 2: Nâng cấp linh hồn video (Remotion)

1. Viết lại `Stickman.tsx` hỗ trợ animation mượt và hiệu ứng thở.
2. Cập nhật `Background.tsx` hỗ trợ danh sách ảnh và hiệu ứng chuyển cảnh.
3. Cấu hình Google Fonts trong `Subtitle.tsx`.

### Bước 3: Xây dựng bộ điều phối thông minh

1. Tạo module `chunker.py` để chia nhỏ dự án.
2. Refactor `renderer.py` để hỗ trợ render chunk và FFmpeg concat.
3. Cập nhật `orchestrator.py` để kết nối tất cả các bước: **Nhập JSON -> Pre-gen tài nguyên -> Render Chunk -> Ghép Video**.

### Bước 4: Kiểm thử & Tối ưu

1. Test render 1 chunk 1 phút để kiểm tra độ mượt của Stickman.
2. Test render toàn bộ 10 phút để kiểm tra tính ổn định của việc ghép nối.

---

## 🏁 5. Tiêu chí kiểm tra cuối cùng (Checklist)

* [ ] Nhân vật Stickman luôn có chuyển động nhẹ (thở) ngay cả khi đứng yên.
* [ ] Ảnh nền thay đổi chính xác theo `time_offset` trong JSON.
* [ ] Không có lỗi font chữ khi hiển thị phụ đề tiếng Anh.
* [ ] Video 10 phút được render hoàn tất mà không bị tràn RAM/VRAM.
* [ ] Điểm nối giữa các chunk video không bị giật hoặc mất tiếng.
