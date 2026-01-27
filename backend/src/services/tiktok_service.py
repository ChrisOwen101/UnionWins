"""
TikTok service for creating union win videos.

This service handles:
- Generating scripts using OpenAI
- Converting text to speech using OpenAI TTS
- Generating images using DALL-E
- Creating animated videos with Ken Burns effects
"""
import os
import tempfile
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional
import numpy as np

from sqlalchemy.orm import Session

from src.config import client as openai_client
from src.services.win_service import get_all_wins_sorted

from moviepy import (
    ColorClip,
    AudioFileClip,
    CompositeVideoClip,
    TextClip,
    ImageClip,
    VideoClip,
    concatenate_videoclips,
)



# Video dimensions for TikTok (9:16 vertical format)
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920

# Colors
BACKGROUND_COLOR = (30, 64, 175)  # Tailwind blue-800
OVERLAY_COLOR = (0, 0, 0)  # Black for overlay

# Text styling
TEXT_COLOR = "white"
TEXT_FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
TITLE_SIZE = 72
SUBTITLE_SIZE = 48
BODY_SIZE = 42
SMALL_SIZE = 36


def get_most_recent_win(db: Session) -> Optional[dict]:
    """
    Get the most recent approved union win from the database.

    Args:
        db: Database session

    Returns:
        Dictionary with win details or None if no wins found
    """
    wins = get_all_wins_sorted(db)
    if not wins:
        return None

    win = wins[0]
    return {
        "id": win.id,
        "title": win.title,
        "union_name": win.union_name,
        "emoji": win.emoji or "✊",
        "summary": win.summary,
        "date": win.date,
        "url": win.url,
    }


def generate_tiktok_script(win: dict) -> str:
    """
    Generate a 20-second script explaining the union win.

    Uses OpenAI to create an engaging, easy-to-understand script
    suitable for TikTok's short-form video format.

    Args:
        win: Dictionary containing win details (title, union_name, summary)

    Returns:
        Generated script text (approximately 50-60 words for 20 seconds)
    """
    prompt = f"""Create a 20-second TikTok script about this union victory. 
Make it engaging, easy to understand, and memorable. 
Use simple language that anyone can understand.
The script should be approximately 50-60 words (about 20 seconds when spoken).
Don't include any stage directions or emojis in the script - just the spoken words.

Union Win Details:
- Title: {win['title']}
- Union: {win['union_name'] or 'Workers'}
- Summary: {win['summary']}
- Date: {win['date']}

Start with a hook to grab attention. End with an inspiring message about worker power.
"""

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are a social media content creator who makes "
                           "engaging short-form videos about workers' rights and "
                           "union victories. Your tone is upbeat, informative, and "
                           "inspiring.",
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=200,
        temperature=0.7,
    )

    script = response.choices[0].message.content.strip()
    print(f"📝 Generated TikTok script ({len(script.split())} words)", flush=True)
    return script


def convert_script_to_audio(script: str, output_path: str) -> str:
    """
    Convert the script text to speech using OpenAI TTS.

    Args:
        script: The script text to convert
        output_path: Path to save the audio file

    Returns:
        Path to the generated audio file
    """
    response = openai_client.audio.speech.create(
        model="tts-1-hd",
        voice="nova",  # Friendly, energetic voice suitable for TikTok
        input=script,
        speed=1.1,  # Slightly faster for TikTok pacing
    )

    response.stream_to_file(output_path)
    print(f"🎤 Generated audio file: {output_path}", flush=True)
    return output_path


