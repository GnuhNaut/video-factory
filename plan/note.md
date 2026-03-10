3 Lưu ý quan trọng (Cần tránh) khi code Remotion & Chia Chunk
Tính tất định (Determinism) trong Remotion:

Lỗi sai: Dùng Math.random(), useState (để tính toán vị trí/hiệu ứng) hoặc dùng useEffect (để fetch dữ liệu) trong Remotion. Do Remotion có thể render các frame song song hoặc nhảy cóc, các hàm này sẽ làm video bị chớp nháy (flicker) liên tục.

Cách đúng: MỌI THỨ phải dựa vào useCurrentFrame(). Nếu cần random, phải dùng hàm random(seed) do chính thư viện Remotion cung cấp để đảm bảo cùng 1 frame luôn ra cùng 1 kết quả. Dữ liệu phải được chuẩn bị sẵn 100% từ Python truyền vào qua props (file JSON).

Lỗi "Đứt âm thanh" khi chia Chunk (Phần 2):

Lỗi sai: Python cắt chunk tròn trĩnh ở giây thứ 60, đúng lúc nhân vật đang nói dở 1 câu dài (file audio kéo dài từ giây 58 đến 62). File audio sẽ bị đứt đôi, gây lỗi đồng bộ.

Cách đúng: Phải ngắt chunk ở khoảng nghỉ (pause) giữa các scene hoặc giữa các câu thoại. Nếu scene dài 65 giây, hãy cho chunk đó dài 65 giây luôn.

Lỗi ghép nối FFmpeg (-c copy):

Lỗi sai: Các chunk render ra có frame rate (fps) hoặc resolution khác nhau. Khi dùng lệnh -c copy của FFmpeg, video sẽ bị đen hình hoặc lỗi tiếng.

Cách đúng: Đảm bảo biến --fps=30 (hoặc 60) được fix cứng trong câu lệnh CLI của tất cả các chunk.