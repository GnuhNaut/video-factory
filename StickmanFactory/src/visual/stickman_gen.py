"""
stickman_gen.py - Bộ sinh nhân vật Stickman bằng SVG

Sinh nhân vật Stickman đồng bộ 100% bằng code (không dùng AI image gen).
Sử dụng svgwrite để tạo file SVG với transparent background.
Tọa độ khớp cố định để đảm bảo tương thích Remotion.
"""

import os
import sys
import math

# Thêm project root vào path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

try:
    import svgwrite
except ImportError:
    svgwrite = None


class Stickman:
    """
    Lớp sinh nhân vật Stickman dưới dạng SVG.

    Tọa độ hệ thống (canvas 200x300):
        - Head center: (100, 50)
        - Neck: (100, 80)
        - Body top (shoulders): (100, 80)
        - Body bottom (hips): (100, 180)
        - Left shoulder: (60, 100)
        - Right shoulder: (140, 100)
        - Left hand (idle): (60, 160)
        - Right hand (idle): (140, 160)
        - Left foot: (70, 280)
        - Right foot: (130, 280)
    """

    # Tọa độ khớp cố định (fixed joints)
    JOINTS = {
        "head_center": (100, 45),
        "head_radius": 25,
        "neck": (100, 70),
        "shoulder_left": (60, 95),
        "shoulder_right": (140, 95),
        "body_top": (100, 70),
        "body_bottom": (100, 180),
        "elbow_left": (40, 130),
        "elbow_right": (160, 130),
        "hand_left": (50, 165),
        "hand_right": (150, 165),
        "hip_left": (80, 180),
        "hip_right": (120, 180),
        "knee_left": (70, 230),
        "knee_right": (130, 230),
        "foot_left": (65, 280),
        "foot_right": (135, 280),
    }

    CANVAS_WIDTH = 200
    CANVAS_HEIGHT = 300

    # Các trạng thái hỗ trợ
    VALID_STATES = ["idle", "wave", "point", "walk", "sad", "happy"]

    def __init__(self, color: str = "#000000", line_width: int = 3, scale: float = 1.0,
                 accent_color: str = "#3498db"):
        """
        Khởi tạo Stickman.

        Args:
            color: Màu chính của nhân vật (hex).
            line_width: Độ dày nét vẽ.
            scale: Tỷ lệ kích thước.
            accent_color: Màu phụ (dùng cho highlights).
        """
        if svgwrite is None:
            raise ImportError(
                "svgwrite is required. Install with: pip install svgwrite"
            )

        self.color = color
        self.line_width = line_width
        self.scale = scale
        self.accent_color = accent_color

    def _scaled(self, x: float, y: float) -> tuple:
        """Áp dụng scale lên tọa độ."""
        cx = self.CANVAS_WIDTH / 2
        cy = self.CANVAS_HEIGHT / 2
        return (
            cx + (x - cx) * self.scale,
            cy + (y - cy) * self.scale
        )

    def _create_svg(self) -> svgwrite.Drawing:
        """Tạo SVG drawing mới với transparent background."""
        w = int(self.CANVAS_WIDTH * self.scale)
        h = int(self.CANVAS_HEIGHT * self.scale)
        dwg = svgwrite.Drawing(size=(f"{w}px", f"{h}px"), profile="tiny")
        dwg.viewbox(0, 0, self.CANVAS_WIDTH, self.CANVAS_HEIGHT)
        return dwg

    def _draw_line(self, dwg, start: tuple, end: tuple, color: str = None, width: int = None):
        """Vẽ đường thẳng."""
        c = color or self.color
        w = width or self.line_width
        dwg.add(dwg.line(
            start=start, end=end,
            stroke=c, stroke_width=w,
            stroke_linecap="round"
        ))

    def _draw_circle(self, dwg, center: tuple, radius: float, fill: str = "none",
                     stroke: str = None, stroke_width: int = None):
        """Vẽ hình tròn."""
        s = stroke or self.color
        sw = stroke_width or self.line_width
        dwg.add(dwg.circle(
            center=center, r=radius,
            fill=fill, stroke=s, stroke_width=sw
        ))

    def _draw_arc(self, dwg, center: tuple, radius: float, start_angle: float,
                  end_angle: float, color: str = None, width: int = None):
        """Vẽ cung tròn (dùng cho miệng)."""
        c = color or self.color
        w = width or self.line_width

        # Chuyển góc sang radian
        sa = math.radians(start_angle)
        ea = math.radians(end_angle)

        # Tính điểm đầu và cuối
        x1 = center[0] + radius * math.cos(sa)
        y1 = center[1] + radius * math.sin(sa)
        x2 = center[0] + radius * math.cos(ea)
        y2 = center[1] + radius * math.sin(ea)

        # Xác định large-arc-flag
        large_arc = 1 if abs(end_angle - start_angle) > 180 else 0

        path_data = (
            f"M {x1},{y1} "
            f"A {radius},{radius} 0 {large_arc},1 {x2},{y2}"
        )
        dwg.add(dwg.path(d=path_data, fill="none", stroke=c, stroke_width=w,
                         stroke_linecap="round"))

    def _draw_head(self, dwg, expression: str = "neutral"):
        """Vẽ đầu (hình tròn + mắt + miệng)."""
        j = self.JOINTS
        hc = j["head_center"]
        hr = j["head_radius"]

        # Đầu
        self._draw_circle(dwg, hc, hr)

        # Mắt
        eye_y = hc[1] - 3
        eye_left = (hc[0] - 8, eye_y)
        eye_right = (hc[0] + 8, eye_y)
        self._draw_circle(dwg, eye_left, 2, fill=self.color, stroke=self.color, stroke_width=1)
        self._draw_circle(dwg, eye_right, 2, fill=self.color, stroke=self.color, stroke_width=1)

        # Miệng (thay đổi theo biểu cảm)
        mouth_center = (hc[0], hc[1] + 10)
        if expression == "happy":
            # Cười - cung cong xuống
            self._draw_arc(dwg, mouth_center, 8, 10, 170, width=2)
        elif expression == "sad":
            # Buồn - cung cong lên
            sad_center = (hc[0], hc[1] + 18)
            self._draw_arc(dwg, sad_center, 8, 190, 350, width=2)
        else:
            # Trung tính - đường thẳng
            self._draw_line(dwg, (hc[0] - 6, mouth_center[1]),
                          (hc[0] + 6, mouth_center[1]), width=2)

    def _draw_body(self, dwg):
        """Vẽ thân (từ cổ đến hông)."""
        j = self.JOINTS
        self._draw_line(dwg, j["body_top"], j["body_bottom"])

    def _draw_arms_idle(self, dwg):
        """Vẽ tay ở trạng thái đứng yên (buông xuống)."""
        j = self.JOINTS
        # Tay trái: vai → khuỷu → bàn tay
        self._draw_line(dwg, j["body_top"], j["shoulder_left"])
        self._draw_line(dwg, j["shoulder_left"], j["hand_left"])
        # Tay phải
        self._draw_line(dwg, j["body_top"], j["shoulder_right"])
        self._draw_line(dwg, j["shoulder_right"], j["hand_right"])

    def _draw_arms_wave(self, dwg):
        """Vẽ tay ở trạng thái vẫy (tay phải giơ lên)."""
        j = self.JOINTS
        # Tay trái: bình thường
        self._draw_line(dwg, j["body_top"], j["shoulder_left"])
        self._draw_line(dwg, j["shoulder_left"], j["hand_left"])
        # Tay phải: giơ lên vẫy
        self._draw_line(dwg, j["body_top"], j["shoulder_right"])
        wave_elbow = (155, 60)
        wave_hand = (175, 25)
        self._draw_line(dwg, j["shoulder_right"], wave_elbow)
        self._draw_line(dwg, wave_elbow, wave_hand)
        # Bàn tay nhỏ
        self._draw_circle(dwg, wave_hand, 4, fill=self.color, stroke=self.color, stroke_width=1)

    def _draw_arms_point(self, dwg):
        """Vẽ tay ở trạng thái chỉ ngang (tay phải chỉ sang phải)."""
        j = self.JOINTS
        # Tay trái: bình thường
        self._draw_line(dwg, j["body_top"], j["shoulder_left"])
        self._draw_line(dwg, j["shoulder_left"], j["hand_left"])
        # Tay phải: chỉ ngang
        self._draw_line(dwg, j["body_top"], j["shoulder_right"])
        point_hand = (195, 95)
        self._draw_line(dwg, j["shoulder_right"], point_hand)
        # Mũi tên nhỏ ở bàn tay
        self._draw_line(dwg, (185, 88), point_hand, width=2)
        self._draw_line(dwg, (185, 102), point_hand, width=2)

    def _draw_legs_idle(self, dwg):
        """Vẽ chân ở trạng thái đứng yên."""
        j = self.JOINTS
        # Chân trái
        self._draw_line(dwg, j["body_bottom"], j["knee_left"])
        self._draw_line(dwg, j["knee_left"], j["foot_left"])
        # Chân phải
        self._draw_line(dwg, j["body_bottom"], j["knee_right"])
        self._draw_line(dwg, j["knee_right"], j["foot_right"])

    def _draw_legs_walk(self, dwg):
        """Vẽ chân ở trạng thái đang đi (chân tách rộng)."""
        j = self.JOINTS
        # Chân trái - bước tới
        walk_knee_left = (55, 225)
        walk_foot_left = (35, 275)
        self._draw_line(dwg, j["body_bottom"], walk_knee_left)
        self._draw_line(dwg, walk_knee_left, walk_foot_left)
        # Chân phải - bước sau
        walk_knee_right = (145, 225)
        walk_foot_right = (165, 275)
        self._draw_line(dwg, j["body_bottom"], walk_knee_right)
        self._draw_line(dwg, walk_knee_right, walk_foot_right)

    def generate_state(self, state: str, output_path: str = None) -> str:
        """
        Sinh file SVG cho một trạng thái cụ thể.

        Args:
            state: Trạng thái nhân vật. Một trong:
                   'idle', 'wave', 'point', 'walk', 'sad', 'happy'
            output_path: Đường dẫn file SVG đầu ra. Nếu None, tự tạo tên.

        Returns:
            Đường dẫn file SVG đã sinh.

        Raises:
            ValueError: Nếu state không hợp lệ.
        """
        if state not in self.VALID_STATES:
            raise ValueError(
                f"Invalid state '{state}'. "
                f"Valid states: {', '.join(self.VALID_STATES)}"
            )

        dwg = self._create_svg()

        # Xác định biểu cảm khuôn mặt
        if state == "happy":
            expression = "happy"
        elif state == "sad":
            expression = "sad"
        else:
            expression = "neutral"

        # Vẽ đầu
        self._draw_head(dwg, expression)

        # Vẽ thân
        self._draw_body(dwg)

        # Vẽ tay theo trạng thái
        if state == "wave":
            self._draw_arms_wave(dwg)
        elif state == "point":
            self._draw_arms_point(dwg)
        else:
            self._draw_arms_idle(dwg)

        # Vẽ chân theo trạng thái
        if state == "walk":
            self._draw_legs_walk(dwg)
        else:
            self._draw_legs_idle(dwg)

        # Nếu sad, nghiêng thân người nhẹ (visual cue)
        if state == "sad":
            # Thêm giọt nước mắt nhỏ
            hc = self.JOINTS["head_center"]
            tear = (hc[0] - 10, hc[1] + 3)
            self._draw_circle(dwg, tear, 2, fill=self.accent_color,
                            stroke=self.accent_color, stroke_width=0.5)

        # Xác định output path
        if output_path is None:
            project_root = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            output_dir = os.path.join(project_root, "assets", "characters")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"stickman_{state}.svg")

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        # Lưu SVG
        dwg.saveas(output_path, pretty=True)
        return output_path


def _run_tests():
    """Sinh tất cả trạng thái Stickman để test."""
    print("=" * 60)
    print("  STICKMAN GENERATOR - Test")
    print("=" * 60)

    try:
        from src.core.config_loader import load_config, get_nested
        config = load_config()
        color = get_nested(config, "character", "base_color", default="#000000")
        accent = get_nested(config, "character", "accent_color", default="#3498db")
        line_w = get_nested(config, "character", "line_width", default=3)
    except Exception:
        color = "#000000"
        accent = "#3498db"
        line_w = 3

    stickman = Stickman(color=color, line_width=line_w, accent_color=accent)

    for state in Stickman.VALID_STATES:
        path = stickman.generate_state(state)
        size = os.path.getsize(path)
        print(f"  ✅ {state:8s} → {path} ({size} bytes)")

    print(f"\n✅ All {len(Stickman.VALID_STATES)} states generated successfully!")
    print("=" * 60)


if __name__ == "__main__":
    if "--test" in sys.argv:
        _run_tests()
    else:
        print("Usage: python src/visual/stickman_gen.py --test")
        print("  Generates stickman SVG files for all states.")