def generate_scene_images(win: dict, temp_dir: str) -> list[str]:
    """
    Generate AI images for the video scenes using DALL-E.

    Creates 3 images:
    1. Hook scene - dramatic workers/union imagery
    2. Story scene - relevant to the specific win
    3. Call to action - empowering union imagery

    Args:
        win: Win details dictionary
        temp_dir: Directory to save generated images

    Returns:
        List of paths to generated images
    """
    image_prompts = [
        # Scene 1: Hook - Attention grabbing
        f"Dramatic wide shot of diverse workers standing united with raised fists, "
        f"dramatic lighting, cinematic style, powerful solidarity moment, "
        f"professional photography, vibrant colors, 9:16 vertical format",
        
        # Scene 2: Story - Specific to the win
        f"Professional photo depicting {win['union_name'] or 'workers'} celebrating "
        f"a victory related to {win['title'][:50]}, diverse group of happy workers, "
        f"warm celebratory atmosphere, documentary style, 9:16 vertical format",
        
        # Scene 3: Call to action - Empowering
        f"Inspiring image of workers joining hands in solidarity, diverse group, "
        f"golden hour lighting, hopeful atmosphere, union strength, "
        f"professional documentary photography, 9:16 vertical format",
    ]
    
    image_paths = []
    
    for i, prompt in enumerate(image_prompts):
        try:
            print(f"🎨 Generating image {i+1}/3...", flush=True)
            response = openai_client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1792",  # Vertical format for TikTok
                quality="standard",
                n=1,
            )
            
            image_url = response.data[0].url
            image_path = os.path.join(temp_dir, f"scene_{i+1}.png")
            
            # Download the image
            img_response = requests.get(image_url, timeout=60)
            img_response.raise_for_status()
            
            with open(image_path, "wb") as f:
                f.write(img_response.content)
            
            image_paths.append(image_path)
            print(f"✅ Generated image {i+1}: {image_path}", flush=True)
            
        except Exception as e:
            print(f"⚠️ Failed to generate image {i+1}: {e}", flush=True)
            # Use a colored fallback
            image_paths.append(None)
    
    return image_paths


def apply_ken_burns_effect(
    clip: ImageClip,
    duration: float,
    effect_type: str = "zoom_in",
) -> ImageClip:
    """
    Apply Ken Burns (pan and zoom) effect to an image clip.

    Args:
        clip: The image clip to animate
        duration: Duration of the animation
        effect_type: Type of effect - 'zoom_in', 'zoom_out', 'pan_left', 'pan_right'

    Returns:
        Animated image clip
    """
    w, h = clip.size
    
    # Calculate the scale to cover the video dimensions
    scale_w = VIDEO_WIDTH / w
    scale_h = VIDEO_HEIGHT / h
    base_scale = max(scale_w, scale_h) * 1.3  # Extra 30% for zoom room
    
    if effect_type == "zoom_in":
        # Start zoomed out, end zoomed in
        def zoom_func(t):
            progress = t / duration
            scale = base_scale * (1 + 0.15 * progress)  # 15% zoom
            return scale
        
        def position_func(t):
            return ("center", "center")
            
    elif effect_type == "zoom_out":
        # Start zoomed in, end zoomed out
        def zoom_func(t):
            progress = t / duration
            scale = base_scale * (1.15 - 0.15 * progress)
            return scale
        
        def position_func(t):
            return ("center", "center")
            
    elif effect_type == "pan_left":
        # Pan from right to left
        def zoom_func(t):
            return base_scale * 1.1
        
        def position_func(t):
            progress = t / duration
            x_offset = int(100 * (1 - progress) - 50)
            return (x_offset, "center")
            
    else:  # pan_right
        # Pan from left to right
        def zoom_func(t):
            return base_scale * 1.1
        
        def position_func(t):
            progress = t / duration
            x_offset = int(100 * progress - 50)
            return (x_offset, "center")
    
    # Apply the resize effect frame by frame
    def make_frame(t):
        scale = zoom_func(t)
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        # Resize the frame
        frame = clip.get_frame(0)
        from PIL import Image
        img = Image.fromarray(frame)
        img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # Crop to video dimensions from center
        left = (new_w - VIDEO_WIDTH) // 2
        top = (new_h - VIDEO_HEIGHT) // 2
        img_cropped = img_resized.crop((left, top, left + VIDEO_WIDTH, top + VIDEO_HEIGHT))
        
        return np.array(img_cropped)
    
    animated_clip = VideoClip(make_frame, duration=duration)
    
    return animated_clip


