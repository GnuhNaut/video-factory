# 🛡️ MASTER PLAN: HOÀN THIỆN HỆ THỐNG STICKMAN VIDEO FACTORY

**Mục tiêu:** Loại bỏ hoàn toàn 6 rủi ro cốt lõi, đưa dự án đạt trạng thái "Production-Ready".

---

## I. XỬ LÝ RỦI RO KỸ THUẬT (PIPELINE HARDENING)

### 1. Chống lệch pha âm thanh/hình ảnh (A/V Desync)

* **Lỗi hiện tại:** Sử dụng `ffmpeg concat` đơn giản dễ gây lệch pha tại điểm nối chunk.
* **Giải pháp kỷ luật:** * **Chuẩn hóa Metadata:** Trước khi render, buộc tất cả file Audio đầu ra từ TTS phải được convert về cùng một Sample Rate (44100Hz) và Bitrate cố định.
* **Cơ chế "Seamless Transition":** Tại `renderer.py`, khi thực hiện lệnh `concat`, phải ép buộc FFmpeg sử dụng bộ lọc `resync` và thiết lập lại `timestamp` (DTS/PTS).
* **Lệnh thực thi chuẩn:** `ffmpeg -f concat -safe 0 -i list.txt -c copy -af "aselect=concat_dec_select,aresample=async=1" output.mp4`.



### 2. Đồng bộ thời gian thực (Dynamic Timing Alignment)

* **Lỗi hiện tại:** `time_offset` trong JSON mang tính ước lượng, không khớp với tốc độ đọc thực tế của TTS.
* **Giải pháp kỷ luật:** * **Giai đoạn "Recalibration":** Sau khi TTS sinh file audio, Agent phải chạy một script lấy thời lượng thực (`actual_duration`) của file audio đó.
* **Nội suy tỷ lệ:** Nếu `actual_duration` sai lệch >5% so với dự tính, hệ thống tự động tính toán lại tỷ lệ (scale) các mốc `time_offset` trong `visual_timeline` của Scene đó trước khi nạp vào Remotion.



---

## II. NÂNG CẤP TRẢI NGHIỆM THỊ GIÁC (ANIMATION POLISH)

### 3. Loại bỏ sự máy móc (Anti-Robotic Motion)

* **Lỗi hiện tại:** Chuyển động lặp lại, thiếu tự nhiên.
* **Giải pháp kỷ luật:** * **Perlin Noise Implementation:** Tích hợp nhiễu Perlin vào tọa độ của Stickman để tạo ra các rung động siêu nhỏ (micro-movements) ngẫu nhiên, mô phỏng sự không hoàn hảo của con người.
* **Secondary Motion:** Khi Stickman di chuyển (action: walk), các bộ phận phụ (như tóc hoặc vạt áo - nếu có) phải có độ trễ (delay) theo nguyên lý "Follow through and Overlapping Action".
* **Easing Standard:** Cấm sử dụng chuyển động tuyến tính (Linear). Tất cả phải là `spring` hoặc `bezier` với thông số `stiffness` thay đổi nhẹ giữa các lần xuất hiện.



### 4. Xử lý Font chữ và Phụ đề

* **Giải pháp:** * **Local Font Fallback:** Ngoài Google Fonts, phải nhúng sẵn một bộ font Serif/Sans-serif local trong thư mục `assets/fonts` để làm dự phòng (fallback) nếu lỗi mạng.
* **Auto-sizing Subtitle:** Viết logic đo độ dài text (Canvas measureText) để tự động hạ size chữ nếu câu thoại quá dài, tránh tràn khung hình.



---

## III. QUẢN LÝ TÀI NGUYÊN (INFRASTRUCTURE & RESOURCE CONTROL)

### 5. Quản lý VRAM và GPU (Resource Locking)

* **Rủi ro:** Tranh chấp GPU giữa AI sinh ảnh và Remotion.
* **Giải pháp kỷ luật:** * **Quy trình "Phase-Locking":** Agent phải tuân thủ nghiêm ngặt thứ tự:
1. Sinh Audio -> 2. Sinh Ảnh (Dùng 100% GPU) -> **[Dọn dẹp VRAM/Clear Cache]** -> 3. Render Video (Dùng CPU & GPU hỗ trợ).
* **Strict Cleanup:** Sau mỗi chunk render thành công, script `cleanup.py` phải được kích thực ngay lập tức để xóa các file ảnh/audio tạm đã dùng, chỉ giữ lại file mp4 cuối.



---

## IV. HỆ THỐNG KIỂM SOÁT LỖI (QUALITY ASSURANCE)

### 6. Validator 2 lớp (Deep Schema & Context Validation)

* **Lớp 1 (Cú pháp):** Dùng Pydantic kiểm tra kiểu dữ liệu JSON.
* **Lớp 2 (Logic):** Thêm bước "LLM Sanity Check". Gửi JSON ngược lại cho một model (như Gemini Flash) với prompt: *"Kiểm tra xem mốc thời gian hình ảnh có logic với nội dung câu thoại không? Có hành động nào mâu thuẫn không?"*.

### 7. Post-Render Audit (Kiểm tra hậu kỳ)

* **Giải pháp:** Sau khi ghép video, hệ thống tự động chạy lệnh `ffprobe` để quét:
* Có khung hình nào bị đen (black frame) không?
* Có đoạn nào bị mất tiếng (silent gap) tại điểm nối không?
* Nếu phát hiện, tự động gắn cờ (flag) và yêu cầu render lại chunk đó.



---

## V. LỘ TRÌNH THỰC HIỆN NGHIÊM NGẶT (ROADMAP)

| Giai đoạn | Thời hạn | Nội dung trọng tâm | Tiêu chí hoàn thành |
| --- | --- | --- | --- |
| **Phase A** | 2 ngày | Củng cố Pipeline & Sync | Ghép 2 video 1 phút đạt sai số <10ms. |
| **Phase B** | 3 ngày | Stickman "Linh hồn" | 100% chuyển động có Easing và Noise. |
| **Phase C** | 1 ngày | Quản lý tài nguyên | Chạy render 12 phút liên tục không tăng RAM quá 20%. |
| **Phase D** | 1 ngày | Hệ thống Monitor | Có log chi tiết từng bước, tự động cleanup 100%. |

---

## Đánh giá kỷ luật:

Nếu bạn thực hiện đúng Plan này, dự án của bạn sẽ chuyển từ một **"Tool hỗ trợ"** thành một **"Hệ thống sản xuất tự động"**.

**Điểm yếu cần sửa ngay lập tức:** Tôi thấy trong code hiện tại của bạn chưa có bộ **"Garbage Collector"** (dọn rác) sau khi render. Đây là lỗi gây tràn ổ cứng nhanh nhất. Bạn có muốn tôi viết script `cleanup.py` tích hợp vào `Orchestrator` không?