import streamlit as st
import pandas as pd
import spacy
import fitz 
import docx2txt
from sentence_transformers import SentenceTransformer, util
from spacy.matcher import PhraseMatcher

# Load models
@st.cache_resource
def load_models():
    return spacy.load("en_core_web_sm"), SentenceTransformer('all-MiniLM-L6-v2')

nlp, model = load_models()

st.title("📄 AI Resume Screening System (PDF & DOCX Upload)")

# Upload resumes
st.subheader("Upload Resumes (PDF or DOCX)")
uploaded_files = st.file_uploader("Choose files", type=["pdf", "docx"], accept_multiple_files=True)

# Job Description Input
st.subheader("Enter Job Description")
jd_input = st.text_area("Job Description", height=200, value="""Looking for a Data Scientist skilled in Python, Machine Learning, NLP and data visualization.""")

# Extract text from PDFs
def extract_text_from_pdf(pdf_file):
    text = ""
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

# Extract text from DOCX
def extract_text_from_docx(docx_file):
    return docx2txt.process(docx_file)

# Generalized text extractor
def extract_text(file):
    if file.name.endswith(".pdf"):
        return extract_text_from_pdf(file)
    elif file.name.endswith(".docx"):
        return extract_text_from_docx(file)
    else:
        return ""

# Extract potential skills from Job Description
def extract_keywords_from_jd(jd_text):
    doc = nlp(jd_text.lower())
    skills = set()
    for chunk in doc.noun_chunks:
        phrase = chunk.text.strip()
        if 1 <= len(phrase.split()) <= 3:
            skills.add(phrase)
    return list(skills)

# Extract skills from resume based on JD
def extract_info(resume_text, jd_skills):
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    patterns = [nlp.make_doc(skill) for skill in jd_skills]
    matcher.add("SKILLS", patterns)

    doc = nlp(resume_text.lower())
    matches = matcher(doc)
    found_skills = set([doc[start:end].text for match_id, start, end in matches])
    return sorted(found_skills)

# Rank resumes based on JD and matched skills
def rank_resumes(resume_dicts, jd_text):
    jd_embedding = model.encode(jd_text, convert_to_tensor=True)
    jd_skills = extract_keywords_from_jd(jd_text)
    total_jd_skills = len(jd_skills)

    ranking = []
    for resume in resume_dicts:
        resume_embedding = model.encode(resume['text'], convert_to_tensor=True)
        semantic_similarity = util.cos_sim(jd_embedding, resume_embedding).item()

        matched_skills = extract_info(resume['text'], jd_skills)
        matched_count = len(matched_skills)

        skill_score = matched_count / total_jd_skills if total_jd_skills > 0 else 0
        final_score = round(0.7 * semantic_similarity + 0.3 * skill_score, 2)

        ranking.append({
            'Name': resume['name'],
            'Matched Skills': ", ".join(matched_skills),
            'Semantic Similarity': round(semantic_similarity, 2),
            'Skill Match Ratio': round(skill_score, 2),
            'Final Score': final_score
        })

    return sorted(ranking, key=lambda x: x['Final Score'], reverse=True)

# Run Screening
if st.button("Run Screening"):
    if not jd_input:
        st.warning("Please enter a job description above.")
    elif not uploaded_files:
        st.warning("Please upload at least one resume.")
    else:
        resume_dicts = []
        for file in uploaded_files:
            text = extract_text(file)
            resume_dicts.append({
                'name': file.name,
                'text': text
            })

        results = rank_resumes(resume_dicts, jd_input)
        df = pd.DataFrame(results)
        st.dataframe(df)

        #export
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Results as CSV", csv, "ranked_resumes.csv", "text/csv")