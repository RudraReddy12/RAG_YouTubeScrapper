# 🎥 YouTube → Website Generator (RAG Application)

Convert any YouTube video into a **professional article-style website** using AI.

This project uses a **Retrieval-Augmented Generation (RAG)** pipeline to:
1. Extract transcript from a YouTube video  
2. Convert it into a structured technical article  
3. Generate a fully functional **frontend website (HTML, CSS, JS)**  

---

##  Features

- 🔗 Input any YouTube video URL  
-  Smart summarization (handles both short & long videos)  
-  Converts transcript → clean technical article  
-  Generates production-ready website:
  - HTML
  - CSS
  - JavaScript 
-  Download website as ZIP  
-  Live preview inside Streamlit  

---

##  Architecture
YouTube URL  
↓  
Transcript Extraction (YoutubeLoader)  
↓  
Text Chunking (RecursiveCharacterTextSplitter)  
↓  
RAG Summarization (LangChain + Gemini)  
↓  
Article Generation  
↓  
Frontend Code Generation (HTML/CSS/JS)  
↓  
Downloadable Website (ZIP)



---

##  Tech Stack

- **Frontend/UI:** Streamlit  
- **LLM:** Google Gemini
- **Framework:** LangChain  
- **Data Source:** Transcript that is extracted from YouTube video  
- **Environment:** Python  

---


