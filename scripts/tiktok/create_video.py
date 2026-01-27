#!/usr/bin/env python3
"""
TikTok video creator for union win videos using OpenAI Sora-2.

This standalone script handles:
- Generating narration scripts using OpenAI
- Converting scripts to audio using OpenAI TTS
- Creating video clips with Sora-2 based on win images
- Combining clips and audio into final TikTok video

Usage:
    python scripts/tiktok/create_video.py [--win-id ID]
    
If no win ID is specified, creates a video for the most recent win.
"""
import argparse
import json
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests
from moviepy.editor import (
    AudioFileClip,
    CompositeVideoClip,
    VideoFileClip,
    concatenate_videoclips,
)

# Add backend to path for imports
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from sqlalchemy.orm import Session
from openai import OpenAI

from src.database import SessionLocal
from src.models import UnionWinDB

# Initialize OpenAI client
openai_client = OpenAI()

# Video dimensions for TikTok (9:16 vertical)
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920


def get_win_by_id(db: Session, win_id: int) -> Optional[dict]:
    """
    Get a specific union win by ID.

    Args:
        db: Database session
        win_id: ID of the win to retrieve

    Returns:
        Dictionary with win details or None if not found
    """
    win = db.query(UnionWinDB).filter(
        UnionWinDB.id == win_id,
        UnionWinDB.status == "approved"
    ).first()
    
    if not win:
        return None

    # Parse image_urls from JSON
    image_urls = []
    if win.image_urls:
        try:
            image_urls = json.loads(win.image_urls)
        except (json.JSONDecodeError, TypeError):
            image_urls = []

    return {
        "id": win.id,
        "title": win.title,
        "union_name": win.union_name,
        "emoji": win.emoji or "✊",
        "summary": win.summary,
        "date": win.date,
        "url": win.url,
        "image_urls": image_urls,
    }


def get_most_recent_win(db: Session) -> Optional[dict]:
    """
    Get the most recent approved union win from the database.

    Args:
        db: Database session

    Returns:
        Dictionary with win details or None if no wins found
    """
    win = db.query(UnionWinDB).filter(
        UnionWinDB.status == "approved"
    ).order_by(UnionWinDB.date.desc()).first()
    
    if not win:
        return None

    # Parse image_urls from JSON
    image_urls = []
    if win.image_urls:
        try:
            image_urls = json.loads(win.image_urls)
        except (json.JSONDecodeError, TypeError):
            image_urls = []

    return {
        "id": win.id,
        "title": win.title,
        "union_name": win.union_name,
        "emoji": win.emoji or "✊",
        "summary": win.summary,
        "date": win.date,
        "url": win.url,
        "image_urls": image_urls,
    }


def generate_script(win: dict) -> str:
    """
    Generate a 20-second narration script for the union win.

    Args:
        win: Dictionary containing win details

    Returns:
        Generated script text (approximately 50-60 words for 20 seconds)
    """
    prompt = f"""Create a 20-second TikTok narration script about this union victory.
Make it engaging, easy to understand, and memorable.
Use simple language that anyone can understand.
The script should be approximately 50-60 words (about 20 seconds when spoken).
Don't include any stage directions or emojis - just the spoken words.

Union Win Details:
- Title: {win['title']}
- Union: {win['union_name'] or 'Workers'}
- Summary: {win['summary']}
- Date: {win['date']}

Start with a hook to grab attention. End with an inspiring message about worker power."""

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are an expert TikTok script writer who creates "
                           "engaging, punchy narration scripts about workers' rights "
                           "and union victories. Keep it conversational and inspiring.",
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=200,
        temperature=0.7,
    )

    script = response.choices[0].message.content.strip()
    print(f"📝 Generated script ({len(script.split())} words)", flush=True)
    return script


def convert_script_to_audio(script: str, output_path: str) -> str:
    """
    Convert script text to audio using OpenAI TTS.

    Args:
        script: The narration script text
        output_path: Path to save the audio file

    Returns:
        Path to the generated audio file
    """
    print("🎙️ Converting script to audio...", flush=True)
    
    response = openai_client.audio.speech.create(
        model="tts-1-hd",
        voice="onyx",  # Deep, authoritative voice
        input=script,
        speed=1.0,
    )
    
    response.stream_to_file(output_path)
    print(f"✅ Audio saved to: {output_path}", flush=True)
    return output_path


