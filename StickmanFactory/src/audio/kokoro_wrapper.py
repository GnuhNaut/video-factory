"""
kokoro_wrapper.py - Wrapper gọi model Kokoro TTS local

Sinh audio tiếng Anh từ văn bản sử dụng model Kokoro local.
Tự động normalize audio về -16 LUFS (chuẩn YouTube) bằng FFmpeg.

Kokoro source nằm tại config.models.kokoro_path (ví dụ D:/Workspace/kokoro_tts/kokoro).
Module sẽ thêm path đó vào sys.path để import trực tiếp từ source,
không cần pip install kokoro.
"""

import os
import sys
import json
import wave
import logging
import subprocess

if sys.platform == "nt":
    sys.stdout.reconfigure(encoding='utf-8')

# Thêm project root vào path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from src.core.config_loader import load_config, get_nested

logger = logging.getLogger(__name__)

# Standard Sample Rate for Production
SAMPLE_RATE = 44100


def _setup_error_logging(log_dir: str = None):
    """Cấu hình logging vào file error.log."""
    if log_dir is None:
        log_dir = os.path.join(PROJECT_ROOT, "logs")
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, "error.log")

    # Tránh thêm handler trùng lặp
    if not logger.handlers:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.ERROR)
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        ))
        logger.addHandler(file_handler)


