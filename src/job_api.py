from apify_client import ApifyClient
import os
import requests
from dotenv import load_dotenv
load_dotenv()

apify_client = ApifyClient(os.getenv("APIFY_API_TOKEN"))
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")


def fetch_jsearch_jobs(search_query, location="USA", num_results=20):
    """Fetch jobs from JSearch API (LinkedIn, Indeed, Glassdoor aggregator)"""
    url = "https://jsearch.p.rapidapi.com/search"

    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "jsearch.p.rapidapi.com"
    }

    params = {
        "query": f"{search_query} in {location}",
        "page": "1",
        "num_pages": "1",
        "date_posted": "month"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])[:num_results]
    except Exception as e:
        print(f"JSearch error: {e}")
        return []

# Fetch LinkedIn jobs based on search query and location
def fetch_linkedin_jobs(search_query, location = "india", rows=60):
    run_input = {
            "title": search_query,
            "location": location,
            "rows": rows,
            "proxy": {
                "useApifyProxy": True,
                "apifyProxyGroups": ["RESIDENTIAL"],
            }
        }
    run = apify_client.actor("BHzefUZlZRKWxkTck").call(run_input=run_input)
    jobs = list(apify_client.dataset(run["defaultDatasetId"]).iterate_items())
    return jobs


# Fetch Naukri jobs based on search query and location
def fetch_naukri_jobs(search_query, location = "india", rows=60):
    run_input = {
        "keyword": search_query,
        "maxJobs": 60,
        "freshness": "all",
        "sortBy": "relevance",
        "experience": "all",
    }
    run = apify_client.actor("alpcnRV9YI9lYVPWk").call(run_input=run_input)
    jobs = list(apify_client.dataset(run["defaultDatasetId"]).iterate_items())
    return jobs
