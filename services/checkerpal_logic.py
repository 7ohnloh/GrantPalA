import os
import requests
import json
import re
import mimetypes
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from database import get_db

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

MAX_TEXT_CHARS = 12000  # Stay under token limits for GPT

def extract_text_from_file(file):
    content_type, _ = mimetypes.guess_type(file.filename)

    if content_type == "application/pdf":
        print("📄 Extracting text from PDF...")
        reader = PdfReader(file)
        text = "\n".join([page.extract_text() or "" for page in reader.pages])
    else:
        print("📄 Reading as plain text...")
        text = file.read().decode("utf-8", errors="ignore")

    return text

def extract_grant_info(file=None, url=None, mode="grant"):
    if not file and not url:
        raise ValueError("No input provided")

    # Get text from file or URL
    if file:
        text = extract_text_from_file(file)
    else:
        print("🌐 Scraping URL:", url)
        html = requests.get(url, timeout=5).text
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator="\n")

    print(f"📏 Original text length: {len(text)} characters")

    # Trim to safe length
    if len(text) > MAX_TEXT_CHARS:
        print(f"✂️ Trimming to {MAX_TEXT_CHARS} characters to stay within token limits")
        text = text[:MAX_TEXT_CHARS]

    # Updated prompts
    if mode == "project":
        prompt = f"""
You are a helpful assistant for extracting structured data from project proposals submitted for community grant funding.

Here is the full project proposal text:

[START PROJECT TEXT]
{text}
[END PROJECT TEXT]

From this, extract and return a valid JSON object with the following keys:
- project_name: The title of the project.
- project_description: A short summary (2–4 sentences) of what the project aims to do.
- timeline: The intended duration or dates of the project.
- budget: The estimated total cost or requested budget (SGD).
- key_objectives: A list of the project’s main objectives or planned activities.
- key_directions: A list of strategic themes or goals this project aligns with (e.g. digital literacy, pandemic support, elderly outreach).
- target_beneficiaries: Groups or individuals that the project benefits (e.g., seniors in rental flats).
- volunteer_roles: What kinds of roles and responsibilities volunteers will have.
- partnerships: Any partner organizations or collaborators mentioned.
- justification: The reason this project was proposed; the background problem or community need.
- evaluation_methods: Metrics or methods used to track the project's success.

Respond only with a valid JSON object. If information is not found, return an empty string or empty array for that key.
"""
    else:
        prompt = f"""
You are a helpful assistant that extracts structured grant information from webpages or PDFs.

Given the following grant page content:

[START GRANT TEXT]
{text}
[END GRANT TEXT]

Extract and return a valid JSON object with the following keys:
- grant_name: The full name of the grant.
- grant_description: A 2–4 sentence summary of what the grant is about, including its purpose and target outcomes.
- timeline_condition: Any restrictions or expectations regarding project duration or start/end dates.
- eligible_applicants: Who can apply (e.g., individuals, nonprofits, students, citizen groups).
- budget_policy: Any rules or caps on funding, such as maximum amount or funding structure.
- key_directions: A list of strategic priorities or themes the grant supports (e.g., elderly care, digital inclusion).
- expenses_allowed: Types of expenses that are covered (e.g., logistics, materials, venue rental).
- expenses_disallowed: Types of expenses that are NOT covered (e.g., staff salaries, overseas travel).
- selection_criteria: The evaluation or selection criteria used to decide on successful applications.
- supporting_documents_required: A list of application documents or information the applicant needs to submit.

Be as detailed and accurate as possible. If some fields are not found in the text, return an empty string or array for those keys.

Respond only with a valid JSON object.
"""

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": "gpt-3.5-turbo",
        "temperature": 0,
        "messages": [{"role": "user", "content": prompt}]
    }

    print("📤 Sending request to OpenAI...")
    res = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=body)

    try:
        res_json = res.json()
        print("✅ Raw OpenAI response received.")
        content = res_json['choices'][0]['message']['content']

        # Attempt to extract valid JSON using regex
        json_str_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_str_match:
            parsed = json.loads(json_str_match.group())
            print("🧾 JSON Extracted:", json.dumps(parsed, indent=2))

            if mode == "grant":
                save_grant_to_db(parsed, url)

            return parsed
        else:
            raise ValueError("No valid JSON found in response.")

    except Exception as e:
        print("❌ Error during OpenAI API call or parsing:", str(e))
        raise ValueError("Failed to process OpenAI response.")

def save_grant_to_db(grant_json, source_url=None):
    db = get_db()

    def safe_str(value):
        if isinstance(value, (dict, list)):
            return json.dumps(value)
        return str(value)

    name = safe_str(grant_json.get("grant_name", "Unnamed Grant"))
    timeline = safe_str(grant_json.get("timeline_condition", ""))
    applicants = safe_str(grant_json.get("eligible_applicants", ""))
    budget = safe_str(grant_json.get("budget_policy", ""))

    db.execute('''
        INSERT INTO grants (name, timeline, applicants, budget, source_url)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        name,
        timeline,
        applicants,
        budget,
        source_url or ""
    ))

    db.commit()
