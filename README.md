# 🎬 Script to Screen – Agentic AI Video Generator

An automated AI system that transforms topics into complete MP4 videos with multilingual scripts, motion clips, and natural voiceovers.

## 🚀 Features
- **Multilingual Support**: Generate videos in English, Hindi, Telugu, Tamil, and more.
- **Natural AI Voices**: Uses Edge-TTS for human-like narration.
- **Smart Planning**: Groq/OpenAI powered agentic scene planning.
- **Stock Footage**: Automatic fetching of motion clips from Pexels.
- **Production UI**: Sleek dark-themed Streamlit interface.

## 🛠️ Deployment Instructions (To get your Shareable Link)

### 1. Upload to GitHub
1. Create a new repository on GitHub.
2. Upload all files from this folder **EXCEPT** the `.env` file.
3. Ensure `requirements.txt` is in the root directory.

### 2. Deploy to Streamlit Cloud
1. Go to [Streamlit Community Cloud](https://share.streamlit.io/).
2. Connect your GitHub account and select your repository.
3. Set the main file to `app.py`.
4. **IMPORTANT**: Before clicking Deploy, go to **Advanced Settings** -> **Secrets** and add:
   ```toml
   GROQ_API_KEY = "your_key"
   PEXELS_API_KEY = "your_key"
   ```
5. Click **Deploy**. You will get a link like `https://your-app.streamlit.app`.

## 💻 Local Usage
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   streamlit run app.py
   ```

---
*Built with Python, Streamlit, MoviePy, and Groq.*
