from flask import Flask, jsonify, render_template, request, redirect, session, url_for, flash, send_file
import os
from database import insert_user, insert_request, add_exam,fetch_alerts, tounix,fetch_exams, fetch_request, is_valid, delete_request, get_time, updated, fetch_teacher,reset_connection, add_alert
from one_more_sql_connection import get_sql_connection
from block import store_hash, retrieve_hash
import random
from flask_cors import CORS
import time

connection = get_sql_connection()
app = Flask(__name__)
CORS(app)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    role = request.form['role']
    username = request.form['username']
    password = request.form['password']

    if is_valid(connection, username, role, password):
        print("user is valid")
        session['username'] = username
        if role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif role == 'teacher':
            return redirect(url_for('teacher_dashboard', username=username))
        elif role == 'superintendent':
            return redirect(url_for('superintendent_dashboard'))
    else:
        flash('Invalid credentials. Please try again.')
        return render_template('index.html')

@app.route('/create_exam',methods=['POST'])
def create_exam():
    try:
        subject_name = request.json['subjectName']
        subject_code = request.json['subjectCode']
        add_exam(connection,subjectCode=subject_code, subjectName= subject_name)
        flash("Exam added successfully!")
    except Exception as e:
        flash(f'Error adding user: {e}')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin_dashboard')
def admin_dashboard():
    exams = fetch_exams(connection)
    # print(exams)
    alerts = fetch_alerts(connection)
    # print(alerts)
    return render_template('admin_dashboard.html', exams = exams, alerts=alerts)

@app.route('/submit_paper', methods=['POST'])
def submit_paper():
    try:
        teacher_id = request.form['teacherId']
        paper_code = request.form['examSelect']
        release_date = request.form['releaseDate']

        print(teacher_id)
        print(paper_code)
        print(release_date)
        
        release_date = tounix(release_date)
        insert_request(connection, paper_code, release_date, teacher_id)
        flash('Question Paper Submitted Successfully!')
    except Exception as e:
        flash(f'Error submitting paper: {e}')
    return redirect(url_for('admin_dashboard'))

@app.route('/add_user', methods=['POST'])
def add_user():
    try:
        user_id = request.form['userId']
        password = request.form['password']
        role = request.form['role']
        insert_user(connection, user_id, role, password)
        flash(f'User {user_id} with role {role} added successfully!')
    except Exception as e:
        flash(f'Error adding user: {e}')
    return redirect(url_for('admin_dashboard'))

@app.route('/teacher_dashboard/')
def teacher_dashboard():
    username = request.args.get('username')  # Get username from query parameters
    if not username:
        flash('Username is required.')
        return redirect(url_for('index'))  # Redirect to login or another appropriate page
    
    # Fetch requests for the teacher
    teacher_requests = fetch_request(connection, username)
    return render_template('teacher_dashboard.html', requests=teacher_requests, username=username)

@app.route('/upload', methods=['POST'])
def upload_file():
    data = request.get_json()
    print(data)

    username = data.get("username")
    req_id = data.get("request_id")
    updated(connection, user_id=username, exam_id=req_id)
    hashcode = data.get("hash")  
    print(f"This is the hash generated after storing in ipfs: {hashcode}")
    release_time = get_time(connection, req_id)
    print('datetime: ', release_time)
    store_hash(req_id,release_time , hashcode, username)
    print("hash stored")  

    flash(f'PDF for request {req_id} uploaded successfully!')
    return redirect(url_for('teacher_dashboard', username=username))
    
    # return redirect(url_for('teacher_dashboard', username=username))

@app.route('/superintendent_dashboard')
def superintendent_dashboard():
    return render_template('superintendent_dashboard.html')

@app.route('/fetch_pdf/<unique_code>')
def fetch_pdf(unique_code):
    try:
        # Fetch teachers associated with the unique code
        teacher_list = fetch_teacher(connection, unique_code)
        print("teachers",teacher_list)
        # Check if any teachers are associated with the code
        if teacher_list == []:
            flash('No teachers found for the given code.')
            return jsonify({"error": "Teacher not found."}), 400
            exam_id = unique_code
    
        teacher_id = teacher_list[0]
    
        if len(teacher_list) > 1:
            # Randomly select a teacher from the list
            teacher_id = random.choice(teacher_list)
            teacher_list.remove(teacher_id)
            # Delete all requests for this unique code
            for i in teacher_list:
                delete_request(connection, unique_code, i)

        # Retrieve hash for the given code and teacher
        result, isReleased = retrieve_hash(unique_code, teacher_id,int(time.time()))
        print("hash", result)
        print(isReleased)
        username = session['username']
        print(username)

        # Additional check for invalid result
        # if result == "":
        #     flash('Invalid unique code. The paper does not exist')
        #     return jsonify({"error": "Invalid code."}), 400
        if result=="None":
            
            add_alert(connection, username,  unique_code)
            flash('The paper does not exist')
            return jsonify({"error": "Paper not released yet."}), 400 
        
        if isReleased == False:
            add_alert(connection, username, unique_code)
            flash('The paper has not been released yet')
            return jsonify({"error": "Paper not released yet."}), 400

        # Check if the hash indicates the paper is ready
        if result != "None":
            # filename = f'{unique_code}.pdf'
            # file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # # Check if the file exists on the server
            # if os.path.exists(file_path):
            #     flash('Question paper downloaded successfully!')
            #     return send_file(file_path, as_attachment=True)
            
            # # File not found on server
            # flash('Question paper file not found on the server.')
            return jsonify({"file_hash": result}), 200
        else:
            # Paper not yet released
            flash('Invalid unique code. The paper does not exist')
            return jsonify({"error": "Invalid code."}), 400
    
    except Exception as e:
        # Log the full error for server-side debugging
        app.logger.error(f'Error fetching PDF: {e}', exc_info=True)
        flash(f'An unexpected error occurred. Please try again later.')
        return "An error occurred.", 500

if __name__ == '__main__':
    app.run(debug=True, port=8001)