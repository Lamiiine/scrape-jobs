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

# Read the current README content
with open("README.md", "r") as f:
    content = f.read()

# Define the section to update
start_marker = "<!-- visa-sponsorship-jobs-start -->"
end_marker = "<!-- visa-sponsorship-jobs-end -->"

# Generate the markdown table with the jobs
job_table = """
| Job Title       | Company | Location       | Visa Sponsorship |
|-----------------|---------|----------------|------------------|
""" + "\n".join(
    f"| {job['title']} | {job['company']} | {job['location']} | {'Yes' if 'visa' in job['description'].lower() else 'No'} |"
    for job in jobs
)

# Update the section in the README
new_content = content.split(start_marker)[0] + start_marker + "\n" + job_table + "\n" + end_marker + content.split(end_marker)[1]

# Write the updated content back to README.md
with open("README.md", "w") as f:
    f.write(new_content)

