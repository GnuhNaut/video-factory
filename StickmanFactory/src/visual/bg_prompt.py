"""
bg_prompt.py - Tạo prompt cho background AI generation

Module reserved cho Phase 2 expansion. Hiện tại cung cấp
các hàm cơ bản để tạo prompt text cho background generation.
"""


# Phong cách background mặc định
DEFAULT_STYLES = {
    "cartoon": "colorful cartoon style, flat design, vibrant colors, clean lines",
    "realistic": "photorealistic, high detail, natural lighting, 8k quality",
    "minimalist": "minimalist style, simple shapes, muted colors, clean background",
    "watercolor": "watercolor painting style, soft edges, pastel colors, artistic",
    "pixel": "pixel art style, retro gaming, 16-bit colors, nostalgic",
}

DEFAULT_STYLE = "cartoon"


def generate_bg_prompt(scene_description: str, style: str = None) -> str:
    """
    Tạo prompt cho AI background generation.

    Args:
        scene_description: Mô tả nội dung scene.
        style: Phong cách ảnh. Một trong: cartoon, realistic, minimalist,
               watercolor, pixel. Mặc định: cartoon.

    Returns:
        Prompt string để truyền vào Stable Diffusion / Flux.

    Ví dụ:
        generate_bg_prompt("A forest with tall trees", "cartoon")
        → "A forest with tall trees, colorful cartoon style, flat design, ..."
    """
    style_key = style or DEFAULT_STYLE
    style_desc = DEFAULT_STYLES.get(style_key, DEFAULT_STYLES[DEFAULT_STYLE])

    # Xây dựng prompt
    prompt_parts = [
        scene_description.strip(),
        style_desc,
        "wide angle shot",
        "no text",
        "no characters",
        "background only",
        "16:9 aspect ratio",
    ]

    prompt = ", ".join(prompt_parts)
    return prompt


def generate_bg_negative_prompt() -> str:
    """
    Tạo negative prompt mặc định cho background generation.

    Returns:
        Negative prompt string.
    """
    negatives = [
        "text", "watermark", "signature", "logo",
        "human", "person", "character", "stickman",
        "blurry", "low quality", "distorted",
        "frame", "border", "ui elements",
    ]
    return ", ".join(negatives)


if __name__ == "__main__":
    # Quick demo
    print("=== Background Prompt Generator ===")
    demo_desc = "A peaceful park with green trees and a sunny sky"
    for style_name in DEFAULT_STYLES:
        prompt = generate_bg_prompt(demo_desc, style_name)
        print(f"\n[{style_name}]")
        print(f"  {prompt}")
    print(f"\n[negative]")
    print(f"  {generate_bg_negative_prompt()}")
