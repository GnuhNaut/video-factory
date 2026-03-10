
### 🚀 BẢN KẾ HOẠCH NÂNG CẤP ĐỘ ĐỘNG (DYNAMIC) CHO VIDEO

Bạn hãy copy các khối Markdown dưới đây và đưa cho AI Agent để hoàn thiện nốt phần nhìn (Visual).

#### TASK 1: Tối ưu Kịch bản & Tách Scene ngắn (Xử lý việc 1 nền nhàm chán)

```markdown
**Nhiệm vụ:** Tối ưu hóa bộ sinh kịch bản (Script Generator) để video thay đổi bối cảnh liên tục.
**Chi tiết:**
1. Hãy tìm file chứa Prompt gốc để gọi LLM (có thể nằm trong `src/script/generator.py`, `api_connector.py` hoặc các file liên quan).
2. Thêm chỉ thị NGHIÊM NGẶT sau vào prompt hệ thống:
   - "Tuyệt đối không tạo ra một Scene quá dài (không vượt quá 30 từ hoặc 10 giây)."
   - "Để duy trì sự chú ý, hãy ngắt kịch bản thành nhiều Scenes ngắn. Cứ mỗi đoạn chuyển ý, hãy tạo một Scene mới kèm theo `bg_prompt` mới để đổi ảnh nền."
3. Kiểm tra lại `src/script/mock_data.py`. Hãy sửa lại mock data sao cho có nhiều scenes ngắn (5-8 giây) thay vì 1 scene dài ngoẵng.

```

#### TASK 2: Nâng cấp Component Stickman (Di chuyển thực sự & Đa dạng Pose)

```markdown
**Nhiệm vụ:** Cập nhật `remotion/src/components/Stickman.tsx` để nhân vật biết đi lại ngang màn hình và hỗ trợ đầy đủ các dáng đứng.
**Chi tiết:**
1. **Di chuyển (TranslateX):**
   - Thêm prop tùy chọn `positionX?: number` (mặc định là 0). 
   - Nếu `action === "walk"`, sử dụng `interpolate` kết hợp với `frame` để tạo ra một giá trị dịch chuyển `translateX` liên tục từ trái sang phải hoặc ngược lại. Đưa giá trị này vào `style` của thẻ `<svg>`.
2. **Hoàn thiện các Pose còn thiếu:**
   - Trong `Stickman.tsx`, hãy bổ sung logic tính toán đường dẫn (path) `rightArmPath`, `legLPath`, `legRPath` cho các action còn thiếu trong Schema bao gồm: `"explain", "counting", "writing", "sitting", "fist_pump"`. 
   - Ví dụ: `sitting` (gập chân 90 độ), `explain` (tay mở rộng), `fist_pump` (tay giơ cao chiến thắng).
3. **Cập nhật `Scene.tsx`:** - Cập nhật hàm `mapAction` để không fallback các action mới này về `"idle"` nữa.

```

#### TASK 3: Tích hợp Biểu cảm (Emotion Icons) & B-roll

```markdown
**Nhiệm vụ:** Mang các thuộc tính `b_roll` và `emotion_icon` từ JSON Schema hiển thị lên màn hình React (`Scene.tsx`).
**Chi tiết:**
1. **Emotion Icons:**
   - Nếu `activeActionObj.emotion_icon` có giá trị (ví dụ: `sweat`, `bulb`, `question`, `anger`), hãy render một thẻ `<svg>` hoặc `<div className="emoji">` nổi ngay trên đầu của Stickman. 
   - Dùng `spring` để làm icon này nảy (pop-up) ra một cách mượt mà khi bắt đầu action.
2. **B-Roll Overlay:**
   - Nếu `activeActionObj.b_roll` có giá trị (thường là một đường dẫn ảnh B-roll), hãy render một thẻ `<img />` đè lên Background nhưng nằm dưới Stickman và Subtitle.
   - Thêm hiệu ứng trượt (slide) hoặc mờ dần (fade-in) cho B-roll này trong khoảng 10-15 frame đầu tiên.

```
