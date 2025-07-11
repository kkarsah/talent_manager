#!/usr/bin/env python3
"""
Video Player and Viewer Guide
Find, play, and manage your created videos
"""

import os
import subprocess
import platform
from pathlib import Path


def find_created_videos():
    """Find all videos created by the system"""

    video_dir = Path("content/video")

    if not video_dir.exists():
        print("❌ Video directory not found: content/video")
        return []

    # Find all video files
    video_extensions = [".mp4", ".avi", ".mov", ".mkv"]
    videos = []

    for ext in video_extensions:
        videos.extend(video_dir.glob(f"*{ext}"))

    if not videos:
        print("❌ No videos found in content/video/")
        return []

    print(f"📹 Found {len(videos)} video(s):")

    for i, video in enumerate(videos, 1):
        file_size = video.stat().st_size / (1024 * 1024)  # MB
        print(f"   {i}. {video.name} ({file_size:.2f} MB)")

    return videos


def play_video_mac(video_path):
    """Play video on macOS"""
    try:
        # Try QuickTime Player first
        subprocess.run(["open", "-a", "QuickTime Player", str(video_path)], check=True)
        print(f"▶️  Opened {video_path.name} in QuickTime Player")
        return True
    except:
        try:
            # Fallback to default app
            subprocess.run(["open", str(video_path)], check=True)
            print(f"▶️  Opened {video_path.name} in default app")
            return True
        except Exception as e:
            print(f"❌ Failed to play video: {e}")
            return False


def play_video_windows(video_path):
    """Play video on Windows"""
    try:
        # Try Windows Media Player
        subprocess.run(["start", str(video_path)], shell=True, check=True)
        print(f"▶️  Opened {video_path.name} in default app")
        return True
    except Exception as e:
        print(f"❌ Failed to play video: {e}")
        return False


def play_video_linux(video_path):
    """Play video on Linux"""
    players = ["vlc", "mpv", "mplayer", "totem", "xdg-open"]

    for player in players:
        try:
            subprocess.run([player, str(video_path)], check=True)
            print(f"▶️  Opened {video_path.name} in {player}")
            return True
        except:
            continue

    print(f"❌ No video player found. Install VLC or another player.")
    return False


def play_video(video_path):
    """Play video using the appropriate method for the OS"""

    system = platform.system().lower()

    if system == "darwin":  # macOS
        return play_video_mac(video_path)
    elif system == "windows":
        return play_video_windows(video_path)
    elif system == "linux":
        return play_video_linux(video_path)
    else:
        print(f"❌ Unsupported operating system: {system}")
        return False


