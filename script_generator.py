from planner import VideoPlan, Scene
from typing import List, Dict

class ScriptGenerator:
    def __init__(self, ai_client=None, provider="openai"):
        self.client = ai_client
        self.provider = provider

    def generate_script(self, plan: VideoPlan) -> VideoPlan:
        """
        Enhances the plan with more detailed narration and scene scripts if needed.
        """
        # The Planner already generates narration, but we can refine it here if necessary.
        # For now, let's just return the plan as it is, or add some refinement if requested.
        return plan

    def refine_scene_narration(self, scene: Scene, language: str) -> str:
        """
        Refines the narration for a single scene to ensure it fits the language naturally.
        """
        if not self.client:
            return scene.narration
            
        prompt = f"""
        Refine the following narration for a video scene about '{scene.visual_description}' in {language}.
        Ensure the tone is natural and fits the context of '{language}'.
        Narration: {scene.narration}
        """
        
        model = "gpt-4o" if self.provider == "openai" else "llama-3.3-70b-versatile"
        
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": "You are a professional multilingual copywriter."},
                      {"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
