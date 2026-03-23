import pdfplumber
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Comprehensive list of skills to look for
SKILL_KEYWORDS = [
    "python", "django", "flask", "react", "nextjs", "javascript", 
    "typescript", "node", "docker", "kubernetes", "postgresql", 
    "mysql", "mongodb", "aws", "azure", "git", "linux", "html", "css",
    "java", "c++", "ruby", "php", "swift", "sql", "rest api", "fastapi"
]

def extract_text(pdf_path):
    """Extracts digital text from PDF."""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + " "
        # Clean up extra spaces and newlines
        text = re.sub(r'\s+', ' ', text).strip()
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text

def score_resume(resume_path, job_description):
    resume_text = extract_text(resume_path).lower()
    job_desc = job_description.lower() if job_description else ""
    
    if not resume_text:
        return 1.0  # Base score if PDF is unreadable/empty

    # 1. Identify skills present in the Job Description
    required_skills = [s for s in SKILL_KEYWORDS if re.search(r"\b" + re.escape(s) + r"\b", job_desc)]
    
    # 2. Identify skills present in the Resume
    candidate_skills = [s for s in SKILL_KEYWORDS if re.search(r"\b" + re.escape(s) + r"\b", resume_text)]
    
    # 3. Calculate Skill Match Score (out of 10)
    if not required_skills:
        # If no specific skills found in JD, score based on general resume strength
        skill_score = min(len(candidate_skills), 5) 
    else:
        # Count how many required skills the candidate actually has
        matches = set(required_skills).intersection(set(candidate_skills))
        skill_score = (len(matches) / len(required_skills)) * 10

    # 4. Semantic Similarity (Bonus check using TF-IDF)
    # This checks if the general context of the resume matches the JD
    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        vectors = vectorizer.fit_transform([resume_text, job_desc])
        semantic_sim = cosine_similarity(vectors[0], vectors[1])[0][0]
    except:
        semantic_sim = 0

    # Weighted Final Score: 70% Skill Match, 30% Context/Semantic Match
    final_score = (skill_score * 0.7) + (semantic_sim * 10 * 0.3)
    
    return round(min(max(final_score, 1.0), 10.0), 1)

def extract_skills(text):
    """Returns a list of matching skills for display."""
    if not text: return []
    text = text.lower()
    found = [s.capitalize() for s in SKILL_KEYWORDS if re.search(r"\b" + re.escape(s) + r"\b", text)]
    return sorted(list(set(found)))