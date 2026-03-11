from diffusers import AutoPipelineForText2Image
import torch
import time
from PIL import Image
def run_sdxl_turbo():
    print("Đang tải model SDXL Turbo vào VRAM...")
    # Tải model. Dùng float16 để giảm dung lượng VRAM tiêu thụ xuống một nửa (rất quan trọng)
    pipe = AutoPipelineForText2Image.from_pretrained(
        "stabilityai/sdxl-turbo",
        torch_dtype=torch.float16,
        variant="fp16"
    )
    
    # Đẩy model sang GPU (RTX 3060)
    pipe.to("cuda")
    
    prompt = "A highly detailed, 2D vector art background of a dark mysterious forest, minimalist, flat colors, suited for stickman animation"
    
    print(f"Đang render ảnh với prompt: '{prompt}'")
    start_time = time.time()
    
    # Render ảnh. 
    # Lưu ý: SDXL Turbo yêu cầu guidance_scale=0.0 và số steps rất nhỏ (1-4)
    image = pipe(
        prompt=prompt, 
        width=1344,         # Chiều rộng chuẩn
        height=768,         # Chiều cao chuẩn
        num_inference_steps=2, 
        guidance_scale=0.0
    ).images[0]
    image_1080p = image.resize((1920, 1080), Image.Resampling.LANCZOS)
    output_file = "turbo_bg_test.png"
    image_1080p.save(output_file)
    
    end_time = time.time()
    print(f"Hoàn thành! Đã lưu ảnh tại {output_file}")
    print(f"Thời gian render: {end_time - start_time:.2f} giây")

if __name__ == "__main__":
    run_sdxl_turbo()