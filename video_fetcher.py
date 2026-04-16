import requests
import os
import random
from typing import List, Optional

class VideoFetcher:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.pexels.com/videos/search"
        self.headers = {"Authorization": self.api_key}

    def fetch_video(self, keywords: List[str], min_duration: float) -> Optional[str]:
        """
        Fetches a video from Pexels using the provided keywords.
        Returns the URL of the video file.
        """
        # Clean up keywords and use the most relevant one first
        search_terms = [k.strip() for k in keywords if k.strip()]
        if not search_terms:
            search_terms = ["nature", "abstract", "technology"] # Ultimate fallback
            
        # Try different combinations of keywords
        queries = [
            " ".join(search_terms[:2]), # Top 2 keywords
            search_terms[0],           # Just the first keyword
            "abstract " + search_terms[0], # Broadening
            "cinematic " + search_terms[0]
        ]
        
        for query in queries:
            params = {
                "query": query,
                "per_page": 5,
                "min_width": 1280,
                "orientation": "landscape"
            }
            
            try:
                response = requests.get(self.base_url, headers=self.headers, params=params)
                if response.status_code == 401:
                    print("Unauthorized: Check Pexels API Key")
                    return None
                response.raise_for_status()
                data = response.json()
                
                if data.get("videos"):
                    # Sort by duration to find a clip long enough, but pick one that exists
                    suitable_videos = [
                        v for v in data["videos"] 
                        if v.get("duration", 0) >= min_duration
                    ]
                    
                    # If none are long enough, just take the longest available one
                    video = suitable_videos[0] if suitable_videos else data["videos"][0]
                    
                    # Find the best quality MP4 file
                    video_files = video.get("video_files", [])
                    # Prefer HD/Full HD if available
                    best_file = None
                    for f in video_files:
                        if f.get("file_type") == "video/mp4":
                            # We want a balance of quality and file size for web
                            if 1280 <= f.get("width", 0) <= 1920:
                                best_file = f["link"]
                                break
                    
                    if not best_file and video_files:
                        best_file = video_files[0]["link"]
                        
                    if best_file:
                        return best_file
            except Exception as e:
                print(f"Error fetching video for query '{query}': {e}")
                continue
                
        return None

    def download_video(self, url: str, save_path: str):
        """
        Downloads the video from the provided URL.
        """
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        except Exception as e:
            print(f"Error downloading video from {url}: {e}")
            return False