def generate_video_prompt_from_image(image_url: str, win: dict, scene_number: int) -> str:
    """
    Generate a Sora-2 video prompt based on an image from the win.

    Args:
        image_url: URL of the source image
        win: Dictionary containing win details for context
        scene_number: Which scene this is (1, 2, or 3)

    Returns:
        Generated video prompt for Sora-2
    """
    scene_focuses = {
        1: "opening hook - dramatic reveal, building anticipation",
        2: "main story - workers in action, solidarity and strength",
        3: "celebration - victory moment, triumphant energy",
    }
    
    focus = scene_focuses.get(scene_number, "dynamic worker imagery")
    
    prompt = f"""Create a 7-second video prompt inspired by this image and context.

Image URL: {image_url}

Union Win Context:
- Title: {win['title']}
- Union: {win['union_name'] or 'Workers'}
- Summary: {win['summary']}

Scene Focus: {focus}

Requirements:
1. Capture the essence and visual style of the source image
2. Add cinematic movement and energy
3. Keep it vertical format (9:16) for TikTok
4. Make it visually engaging and professional
5. Focus on: {focus}

Write a detailed visual description for video generation."""

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are an expert at creating detailed video prompts for "
                           "AI video generation. Create vivid, cinematic descriptions "
                           "that capture the spirit of workers' victories.",
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=250,
        temperature=0.7,
    )

    video_prompt = response.choices[0].message.content.strip()
    return video_prompt


def generate_generic_video_prompt(win: dict, scene_number: int) -> str:
    """
    Generate a Sora-2 video prompt when no image is available.

    Args:
        win: Dictionary containing win details
        scene_number: Which scene this is (1, 2, or 3)

    Returns:
        Generated video prompt for Sora-2
    """
    scene_descriptions = {
        1: "Opening scene: Dramatic wide shot of workers gathering, "
           "morning light, sense of anticipation and determination",
        2: "Middle scene: Close-ups of diverse workers united, "
           "signs of solidarity, powerful imagery of collective action",
        3: "Closing scene: Celebration moment, workers cheering, "
           "triumphant atmosphere, victory energy",
    }
    
    base_description = scene_descriptions.get(scene_number, "Workers united")
    
    prompt = f"""Create a 7-second cinematic video prompt for this union victory scene.

Union Win: {win['title']}
Union: {win['union_name'] or 'Workers'}
Summary: {win['summary']}

Scene: {base_description}

Requirements:
1. Vertical format (9:16) for TikTok
2. Cinematic quality with movement
3. Inspiring and empowering tone
4. Professional documentary style

Write a detailed visual description."""

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are an expert cinematographer creating video prompts "
                           "for inspiring documentaries about workers' rights.",
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=200,
        temperature=0.7,
    )

    return response.choices[0].message.content.strip()


def generate_video_clip_with_sora(
    video_prompt: str,
    output_path: str,
    duration: int = 7,
) -> str:
    """
    Generate a video clip using OpenAI Sora-2.

    Args:
        video_prompt: The detailed description of the video to generate
        output_path: Path to save the generated video file
        duration: Duration in seconds (default 7 for ~20s total with 3 clips)

    Returns:
        Path to the generated video file
    """
    print(f"🎬 Generating video clip with Sora-2...", flush=True)
    
    response = openai_client.video.generations.create(
        model="sora-2",
        prompt=video_prompt,
        size="1080x1920",  # Vertical 9:16 format for TikTok
        duration=duration,
    )
    
    video_url = response.data[0].url
    print(f"✅ Video clip generated, downloading...", flush=True)
    
    video_response = requests.get(video_url, timeout=300)
    video_response.raise_for_status()
    
    with open(output_path, "wb") as f:
        f.write(video_response.content)
    
    return output_path


def combine_videos_with_audio(
    video_paths: list[str],
    audio_path: str,
    output_path: str,
) -> str:
    """
    Combine multiple video clips with audio into final video.

    Args:
        video_paths: List of paths to video clips
        audio_path: Path to the audio file
        output_path: Path to save the final video

    Returns:
        Path to the final combined video
    """
    print("🎬 Combining video clips with audio...", flush=True)
    
    # Load video clips
    clips = []
    for path in video_paths:
        if os.path.exists(path):
            clip = VideoFileClip(path)
            clips.append(clip)
    
    if not clips:
        raise ValueError("No valid video clips to combine")
    
    # Concatenate video clips
    final_video = concatenate_videoclips(clips, method="compose")
    
    # Load and add audio
    audio = AudioFileClip(audio_path)
    
    # Adjust video duration to match audio if needed
    if final_video.duration > audio.duration:
        final_video = final_video.subclip(0, audio.duration)
    elif final_video.duration < audio.duration:
        # Loop or extend last frame if video is shorter
        audio = audio.subclip(0, final_video.duration)
    
    final_video = final_video.set_audio(audio)
    
    # Write final video
    print(f"💾 Writing final video to: {output_path}", flush=True)
    final_video.write_videofile(
        output_path,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        logger=None,
    )
    
    # Clean up
    for clip in clips:
        clip.close()
    audio.close()
    final_video.close()
    
    print(f"✅ Final video saved: {output_path}", flush=True)
    return output_path


