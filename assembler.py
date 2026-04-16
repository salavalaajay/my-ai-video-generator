import os
from typing import List, Dict
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, TextClip, CompositeVideoClip, ColorClip
from planner import VideoPlan

class VideoAssembler:
    def __init__(self, temp_dir: str = "temp"):
        self.temp_dir = temp_dir
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)

    def assemble_video(self, plan: VideoPlan, video_paths: List[str], audio_paths: List[str], output_path: str):
        """
        Assembles video clips and audio voiceovers into a single MP4 video.
        """
        clips = []
        
        for i, scene in enumerate(plan.scenes):
            try:
                # Load video and audio
                video_clip = None
                audio_clip = None
                
                if i < len(video_paths) and video_paths[i] and os.path.exists(video_paths[i]):
                    video_clip = VideoFileClip(video_paths[i])
                
                if i < len(audio_paths) and audio_paths[i] and os.path.exists(audio_paths[i]):
                    audio_clip = AudioFileClip(audio_paths[i])
                
                # If both are missing, use a placeholder
                if not video_clip and not audio_clip:
                    clips.append(ColorClip(size=(1280, 720), color=(0,0,0), duration=scene.duration))
                    continue
                
                # Determine the target duration for this scene
                scene_duration = scene.duration
                if audio_clip:
                    scene_duration = max(audio_clip.duration, scene_duration)
                
                # Handle missing video: create a dark gray background
                if not video_clip:
                    video_clip = ColorClip(size=(1280, 720), color=(20, 20, 20), duration=scene_duration)
                else:
                    # Resize and sync video
                    video_clip = video_clip.resize(height=720).crop(x_center=video_clip.w/2, y_center=video_clip.h/2, width=1280, height=720)
                    if video_clip.duration < scene_duration:
                        video_clip = video_clip.loop(duration=scene_duration)
                    else:
                        video_clip = video_clip.subclip(0, scene_duration)
                
                # Set audio if it exists
                if audio_clip:
                    video_clip = video_clip.set_audio(audio_clip)
                
                # Optional: Add subtitles
                # For now, let's keep it simple and just add the narration text if possible
                # (Requires ImageMagick for TextClip)
                try:
                    txt_clip = TextClip(
                        scene.narration, 
                        fontsize=24, 
                        color='white', 
                        bg_color='black', 
                        method='caption', 
                        size=(1000, None)
                    ).set_position(('center', 'bottom')).set_duration(audio_clip.duration).set_start(0)
                    video_clip = CompositeVideoClip([video_clip, txt_clip])
                except Exception as te:
                    print(f"TextClip failed (probably missing ImageMagick): {te}")
                
                clips.append(video_clip)
            except Exception as e:
                print(f"Error processing scene {i+1}: {e}")
                # Fallback to a placeholder if scene fails
                placeholder = ColorClip(size=(1280, 720), color=(0,0,0), duration=scene.duration)
                clips.append(placeholder)

        if not clips:
            print("No clips to assemble.")
            return False

        try:
            final_video = concatenate_videoclips(clips, method="compose")
            final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
            return True
        except Exception as e:
            print(f"Error during final assembly: {e}")
            return False
        finally:
            # Close clips to free resources
            for clip in clips:
                clip.close()
