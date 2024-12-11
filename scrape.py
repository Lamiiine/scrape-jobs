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

# Generate the new job listings section
new_section = []
new_section.append("<!-- START OF JOB LISTINGS -->")
new_section.append("# Visa Sponsorship Jobs at Monzo")
new_section.append(f"Updated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
new_section.append("| Title | Location | Apply Link | Visa Sponsorship |")
new_section.append("|-------|----------|------------|------------------|")

for title, location, apply_link, visa_support in job_data:
    new_section.append(f"| {title} | {location} | [Apply]({apply_link}) | {visa_support} |")

new_section.append("<!-- END OF JOB LISTINGS -->")

# Read the existing README.md
with open("README.md", "r") as file:
    content = file.read()

# Replace the old section with the new section
start_marker = "<!-- START OF JOB LISTINGS -->"
end_marker = "<!-- END OF JOB LISTINGS -->"

start_index = content.find(start_marker)
end_index = content.find(end_marker) + len(end_marker)

if start_index != -1 and end_index != -1:
    updated_content = content[:start_index] + "\n".join(new_section) + content[end_index:]
else:
    # If markers are not found, append the new section at the end
    updated_content = content + "\n" + "\n".join(new_section)

# Write the updated content back to README.md
with open("README.md", "w") as file:
    file.write(updated_content)
