

```markdown
# 🎯 KẾ HOẠCH NÂNG CẤP: CHIA NHỎ SCENE ĐỂ ĐA DẠNG BỐI CẢNH (DYNAMIC BACKGROUNDS)

**Ngữ cảnh:** Hiện tại, mỗi Scene trong kịch bản đang quá dài (chứa 10-20 câu thoại, kéo dài 15-20 giây). Do cấu trúc mỗi Scene chỉ có 1 `bg_prompt`, video sẽ hiển thị một ảnh nền tĩnh quá lâu gây nhàm chán.
**Mục tiêu:** Ép luồng sinh kịch bản (Mock và LLM) phải cắt nhỏ câu thoại. Mỗi Scene chỉ giới hạn 1-2 câu ngắn (5-8 giây) để video liên tục đổi hình nền và góc máy.

---

## 🛠️ TASK 1: Tái cấu trúc Dữ liệu mẫu (Mock Data)
**File cần sửa:** `src/script/mock_data.py`
Nhiệm vụ: Cập nhật lại file mock để phục vụ việc test giao diện local ngay lập tức.
1. Xóa cấu trúc scenes cũ. Tạo ra một kịch bản mới có ít nhất 4-6 scenes nối tiếp nhau.
2. **Quy tắc cứng cho mỗi Scene trong Mock Data:**
   - `text`: Tối đa 15-25 từ (1-2 câu ngắn).
   - `expected_duration`: Giới hạn trong khoảng 4.0 đến 8.0 giây.
   - `bg_prompt`: **BẮT BUỘC thay đổi liên tục** giữa các scene kề nhau để mô phỏng chuyển cảnh. 
     *(Ví dụ: Scene 1: "wide shot of a modern office", Scene 2: "close up of a computer screen with code", Scene 3: "coffee shop table with a laptop", Scene 4: "low angle shot of office ceiling")*.
   - `actions`: Mỗi scene chỉ cần 1-2 action (tương ứng với thời lượng ngắn của scene).

---

## 🛠️ TASK 2: Nâng cấp LLM Prompt (Ép AI sinh kịch bản ngắn)
**File cần sửa:** `src/script/api_connector.py` (hoặc file định nghĩa System Prompt gửi cho OpenAI/Gemini).
Nhiệm vụ: Thêm các rào cản bằng tiếng Anh vào Prompt để LLM không bao giờ viết Scene dài.
1. Tìm đoạn chứa System Instruction hoặc Prompt template.
2. Thêm các dòng chỉ thị NGHIÊM NGẶT sau (viết bằng tiếng Anh):
   ```text
   CRITICAL PACING RULES:
   1. SHORT SCENES ONLY: Never create a scene longer than 20 words (approx. 5-8 seconds). Break down long explanations into multiple, consecutive short scenes.
   2. DYNAMIC VISUALS: Every new scene MUST have a distinctly different `bg_prompt` to ensure the background image changes frequently. Vary the camera angles (e.g., wide shot, close-up, over-the-shoulder) and locations.
   3. CONTINUOUS FLOW: Even though scenes are short, the narration `text` must flow naturally from one scene to the next.

```

---

## 🛠️ TASK 3: Thêm cơ chế Cảnh báo (Length Validator)

**File cần sửa:** `src/script/generator.py` (Hàm `get_script` hoặc bước ngay sau khi lấy script).
Nhiệm vụ: Viết code kiểm tra xem LLM (hoặc Mock Data) có tuân thủ quy tắc ngắn không.

1. Sau khi biến `script` (chứa dict JSON) được load ra, hãy viết một vòng lặp kiểm tra mảng `scenes`.
2. Logic kiểm tra:
* Nếu có bất kỳ scene nào có `word_count > 35` HOẶC `expected_duration > 12.0`.
* Bắn ra một cảnh báo ở Terminal bằng `logger.warning()` hoặc `print()` với nội dung:
`[WARNING] Scene {scene_id} quá dài ({word_count} từ). Hình nền sẽ bị tĩnh lâu, cân nhắc tối ưu lại Prompt.`


3. Đảm bảo chạy Unit Test (nếu có) không bị lỗi do cảnh báo này.

```

***

### 💡 Lời khuyên cho bạn sau khi chạy Plan này:
Vì bạn đang test ở môi trường local (chạy cá nhân), việc AI Agent sửa xong **Task 1 (`mock_data.py`)** là quan trọng nhất. Ngay sau khi Task 1 hoàn thành, bạn có thể chạy lại lệnh `python src/main.py` để sinh ra file `project_ready.json` mới và thấy ngay kết quả trên video render: cứ mỗi 5 giây bối cảnh sẽ đổi một lần cực kỳ sống động!

```