from mcp.server.fastmcp import FastMCP
from src.job_api import fetch_jsearch_jobs
from src.llm_provider import get_completion

mcp = FastMCP("Job Recommender")


@mcp.tool()
async def analyze_resume(resume_text: str) -> dict:
    """Analyze a resume and return summary, skill gaps, and career roadmap"""
    summary = get_completion(
        f"Summarize this resume highlighting skills, education, and experience. Be concise:\n\n{resume_text}",
        max_tokens=400
    )
    gaps = get_completion(
        f"List 3-5 missing skills or certifications needed for better job opportunities:\n\n{resume_text}",
        max_tokens=300
    )
    roadmap = get_completion(
        f"Suggest a brief career roadmap (skills to learn, certifications, next steps):\n\n{resume_text}",
        max_tokens=300
    )
    return {
        "summary": summary,
        "skill_gaps": gaps,
        "roadmap": roadmap
    }


@mcp.tool()
async def search_jobs(keywords: str, location: str = "USA", num_results: int = 10) -> list:
    """Search for jobs using keywords and location"""
    jobs = fetch_jsearch_jobs(keywords, location=location, num_results=num_results)
    return [
        {
            "title": job.get("job_title"),
            "company": job.get("employer_name"),
            "location": f"{job.get('job_city', 'N/A')}, {job.get('job_state', '')}",
            "link": job.get("job_apply_link")
        }
        for job in jobs
    ]


@mcp.tool()
async def get_job_keywords(resume_summary: str) -> str:
    """Extract job search keywords from a resume summary"""
    keywords = get_completion(
        f"Based on this resume summary, suggest 3 best job titles for searching. Comma-separated list only:\n\n{resume_summary}",
        max_tokens=50
    )
    return keywords.strip()


if __name__ == "__main__":
    mcp.run(transport='stdio')
