#  AI Video Assistant

An AI-powered assistant that turns videos and audio into actionable insights through transcription, summarization, and conversational Q&A.

Built with OpenAI Whisper for speech-to-text, Mistral AI for content generation, and Retrieval-Augmented Generation (RAG) for context-aware conversations with uploaded content.

##  Live Demo

**Streamlit App:** https://wavelength-ai-video-assistant.streamlit.app

##  Features

###  Content Ingestion
- Upload audio files (MP3, WAV, M4A, etc.)
- Upload video files (MP4 and other supported formats)
- Automatic audio extraction and preprocessing from video
- Long-audio chunking for efficient processing

> **Note:** YouTube URL ingestion was originally planned, but Streamlit Cloud blocks `yt-dlp` downloads at the network level. File upload (audio or video) is the current supported path — YouTube support is tracked under [Future Improvements](#-future-improvements).

###  Speech-to-Text Transcription
- OpenAI Whisper-powered transcription
- Chunked processing for long audio/video files
- Multi-language support
- High-quality transcript generation

###  AI-Powered Analysis
- Automatic title generation
- Intelligent content summarization
- Key insights extraction
- Context-aware response generation via Mistral AI

###  Conversational Q&A
- Chat with your transcript
- Retrieval-Augmented Generation (RAG)
- Semantic search over video/audio content
- Context-preserving conversations

##  Processing Pipeline

```text
Input Source (Audio / Video upload)
        ↓
Audio Extraction
        ↓
Audio Preprocessing
        ↓
Chunking
        ↓
Whisper Transcription
        ↓
Transcript Generation
        ↓
Embedding Creation
        ↓
Vector Database Storage (ChromaDB)
        ↓
RAG Retrieval
        ↓
Mistral AI
        ↓
Summary • Insights • Chat
```

##  Tech Stack

| Category | Tools |
|---|---|
| AI & Machine Learning | OpenAI Whisper, Mistral AI, LangChain |
| Vector Database | ChromaDB |
| Audio Processing | FFmpeg, pydub |
| Backend | Python |
| Frontend | Streamlit |
| Deployment | Streamlit Cloud |

##  Project Structure

```text
AI-Video-Assistant/
│
├── app.py
├── main.py
├── test.py
│
├── core/
│   ├── extractor.py
│   ├── rag_engine.py
│   ├── summarize.py
│   ├── transcriber.py
│   └── vector_store.py
│
├── utils/
│   └── audio_processor.py
│
├── downloads/
├── vector_db/
├── screenshot/
│
├── requirements.txt
├── packages.txt
├── runtime.txt
└── README.md
```

##  Installation

**Clone the repository**
```bash
git clone https://github.com/raghuvendra34/AI-Video-Assistant.git
cd AI-Video-Assistant
```

**Create a virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate
```

**Install dependencies**
```bash
pip install -r requirements.txt
```

**Configure environment variables**

Create a `.env` file in the project root:
```env
MISTRAL_API_KEY=your_mistral_api_key
SARVAM_API_KEY=your_sarvam_api_key
WHISPER_MODEL=small
SARVAM_STT_MODEL=saaras:v2.5
```

**Run the app**
```bash
streamlit run app.py
```

##  Use Cases

- Meeting transcription and summarization
- Podcast analysis
- Lecture and educational content review
- Interview transcript generation
- Video content research
- Knowledge extraction from long-form content

##  Key Highlights

- End-to-end AI-powered multimedia processing pipeline
- Retrieval-Augmented Generation (RAG) implementation
- Vector database integration using ChromaDB
- Real-time conversational interface
- Deployed and live on Streamlit Cloud
- Built to handle long-form audio/video content via chunked transcription

##  Future Improvements

- YouTube URL ingestion (blocked on Streamlit Cloud due to `yt-dlp` network restrictions — exploring alternate hosting/proxy solutions)
- Deployment to additional platforms beyond Streamlit Cloud (e.g. Render, Hugging Face Spaces) to support YouTube ingestion and remove current platform constraints
- Speaker diarization
- Timestamp-based transcript navigation
- Multi-document knowledge base
- Real-time transcription
- Advanced analytics dashboard
- Multi-video conversational memory

##  Author

**Raghuvendra Kumar**
GitHub: [@raghuvendra34](https://github.com/raghuvendra34)

##  License

This project is intended for educational, research, and portfolio purposes.