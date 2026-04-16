import json
from typing import List, Dict
from pydantic import BaseModel

class Scene(BaseModel):
    scene_number: int
    narration: str
    visual_description: str
    keywords: List[str]
    duration: float

class VideoPlan(BaseModel):
    topic: str
    video_type: str
    total_duration: int
    language: str
    scenes: List[Scene]

class Planner:
    def __init__(self, ai_client=None, provider="openai"):
        self.client = ai_client
        self.provider = provider

    def plan_video(self, topic: str, video_type: str, duration: int, language: str) -> VideoPlan:
        """
        Plans the video structure including number of scenes and visual descriptions.
        """
        # Determine number of scenes based on duration (approx 6-10 seconds per scene)
        num_scenes = max(3, duration // 7)
        avg_scene_duration = duration / num_scenes
        
        prompt = f"""
        You are a professional video production planner. 
        TASK: Plan a {duration}-second {video_type} video about '{topic}'.
        LANGUAGE: The narration MUST be written ENTIRELY in {language}. This is a critical requirement.
        
        STRUCTURE:
        - Total Duration: {duration} seconds.
        - Number of Scenes: {num_scenes}.
        - Average Scene Duration: {avg_scene_duration:.1f} seconds.
        
        FOR EACH SCENE, PROVIDE:
        1. "narration": Detailed narration text written ONLY in {language}. 
           IMPORTANT: The narration length must be sufficient to fill the scene duration (approx 130-150 words per minute).
        2. "visual_description": A detailed visual description of the scene (MUST be in English).
        3. "keywords": 3-5 specific keywords for stock video search (MUST be in English).
        4. "duration": The duration of this scene in seconds (Total must sum to {duration}).
        
        OUTPUT FORMAT:
        Return ONLY a JSON object with this exact structure:
        {{
            "topic": "{topic}",
            "video_type": "{video_type}",
            "total_duration": {duration},
            "language": "{language}",
            "scenes": [
                {{
                    "scene_number": 1,
                    "narration": "Detailed text in {language}...",
                    "visual_description": "English description...",
                    "keywords": ["keyword1", "keyword2"],
                    "duration": {avg_scene_duration:.1f}
                }}
            ]
        }}
        """
        
        if self.client:
            model = "gpt-4o" if self.provider == "openai" else "llama-3.3-70b-versatile"
            
            # Groq and OpenAI use almost identical chat completion calls
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": "You are a professional video scriptwriter and planner. Always respond in valid JSON format."},
                          {"role": "user", "content": prompt}],
                response_format={"type": "json_object"} if self.provider == "openai" or self.provider == "groq" else None
            )
            
            content = response.choices[0].message.content
            # Handle potential non-JSON wrapper text if provider is not OpenAI/Groq
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            
            plan_dict = json.loads(content)
            return VideoPlan(**plan_dict)
        else:
            # Fallback for testing without API key
            return self._get_mock_plan(topic, video_type, duration, language, num_scenes)

    def _get_mock_plan(self, topic, video_type, duration, language, num_scenes) -> VideoPlan:
        scenes = []
        scene_duration = duration / num_scenes
        for i in range(1, num_scenes + 1):
            scenes.append(Scene(
                scene_number=i,
                narration=f"This is the narration for scene {i} about {topic} in {language}.",
                visual_description=f"Visuals showing {topic} related content for scene {i}.",
                keywords=[topic.replace(" ", ","), "nature", "technology"],
                duration=scene_duration
            ))
        return VideoPlan(
            topic=topic,
            video_type=video_type,
            total_duration=duration,
            language=language,
            scenes=scenes
        )
