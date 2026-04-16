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
                video_clip = VideoFileClip(video_paths[i])
                audio_clip = AudioFileClip(audio_paths[i])
                
                # Determine the target duration for this scene
                # We prioritize the audio duration but ensure it's at least a reasonable length
                scene_duration = max(audio_clip.duration, scene.duration)
                
                # Resize video clip to 1080p landscape (if needed)
                video_clip = video_clip.resize(height=720).crop(x_center=video_clip.w/2, y_center=video_clip.h/2, width=1280, height=720)
                
                # Sync durations
                if video_clip.duration < scene_duration:
                    # Loop video if it's too short for the scene
                    video_clip = video_clip.loop(duration=scene_duration)
                else:
                    # Trim video to the target scene duration
                    video_clip = video_clip.subclip(0, scene_duration)
                
                # Set audio (it will play from the start)
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
