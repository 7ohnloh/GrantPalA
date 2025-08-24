from flask import request, jsonify
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_text(file_storage):
    filename = file_storage.filename.lower()
    if filename.endswith(".txt"):
        return file_storage.read().decode("utf-8")
    elif filename.endswith(".pdf"):
        from PyPDF2 import PdfReader
        reader = PdfReader(file_storage.stream)
        return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    elif filename.endswith(".docx"):
        import docx
        doc = docx.Document(file_storage.stream)
        return "\n".join([para.text for para in doc.paragraphs])
    else:
        return ""

def generate_answers(questions_text, proposal_text):
    questions = [q.strip() for q in questions_text.split("\n") if q.strip()]
    combined_prompt = f"The following is a project proposal:\n{proposal_text}\n\nPlease answer each of the following grant application questions in a professional tone, based on the proposal:\n"

    responses = []
    for q in questions:
        prompt = combined_prompt + f"\nQuestion: {q}\nAnswer:"
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )
        answer = response.choices[0].message.content.strip()
        responses.append({"question": q, "answer": answer})
    return responses

def handle_generate():
    if 'questions' not in request.files or 'proposal' not in request.files:
        return jsonify({"error": "Missing files"}), 400

    questions_file = request.files['questions']
    proposal_file = request.files['proposal']

    questions_text = extract_text(questions_file)
    proposal_text = extract_text(proposal_file)

    if not questions_text or not proposal_text:
        return jsonify({"error": "Empty or unsupported file types"}), 400

    try:
        answers = generate_answers(questions_text, proposal_text)
        return jsonify({
            "answers": answers,
            "proposal": proposal_text
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def handle_regenerate():
    if request.method == "OPTIONS":
        return '', 200

    data = request.get_json()
    question = data.get("question")
    proposal = data.get("proposal")

    if not question or not proposal:
        return jsonify({"error": "Missing question or proposal"}), 400

    try:
        prompt = f"The following is a project proposal:\n{proposal}\n\nPlease answer the following grant question in a professional tone:\nQuestion: {question}\nAnswer:"
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )
        answer = response.choices[0].message.content.strip()
        return jsonify({"answer": answer})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