class KokoroWrapper:
    """
    Wrapper cho Kokoro TTS model (local source).

    Sử dụng KPipeline từ Kokoro source directory thay vì pip install.
    API: KPipeline(lang_code='a') cho American English.
    Output: WAV 24kHz, tự động normalize -16 LUFS.
    """

    def __init__(self, config: dict = None):
        """
        Khởi tạo KokoroWrapper.

        Args:
            config: Dict cấu hình. Nếu None, tự load từ config.json.
        """
        _setup_error_logging()

        if config is None:
            config = load_config()

        self.kokoro_path = get_nested(config, "models", "kokoro_path")
        self.default_voice = get_nested(config, "models", "kokoro_voice", default="af_bella")
        self.ffmpeg_path = get_nested(config, "paths", "ffmpeg", default="ffmpeg")

        self._pipeline = None
        self._model_loaded = False

    def _load_model(self):
        """
        Load Kokoro KPipeline từ local source.

        Thêm kokoro_path vào sys.path để import trực tiếp module kokoro
        từ source directory (không cần pip install).
        """
        if self._model_loaded:
            return

        # Thêm Kokoro source vào sys.path nếu chưa có
        kokoro_src = self.kokoro_path
        if kokoro_src and kokoro_src not in sys.path:
            sys.path.insert(0, kokoro_src)
            # Thêm luôn môi trường ảo (venv) của Kokoro nếu có để tận dụng thư viện (torch, transformers, misaki...)
            kokoro_site_packages = os.path.join(kokoro_src, "venv", "Lib", "site-packages")
            if os.path.exists(kokoro_site_packages) and kokoro_site_packages not in sys.path:
                sys.path.insert(1, kokoro_site_packages)
                logger.info(f"Added Kokoro venv site-packages to path: {kokoro_site_packages}")
            logger.info(f"Added Kokoro source to path: {kokoro_src}")

        try:
            from kokoro import KPipeline

            # lang_code='a' = American English (theo test.py và main.py của Kokoro)
            self._pipeline = KPipeline(lang_code="a")
            self._model_loaded = True
            logger.info("Kokoro KPipeline loaded successfully")
            print(f"✅ Kokoro loaded from: {kokoro_src}")

        except ImportError as e:
            error_msg = (
                f"Cannot import kokoro from '{kokoro_src}'.\n"
                f"Kiểm tra lại models.kokoro_path trong config.json.\n"
                f"Path phải trỏ tới thư mục chứa folder 'kokoro/' (package).\n"
                f"Error: {e}"
            )
            logger.error(error_msg)
            raise ImportError(error_msg)

        except Exception as e:
            error_msg = f"Failed to load Kokoro model: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def generate_audio(
        self,
        text: str,
        output_path: str,
        voice_id: str = None,
        speed: float = 1.0,
        split_pattern: str = r'\n+'
    ) -> float:
        """
        Sinh file audio WAV từ văn bản.

        Args:
            text: Văn bản cần đọc (tiếng Anh).
            output_path: Đường dẫn file WAV đầu ra.
            voice_id: ID giọng đọc. Mặc định dùng từ config.
            speed: Tốc độ đọc (1.0 = bình thường, 0.95 = storytelling).
            split_pattern: Regex để tách đoạn dài (mặc định tách theo newline).

        Returns:
            Duration (giây) của file audio đã sinh.

        Raises:
            ValueError: Nếu text rỗng.
            RuntimeError: Nếu model không load được hoặc không sinh được audio.
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        voice = voice_id or self.default_voice
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        self._load_model()

        try:
            import soundfile as sf
            import numpy as np

            # Sinh audio qua Kokoro pipeline
            # API: pipeline(text, voice=voice, speed=speed, split_pattern=split_pattern)
            # Returns generator of (graphemes, phonemes, audio_chunk)
            audio_chunks = []
            generator = self._pipeline(
                text,
                voice=voice,
                speed=float(speed),
                split_pattern=split_pattern
            )

            for _gs, _ps, audio_chunk in generator:
                if audio_chunk is not None:
                    audio_chunks.append(audio_chunk)

            if not audio_chunks:
                raise RuntimeError("Kokoro produced no audio output")

            # Ghép tất cả các chunk thành 1 audio array
            full_audio = np.concatenate(audio_chunks).astype(np.float32)

            # Lưu file WAV (24kHz)
            sf.write(output_path, full_audio, SAMPLE_RATE)

            # Normalize audio về -16 LUFS (chuẩn YouTube)
            self._normalize_audio(output_path)

            # Đo duration chính xác
            duration = self._get_audio_duration(output_path)

            print(f"✅ Audio generated: {output_path} ({duration:.2f}s)")
            return duration

        except Exception as e:
            error_msg = f"Failed to generate audio: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def _normalize_audio(self, audio_path: str) -> bool:
        """
        Normalize audio về -16 LUFS bằng FFmpeg (chuẩn YouTube).

        Args:
            audio_path: Đường dẫn file audio.

        Returns:
            True nếu normalize thành công, False nếu skip/lỗi.
        """
        try:
            temp_path = audio_path + ".tmp.wav"

            cmd = [
                self.ffmpeg_path,
                "-y",
                "-i", audio_path,
                "-af", "loudnorm=I=-16:TP=-1.5:LRA=11,aresample=async=1",
                "-ar", str(SAMPLE_RATE),
                "-ac", "1",
                temp_path
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                os.replace(temp_path, audio_path)
                logger.info(f"Audio normalized to -16 LUFS: {audio_path}")
                return True
            else:
                logger.warning(f"FFmpeg normalize failed: {result.stderr[:200]}")
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                return False

        except FileNotFoundError:
            logger.warning(
                f"FFmpeg not found at '{self.ffmpeg_path}'. "
                f"Skipping audio normalization."
            )
            return False
        except Exception as e:
            logger.warning(f"Audio normalization failed: {e}")
            return False

    def _get_audio_duration(self, audio_path: str) -> float:
        """
        Lấy duration chính xác của file audio.

        Ưu tiên: ffprobe → soundfile → wave module.

        Args:
            audio_path: Đường dẫn file audio.

        Returns:
            Duration (giây).
        """
        # 1) Thử dùng ffprobe
        try:
            ffprobe_path = self.ffmpeg_path.replace("ffmpeg.exe", "ffprobe.exe")
            cmd = [
                ffprobe_path,
                "-v", "quiet",
                "-show_entries", "format=duration",
                "-of", "json",
                audio_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return float(data["format"]["duration"])
        except Exception:
            pass

        # 2) Fallback: soundfile
        try:
            import soundfile as sf
            data, samplerate = sf.read(audio_path)
            return len(data) / float(samplerate)
        except Exception:
            pass

        # 3) Fallback: wave module
        try:
            with wave.open(audio_path, "rb") as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                return frames / float(rate)
        except Exception:
            logger.warning(f"Could not determine duration of {audio_path}")
            return 0.0


def _run_test(text: str = "Hello world"):
    """Chạy test Kokoro với đoạn văn bản."""
    print("=" * 60)
    print("  KOKORO TTS - Test")
    print("=" * 60)

    # Output path
    cache_dir = os.path.join(PROJECT_ROOT, "storage", "cache")
    os.makedirs(cache_dir, exist_ok=True)
    output_path = os.path.join(cache_dir, "test.wav")

    try:
        wrapper = KokoroWrapper()
        print(f"\n🎤 Text: \"{text}\"")
        print(f"🎙️  Voice: {wrapper.default_voice}")
        print(f"📂 Kokoro path: {wrapper.kokoro_path}")
        print(f"📂 FFmpeg path: {wrapper.ffmpeg_path}")
        print()

        duration = wrapper.generate_audio(text, output_path)

        print(f"\n📁 Output: {output_path}")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        file_size = os.path.getsize(output_path)
        print(f"📦 File size: {file_size:,} bytes")
        print(f"\n✅ Kokoro test PASSED!")

    except ImportError as e:
        print(f"\n⚠️  Kokoro import failed:\n   {e}")
        print("   Test SKIPPED.")

    except Exception as e:
        print(f"\n❌ Kokoro test FAILED: {e}")
        logger.error(f"Kokoro test failed: {e}")

    print("=" * 60)


if __name__ == "__main__":
    if "--test" in sys.argv:
        # Lấy text: --test "some text here"
        text = "Hello world. This is a test of the Kokoro text to speech system."
        for i, arg in enumerate(sys.argv):
            if arg == "--test" and i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith("-"):
                text = sys.argv[i + 1]
                break
        _run_test(text)
    else:
        print("Usage: python src/audio/kokoro_wrapper.py --test [\"text\"]")
        print("  Generates a test audio file using Kokoro TTS.")
