# 🎬 Stickman AI Video Factory - Hướng dẫn sử dụng từng bước

Tài liệu này hướng dẫn bạn cách sử dụng hệ thống **Stickman AI Video Factory** từ con số không đến khi xuất ra được video MP4 hoàn chỉnh.

---

## � Bước 1: Chuẩn bị kịch bản JSON (`sample_project.json`)

Hệ thống hoạt động dựa trên kịch bản đầu vào. Bạn **BẮT BUỘC** phải chuẩn bị một file JSON (mặc định hệ thống sẽ đọc file `sample_project.json` nằm ở thư mục gốc). 

Nếu bạn chưa có, hãy tạo mới hoặc sửa trực tiếp file `sample_project.json` theo cấu trúc mẫu sau. Hệ thống chia video thành nhiều phân cảnh (`scenes`).

**Cấu trúc mẫu của 1 phân cảnh trong mảng `scenes`:**
```json
{
    "scene_id": 1,
    "text": "Xin chào, đây là video đầu tiên do AI tạo ra.",
    "expected_duration": 4.5,
    "visual_timeline": [
        {
            "time_offset": 0,
            "bg_prompt": "Một căn phòng làm việc hiện đại, có nắng chiếu qua cửa sổ",
            "action": "walk",
            "camera_effect": "zoom_in"
        },
        {
            "time_offset": 2.0,
            "bg_prompt": "Cận cảnh bàn làm việc với máy tính",
            "action": "typing",
            "emotion_icon": "happy",
            "camera_effect": "pan_left"
        }
    ]
}
```

*   **`text`**: Lời thoại (AI Kokoro sẽ đọc câu này).
*   **`expected_duration`**: Độ dài ước tính (giây).
*   **`visual_timeline`**: Danh sách các sự kiện hình ảnh. Bạn có thể cho AI tạo nhiều nền (`bg_prompt`) đổi cảnh ngay trong 1 Scene.
*   **`action`**: Các hành động Stickman hỗ trợ: `idle`, `walk`, `run`, `jump`, `wave`, `point`, `think`, `sitting`, `typing`, `panning`, `zoom_in`, `static_shot`, `focus_shift`.

---

## ⚙️ Bước 2: Kiểm tra cấu hình (Tùy chọn)

Mở file `config.json` ở thư mục gốc nếu bạn muốn chỉnh sửa cấu hình xuất video:
*   Đổi tốc độ khung hình: `"project": { "fps": 30 }`
*   Thay đổi chất lượng render FFmpeg / Remotion: `"render": { "codec": "h264", "crf": 23 }`
*   Tốc độ render (để gen video nhanh hơn): Tăng `"chunk_workers": 2` và `"render_concurrency": 2` nếu máy tính của bạn mạnh (RAM to, CPU nhiều nhân).

*Lưu ý: Bạn hoàn toàn có thể bỏ qua Bước 2 nếu muốn dùng cài đặt mặc định.*

---

## 🚀 Bước 3: Chạy Pipeline sinh Video

Sau khi đã có file `sample_project.json` chuẩn chỉnh, hãy mở Terminal (Command Prompt hoặc PowerShell hoặc Git Bash) và làm theo 2 lệnh sau:

**1. Kích hoạt môi trường chạy (chỉ cần làm 1 lần mỗi khi mở cửa sổ Terminal mới):**
```bash
venv\Scripts\activate
```
*(Nếu dùng Mac/Linux hoặc Git Bash, dùng lệnh: `source venv/Scripts/activate`)*

**2. Bấm nút "chạy" tự động:**
```bash
python src/main.py --run-pipeline
```

Hệ thống sẽ tự động thực hiện các bước sau mà bạn không cần can thiệp:
1. Validate kiểm tra xem file JSON của bạn có lỗi cú pháp không.
2. Dùng AI tạo giọng đọc (TTS) cho toàn bộ lời thoại.
3. Dùng Image Provider để tạo background.
4. Auto-chia kịch bản thành các đoạn nhỏ ~60 giây để tối ưu bộ nhớ (Smart Chunking).
5. Render cực tốc độ bằng Remotion qua công nghệ đa luồng.
6. Ghép nối ra video MP4 hoàn chỉnh.

---

## 🍿 Bước 4: Lấy Video Kết Quả

Khi Terminal (màn hình đen) báo **`[RENDER COMPLETE]`**, bạn có thể tìm thấy video MP4 hoàn chỉnh tại thư mục:

👉 `storage/renders/`

Video này sẽ có tên được lấy từ trường `project_name` trong file json hoặc là `output_chunk...`. 

---

## 🆘 Bước 5: Phân tích lỗi (Nếu có)

Nếu quá trình gen video bị lỗi giữa chừng, bạn có thể chạy dòng lệnh chẩn đoán xem hệ thống đang hỏng ở khâu nào:
```bash
python src/main.py --test-all
```
Kết quả sẽ trả về xem Kokoro TTS, file JSON hay Remotion đang gặp vấn đề để bạn dễ dàng sửa chữa!
