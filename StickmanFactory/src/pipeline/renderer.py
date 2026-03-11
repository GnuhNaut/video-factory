"""
renderer.py - Goi Remotion de render video MP4

Doc project_ready.json, truyen props vao Remotion, xuat video.
Toi uu: concurrency, CRF, skip logic.
"""

import os
import sys
import json
import shutil
import subprocess
import time
import logging

# Force UTF-8 stdout cho Windows cp1252 terminal
if sys.platform == "nt":
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from src.core.config_loader import load_config, get_nested

logger = logging.getLogger(__name__)

REMOTION_DIR = os.path.join(PROJECT_ROOT, "remotion")


def render_video(
    project_json_path: str = None,
    output_path: str = None,
    config: dict = None
) -> str:
    """
    Goi Remotion render video MP4 tu project JSON.

    Args:
        project_json_path: Duong dan file JSON (project_ready.json).
        output_path: Duong dan file MP4 output.
        config: Dict cau hinh.

    Returns:
        Duong dan file MP4 da render.
    """
    if config is None:
        config = load_config()

    if project_json_path is None:
        project_json_path = os.path.join(
            PROJECT_ROOT, "storage", "cache", "json", "project_ready.json"
        )

    if not os.path.exists(project_json_path):
        raise FileNotFoundError(f"Project JSON not found: {project_json_path}")

    # Doc project data
    with open(project_json_path, "r", encoding="utf-8") as f:
        project_data = json.load(f)

    # Output path
    if output_path is None:
        output_dir = os.path.join(PROJECT_ROOT, "storage", "renders")
        os.makedirs(output_dir, exist_ok=True)
        title = project_data.get("meta", {}).get("title", "output")
        safe_title = "".join(c if c.isalnum() or c in "_ -" else "_" for c in title)
        output_path = os.path.join(output_dir, f"{safe_title}.mp4")

    # Skip render if exists
    skip_if_exists = get_nested(config, "optimization", "skip_render_if_exists", default=False)
    if skip_if_exists and os.path.exists(output_path):
        file_size = os.path.getsize(output_path)
        if file_size > 0:
            print(f"  [Renderer] SKIP: Output already exists ({file_size / 1024 / 1024:.1f} MB)")
            print(f"  [Renderer] Path: {output_path}")
            logger.info(f"Skipped render - output exists: {output_path}")
            return output_path

    # Chuẩn bị props cho Remotion (copy assets vào public/cache)
    import shutil
    public_cache_dir = os.path.join(REMOTION_DIR, "public", "cache")
    os.makedirs(os.path.join(public_cache_dir, "audio"), exist_ok=True)
    os.makedirs(os.path.join(public_cache_dir, "images"), exist_ok=True)

    def process_asset_path(path_value):
        if not path_value: return ""
        src_abs = os.path.abspath(os.path.join(PROJECT_ROOT, path_value)) if not os.path.isabs(path_value) else path_value
        dest_sub = "audio" if src_abs.lower().endswith(('.wav', '.mp3')) else "images"
        filename = os.path.basename(src_abs)
        dest_abs = os.path.join(public_cache_dir, dest_sub, filename)

        if os.path.exists(src_abs):
            shutil.copy2(src_abs, dest_abs)
        return f"cache/{dest_sub}/{filename}"

    for scene in project_data.get("scenes", []):
        scene["audio_path"] = process_asset_path(scene.get("audio_path"))
        if scene.get("bg_image_path"):
            scene["bg_image_path"] = process_asset_path(scene.get("bg_image_path"))
        
        for timeline_item in scene.get("visual_timeline", []):
            if timeline_item.get("bg_image_path"):
                timeline_item["bg_image_path"] = process_asset_path(timeline_item["bg_image_path"])
            if timeline_item.get("b_roll_path"):
                timeline_item["b_roll_path"] = process_asset_path(timeline_item["b_roll_path"])
                
        for action_item in scene.get("actions", []):
            if action_item.get("b_roll_path"):
                action_item["b_roll_path"] = process_asset_path(action_item["b_roll_path"])

    fps = get_nested(config, "video", "fps", default=get_nested(config, "project", "fps", default=30))
    codec = get_nested(config, "render", "codec", default="h264")
    crf = get_nested(config, "render", "crf", default=23)
    concurrency = get_nested(config, "optimization", "render_concurrency", default=2)

    # ==========================================
    # SMART CHUNKING LOGIC (Phase 5)
    # ==========================================
    from src.pipeline.chunker import create_chunks
    from concurrent.futures import ThreadPoolExecutor, as_completed

    chunk_dir = os.path.join(PROJECT_ROOT, "storage", "cache", "json", "chunks")
    chunk_files = create_chunks(project_data, chunk_dir, target_chunk_duration=60.0)

    print("=" * 60)
    print("  [REMOTION RENDERER - SMART CHUNKING]")
    print("=" * 60)
    print(f"  Input: {project_json_path}")
    print(f"  Output: {output_path}")
    print(f"  Total Chunks: {len(chunk_files)}")
    print(f"  Codec: {codec} | CRF: {crf} | FPS: {fps} | Concurrency/Chunk: {concurrency}")
    print()

    start_time = time.time()
    npx_cmd = "npx.cmd" if os.name == "nt" else "npx"
    rendered_chunks = [None] * len(chunk_files)
    
    def render_single_chunk(chunk_path, idx):
        chunk_id = idx + 1
        chunk_output_path = os.path.join(output_dir, f"{safe_title}_chunk_{chunk_id}.mp4")
        
        print(f"  -> Started Rendering Chunk {chunk_id}/{len(chunk_files)}")
        cmd = [
            npx_cmd, "remotion", "render",
            "src/index.ts",
            "VideoRoot",
            chunk_output_path,
            f"--props={chunk_path}",
            f"--fps={fps}",
            f"--codec={codec}",
            f"--crf={crf}",
            f"--concurrency={concurrency}",
            "--log=error", 
        ]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=REMOTION_DIR,
                capture_output=False,
                text=True,
                timeout=3600,
            )
            if result.returncode == 0 and os.path.exists(chunk_output_path):
                print(f"  -> Finished Chunk {chunk_id}")
                return idx, chunk_output_path
            else:
                logger.error(f"Chunk {chunk_id} render failed with exit code: {result.returncode}")
                return idx, None
        except Exception as e:
            logger.error(f"Chunk {chunk_id} render exception: {e}")
            return idx, None

    # Render parallel
    max_workers = get_nested(config, "optimization", "chunk_workers", default=2)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(render_single_chunk, chunk_file, idx): idx for idx, chunk_file in enumerate(chunk_files)}
        for future in as_completed(futures):
            idx, out_path = future.result()
            if out_path:
                rendered_chunks[idx] = out_path
            else:
                return None

    # Filter out any Nones (should be caught by the return None above, but just in case)
    rendered_chunks = [c for c in rendered_chunks if c is not None]

    # Tat ca cac chunk da render xong. Tien hanh ghep noi FFmpeg
    print("=" * 60)
    print("  [FFMPEG CONCATENATION]")
    print("=" * 60)
    
    list_txt_path = os.path.join(output_dir, "concat_list.txt")
    with open(list_txt_path, "w", encoding="utf-8") as f:
        for chunk_file in rendered_chunks:
            # QUAN TRONG: Dung ten file tuong doi theo yeu cau de tranh roi loan \ va / tren Windows
            rel_chunk = os.path.basename(chunk_file).replace("\\", "/")
            f.write(f"file '{rel_chunk}'\n")
            
    try:
        ffmpeg_cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", 
            "-i", os.path.basename(list_txt_path), 
            "-c:v", "copy", 
            "-c:a", "aac", "-b:a", "128k", 
            "-af", "aresample=async=1",
            os.path.basename(output_path)
        ]
        
        print(f"  Command: {' '.join(ffmpeg_cmd)}")
        concat_result = subprocess.run(ffmpeg_cmd, cwd=output_dir, capture_output=True, text=True)
        
        if concat_result.returncode != 0:
            logger.error(f"FFmpeg concat failed: {concat_result.stderr}")
            return None
            
        elapsed = time.time() - start_time

        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"\n{'=' * 60}")
            print(f"  [RENDER COMPLETE]")
            print(f"  Output: {output_path}")
            print(f"  Size: {file_size / 1024 / 1024:.1f} MB")
            print(f"  Total time: {elapsed:.1f}s")
            print(f"{'=' * 60}")
            
            # Clean up chunks and logs
            from src.utils.cleanup import cleanup_temp_files
            cleanup_temp_files(PROJECT_ROOT)
            
            import gc
            gc.collect()
            
            logger.info(f"Render complete: {output_path} ({file_size/1024/1024:.1f} MB, {elapsed:.1f}s)")
            return output_path
        else:
            print(f"\n[ERROR] FFmpeg concat failed to produce output file.")
            logger.error(f"Output file missing after concat: {output_path}")
            return None

    except FileNotFoundError:
        print("\n[ERROR] npx/remotion not found. Please run:")
        print("   cd remotion && npm install")
        logger.error("npx or remotion not found")
        return None
    except subprocess.TimeoutExpired:
        print("\n[ERROR] Render timed out (> 1 hour)")
        logger.error("Render timed out")
        return None
    except Exception as e:
        print(f"\n[ERROR] Render error: {e}")
        logger.error(f"Render error: {e}")
        return None


if __name__ == "__main__":
    render_video()
