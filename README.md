# 🧠 Meet_Mate — AI Meeting Assistant

Meet_Mate is an **AI-powered meeting assistant** that automatically generates transcripts, meeting minutes, key decisions, and action items from your meeting recordings.  
Simply upload an audio or video file — Meet_Mate does the rest!

---

## 🚀 Features

- 🎙️ **Audio/Video Uploads:** Accepts `.mp3`, `.wav`, `.mp4`, `.mkv`, `.mov`, etc.  
- 🗣️ **Automatic Transcription:** Converts speech to text using SpeechRecognition (Google API).  
- 👥 **Speaker Diarization:** Separates speakers using timestamp-based segmentation (can be extended to `pyannote.audio`).  
- 📝 **Meeting Minutes Extraction:** Summarizes important discussion points.  
- ✅ **Action & Decision Detection:** Extracts follow-up actions and decisions.  
- 🌐 **Web App Interface:** Flask-based minimal UI for uploads and results viewing.  
- 💾 **Downloadable Results:** Get the transcript and minutes in `.txt` format.  

---

## 🏗️ Tech Stack

| Component | Technology |
|------------|-------------|
| Frontend | HTML5, CSS3 (Flask Templates) |
| Backend | Python (Flask) |
| Audio Processing | MoviePy, pydub |
| Speech Recognition | SpeechRecognition (Google API) |
| NLP & Summarization | NLTK |
| Storage | Local filesystem (`meetmate_results/`) |

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

git clone https://github.com/Yukivid/Meet_Mate.git
cd Meet_Mate

2️⃣ Create a Virtual Environment
python3 -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Run the Application
python app.py

---
💡 How It Works


Upload Meeting File: Accepts both audio and video files.

Extract Audio: Converts video to .wav using moviepy.

Transcription: Speech-to-text via SpeechRecognition (Google Web Speech API).

Speaker Diarization: Identifies speaker turns (naive or model-based).

Summarization: Uses frequency-based extraction and heuristics to generate MOM (Minutes of Meeting).

Action & Decision Extraction: Pattern-based detection (e.g., “will”, “should”, “decide”).

Display & Download: Organized results shown on the dashboard, downloadable in .txt format.
---
🔒 Security Notes

Do not commit your credentials.json, keys.json, or token.json to GitHub.

Use .gitignore to keep sensitive data out of version control.

Consider environment variables or a .env file for production deployments.
---
🔮 Future Enhancements

🔊 Integration with Whisper, PyAnnote, or OpenAI Realtime API for more accurate transcription & diarization.

🌍 Multi-language transcription support.

📄 Export summaries to PDF/Word.

☁️ Cloud deployment (AWS / Render / HuggingFace Spaces).

🧾 Meeting sentiment analysis.
---

📜 License
This project is licensed under the MIT License — see the LICENSE file for details.

🧑‍💻 Author
Deepesh Raj A.Y.
🎓 B.Tech Student, VIT
💬 GitHub: @Yukivid
“Meet_Mate — Turning Meetings into Meaningful Minutes.”

