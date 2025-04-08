# 📄 AI Resume Screening System

An interactive AI-powered resume screening web app built with Streamlit and NLP.

## 🚀 Features
- Upload multiple resumes (PDF & DOCX supported)
- Extracts key skills from job description dynamically
- Matches and ranks resumes based on:
  - Semantic similarity (SentenceTransformer)
  - Skill overlap with JD
- Final ranking = `0.7 * similarity + 0.3 * skill match ratio`

---

## 🛠️ Technologies Used
- Python, Streamlit
- spaCy, Sentence-Transformers, PyMuPDF, docx2txt

---

## 📥 How to Run

```bash
  # Clone the repository
  git clone https://github.com/yourusername/resume-screening-app.git
  cd resume-screening-app
  
  # Install dependencies
  pip install -r requirements.txt
  
  # Run the Streamlit app
  streamlit run app.py
```

---

## 🌐 Making the App Public with ngrok (Optional)

If you're running the app on a remote server or in a cloud notebook like Google Colab and want to expose it via a public URL:

```python
from pyngrok import ngrok

# Connect to port 8501 (Streamlit default)
public_url = ngrok.connect(8501)
print(f"✅ App is live at: {public_url}")
```

Make sure to install pyngrok:
```python
pip install pyngrok
```




