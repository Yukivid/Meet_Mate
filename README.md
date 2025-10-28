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

Meet_Mate/
│
├── app.py # Main Flask application
├── diarize_MOM.py # Logic for meeting diarization and MOM extraction
├── cal1.py # Auxiliary computation or processing script
├── requirements.txt # Python dependencies
│
├── static/ # Static assets (CSS, JS, icons)
├── templates/ # HTML templates for Flask
│
├── credentials.json # OAuth credentials (secure this)
├── keys.json # API keys (secure this)
└── token.json # Authentication tokens


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


💡 How It Works


Upload Meeting File: Accepts both audio and video files.


Extract Audio: Converts video to .wav using moviepy.


Transcription: Speech-to-text via SpeechRecognition (Google Web Speech API).


Speaker Diarization: Identifies speaker turns (naive or model-based).


Summarization: Uses frequency-based extraction and heuristics to generate MOM (Minutes of Meeting).


Action & Decision Extraction: Pattern-based detection (e.g., “will”, “should”, “decide”).


Display & Download: Organized results shown on the dashboard, downloadable in .txt format.



📊 Sample Output
ComponentExampleTranscript"Good morning everyone, let's review the project timeline..."Minutes (Summary)- Project timeline discussed- Budget approval scheduled next weekAction Items- John will prepare the financial report by FridayDecisions- Launch postponed to Q2

🔒 Security Notes


Do not commit your credentials.json, keys.json, or token.json to GitHub.


Use .gitignore to keep sensitive data out of version control.


Consider environment variables or a .env file for production deployments.



🔮 Future Enhancements


🔊 Integration with Whisper, PyAnnote, or OpenAI Realtime API for more accurate transcription & diarization.


🌍 Multi-language transcription support.


📄 Export summaries to PDF/Word.


☁️ Cloud deployment (AWS / Render / HuggingFace Spaces).


🧾 Meeting sentiment analysis.



🤝 Contributing
Contributions are welcome!
To contribute:


Fork this repository.


Create your feature branch:
git checkout -b feature/your-feature-name



Commit your changes:
git commit -m "Add your feature"



Push to your branch and open a Pull Request.



🧰 Requirements
Flask
moviepy
pydub
SpeechRecognition
nltk

Install them manually (if not using requirements.txt):
pip install flask moviepy pydub SpeechRecognition nltk


🖼️ Screenshots
(Add your own screenshots here)
Upload PageResults Page

📜 License
This project is licensed under the MIT License — see the LICENSE file for details.

🧑‍💻 Author
Deepesh Raj A.Y.
🎓 B.Tech Student, VIT
💬 GitHub: @Yukivid

⭐ Acknowledgments


SpeechRecognition Library


MoviePy


PyDub


NLTK




“Meet_Mate — Turning Meetings into Meaningful Minutes.”


---

Would you like me to generate an enhanced version with **badges** (build, license, Python version, stars, etc.) and a **preview GIF section** for your Render-hosted demo?


## 📁 Repository Structure

