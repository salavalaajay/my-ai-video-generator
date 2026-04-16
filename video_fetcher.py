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
        query = " ".join(keywords)
        params = {
            "query": query,
            "per_page": 10,
            "min_width": 1280,
            "min_height": 720,
            "orientation": "landscape"
        }
        
        try:
            response = requests.get(self.base_url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data.get("videos"):
                # Try with a broader query if no results found
                if len(keywords) > 1:
                    return self.fetch_video(keywords[:1], min_duration)
                return None
            
            # Filter videos by duration and select one randomly from the top results
            suitable_videos = [
                v for v in data["videos"] 
                if v.get("duration", 0) >= min_duration
            ]
            
            if not suitable_videos:
                suitable_videos = data["videos"]
            
            video = random.choice(suitable_videos)
            
            # Find the best quality MP4 file
            video_files = video.get("video_files", [])
            # Prefer HD/Full HD if available
            best_file = None
            for f in video_files:
                if f.get("file_type") == "video/mp4":
                    if f.get("quality") == "hd" or f.get("width") >= 1280:
                        best_file = f["link"]
                        break
            
            if not best_file and video_files:
                best_file = video_files[0]["link"]
                
            return best_file
        except Exception as e:
            print(f"Error fetching video for query '{query}': {e}")
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