def get_video_info(video_path):
    """Get detailed video information using ffprobe"""

    try:
        cmd = [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            str(video_path),
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            import json

            data = json.loads(result.stdout)

            # Extract video info
            format_info = data.get("format", {})
            video_stream = None
            audio_stream = None

            for stream in data.get("streams", []):
                if stream.get("codec_type") == "video":
                    video_stream = stream
                elif stream.get("codec_type") == "audio":
                    audio_stream = stream

            print(f"📊 Video Information for {video_path.name}:")
            print(f"   Duration: {float(format_info.get('duration', 0)):.2f} seconds")
            print(
                f"   File Size: {int(format_info.get('size', 0)) / (1024*1024):.2f} MB"
            )

            if video_stream:
                width = video_stream.get("width", "Unknown")
                height = video_stream.get("height", "Unknown")
                fps = video_stream.get("r_frame_rate", "Unknown")
                codec = video_stream.get("codec_name", "Unknown")
                print(f"   Resolution: {width}x{height}")
                print(f"   Codec: {codec}")
                print(f"   Frame Rate: {fps}")

            if audio_stream:
                audio_codec = audio_stream.get("codec_name", "Unknown")
                sample_rate = audio_stream.get("sample_rate", "Unknown")
                print(f"   Audio Codec: {audio_codec}")
                print(f"   Sample Rate: {sample_rate} Hz")
            else:
                print("   Audio: None")

            return True

    except Exception as e:
        print(f"⚠️  Could not get video info: {e}")
        return False


def create_video_thumbnail(video_path):
    """Create a thumbnail from the video"""

    thumbnail_path = video_path.with_suffix(".jpg")

    try:
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(video_path),
            "-ss",
            "00:00:01",
            "-vframes",
            "1",
            "-q:v",
            "2",
            str(thumbnail_path),
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0 and thumbnail_path.exists():
            print(f"🖼️  Thumbnail created: {thumbnail_path.name}")

            # Try to open thumbnail
            system = platform.system().lower()
            if system == "darwin":
                subprocess.run(["open", str(thumbnail_path)])
            elif system == "windows":
                subprocess.run(["start", str(thumbnail_path)], shell=True)
            elif system == "linux":
                subprocess.run(["xdg-open", str(thumbnail_path)])

            return thumbnail_path
        else:
            print(f"❌ Failed to create thumbnail: {result.stderr}")
            return None

    except Exception as e:
        print(f"❌ Thumbnail creation failed: {e}")
        return None


def interactive_video_player():
    """Interactive video player interface"""

    print("🎬 Video Player Interface")
    print("=" * 40)

    videos = find_created_videos()

    if not videos:
        return

    while True:
        print(f"\n📹 Available Videos:")
        for i, video in enumerate(videos, 1):
            file_size = video.stat().st_size / (1024 * 1024)
            print(f"   {i}. {video.name} ({file_size:.2f} MB)")

        print(f"\n🎮 Options:")
        print("   p <number> - Play video")
        print("   i <number> - Show video info")
        print("   t <number> - Create thumbnail")
        print("   o - Open video directory")
        print("   r - Refresh video list")
        print("   q - Quit")

        choice = input("\n💡 Enter choice: ").strip().lower()

        if choice == "q":
            print("👋 Goodbye!")
            break
        elif choice == "r":
            videos = find_created_videos()
            continue
        elif choice == "o":
            # Open video directory
            video_dir = Path("content/video")
            system = platform.system().lower()
            if system == "darwin":
                subprocess.run(["open", str(video_dir)])
            elif system == "windows":
                subprocess.run(["explorer", str(video_dir)])
            elif system == "linux":
                subprocess.run(["xdg-open", str(video_dir)])
            print(f"📁 Opened directory: {video_dir}")
            continue

        # Parse commands with numbers
        if len(choice) >= 2 and choice[0] in ["p", "i", "t"]:
            try:
                action = choice[0]
                number = int(choice[2:]) if len(choice) > 2 else int(choice[1])

                if 1 <= number <= len(videos):
                    video = videos[number - 1]

                    if action == "p":
                        print(f"\n▶️  Playing: {video.name}")
                        play_video(video)
                    elif action == "i":
                        print(f"\n📊 Getting info for: {video.name}")
                        get_video_info(video)
                    elif action == "t":
                        print(f"\n🖼️  Creating thumbnail for: {video.name}")
                        create_video_thumbnail(video)
                else:
                    print(f"❌ Invalid video number: {number}")
            except ValueError:
                print("❌ Invalid command format. Use 'p 1', 'i 2', etc.")
        else:
            print("❌ Invalid command. Try 'p 1' to play video 1, 'i 1' for info, etc.")


def quick_play_latest():
    """Quickly play the most recently created video"""

    videos = find_created_videos()

    if not videos:
        return

    # Sort by modification time (newest first)
    latest_video = max(videos, key=lambda v: v.stat().st_mtime)

    print(f"🎬 Playing latest video: {latest_video.name}")
    get_video_info(latest_video)
    print()
    play_video(latest_video)


def main():
    """Main video player interface"""

    print("🎬 DALL-E Video Player")
    print("=" * 30)

    # Check if we have any videos
    videos = find_created_videos()

    if not videos:
        print("\n💡 Create some videos first:")
        print("   python dalle_video_setup.py")
        print("   python cli.py alex generate --topic 'Test Video'")
        return

    print(f"\n🎮 Quick Actions:")
    print("   1. Play latest video")
    print("   2. Interactive player")
    print("   3. Open video directory")
    print("   4. Show all video info")

    choice = input("\n💡 Choose option (1-4): ").strip()

    if choice == "1":
        quick_play_latest()
    elif choice == "2":
        interactive_video_player()
    elif choice == "3":
        video_dir = Path("content/video")
        system = platform.system().lower()
        if system == "darwin":
            subprocess.run(["open", str(video_dir)])
        elif system == "windows":
            subprocess.run(["explorer", str(video_dir)])
        elif system == "linux":
            subprocess.run(["xdg-open", str(video_dir)])
        print(f"📁 Opened: {video_dir}")
    elif choice == "4":
        for video in videos:
            print(f"\n{'='*50}")
            get_video_info(video)
    else:
        print("❌ Invalid choice")


if __name__ == "__main__":
    main()