def create_tiktok_video(
    db: Session,
    win_id: Optional[int] = None,
    output_dir: Optional[str] = None
) -> dict:
    """
    Create a TikTok video for a union win using Sora-2.

    This orchestrates the workflow:
    1. Get the specified win (or most recent if not specified)
    2. Generate a narration script
    3. Convert script to audio using OpenAI TTS
    4. Generate 3 video clips with Sora-2 based on win images
    5. Combine clips and audio into final video
    6. Save video to ./videos directory

    Args:
        db: Database session
        win_id: Optional ID of the win to create video for. If None, uses most recent.
        output_dir: Optional directory to save the video. If None, uses project /videos.

    Returns:
        Dictionary with result status, video path, and details
    """
    # Get win by ID or most recent
    if win_id:
        win = get_win_by_id(db, win_id)
        if not win:
            return {
                "success": False,
                "message": f"No approved win found with ID {win_id}",
            }
    else:
        win = get_most_recent_win(db)
        if not win:
            return {
                "success": False,
                "message": "No union wins found to create video",
            }

    print(f"🎯 Creating TikTok for: {win['title']}", flush=True)
    print(f"📸 Found {len(win['image_urls'])} images for this win", flush=True)

    # Determine output directory - use ./videos at project root
    project_root = Path(__file__).parent.parent.parent
    videos_dir = project_root / "videos"
    videos_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename with timestamp and win ID
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    video_filename = f"union_win_{win['id']}_{timestamp}.mp4"
    video_path = str(videos_dir / video_filename)
    
    # Create temp directory for intermediate files
    temp_dir = tempfile.mkdtemp()
    audio_path = os.path.join(temp_dir, "narration.mp3")
    clip_paths = []

    try:
        # Step 1: Generate narration script
        print("\n📝 Step 1: Generating script...", flush=True)
        script = generate_script(win)
        print(f"   Script: {script[:100]}...", flush=True)

        # Step 2: Convert script to audio
        print("\n🎙️ Step 2: Converting to audio...", flush=True)
        convert_script_to_audio(script, audio_path)

        # Step 3: Generate 3 video clips with Sora-2
        print("\n🎬 Step 3: Generating video clips with Sora-2...", flush=True)
        image_urls = win["image_urls"][:3]  # Use up to 3 images
        
        for i in range(3):
            clip_path = os.path.join(temp_dir, f"clip_{i+1}.mp4")
            
            # Generate prompt based on image if available, otherwise generic
            if i < len(image_urls) and image_urls[i]:
                print(f"   Clip {i+1}: Using image {image_urls[i][:50]}...", flush=True)
                video_prompt = generate_video_prompt_from_image(
                    image_urls[i], win, i + 1
                )
            else:
                print(f"   Clip {i+1}: Using generic prompt", flush=True)
                video_prompt = generate_generic_video_prompt(win, i + 1)
            
            print(f"   Prompt: {video_prompt[:80]}...", flush=True)
            generate_video_clip_with_sora(video_prompt, clip_path)
            clip_paths.append(clip_path)
            print(f"   ✅ Clip {i+1} generated", flush=True)

        # Step 4: Combine video clips with audio
        print("\n🎞️ Step 4: Combining clips with audio...", flush=True)
        combine_videos_with_audio(clip_paths, audio_path, video_path)

        # Step 5: Create caption with hashtags
        caption = (
            f"{win['emoji']} {win['title']}\n\n"
            f"Another win for {win['union_name'] or 'workers'}! "
            f"#UnionStrong #WorkersRights #UnionWins #LaborMovement"
        )

        # Clean up temp files
        for path in clip_paths + [audio_path]:
            if os.path.exists(path):
                os.remove(path)
        os.rmdir(temp_dir)

        return {
            "success": True,
            "win_id": win["id"],
            "win_title": win["title"],
            "script": script,
            "caption": caption,
            "video_path": video_path,
            "message": "TikTok video created successfully with Sora-2",
        }

    except Exception as e:
        error_msg = f"Error creating TikTok: {str(e)}"
        print(f"❌ {error_msg}", flush=True)
        # Clean up on error
        for path in clip_paths + [audio_path, video_path]:
            if os.path.exists(path):
                os.remove(path)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)
        return {
            "success": False,
            "win_id": win["id"] if win else None,
            "message": error_msg,
        }


def main():
    """Main entry point for the TikTok video creation script."""
    parser = argparse.ArgumentParser(
        description="Create a TikTok video for a union win using Sora-2"
    )
    parser.add_argument(
        "--win-id",
        type=int,
        default=None,
        help="ID of the win to create video for (default: most recent)"
    )
    args = parser.parse_args()

    print("🎬 TikTok Video Creator for Union Wins (Sora-2)")
    print("=" * 50)

    # Create database session
    db = SessionLocal()
    
    try:
        result = create_tiktok_video(
            db=db,
            win_id=args.win_id,
        )
        
        if result["success"]:
            print("\n" + "=" * 50)
            print("✅ Video created successfully!")
            print(f"📁 Video path: {result['video_path']}")
            print(f"🎯 Win: {result['win_title']}")
            print(f"\n📝 Script:\n{result['script']}")
            print(f"\n📱 Caption:\n{result['caption']}")
        else:
            print(f"\n❌ Failed: {result['message']}")
            sys.exit(1)
            
    finally:
        db.close()


if __name__ == "__main__":
    main()
