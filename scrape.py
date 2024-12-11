import requests
from datetime import datetime

# Define the company job board token
board_token = 'monzo'

# API endpoint with content parameter set to true
url = f'https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true'

# Make the GET request to the API
response = requests.get(url)
jobs = response.json()

# Phrase to identify visa sponsorship
visa_phrase = "We can sponsor visas"

# Collect job data for Markdown
job_data = []

for job in jobs['jobs']:
    title = job.get('title', 'N/A')
    location = job.get('location', {}).get('name', 'N/A')
    description = job.get('content', 'No description available')
    apply_link = job.get('absolute_url', 'No apply link available')

    # Check for the exact visa sponsorship phrase in the description
    if visa_phrase.lower() in description.lower():
        visa_support = "✅"
        job_data.append((title, location, apply_link, visa_support))

# Write results to a Markdown file
with open("visa_sponsorship_jobs_new.md", "w") as f:
    # Write header
    f.write("# Visa Sponsorship Jobs at Monzo\n")
    f.write(f"Updated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    f.write("| Title | Location | Apply Link | Visa Sponsorship |\n")
    f.write("|-------|----------|------------|-------------------|\n")

    # Write job entries
    for title, location, apply_link, visa_support in job_data:
        f.write(f"| {title} | {location} | [Apply]({apply_link}) | {visa_support} |\n")