def create_text_overlay(
    text: str,
    position: tuple,
    font_size: int,
    duration: float,
    start_time: float = 0,
    bg_opacity: float = 0.7,
) -> CompositeVideoClip:
    """
    Create a text overlay with semi-transparent background.

    Args:
        text: Text to display
        position: Position tuple (x, y) or ("center", y)
        font_size: Font size
        duration: Duration of the clip
        start_time: When the text appears
        bg_opacity: Opacity of background (0-1)

    Returns:
        Composite clip with text and background
    """
    # Create text clip
    txt_clip = TextClip(
        text=text,
        font_size=font_size,
        color=TEXT_COLOR,
        font=TEXT_FONT,
        size=(VIDEO_WIDTH - 120, None),
        method="caption",
        text_align="center",
    )
    
    # Get text dimensions
    txt_w, txt_h = txt_clip.size
    
    # Create background box
    padding = 30
    bg_clip = ColorClip(
        size=(txt_w + padding * 2, txt_h + padding * 2),
        color=OVERLAY_COLOR,
    ).with_opacity(bg_opacity)
    
    # Position background
    if position[0] == "center":
        bg_x = (VIDEO_WIDTH - txt_w - padding * 2) // 2
    else:
        bg_x = position[0] - padding
    bg_y = position[1] - padding
    
    bg_clip = bg_clip.with_position((bg_x, bg_y)).with_duration(duration)
    txt_clip = txt_clip.with_position(position).with_duration(duration)
    
    return [bg_clip, txt_clip]


