"""
Job Recommender API Server
Flask backend for Render deployment
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from src.helper import extract_text_from_pdf, ask_llm
from src.job_api import fetch_jsearch_jobs
from io import BytesIO

app = Flask(__name__, static_folder='static')
CORS(app)


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "job-recommender"})


@app.route('/analyze', methods=['POST'])
def analyze_resume():
    """Analyze resume and return summary, gaps, roadmap"""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    try:
        # Extract text from PDF
        file_stream = BytesIO(file.read())
        file_stream.name = file.filename

        import fitz
        doc = fitz.open(stream=file_stream.read(), filetype="pdf")
        resume_text = ""
        for page in doc:
            resume_text += page.get_text()

        if not resume_text.strip():
            return jsonify({"error": "Could not extract text from PDF"}), 400

        # Get AI analysis
        summary = ask_llm(
            f"Summarize this resume highlighting the skills, education, and experience. Be concise:\n\n{resume_text}",
            max_tokens=400
        )

        gaps = ask_llm(
            f"Analyze this resume and list 3-5 missing skills or certifications needed for better job opportunities. Be specific:\n\n{resume_text}",
            max_tokens=300
        )

        roadmap = ask_llm(
            f"Based on this resume, suggest a brief career roadmap (skills to learn, certifications, next steps). Be actionable:\n\n{resume_text}",
            max_tokens=300
        )

        return jsonify({
            "success": True,
            "summary": summary,
            "gaps": gaps,
            "roadmap": roadmap,
            "resume_text": resume_text[:500] + "..."  # Preview
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/jobs', methods=['POST'])
def get_jobs():
    """Get job recommendations based on resume"""
    data = request.json
    resume_text = data.get('resume_text', '')
    summary = data.get('summary', '')

    if not summary and not resume_text:
        return jsonify({"error": "No resume data provided"}), 400

    try:
        # Extract job keywords
        keywords = ask_llm(
            f"Based on this resume summary, suggest the best 3 job titles for searching. Give comma-separated list only, no explanation:\n\n{summary}",
            max_tokens=50
        )

        search_query = keywords.replace("\n", "").strip()
        top_keywords = ", ".join(search_query.split(",")[:3])

        # Fetch jobs
        jobs = fetch_jsearch_jobs(top_keywords, location="USA", num_results=15)

        # Format jobs for response
        formatted_jobs = []
        for job in jobs:
            formatted_jobs.append({
                "title": job.get("job_title", "N/A"),
                "company": job.get("employer_name", "N/A"),
                "location": f"{job.get('job_city', 'N/A')}, {job.get('job_state', '')}",
                "link": job.get("job_apply_link", "#"),
                "type": job.get("job_employment_type", "N/A")
            })

        return jsonify({
            "success": True,
            "keywords": top_keywords,
            "jobs": formatted_jobs
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
