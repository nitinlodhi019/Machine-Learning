# app.py (main Flask application file)
from flask import Flask, request, jsonify
from flask_cors import CORS  # For handling CORS if frontend and backend are on different ports
import os
import json

# Import your NLP processing modules
from text_extractor import extract_text_from_file
from text_processor import preprocess_text, \
    extract_skills_from_text  # Corrected: extract_skills_from_text from text_processor
from resume_matcher import calculate_match_score  # Corrected: only calculate_match_score from resume_matcher

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# --- Database (Placeholder - replace with actual DB integration) ---
# In a real app, use SQLAlchemy (for SQL) or PyMongo (for MongoDB)
# For simplicity, we'll use in-memory dictionaries for demonstration
users_db = {}
job_requirements_db = {}
resumes_db = {}  # Stores processed resume data
screening_results_db = {}

# --- Configuration ---
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# --- Helper Functions (for demo) ---
def generate_id():
    import uuid
    return str(uuid.uuid4())


# --- API Endpoints ---

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    # In a real app, you'd generate and send a real OTP here
    # For demo, we'll just simulate sending and expect a fixed OTP for verification

    if email not in users_db:
        users_db[email] = {'otp': '123456', 'role': None, 'logged_in': False}  # Demo OTP
        print(f"Demo OTP for {email}: 123456")  # Log for testing
        return jsonify({"message": "OTP sent (demo: 123456)"}), 200

    # If user already exists, just resend/confirm OTP
    return jsonify({"message": "OTP re-sent (demo: 123456)"}), 200


@app.route('/api/verify_otp', methods=['POST'])
def verify_otp():
    data = request.json
    email = data.get('email')
    otp = data.get('otp')

    if email not in users_db or users_db[email]['otp'] != otp:
        return jsonify({"message": "Invalid OTP"}), 401

    users_db[email]['logged_in'] = True
    return jsonify({"message": "Login successful", "user_id": email}), 200


@app.route('/api/select_role', methods=['POST'])
def select_role():
    data = request.json
    user_id = data.get('user_id')  # Assuming user_id is passed after login
    role = data.get('role')

    if user_id in users_db:
        users_db[user_id]['role'] = role
        return jsonify({"message": f"Role '{role}' selected for {user_id}"}), 200
    return jsonify({"message": "User not found"}), 404


@app.route('/api/job_requirements', methods=['POST'])
def save_job_requirements():
    data = request.json
    user_id = data.get('user_id')  # Associate with user
    job_description = data.get('job_description')
    department = data.get('department')
    skills = data.get('skills')

    job_id = generate_id()
    job_requirements_db[job_id] = {
        'user_id': user_id,
        'job_description': job_description,
        'department': department,
        'skills': skills
    }
    return jsonify({"message": "Job requirements saved", "job_id": job_id}), 201


@app.route('/api/upload_resumes', methods=['POST'])
def upload_resumes():
    if 'files' not in request.files:
        return jsonify({"message": "No file part"}), 400

    files = request.files.getlist('files')
    uploaded_resume_ids = []

    for file in files:
        if file.filename == '':
            continue

        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # --- NLP: Text Extraction & Preprocessing ---
        raw_text = extract_text_from_file(filepath)
        processed_text = preprocess_text(raw_text)

        # --- NLP: Optional Information Extraction (e.g., skills) ---
        # This is a simplified example; a real system would use more robust NER/IE
        extracted_skills = extract_skills_from_text(processed_text)

        resume_id = generate_id()
        resumes_db[resume_id] = {
            'filename': filename,
            'raw_text': raw_text,
            'processed_text': processed_text,
            'extracted_skills': extracted_skills  # Store extracted skills
        }
        uploaded_resume_ids.append(resume_id)

    return jsonify({"message": "Resumes uploaded and processed", "resume_ids": uploaded_resume_ids}), 200


@app.route('/api/screen_resumes', methods=['POST'])
def screen_resumes():
    data = request.json
    job_id = data.get('job_id')
    resume_ids = data.get('resume_ids')  # List of resume IDs to screen

    if job_id not in job_requirements_db:
        return jsonify({"message": "Job requirements not found"}), 404

    job_req = job_requirements_db[job_id]
    job_description_text = job_req['job_description']
    required_skills = job_req['skills']
    required_department = job_req['department']

    results = []
    for resume_id in resume_ids:
        if resume_id not in resumes_db:
            continue

        resume_data = resumes_db[resume_id]
        resume_processed_text = resume_data['processed_text']
        resume_extracted_skills = resume_data['extracted_skills']  # Use extracted skills

        # --- NLP: Calculate Match Score ---
        # This function will implement TF-IDF, Cosine Similarity, Skill Matching etc.
        match_score, matched_skills = calculate_match_score(
            job_description_text,
            required_skills,
            resume_processed_text,
            resume_extracted_skills
        )

        # Simulate department matching (can be more sophisticated)
        # For demo, if department is selected, give a small boost if it's mentioned in resume text
        department_match_factor = 1.0
        if required_department and required_department.lower() in resume_processed_text.lower():
            department_match_factor = 1.05  # Small boost for department match

        final_score = int(match_score * department_match_factor)  # Adjust score based on department

        screening_results_db[resume_id] = {
            'job_id': job_id,
            'resume_id': resume_id,
            'filename': resume_data['filename'],
            'match_score': final_score,
            'matched_skills': matched_skills,
            'department': required_department  # Store the required department for display
        }
        results.append(screening_results_db[resume_id])

    return jsonify({"message": "Screening complete", "results": results}), 200


@app.route('/api/dashboard_data', methods=['GET'])
def get_dashboard_data():
    # In a real app, filter by user_id and job_id
    # For demo, return all results
    results = list(screening_results_db.values())

    sort_by = request.args.get('sort_by', 'score')  # Default sort by score
    if sort_by == 'score':
        results.sort(key=lambda x: x['match_score'], reverse=True)
    elif sort_by == 'name':
        results.sort(key=lambda x: x['filename'])  # Sort by filename as a proxy for name

    # Frontend expects 'name' and 'department' fields
    formatted_results = []
    for res in results:
        formatted_results.append({
            'id': res['resume_id'],
            'name': res['filename'].split('.')[0],  # Use filename as name
            'matchScore': res['match_score'],
            'matchedSkills': res['matched_skills'],
            'department': res.get('department', 'N/A'),  # Use department from job req or infer
            'shortlisted': False  # Shortlisting handled on frontend for this demo
        })

    return jsonify(formatted_results), 200


@app.route('/api/resume_raw_text/<resume_id>', methods=['GET'])
def get_resume_raw_text(resume_id):
    if resume_id in resumes_db:
        return jsonify({"raw_text": resumes_db[resume_id]['raw_text']}), 200
    return jsonify({"message": "Resume not found"}), 404


if __name__ == '__main__':
    app.run(debug=True, port=5000)