def create_video(
    audio_path: str,
    script: str,
    win: dict,
    output_path: str,
    image_paths: list[str] = None,
) -> str:
    """
    Create an animated video with Ken Burns effects and text overlays.

    The video features:
    - AI-generated images with Ken Burns animations
    - Animated text overlays
    - Professional transitions
    - Voiceover audio

    Args:
        audio_path: Path to the audio file
        script: The script text (for potential subtitles)
        win: Win details dictionary
        output_path: Path to save the video file
        image_paths: List of paths to scene images

    Returns:
        Path to the generated video file
    """
    # Load audio to get duration
    audio = AudioFileClip(audio_path)
    total_duration = audio.duration
    
    # Calculate scene durations (3 scenes)
    scene_duration = total_duration / 3
    
    scenes = []
    effects = ["zoom_in", "pan_left", "zoom_out"]
    
    for i in range(3):
        scene_start = i * scene_duration
        
        # Create background for this scene
        if image_paths and image_paths[i] and os.path.exists(image_paths[i]):
            # Use AI-generated image with Ken Burns effect
            img_clip = ImageClip(image_paths[i])
            scene_bg = apply_ken_burns_effect(
                img_clip,
                scene_duration,
                effect_type=effects[i],
            )
        else:
            # Fallback to colored background with gradient effect
            scene_bg = ColorClip(
                size=(VIDEO_WIDTH, VIDEO_HEIGHT),
                color=BACKGROUND_COLOR,
                duration=scene_duration,
            )
        
        # Add dark overlay for text readability
        overlay = ColorClip(
            size=(VIDEO_WIDTH, VIDEO_HEIGHT),
            color=(0, 0, 0),
            duration=scene_duration,
        ).with_opacity(0.4)
        
        # Create text for each scene
        if i == 0:
            # Scene 1: Hook with emoji and "UNION WIN"
            text_elements = [
                *create_text_overlay(
                    f"{win['emoji']} UNION WIN",
                    ("center", VIDEO_HEIGHT // 2 - 200),
                    TITLE_SIZE + 20,
                    scene_duration,
                ),
                *create_text_overlay(
                    win['union_name'] or "Workers United",
                    ("center", VIDEO_HEIGHT // 2 + 50),
                    SUBTITLE_SIZE,
                    scene_duration,
                ),
            ]
        elif i == 1:
            # Scene 2: The story/title
            text_elements = create_text_overlay(
                win['title'],
                ("center", VIDEO_HEIGHT // 2 - 100),
                BODY_SIZE,
                scene_duration,
            )
        else:
            # Scene 3: Call to action + branding
            text_elements = [
                *create_text_overlay(
                    "Workers win when\nwe stand together!",
                    ("center", VIDEO_HEIGHT // 2 - 150),
                    SUBTITLE_SIZE,
                    scene_duration,
                ),
                *create_text_overlay(
                    "✊ UnionWins.com",
                    ("center", VIDEO_HEIGHT - 300),
                    SMALL_SIZE,
                    scene_duration,
                ),
            ]
        
        # Ensure text_elements is a list
        if not isinstance(text_elements, list):
            text_elements = [text_elements]
        
        # Composite scene
        scene_clips = [scene_bg, overlay] + text_elements
        scene = CompositeVideoClip(scene_clips, size=(VIDEO_WIDTH, VIDEO_HEIGHT))
        scene = scene.with_duration(scene_duration)
        scenes.append(scene)
    
    # Concatenate all scenes
    final_video = concatenate_videoclips(scenes, method="compose")
    
    # Add audio
    final_video = final_video.with_audio(audio)
    
    # Write video file
    print("🎬 Rendering video...", flush=True)
    final_video.write_videofile(
        output_path,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        audio_bitrate="192k",
        threads=16,
        preset="medium",
        write_logfile=False,
    )
    
    # Clean up
    audio.close()
    final_video.close()
    for scene in scenes:
        scene.close()
    
    print(f"🎬 Created video: {output_path}", flush=True)
    return output_path


def create_tiktok_video(db: Session, output_dir: Optional[str] = None) -> dict:
    """
    Create a TikTok video for the most recent win and save it to a file.

    This orchestrates the workflow:
    1. Get the most recent win
    2. Generate a script
    3. Generate AI images for scenes
    4. Convert script to audio
    5. Create animated video with Ken Burns effects
    6. Save video to /videos directory

    Args:
        db: Database session
        output_dir: Optional directory to save the video. If None, uses project /videos.

    Returns:
        Dictionary with result status, video path, and details
    """
    # Get most recent win
    win = get_most_recent_win(db)
    if not win:
        return {
            "success": False,
            "message": "No union wins found to create video",
        }

    print(f"🎯 Creating TikTok for: {win['title']}", flush=True)

    # Determine output directory - use /videos at project root
    project_root = Path(__file__).parent.parent.parent
    videos_dir = project_root / "videos"
    videos_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename with timestamp and win ID
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    video_filename = f"union_win_{win['id']}_{timestamp}.mp4"
    video_path = str(videos_dir / video_filename)
    audio_path = str(videos_dir / f"audio_{timestamp}.mp3")
    
    # Create temp directory for images
    temp_dir = tempfile.mkdtemp()
    image_paths = []

    try:
        # Step 1: Generate script
        script = generate_tiktok_script(win)

        # Step 2: Generate AI images for scenes
        print("🎨 Generating scene images...", flush=True)
        image_paths = generate_scene_images(win, temp_dir)

        # Step 3: Convert to audio
        convert_script_to_audio(script, audio_path)

        # Step 4: Create animated video with images
        create_video(audio_path, script, win, video_path, image_paths)

        # Clean up temp files
        if os.path.exists(audio_path):
            os.remove(audio_path)
        for img_path in image_paths:
            if img_path and os.path.exists(img_path):
                os.remove(img_path)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)

        # Step 5: Create caption with hashtags
        caption = (
            f"{win['emoji']} {win['title']}\n\n"
            f"Another win for {win['union_name'] or 'workers'}! "
            f"#UnionStrong #WorkersRights #UnionWins #LaborMovement"
        )

        return {
            "success": True,
            "win_id": win["id"],
            "win_title": win["title"],
            "script": script,
            "caption": caption,
            "video_path": video_path,
            "message": "TikTok video created successfully",
        }

    except Exception as e:
        error_msg = f"Error creating TikTok: {str(e)}"
        print(f"❌ {error_msg}", flush=True)
        # Clean up on error
        if os.path.exists(audio_path):
            os.remove(audio_path)
        if os.path.exists(video_path):
            os.remove(video_path)
        for img_path in image_paths:
            if img_path and os.path.exists(img_path):
                os.remove(img_path)
        return {
            "success": False,
            "win_id": win["id"] if win else None,
            "message": error_msg,
        }
