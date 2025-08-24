# GrantPal

GrantPal is an AI-enabled web application that simplifies the grant application process.  
It was developed as part of the 60.004 Service Design Studio module in SUTD’s Design and Artificial Intelligence programme.

---

## 🚀 Features

- **CheckerPal**  
  Upload a grant document or link, extract structured information, and compare it against your project for eligibility.

- **EligibilityPal**  
  Upload project details, run automatic checks, and see if your project aligns with grant requirements.

- **AnswerPal**  
  Generate suggested answers for grant application forms using AI. Edit answers directly and export them as Word documents.

- **TrackerPal (planned)**  
  Calendar + project management integration with Google Calendar API.

---

## 🛠️ Tech Stack

- **Backend**: Python (Flask), SQLite  
- **Frontend**: HTML/CSS, Jinja templates, React (AnswerPal UI)  
- **APIs**: OpenAI API (summarisation, text generation), Google Calendar API  
- **Deployment**: Render (Flask backend), Vercel/Netlify (optional frontend)

---


## 🛠️ How to Run Locally

1. **Install dependencies**
   Make sure you have Python 3.11+ and install required packages:

   ```bash
   pip install -r requirements.txt
   ```

2. **Add API key and account to `.env`**
   Create a `.env` file in the project root with the following entries (replace with your actual values):

   ```env
   OPENAI_API_KEY=your_api_key_here
   OPENAI_API_BASE64_ACCOUNT=your_base64_account_here
   ```

3. **Run the Flask app**

   ```bash
   python app.py
   ```

   Then open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

---

## 📂 Testing the Features

We’ve included sample documents in the `testdocuments/` folder so you can try out GrantPal immediately:

### ✅ CheckerPal

1. In **Step 1 (Upload Grant)**, paste this URL:
   [https://www.temasekfoundation.org.sg/OSCAR](https://www.temasekfoundation.org.sg/OSCAR)
2. In **Step 2 (Upload Project)**, upload:
   `testdocuments/CareBridge_Project_Proposal.pdf`

This will let you see how CheckerPal extracts and compares grant/project info.

### ✅ AnswerPal

1. Upload grant questions:
   `testdocuments/sample_questions.pdf`
2. Upload project proposal:
   `testdocuments/sample_proposal.docx`

This will generate draft answers to the uploaded questions.







