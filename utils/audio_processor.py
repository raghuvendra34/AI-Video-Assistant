import yt_dlp
import os
import ffmpeg

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def download_youtube_audio(url: str) -> str:
    """
    Download audio from a YouTube URL and convert it to WAV.
    """

    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "noplaylist": True,
        "extract_flat": False,
        "quiet": False,
        "extractor_args": {
            "youtube": {
                "player_client": ["android"]
            }
        },
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            filename = ydl.prepare_filename(info)

            filename = (
                filename.replace(".webm", ".wav")
                .replace(".m4a", ".wav")
                .replace(".mp4", ".wav")
            )

            print(f"Downloaded audio: {filename}")

            return filename

    except Exception as e:
        print(f"YT-DLP FULL ERROR: {repr(e)}")
        raise Exception(f"YouTube download failed: {e}")


def convert_to_wav(input_path: str) -> str:
    """
    Convert any audio/video file to WAV format.
    """

    from pydub import AudioSegment

    output_path = os.path.splitext(input_path)[0] + "_converted.wav"

    audio = AudioSegment.from_file(input_path)

    audio = (
        audio
        .set_channels(1)
        .set_frame_rate(16000)
    )

    audio.export(output_path, format="wav")

    return output_path


def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list:
    """
    Split WAV file into chunks.
    """

    from pydub import AudioSegment

    audio = AudioSegment.from_wav(wav_path)

    chunk_ms = chunk_minutes * 60 * 1000

    chunks = []

    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk = audio[start:start + chunk_ms]

        chunk_path = f"{wav_path}_chunk_{i}.wav"

        chunk.export(chunk_path, format="wav")

        chunks.append(chunk_path)

    return chunks


def process_input(source: str) -> list:
    """
    Accept either:
    - YouTube URL
    - Local audio/video file
    """

    if source.startswith("http://") or source.startswith("https://"):
        print("Detected YouTube URL. Downloading audio...")
        wav_path = download_youtube_audio(source)

    else:
        print("Detected local file. Converting to WAV...")
        wav_path = convert_to_wav(source)

    print("Chunking audio...")

    chunks = chunk_audio(wav_path)

    print(f"Audio ready — {len(chunks)} chunk(s) created.")

    return chunks