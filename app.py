import streamlit as st
from src.helper import extract_text_from_pdf, ask_llm
from src.job_api import fetch_jsearch_jobs

st.set_page_config(page_title="Job Recommender", layout="wide")
st.title("📄AI Job Recommender")
st.markdown("Upload your resume and get job recommendations based on your skills and experience.")

uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

if uploaded_file:
    with st.spinner("Extracting text from your resume..."):
        resume_text = extract_text_from_pdf(uploaded_file)

    with st.spinner("Summarizing your resume..."):
        summary = ask_llm(f"Summarize this resume highlighting the skills, edcucation, and experience: \n\n{resume_text}", max_tokens=500)


    with st.spinner("Finding skill Gaps..."):
        gaps = ask_llm(f"Analyze this resume and highlight missing skills, certifications, and experiences needed for better job opportunities: \n\n{resume_text}", max_tokens=400)


    with st.spinner("Creating Future Roadmap..."):
        roadmap = ask_llm(f"Based on this resume, suggest a future roadmap to improve this person's career prospects (Skill to learn, certification needed, industry exposure): \n\n{resume_text}", max_tokens=400)

    # Display nicely formatted results
    st.markdown("---")
    st.header("📑 Resume Summary")
    st.markdown(f"<div style='background-color: #000000; padding: 15px; border-radius: 10px; font-size:16px; color:white;'>{summary}</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.header("🛠️ Skill Gaps & Missing Areas")
    st.markdown(f"<div style='background-color: #000000; padding: 15px; border-radius: 10px; font-size:16px; color:white;'>{gaps}</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.header("🚀 Future Roadmap & Preparation Strategy")
    st.markdown(f"<div style='background-color: #000000; padding: 15px; border-radius: 10px; font-size:16px; color:white;'>{roadmap}</div>", unsafe_allow_html=True)

    st.success("✅ Analysis Completed Successfully!")


    if st.button("🔎Get Job Recommendations"):
        with st.spinner("Fetching job recommendations..."):
            keywords = ask_llm(
                f"Based on this resume summary, suggest the best job titles and keywords for searching jobs. Give a comma-separated list only, no explanation.\n\nSummary: {summary}",
                max_tokens=100
            )

            search_keywords_clean = keywords.replace("\n", "").strip()
            # Use first 3 keywords for better search results
            top_keywords = ", ".join(search_keywords_clean.split(",")[:3])

        st.success(f"Extracted Job Keywords: {search_keywords_clean}")
        st.info(f"Searching for: {top_keywords}")

        with st.spinner("Fetching US jobs from LinkedIn, Indeed, Glassdoor..."):
            jobs = fetch_jsearch_jobs(top_keywords, location="USA", num_results=20)

        st.markdown("---")
        st.header("💼 Top US Jobs")

        if jobs:
            for job in jobs:
                st.markdown(f"**{job.get('job_title')}** at *{job.get('employer_name')}*")
                st.markdown(f"- 📍 {job.get('job_city', 'N/A')}, {job.get('job_state', '')}")
                st.markdown(f"- 🔗 [Apply Here]({job.get('job_apply_link')})")
                st.markdown("---")
        else:
            st.warning("No US jobs found.")
