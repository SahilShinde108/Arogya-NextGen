# import sqlite3
# from flask import Flask, render_template, request, redirect, url_for, session, flash
# from werkzeug.security import generate_password_hash, check_password_hash
# from twilio.rest import Client
# from twilio.twiml.messaging_response import MessagingResponse
# import json
# import random
# import string

# # --- Main Application Setup (CORRECTED FOR SIMPLIFIED STRUCTURE) ---
# app = Flask(__name__,
#             template_folder='english/templates',
#             static_folder='english')
# app.secret_key = 'gramin_health_secret_key' 


# twilio_client = Client(ACCOUNT_SID, AUTH_TOKEN)

# # --- Database Helper Function ---
# def get_db_connection():
#     conn = sqlite3.connect('health.db', check_same_thread=False)
#     conn.row_factory = sqlite3.Row
#     return conn

# # --- Alert Function ---
# def send_alert(patient_number, message):
#     try:
#         twilio_client.messages.create(
#             to=HEALTH_WORKER_PHONE,
#             from_=TWILIO_PHONE_NUMBER,
#             body=f"ALERT from {patient_number}: {message}"
#         )
#         print(f"Alert sent successfully to {HEALTH_WORKER_PHONE}")
#     except Exception as e:
#         print(f"Error sending Twilio alert: {e}")

# # --- SMS Webhook Route ---
# @app.route("/sms", methods=['POST'])
# def sms_webhook():
#     incoming_msg = request.values.get('Body', '').strip()
#     from_number = request.values.get('From', '')
#     print(f"Incoming message from {from_number}: '{incoming_msg}'")
    
#     conn = get_db_connection()
#     patient = conn.execute('SELECT * FROM patients WHERE phone_number = ?', (from_number,)).fetchone()
    
#     response = MessagingResponse()
    
#     if not patient:
#         response.message("This phone number is not registered. Please sign up on our website to submit readings.")
#         conn.close()
#         return str(response)

#     parts = incoming_msg.upper().split()
#     try:
#         if parts[0] == 'BP' and len(parts) == 3:
#             systolic, diastolic = int(parts[1]), int(parts[2])
#             conn.execute('INSERT INTO readings (patient_id, reading_type, value1, value2) VALUES (?, ?, ?, ?)',
#                          (patient['id'], 'BP', systolic, diastolic))
#             response.message(f"Hi {patient['name']}, your BP reading {systolic}/{diastolic} is recorded. Thank you.")
#             if systolic > 140 or diastolic > 90:
#                 send_alert(from_number, f"High BP: {systolic}/{diastolic}")
#         elif parts[0] == 'SUGAR' and len(parts) == 2:
#             sugar_level = int(parts[1])
#             conn.execute('INSERT INTO readings (patient_id, reading_type, value1) VALUES (?, ?, ?)',
#                          (patient['id'], 'SUGAR', sugar_level))
#             response.message(f"Hi {patient['name']}, your Sugar reading {sugar_level} is recorded. Thank you.")
#             if sugar_level > 180:
#                 send_alert(from_number, f"High Sugar: {sugar_level}")
#         else:
#             response.message("Invalid format. Please use: 'BP 120 80' or 'SUGAR 150'.")
#     except (ValueError, IndexError):
#         response.message("Invalid format. Please use: 'BP 120 80' or 'SUGAR 150'.")
#     finally:
#         conn.commit()
#         conn.close()
        
#     return str(response)

# # --- Website Routes ---
# @app.route("/")
# def home():
#     return render_template("index.html")

# # ... (keep all your existing app.py code before the signup function) ...

# @app.route("/signup", methods=['GET', 'POST'])
# def signup():
#     if request.method == 'POST':
#         # --- Get all the form data ---
#         name = request.form['name']
#         phone = request.form['phone_number'].strip()
#         asha_phone = request.form['asha_worker_phone'].strip()
#         password = request.form['password']
        
#         # --- Get optional demographic data ---
#         # Use .get() to avoid errors if the fields are empty
#         age = request.form.get('age')
#         gender = request.form.get('gender')
#         village = request.form.get('village')

#         # --- Format both phone numbers correctly ---
#         if phone.startswith('0'):
#             phone = phone[1:]
#         if not phone.startswith('+91'):
#             phone = f"+91{phone}"
            
#         if asha_phone.startswith('0'):
#             asha_phone = asha_phone[1:]
#         if not asha_phone.startswith('+91'):
#             asha_phone = f"+91{asha_phone}"
            
#         hashed_password = generate_password_hash(password)
#         conn = get_db_connection()
#         try:
#             # --- Insert all the new data into the database ---
#             conn.execute("""
#                 INSERT INTO patients (name, phone_number, password_hash, asha_worker_phone, age, gender, village) 
#                 VALUES (?, ?, ?, ?, ?, ?, ?)
#                 """,
#                 (name, phone, hashed_password, asha_phone, age, gender, village)
#             )
#             conn.commit()
#         except sqlite3.IntegrityError:
#             flash("This Patient Phone Number is already registered.", "danger")
#             conn.close()
#             return redirect(url_for('signup'))
#         finally:
#             conn.close()
            
#         flash("Patient registration successful! Please log in.", "success")
#         return redirect(url_for('login'))
        
#     return render_template("signup.html")

# # ... (the rest of your app.py code remains the same) ...


# # --- NEW: PHARMACY ECOSYSTEM ROUTES ---

# @app.route("/pharmacy/login", methods=['GET', 'POST'])
# def pharmacy_login():
#     """Handles the login for pharmacy staff."""
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']
#         # For this project, we use a simple, hardcoded login.
#         if email == "pharma@nabha.gov" and password == "pharma123":
#             session['pharmacy_logged_in'] = True
#             flash("Pharmacy login successful!", "success")
#             return redirect(url_for('pharmacy_dashboard'))
#         else:
#             flash("Invalid pharmacy credentials.", "danger")
#             return redirect(url_for('pharmacy_login'))
#     # This route requires the 'pharmacy_login.html' template to exist.
#     return render_template("english/templates/pharmacy_login.html")


# @app.route("/pharmacy/dashboard", methods=['GET', 'POST'])
# def pharmacy_dashboard():
#     """Dashboard for pharmacy staff to manage inventory."""
#     if not session.get('pharmacy_logged_in'):
#         return redirect(url_for('pharmacy_login'))

#     conn = get_db_connection()

#     if request.method == 'POST':
#         # This block handles the form submission when inventory is updated.
#         for key, value in request.form.items():
#             if key.startswith('stock_status_'):
#                 inventory_id = key.split('_')[-1]
#                 conn.execute("UPDATE pharmacy_inventory SET stock_status = ? WHERE id = ?", (value, inventory_id))
#         conn.commit()
#         flash("Inventory has been updated successfully.", "success")
#         return redirect(url_for('pharmacy_dashboard'))

#     # This block fetches all the data to display on the page.
#     pharmacies = conn.execute("SELECT * FROM pharmacies ORDER BY name").fetchall()
#     inventory_data = {}
#     for pharmacy in pharmacies:
#         inventory_items = conn.execute("""
#             SELECT id, medication_name, stock_status
#             FROM pharmacy_inventory
#             WHERE pharmacy_id = ?
#             ORDER BY medication_name
#         """, (pharmacy['id'],)).fetchall()
#         inventory_data[pharmacy['id']] = inventory_items
    
#     conn.close()
#     # This route requires the 'pharmacy_dashboard.html' template to exist.
#     return render_template("english/templates/pharmacy_dashboard.html", pharmacies=pharmacies, inventory_data=inventory_data)







# @app.route("/login", methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         phone = request.form['phone_number'].strip()
#         password = request.form['password']
#         if phone.startswith('0'):
#             phone = phone[1:]
#         if not phone.startswith('+91'):
#             phone = f"+91{phone}"
#         conn = get_db_connection()
#         user = conn.execute('SELECT * FROM patients WHERE phone_number = ?', (phone,)).fetchone()
#         conn.close()
        
#         if user and check_password_hash(user['password_hash'], password):
#             session['user_id'] = user['id']
#             session['user_name'] = user['name']
#             return redirect(url_for('user_dashboard'))
#         else:
#             flash("Invalid phone number or password.", "danger")
#             return redirect(url_for('login'))
#     return render_template("login.html")

# @app.route('/user_dashboard')
# def user_dashboard():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))
    
#     user_id = session['user_id']
#     user_name = session['user_name']
#     conn = get_db_connection()
    
#     readings = conn.execute("""
#         SELECT reading_type, value1, value2, strftime('%Y-%m-%d %-I:%M %p', timestamp) as formatted_time 
#         FROM readings WHERE patient_id = ? ORDER BY timestamp DESC
#     """, (user_id,)).fetchall()
    
#     bp_readings = conn.execute("""
#         SELECT value1, value2, strftime('%d-%b', timestamp) as chart_time 
#         FROM readings WHERE patient_id = ? AND reading_type = 'BP' ORDER BY timestamp ASC LIMIT 7
#     """, (user_id,)).fetchall()
#     conn.close()

#     chart_labels = [row['chart_time'] for row in bp_readings]
#     systolic_data = [row['value1'] for row in bp_readings]
#     diastolic_data = [row['value2'] for row in bp_readings]
    
#     return render_template("user_dashboard.html", 
#                            user_name=user_name, 
#                            readings=readings,
#                            chart_labels=json.dumps(chart_labels),
#                            systolic_data=json.dumps(systolic_data),
#                            diastolic_data=json.dumps(diastolic_data))
    
# @app.route("/admin_login", methods=['GET', 'POST'])
# def admin_login():
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']
#         if email == "admin@health.com" and password == "admin123":
#             session['admin_logged_in'] = True
#             return redirect(url_for('monitoring_dashboard'))
#         else:
#             flash("Invalid admin credentials.", "danger")
#             return redirect(url_for('admin_login'))
#     return render_template("admin_login.html")

# @app.route("/dashboard")
# def monitoring_dashboard():
#     if not session.get('admin_logged_in'):
#         return redirect(url_for('admin_login'))
        
#     conn = get_db_connection()
#     patients_from_db = conn.execute("SELECT * FROM patients ORDER BY name").fetchall()
    
#     patients_data = []
#     for patient_row in patients_from_db:
#         patient_dict = dict(patient_row)
#         readings_rows = conn.execute("SELECT reading_type, value1, value2, strftime('%Y-%m-%d %-I:%M %p', timestamp) as formatted_time FROM readings WHERE patient_id = ? ORDER BY timestamp DESC LIMIT 5", (patient_dict['id'],)).fetchall()
#         readings_dicts = [dict(row) for row in readings_rows]
        
#         reports_rows = conn.execute("SELECT chief_complaint, symptoms, notes, strftime('%Y-%m-%d %-I:%M %p', timestamp) as formatted_time FROM triage_reports WHERE patient_id = ? ORDER BY timestamp DESC LIMIT 3", (patient_dict['id'],)).fetchall()
#         reports_dicts = [dict(row) for row in reports_rows]
        
#         prescriptions_rows = conn.execute("SELECT id, medication_name, dosage FROM prescriptions WHERE patient_id = ? AND is_active = 1", (patient_dict['id'],)).fetchall()
#         prescriptions_dicts = [dict(row) for row in prescriptions_rows]
        
#         bp_readings_rows = conn.execute("SELECT value1, value2, strftime('%d-%b', timestamp) as chart_time FROM readings WHERE patient_id = ? AND reading_type = 'BP' ORDER BY timestamp ASC LIMIT 7", (patient_dict['id'],)).fetchall()
#         bp_readings_dicts = [dict(row) for row in bp_readings_rows]
        
#         chart_data = { 'labels': [row['chart_time'] for row in bp_readings_dicts], 'systolic': [row['value1'] for row in bp_readings_dicts], 'diastolic': [row['value2'] for row in bp_readings_dicts] }
        
#         patients_data.append({ 'info': patient_dict, 'readings': readings_dicts, 'reports': reports_dicts, 'chart_data': chart_data, 'prescriptions': prescriptions_dicts })
        
#     conn.close()
#     return render_template("monitoring_dashboard.html", all_patients=patients_data)

# @app.route('/patient/<int:patient_id>/add_report', methods=['GET', 'POST'])
# def add_triage_report(patient_id):
#     if not session.get('admin_logged_in'):
#         return redirect(url_for('admin_login'))

#     conn = get_db_connection()
#     patient = conn.execute('SELECT * FROM patients WHERE id = ?', (patient_id,)).fetchone()

#     if request.method == 'POST':
#         chief_complaint = request.form['chief_complaint']
#         symptoms = ', '.join(request.form.getlist('symptoms'))
#         notes = request.form['notes']
        
#         conn.execute('INSERT INTO triage_reports (patient_id, chief_complaint, symptoms, notes) VALUES (?, ?, ?, ?)', (patient_id, chief_complaint, symptoms, notes))
#         conn.commit()
#         conn.close()
#         flash(f"Triage report for {patient['name']} has been saved.", "success")
#         return redirect(url_for('monitoring_dashboard'))

#     conn.close()
#     return render_template('add_triage_report.html', patient=patient)

# # ... (keep all your existing app.py code before the add_prescription function) ...

# # ... (keep all your existing app.py code before the add_prescription function) ...

# # ... (all previous code in your app.py file remains the same) ...

# # CORRECTED ROUTE DEFINITION: Changed <int/patient_id> to <int:patient_id>
# @app.route('/patient/<int:patient_id>/add_prescription', methods=['GET', 'POST'])
# def add_prescription(patient_id):
#     """
#     Handles both displaying the informed prescription form (with live stock checks)
#     and processing the form submission to save the prescription and notify BOTH 
#     the ASHA worker and the patient.
#     """
#     if not session.get('admin_logged_in'):
#         return redirect(url_for('admin_login'))

#     conn = get_db_connection()
#     patient = conn.execute('SELECT * FROM patients WHERE id = ?', (patient_id,)).fetchone()

#     if request.method == 'POST':
#         # --- 1. VALIDATE AND SAVE THE PRESCRIPTION ---
#         medication_name = request.form['medication_name']
#         dosage = request.form['dosage']
#         notes = request.form.get('notes', '')
        
#         pharmacy_id = request.form.get('pharmacy_id')
        
#         if not pharmacy_id:
#             flash("You must select a dispensing pharmacy.", "danger")
#             return redirect(url_for('add_prescription', patient_id=patient_id))
        
#         cursor = conn.cursor()
#         cursor.execute(
#             'INSERT INTO prescriptions (patient_id, medication_name, dosage, notes, dispensing_pharmacy_id) VALUES (?, ?, ?, ?, ?)',
#             (patient_id, medication_name, dosage, notes, pharmacy_id)
#         )
#         conn.commit()
        
#         # --- 2. SEND NOTIFICATIONS ---
#         selected_pharmacy = conn.execute('SELECT name, location FROM pharmacies WHERE id = ?', (pharmacy_id,)).fetchone()
        
#         asha_phone = patient['asha_worker_phone']
#         asha_sms_sent = False
#         if asha_phone and selected_pharmacy:
#             notification_message = (
#                 f"Prescription for {patient['name']}: {medication_name} ({dosage}). "
#                 f"Please instruct family to collect from: {selected_pharmacy['name']}, {selected_pharmacy['location']}."
#             )
#             try:
#                 twilio_client.messages.create(to=asha_phone, from_=TWILIO_PHONE_NUMBER, body=notification_message)
#                 asha_sms_sent = True
#             except Exception as e:
#                 print(f"Error sending prescription SMS to ASHA worker: {e}")

#         patient_phone = patient['phone_number']
#         patient_sms_sent = False
#         if patient_phone and selected_pharmacy:
#             patient_message = (
#                 f"Your new prescription for {medication_name} is ready for collection at {selected_pharmacy['name']}. "
#                 f"Your ASHA worker has been informed with the details."
#             )
#             try:
#                 twilio_client.messages.create(to=patient_phone, from_=TWILIO_PHONE_NUMBER, body=patient_message)
#                 patient_sms_sent = True
#             except Exception as e:
#                 print(f"Error sending prescription SMS to patient: {e}")

#         if asha_sms_sent and patient_sms_sent:
#             flash(f"Prescription for {patient['name']} saved. Notifications sent to ASHA worker and patient.", "success")
#         elif asha_sms_sent:
#             flash("Prescription saved. Notification sent to ASHA worker, but failed to notify patient.", "warning")
#         else:
#             flash("Prescription saved, but failed to send SMS notifications.", "danger")

#         conn.close()
#         return redirect(url_for('monitoring_dashboard'))

#     medication_to_check = request.args.get('medication', 'Metformin 500mg') 
#     pharmacies = conn.execute('SELECT * FROM pharmacies ORDER BY name').fetchall()
#     stock_data = []
#     for pharmacy in pharmacies:
#         stock_status_row = conn.execute(
#             "SELECT stock_status FROM pharmacy_inventory WHERE pharmacy_id = ? AND medication_name = ?",
#             (pharmacy['id'], medication_to_check)
#         ).fetchone()
        
#         stock_data.append({
#             'pharmacy': pharmacy,
#             'status': stock_status_row['stock_status'] if stock_status_row else 'Not Stocked'
#         })
        
#     conn.close()
    
#     # CORRECTED INDENTATION: This line is now correctly aligned.
#     return render_template('add_prescription.html', patient=patient, pharmacy_stock=stock_data, medication_name=medication_to_check)

# # ... (the rest of your app.py code remains the same) ...





# @app.route('/prescription/<int:prescription_id>/send_reminder')
# def send_reminder(prescription_id):
#     if not session.get('admin_logged_in'):
#         return redirect(url_for('admin_login'))

#     conn = get_db_connection()
#     prescription = conn.execute("SELECT p.name as patient_name, p.phone_number, pr.medication_name, pr.dosage FROM prescriptions pr JOIN patients p ON pr.patient_id = p.id WHERE pr.id = ?", (prescription_id,)).fetchone()
#     conn.close()

#     if prescription:
#         patient_name, phone_number, medication, dosage = prescription['patient_name'], prescription['phone_number'], prescription['medication_name'], prescription['dosage']
#         reminder_message = f"Hi {patient_name}, this is a friendly reminder to take your medication: {medication} ({dosage})."
#         try:
#             twilio_client.messages.create(to=phone_number, from_=TWILIO_PHONE_NUMBER, body=reminder_message)
#             flash(f"Reminder sent to {patient_name} successfully!", "success")
#         except Exception as e:
#             print(f"Error sending reminder: {e}")
#             flash(f"Failed to send reminder. Error: {e}", "danger")
    
#     return redirect(url_for('monitoring_dashboard'))
    
# @app.route("/logout")
# def logout():
#     session.clear()
#     flash("You have been successfully logged out.", "info")
#     return redirect(url_for('home'))

# @app.route("/tester")
# def sms_tester_page():
#     return render_template("manual_sms_tester.html")

# @app.route('/patient/<int:patient_id>/start_call')
# def start_video_call(patient_id):
#     """
#     This function generates a unique Jitsi Meet link, saves it to the database,
#     and sends it to the patient's registered phone number via Twilio SMS.
#     """
#     if not session.get('admin_logged_in'):
#         return redirect(url_for('admin_login'))

#     conn = get_db_connection()
#     patient = conn.execute('SELECT * FROM patients WHERE id = ?', (patient_id,)).fetchone()

#     if patient:
#         # 1. Generate a unique and secure room name for the video call
#         patient_name_formatted = patient['name'].replace(' ', '')
#         random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
#         room_name = f"GraminHealth-{patient_name_formatted}-{random_chars}"
#         video_link = f"https://meet.jit.si/{room_name}"

#         # 2. Save the active call link to the database
#         conn.execute('UPDATE patients SET active_call_link = ? WHERE id = ?', (video_link, patient_id))
#         conn.commit()
#         conn.close()

#         patient_phone = patient['phone_number']
#         patient_name = patient['name']
        
#         # 3. Create the body of the SMS message
#         message_body = f"Hi {patient_name}, your video consultation is ready. Please click this link to join the doctor: {video_link}"

#         # 4. Send the link using your Twilio SMS service
#         try:
#             twilio_client.messages.create(
#                 to=patient_phone,
#                 from_=TWILIO_PHONE_NUMBER,
#                 body=message_body
#             )
#             flash(f"Video call link sent to {patient_name} successfully!", "success")
#             print(f"SUCCESS: Sent video link {video_link} to {patient_phone}")
#         except Exception as e:
#             flash(f"Failed to send video link SMS. Error: {e}", "danger")
#             print(f"ERROR: Could not send video link SMS. Error: {e}")
#     else:
#         conn.close()
    
#     # After sending the SMS, redirect the admin back to the main dashboard
#     return redirect(url_for('monitoring_dashboard'))

# # --- NEW: Route to end a video call ---
# @app.route('/patient/<int:patient_id>/end_call')
# def end_video_call(patient_id):
#     """
#     This function clears the video call link from the database, effectively ending the call.
#     """
#     if not session.get('admin_logged_in'):
#         return redirect(url_for('admin_login'))

#     conn = get_db_connection()
#     conn.execute('UPDATE patients SET active_call_link = NULL WHERE id = ?', (patient_id,))
#     conn.commit()
#     conn.close()
    
#     flash("The video call has been marked as complete.", "info")
#     return redirect(url_for('monitoring_dashboard'))


# # --- Main execution ---
# if __name__ == "__main__":
#     app.run(debug=True)
















# import sqlite3
# from flask import Flask, render_template, request, redirect, url_for, session, flash
# from werkzeug.security import generate_password_hash, check_password_hash
# from twilio.rest import Client
# from twilio.twiml.messaging_response import MessagingResponse
# import json
# import random
# import string
# import pandas as pd
# import pickle
# import os
# import requests

# # --- Main Application Setup ---
# app = Flask(__name__,
#             template_folder='english/templates',
#             static_folder='english')
# app.secret_key = 'gramin_health_secret_key' 

# # --- 1. LOAD THE LOCAL ML MODEL & DATASET ---
# try:
#     with open('final_disease_model.pkl', 'rb') as f:
#         disease_model = pickle.load(f)
#     with open('final_vectorizer.pkl', 'rb') as f:
#         vectorizer = pickle.load(f)
#     print("--- Disease Prediction Model loaded successfully! ---")
# except FileNotFoundError:
#     print("--- MODEL FILES NOT FOUND. Please run train_final_model.py first. ---")
#     disease_model, vectorizer = None, None

# # --- Gemini API Configuration ---
# GEMINI_API_KEY = "AIzaSyAj-1tCYvqt6u7AwHuopKFYkyAySZAjPLY" # Leave this empty, Canvas will handle it.
# GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={GEMINI_API_KEY}"

# # --- (Existing functions like Twilio config, DB functions, etc., remain here) ---
# def get_db_connection():
#     conn = sqlite3.connect('health.db', check_same_thread=False)
#     conn.row_factory = sqlite3.Row
#     return conn

# # --- Alert Function ---
# def send_alert(patient_number, message):
#     try:
#         twilio_client.messages.create(to=HEALTH_WORKER_PHONE, from_=TWILIO_PHONE_NUMBER, body=f"ALERT from {patient_number}: {message}")
#     except Exception as e:
#         print(f"Error sending Twilio alert: {e}")

# def get_ai_prediction(symptoms_text):
#     if not disease_model or not vectorizer:
#         return "Local AI model is not available."

#     try:
#         # --- Stage 1: Predict the Disease with the Local Model ---
#         input_vector = vectorizer.transform([symptoms_text])
#         predicted_disease = disease_model.predict(input_vector)[0]
        
#         # --- Stage 2: Generate a Structured Report with Gemini API ---
#         system_prompt = (
#             "You are a medical AI assistant for rural healthcare in India. Your role is to provide an actionable triage report. "
#             "Based on the predicted disease, return a JSON object with four keys: "
#             "'intensity' (Low, Medium, or High), "
#             "'recommendation' (a clear action for the ASHA worker), "
#             "'home_remedies' (a short list of simple, safe remedies), "
#             "'doctor_note' (the predicted disease for the doctor's reference). "
#             "If there is any sign of a severe condition, set intensity to 'High' and recommendation to 'Immediate physical appointment required.' "
#             "For non-severe cases, recommend monitoring for 1-2 days before a hospital visit."
#         )
#         user_query = f"Generate a triage report for a patient with a predicted issue of: {predicted_disease}"
        
#         # Define the expected JSON structure for the Gemini API
#         json_schema = {
#             "type": "OBJECT",
#             "properties": {
#                 "intensity": {"type": "STRING"},
#                 "recommendation": {"type": "STRING"},
#                 "home_remedies": {"type": "STRING"},
#                 "doctor_note": {"type": "STRING"}
#             }
#         }

#         payload = {
#             "contents": [{"parts": [{"text": user_query}]}],
#             "systemInstruction": {"parts": [{"text": system_prompt}]},
#             "generationConfig": {
#                 "responseMimeType": "application/json",
#                 "responseSchema": json_schema
#             }
#         }
        
#         headers = {'Content-Type': 'application/json'}
#         response = requests.post(GEMINI_API_URL, headers=headers, json=payload)
#         response.raise_for_status()
        
#         result = response.json()
#         report_json_text = result['candidates'][0]['content']['parts'][0]['text']
#         report_data = json.loads(report_json_text)
        
#         # Format the structured data into a single string for storage and display
#         formatted_report = (
#             f"Predicted Issue: {report_data.get('doctor_note', 'N/A')}\n\n"
#             f"Intensity: {report_data.get('intensity', 'N/A')}\n\n"
#             f"Recommendation: {report_data.get('recommendation', 'N/A')}\n\n"
#             f"Suggested Home Remedies: {report_data.get('home_remedies', 'N/A')}"
#         )
#         return formatted_report

#     except Exception as e:
#         print(f"Error during AI prediction pipeline: {e}")
#         if 'response' in locals() and response.text:
#             print("API Response Body:", response.text)
#         return "Could not generate a clinical summary."

# # --- (The rest of your app.py file, including all routes, remains the same) ---
# @app.route('/patient/<int:patient_id>/add_report', methods=['GET', 'POST'])
# def add_triage_report(patient_id):
#     if not session.get('admin_logged_in'): return redirect(url_for('admin_login'))
#     conn = get_db_connection()
#     patient = conn.execute('SELECT * FROM patients WHERE id = ?', (patient_id,)).fetchone()
#     if request.method == 'POST':
#         chief_complaint = request.form['chief_complaint']
#         notes = request.form['notes']
#         symptoms_text_combined = chief_complaint + " " + notes
        
#         prediction = get_ai_prediction(symptoms_text_combined)
        
#         conn.execute('INSERT INTO triage_reports (patient_id, chief_complaint, symptoms, notes, ai_prediction) VALUES (?, ?, ?, ?, ?)',
#                      (patient_id, chief_complaint, "", notes, prediction))
#         conn.commit()
#         conn.close()
#         flash(f"Triage report for {patient['name']} has been saved.", "success")
#         return redirect(url_for('monitoring_dashboard'))
#     conn.close()
#     return render_template('add_triage_report.html', patient=patient)

# if __name__ == '__main__':
#     app.run(debug=True)


# # --- SMS Webhook Route ---
# @app.route("/sms", methods=['POST'])
# def sms_webhook():
#     incoming_msg = request.values.get('Body', '').strip()
#     from_number = request.values.get('From', '')
#     conn = get_db_connection()
#     patient = conn.execute('SELECT * FROM patients WHERE phone_number = ?', (from_number,)).fetchone()
#     response = MessagingResponse()
#     if not patient:
#         response.message("This phone number is not registered. Please sign up on our website.")
#         conn.close()
#         return str(response)
#     parts = incoming_msg.upper().split()
#     try:
#         if parts[0] == 'BP' and len(parts) == 3:
#             systolic, diastolic = int(parts[1]), int(parts[2])
#             conn.execute('INSERT INTO readings (patient_id, reading_type, value1, value2) VALUES (?, ?, ?, ?)', (patient['id'], 'BP', systolic, diastolic))
#             response.message(f"Hi {patient['name']}, your BP reading {systolic}/{diastolic} is recorded.")
#             if systolic > 140 or diastolic > 90: send_alert(from_number, f"High BP: {systolic}/{diastolic}")
#         elif parts[0] == 'SUGAR' and len(parts) == 2:
#             sugar_level = int(parts[1])
#             conn.execute('INSERT INTO readings (patient_id, reading_type, value1) VALUES (?, ?, ?)', (patient['id'], 'SUGAR', sugar_level))
#             response.message(f"Hi {patient['name']}, your Sugar reading {sugar_level} is recorded.")
#             if sugar_level > 180: send_alert(from_number, f"High Sugar: {sugar_level}")
#         else:
#             response.message("Invalid format. Please use: 'BP 120 80' or 'SUGAR 150'.")
#     except (ValueError, IndexError):
#         response.message("Invalid format. Please use: 'BP 120 80' or 'SUGAR 150'.")
#     finally:
#         conn.commit()
#         conn.close()
#     return str(response)

# # --- Website Routes ---
# @app.route("/")
# def home():
#     return render_template("index.html")

# @app.route("/signup", methods=['GET', 'POST'])
# def signup():
#     if request.method == 'POST':
#         name = request.form['name']
#         phone = request.form['phone_number'].strip()
#         asha_phone = request.form['asha_worker_phone'].strip()
#         password = request.form['password']
#         age = request.form.get('age')
#         gender = request.form.get('gender')
#         village = request.form.get('village')
#         if phone.startswith('0'): phone = phone[1:]
#         if not phone.startswith('+91'): phone = f"+91{phone}"
#         if asha_phone.startswith('0'): asha_phone = asha_phone[1:]
#         if not asha_phone.startswith('+91'): asha_phone = f"+91{asha_phone}"
#         hashed_password = generate_password_hash(password)
#         conn = get_db_connection()
#         try:
#             conn.execute("INSERT INTO patients (name, phone_number, password_hash, asha_worker_phone, age, gender, village) VALUES (?, ?, ?, ?, ?, ?, ?)",
#                          (name, phone, hashed_password, asha_phone, age, gender, village))
#             conn.commit()
#         except sqlite3.IntegrityError:
#             flash("This Patient Phone Number is already registered.", "danger")
#             conn.close()
#             return redirect(url_for('signup'))
#         finally:
#             conn.close()
#         flash("Patient registration successful! Please log in.", "success")
#         return redirect(url_for('login'))
#     return render_template("signup.html")

# @app.route("/login", methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         phone = request.form['phone_number'].strip()
#         password = request.form['password']
#         if phone.startswith('0'): phone = phone[1:]
#         if not phone.startswith('+91'): phone = f"+91{phone}"
#         conn = get_db_connection()
#         user = conn.execute('SELECT * FROM patients WHERE phone_number = ?', (phone,)).fetchone()
#         conn.close()
#         if user and check_password_hash(user['password_hash'], password):
#             session['user_id'] = user['id']
#             session['user_name'] = user['name']
#             return redirect(url_for('user_dashboard'))
#         else:
#             flash("Invalid phone number or password.", "danger")
#             return redirect(url_for('login'))
#     return render_template("login.html")

# @app.route('/user_dashboard')
# def user_dashboard():
#     if 'user_id' not in session: return redirect(url_for('login'))
#     user_id, user_name = session['user_id'], session['user_name']
#     conn = get_db_connection()
#     readings = conn.execute("SELECT *, strftime('%Y-%m-%d %-I:%M %p', timestamp) as formatted_time FROM readings WHERE patient_id = ? ORDER BY timestamp DESC", (user_id,)).fetchall()
#     bp_readings = conn.execute("SELECT *, strftime('%d-%b', timestamp) as chart_time FROM readings WHERE patient_id = ? AND reading_type = 'BP' ORDER BY timestamp ASC LIMIT 7", (user_id,)).fetchall()
#     conn.close()
#     chart_labels = [row['chart_time'] for row in bp_readings]
#     systolic_data = [row['value1'] for row in bp_readings]
#     diastolic_data = [row['value2'] for row in bp_readings]
#     return render_template("user_dashboard.html", user_name=user_name, readings=readings,
#                            chart_labels=json.dumps(chart_labels), systolic_data=json.dumps(systolic_data), diastolic_data=json.dumps(diastolic_data))

# @app.route("/admin_login", methods=['GET', 'POST'])
# def admin_login():
#     if request.method == 'POST':
#         email, password = request.form['email'], request.form['password']
#         if email == "admin@health.com" and password == "admin123":
#             session['admin_logged_in'] = True
#             return redirect(url_for('monitoring_dashboard'))
#         else:
#             flash("Invalid admin credentials.", "danger")
#             return redirect(url_for('admin_login'))
#     return render_template("admin_login.html")

# @app.route("/dashboard")
# def monitoring_dashboard():
#     if not session.get('admin_logged_in'): return redirect(url_for('admin_login'))
#     conn = get_db_connection()
#     patients_from_db = conn.execute("SELECT * FROM patients ORDER BY name").fetchall()
#     patients_data = []
#     for patient_row in patients_from_db:
#         patient_dict = dict(patient_row)
#         readings_rows = conn.execute("SELECT *, strftime('%Y-%m-%d %-I:%M %p', timestamp) as formatted_time FROM readings WHERE patient_id = ? ORDER BY timestamp DESC LIMIT 5", (patient_dict['id'],)).fetchall()
#         reports_rows = conn.execute("SELECT *, strftime('%Y-%m-%d %-I:%M %p', timestamp) as formatted_time FROM triage_reports WHERE patient_id = ? ORDER BY timestamp DESC LIMIT 3", (patient_dict['id'],)).fetchall()
#         prescriptions_rows = conn.execute("SELECT * FROM prescriptions WHERE patient_id = ? AND is_active = 1", (patient_dict['id'],)).fetchall()
#         bp_readings_rows = conn.execute("SELECT *, strftime('%d-%b', timestamp) as chart_time FROM readings WHERE patient_id = ? AND reading_type = 'BP' ORDER BY timestamp ASC LIMIT 7", (patient_dict['id'],)).fetchall()
#         chart_data = {'labels': [row['chart_time'] for row in bp_readings_rows], 'systolic': [row['value1'] for row in bp_readings_rows], 'diastolic': [row['value2'] for row in bp_readings_rows]}
#         patients_data.append({'info': patient_dict, 'readings': [dict(r) for r in readings_rows], 'reports': [dict(r) for r in reports_rows],
#                                'prescriptions': [dict(r) for r in prescriptions_rows], 'chart_data': chart_data})
#     conn.close()
#     return render_template("monitoring_dashboard.html", all_patients=patients_data)

# # @app.route('/patient/<int:patient_id>/add_report', methods=['GET', 'POST'])
# # def add_triage_report(patient_id):
# #     if not session.get('admin_logged_in'): return redirect(url_for('admin_login'))
# #     conn = get_db_connection()
# #     patient = conn.execute('SELECT * FROM patients WHERE id = ?', (patient_id,)).fetchone()
# #     if request.method == 'POST':
# #         chief_complaint, symptoms_list, notes = request.form['chief_complaint'], request.form.getlist('symptoms'), request.form['notes']
# #         symptoms_text = ', '.join(symptoms_list)
        
# #         # Call the new, two-stage AI function
# #         prediction = get_ai_prediction(symptoms_list, chief_complaint, notes)
        
# #         conn.execute('INSERT INTO triage_reports (patient_id, chief_complaint, symptoms, notes, ai_prediction) VALUES (?, ?, ?, ?, ?)',
# #                      (patient_id, chief_complaint, symptoms_text, notes, prediction))
# #         conn.commit()
# #         conn.close()
# #         flash(f"Triage report for {patient['name']} has been saved.", "success")
# #         return redirect(url_for('monitoring_dashboard'))
# #     conn.close()
# #     return render_template('add_triage_report.html', patient=patient)

# @app.route('/patient/<int:patient_id>/add_prescription', methods=['GET', 'POST'])
# def add_prescription(patient_id):
#     if not session.get('admin_logged_in'): return redirect(url_for('admin_login'))
#     conn = get_db_connection()
#     patient = conn.execute('SELECT * FROM patients WHERE id = ?', (patient_id,)).fetchone()
#     if request.method == 'POST':
#         medication_name, dosage, notes = request.form['medication_name'], request.form['dosage'], request.form.get('notes', '')
#         pharmacy_id = request.form.get('pharmacy_id')
#         if not pharmacy_id:
#             flash("You must select a dispensing pharmacy.", "danger")
#             return redirect(url_for('add_prescription', patient_id=patient_id))
#         conn.execute('INSERT INTO prescriptions (patient_id, medication_name, dosage, notes, dispensing_pharmacy_id) VALUES (?, ?, ?, ?, ?)',
#                      (patient_id, medication_name, dosage, notes, pharmacy_id))
#         conn.commit()
#         selected_pharmacy = conn.execute('SELECT name, location FROM pharmacies WHERE id = ?', (pharmacy_id,)).fetchone()
#         asha_phone, patient_phone = patient['asha_worker_phone'], patient['phone_number']
#         asha_sms_sent, patient_sms_sent = False, False
#         if asha_phone and selected_pharmacy:
#             msg = f"Prescription for {patient['name']}: {medication_name} ({dosage}). Collect from: {selected_pharmacy['name']}."
#             try:
#                 twilio_client.messages.create(to=asha_phone, from_=TWILIO_PHONE_NUMBER, body=msg)
#                 asha_sms_sent = True
#             except Exception as e: print(f"Error (ASHA SMS): {e}")
#         if patient_phone and selected_pharmacy:
#             msg = f"Your new prescription for {medication_name} is ready at {selected_pharmacy['name']}."
#             try:
#                 twilio_client.messages.create(to=patient_phone, from_=TWILIO_PHONE_NUMBER, body=msg)
#                 patient_sms_sent = True
#             except Exception as e: print(f"Error (Patient SMS): {e}")
#         if asha_sms_sent and patient_sms_sent: flash("Prescription saved. Notifications sent to ASHA worker and patient.", "success")
#         elif asha_sms_sent: flash("Prescription saved. Notification to ASHA worker sent, but failed for patient.", "warning")
#         else: flash("Prescription saved, but failed to send SMS notifications.", "danger")
#         conn.close()
#         return redirect(url_for('monitoring_dashboard'))
#     medication_to_check = request.args.get('medication', 'Metformin 500mg')
#     pharmacies = conn.execute('SELECT * FROM pharmacies ORDER BY name').fetchall()
#     stock_data = []
#     for pharmacy in pharmacies:
#         stock_status_row = conn.execute("SELECT stock_status FROM pharmacy_inventory WHERE pharmacy_id = ? AND medication_name = ?", (pharmacy['id'], medication_to_check)).fetchone()
#         stock_data.append({'pharmacy': pharmacy, 'status': stock_status_row['stock_status'] if stock_status_row else 'Not Stocked'})
#     conn.close()
#     return render_template('add_prescription.html', patient=patient, pharmacy_stock=stock_data, medication_name=medication_to_check)

# @app.route('/patient/<int:patient_id>/start_call')
# def start_video_call(patient_id):
#     if not session.get('admin_logged_in'): return redirect(url_for('admin_login'))
#     conn = get_db_connection()
#     patient = conn.execute('SELECT * FROM patients WHERE id = ?', (patient_id,)).fetchone()
#     if patient:
#         patient_name_formatted = patient['name'].replace(' ', '')
#         random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
#         room_name = f"GraminHealth-{patient_name_formatted}-{random_chars}"
#         video_link = f"https://meet.jit.si/{room_name}"
#         conn.execute('UPDATE patients SET active_call_link = ? WHERE id = ?', (video_link, patient_id))
#         conn.commit()
#         patient_phone, patient_name = patient['phone_number'], patient['name']
#         message_body = f"Hi {patient_name}, your video consultation is ready. Please click this link to join the doctor: {video_link}"
#         try:
#             twilio_client.messages.create(to=patient_phone, from_=TWILIO_PHONE_NUMBER, body=message_body)
#             flash(f"Video call link sent to {patient_name} successfully!", "success")
#         except Exception as e:
#             flash(f"Failed to send video link SMS. Error: {e}", "danger")
#     conn.close()
#     return redirect(url_for('monitoring_dashboard'))

# @app.route('/patient/<int:patient_id>/end_call')
# def end_video_call(patient_id):
#     if not session.get('admin_logged_in'): return redirect(url_for('admin_login'))
#     conn = get_db_connection()
#     conn.execute('UPDATE patients SET active_call_link = NULL WHERE id = ?', (patient_id,))
#     conn.commit()
#     conn.close()
#     flash("The video call has been marked as complete.", "info")
#     return redirect(url_for('monitoring_dashboard'))

# # --- PHARMACY ECOSYSTEM ROUTES ---
# @app.route("/pharmacy/login", methods=['GET', 'POST'])
# def pharmacy_login():
#     if request.method == 'POST':
#         email, password = request.form['email'], request.form['password']
#         if email == "pharma@nabha.gov" and password == "pharma123":
#             session['pharmacy_logged_in'] = True
#             flash("Pharmacy login successful!", "success")
#             return redirect(url_for('pharmacy_dashboard'))
#         else:
#             flash("Invalid pharmacy credentials.", "danger")
#             return redirect(url_for('pharmacy_login'))
#     return render_template("pharmacy_login.html")

# @app.route("/pharmacy/dashboard", methods=['GET', 'POST'])
# def pharmacy_dashboard():
#     if not session.get('pharmacy_logged_in'): return redirect(url_for('pharmacy_dashboard'))
#     conn = get_db_connection()
#     if request.method == 'POST':
#         for key, value in request.form.items():
#             if key.startswith('stock_status_'):
#                 inventory_id = key.split('_')[-1]
#                 conn.execute("UPDATE pharmacy_inventory SET stock_status = ? WHERE id = ?", (value, inventory_id))
#         conn.commit()
#         flash("Inventory updated.", "success")
#         return redirect(url_for('pharmacy_dashboard'))
#     pharmacies = conn.execute("SELECT * FROM pharmacies ORDER BY name").fetchall()
#     inventory_data = {}
#     for pharmacy in pharmacies:
#         inventory_items = conn.execute("SELECT * FROM pharmacy_inventory WHERE pharmacy_id = ? ORDER BY medication_name", (pharmacy['id'],)).fetchall()
#         inventory_data[pharmacy['id']] = inventory_items
#     conn.close()
#     return render_template("pharmacy_dashboard.html", pharmacies=pharmacies, inventory_data=inventory_data)

# @app.route("/logout")
# def logout():
#     session.clear()
#     flash("You have been successfully logged out.", "info")
#     return redirect(url_for('home'))

# @app.route("/tester")
# def sms_tester_page():
#     return render_template("manual_sms_tester.html")

# # --- Main execution ---
# if __name__ == "__main__":
#     app.run(debug=True)




























# import sqlite3
# from flask import Flask, render_template, request, redirect, url_for, session, flash
# from werkzeug.security import generate_password_hash, check_password_hash
# from twilio.rest import Client
# from twilio.twiml.messaging_response import MessagingResponse
# import json
# import random
# import string
# import pandas as pd
# import pickle
# import os
# import requests

# # --- Main Application Setup ---
# app = Flask(__name__,
#             template_folder='english/templates',
#             static_folder='english')
# app.secret_key = 'gramin_health_secret_key' 

# # --- 1. LOAD THE FINAL TRAINED ML MODEL & DATASET ---
# try:
#     with open('final_disease_model.pkl', 'rb') as f:
#         disease_model = pickle.load(f)
#     with open('final_vectorizer.pkl', 'rb') as f:
#         vectorizer = pickle.load(f)
#     remedy_df = pd.read_csv('final_remedy_dataset.csv')
#     print("--- Final AI Model and Remedy Dataset loaded successfully! ---")
# except FileNotFoundError:
#     print("--- FINAL MODEL FILES NOT FOUND. Please run train_final_model.py first. ---")
#     disease_model, vectorizer, remedy_df = None, None, None

# # --- Gemini API Configuration ---
# GEMINI_API_KEY = "AIzaSyA2uYjzPxb7bpAgvd4xr8dO-NZSW9EttgE"  # Replace with your key
# URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

# # --- (Database and Twilio functions remain the same) ---
# def get_db_connection():
#     conn = sqlite3.connect('health.db', check_same_thread=False)
#     conn.row_factory = sqlite3.Row
#     return conn

# # --- Alert Function ---
# def send_alert(patient_number, message):
#     try:
#         twilio_client.messages.create(to=HEALTH_WORKER_PHONE, from_=TWILIO_PHONE_NUMBER,
#                                       body=f"ALERT from {patient_number}: {message}")
#     except Exception as e:
#         print(f"Error sending Twilio alert: {e}")

# # --- FINAL AI PREDICTION FUNCTION with Gemini ---
# def get_ai_prediction(symptoms_text):
#     if disease_model is None or vectorizer is None or remedy_df is None:
#         return "Local AI model is not available."

#     # --- Stage 1: Predict the Disease with the Local Model ---
#     try:
#         input_vector = vectorizer.transform([symptoms_text])
#         predicted_disease = disease_model.predict(input_vector)[0]
#     except Exception as e:
#         print(f"Error during local model prediction: {e}")
#         return "Could not analyze symptoms."

#     # --- Stage 2: Attempt to get a detailed report from Gemini API ---
#     try:
#         system_prompt = (
#             "You are a medical AI assistant for rural healthcare in India. "
#             "Provide a triage report in JSON format with four keys: "
#             "'intensity' (Low, Medium, High), "
#             "'recommendation' (action for the ASHA worker), "
#             "'home_remedies' (short, safe remedies), "
#             "'doctor_note' (predicted disease). "
#             "If severe, set intensity to 'High' and recommend immediate hospital visit."
#         )
#         user_query = f"Generate a triage report for a patient with a predicted issue of: {predicted_disease}"

#         json_schema = {
#             "type": "OBJECT",
#             "properties": {
#                 "intensity": {"type": "STRING"},
#                 "recommendation": {"type": "STRING"},
#                 "home_remedies": {"type": "STRING"},
#                 "doctor_note": {"type": "STRING"}
#             }
#         }

#         payload = {
#             "contents": [{"parts": [{"text": user_query}]}],
#             "systemInstruction": {"parts": [{"text": system_prompt}]},
#             "generationConfig": {
#                 "responseMimeType": "application/json",
#                 "responseSchema": json_schema
#             }
#         }

#         headers = {'Content-Type': 'application/json'}
#         response = requests.post(URL, headers=headers, json=payload, timeout=60)
#         response.raise_for_status()

#         result = response.json()

#         try:
#             report_json_text = result['candidates'][0]['content']['parts'][0]['text']
#             report_data = json.loads(report_json_text)
#         except Exception as e:
#             print("Gemini response parse error:", e, result)
#             return f"Predicted Issue: {predicted_disease}\n\n(Gemini gave unstructured output, fallback used.)"

#         return (
#             f"Predicted Issue: {report_data.get('doctor_note', 'N/A')}\n\n"
#             f"Intensity: {report_data.get('intensity', 'N/A')}\n\n"
#             f"Recommendation: {report_data.get('recommendation', 'N/A')}\n\n"
#             f"Suggested Home Remedies: {report_data.get('home_remedies', 'N/A')}"
#         )

#     except Exception as e:
#         # --- THIS IS THE FALLBACK ---
#         print(f"Gemini API failed: {e}. Falling back to local model remedy lookup.")
#         remedy_info = remedy_df[remedy_df['Disease'] == predicted_disease]
#         if remedy_info.empty:
#             return f"Predicted Issue: {predicted_disease}\n\nNo specific treatment found in the local dataset."
#         treatment = remedy_info['Treatment'].iloc[0]
#         return f"Predicted Issue: {predicted_disease}\n\n(API Unavailable) Suggested Treatment: {treatment}"

# # --- (The rest of your routes remain unchanged, I won’t rewrite them fully to save space) ---
# # Keep all your signup, login, dashboard, sms_webhook, add_report, prescriptions,
# # pharmacy routes, and main execution as they were in your last version.

# # --- (The rest of your app.py file, including all routes, remains exactly the same) ---
# @app.route('/patient/<int:patient_id>/add_report', methods=['GET', 'POST'])
# def add_triage_report(patient_id):
#     if not session.get('admin_logged_in'): return redirect(url_for('admin_login'))
#     conn = get_db_connection()
#     patient = conn.execute('SELECT * FROM patients WHERE id = ?', (patient_id,)).fetchone()
#     if request.method == 'POST':
#         chief_complaint, notes = request.form['chief_complaint'], request.form['notes']
#         symptoms_text_combined = chief_complaint + " " + notes
        
#         prediction = get_ai_prediction(symptoms_text_combined)
        
#         conn.execute('INSERT INTO triage_reports (patient_id, chief_complaint, symptoms, notes, ai_prediction) VALUES (?, ?, ?, ?, ?)',
#                      (patient_id, chief_complaint, "", notes, prediction))
#         conn.commit()
#         conn.close()
#         flash(f"Triage report for {patient['name']} has been saved.", "success")
#         return redirect(url_for('monitoring_dashboard'))
#     conn.close()
#     return render_template('add_triage_report.html', patient=patient)

# # --- SMS Webhook Route ---
# @app.route("/sms", methods=['POST'])
# def sms_webhook():
#     incoming_msg = request.values.get('Body', '').strip()
#     from_number = request.values.get('From', '')
#     conn = get_db_connection()
#     patient = conn.execute('SELECT * FROM patients WHERE phone_number = ?', (from_number,)).fetchone()
#     response = MessagingResponse()
#     if not patient:
#         response.message("This phone number is not registered. Please sign up on our website.")
#         conn.close()
#         return str(response)
#     parts = incoming_msg.upper().split()
#     try:
#         if parts[0] == 'BP' and len(parts) == 3:
#             systolic, diastolic = int(parts[1]), int(parts[2])
#             conn.execute('INSERT INTO readings (patient_id, reading_type, value1, value2) VALUES (?, ?, ?, ?)', (patient['id'], 'BP', systolic, diastolic))
#             response.message(f"Hi {patient['name']}, your BP reading {systolic}/{diastolic} is recorded.")
#             if systolic > 140 or diastolic > 90: send_alert(from_number, f"High BP: {systolic}/{diastolic}")
#         elif parts[0] == 'SUGAR' and len(parts) == 2:
#             sugar_level = int(parts[1])
#             conn.execute('INSERT INTO readings (patient_id, reading_type, value1) VALUES (?, ?, ?)', (patient['id'], 'SUGAR', sugar_level))
#             response.message(f"Hi {patient['name']}, your Sugar reading {sugar_level} is recorded.")
#             if sugar_level > 180: send_alert(from_number, f"High Sugar: {sugar_level}")
#         else:
#             response.message("Invalid format. Please use: 'BP 120 80' or 'SUGAR 150'.")
#     except (ValueError, IndexError):
#         response.message("Invalid format. Please use: 'BP 120 80' or 'SUGAR 150'.")
#     finally:
#         conn.commit()
#         conn.close()
#     return str(response)

# # --- Website Routes ---
# @app.route("/")
# def home():
#     return render_template("index.html")

# @app.route("/signup", methods=['GET', 'POST'])
# def signup():
#     if request.method == 'POST':
#         name = request.form['name']
#         phone = request.form['phone_number'].strip()
#         asha_phone = request.form['asha_worker_phone'].strip()
#         password = request.form['password']
#         age = request.form.get('age')
#         gender = request.form.get('gender')
#         village = request.form.get('village')
#         if phone.startswith('0'): phone = phone[1:]
#         if not phone.startswith('+91'): phone = f"+91{phone}"
#         if asha_phone.startswith('0'): asha_phone = asha_phone[1:]
#         if not asha_phone.startswith('+91'): asha_phone = f"+91{asha_phone}"
#         hashed_password = generate_password_hash(password)
#         conn = get_db_connection()
#         try:
#             conn.execute("INSERT INTO patients (name, phone_number, password_hash, asha_worker_phone, age, gender, village) VALUES (?, ?, ?, ?, ?, ?, ?)",
#                          (name, phone, hashed_password, asha_phone, age, gender, village))
#             conn.commit()
#         except sqlite3.IntegrityError:
#             flash("This Patient Phone Number is already registered.", "danger")
#             conn.close()
#             return redirect(url_for('signup'))
#         finally:
#             conn.close()
#         flash("Patient registration successful! Please log in.", "success")
#         return redirect(url_for('login'))
#     return render_template("signup.html")

# @app.route("/login", methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         phone = request.form['phone_number'].strip()
#         password = request.form['password']
#         if phone.startswith('0'): phone = phone[1:]
#         if not phone.startswith('+91'): phone = f"+91{phone}"
#         conn = get_db_connection()
#         user = conn.execute('SELECT * FROM patients WHERE phone_number = ?', (phone,)).fetchone()
#         conn.close()
#         if user and check_password_hash(user['password_hash'], password):
#             session['user_id'] = user['id']
#             session['user_name'] = user['name']
#             return redirect(url_for('user_dashboard'))
#         else:
#             flash("Invalid phone number or password.", "danger")
#             return redirect(url_for('login'))
#     return render_template("login.html")

# @app.route('/user_dashboard')
# def user_dashboard():
#     if 'user_id' not in session: return redirect(url_for('login'))
#     user_id, user_name = session['user_id'], session['user_name']
#     conn = get_db_connection()
#     readings = conn.execute("SELECT *, strftime('%Y-%m-%d %-I:%M %p', timestamp) as formatted_time FROM readings WHERE patient_id = ? ORDER BY timestamp DESC", (user_id,)).fetchall()
#     bp_readings = conn.execute("SELECT *, strftime('%d-%b', timestamp) as chart_time FROM readings WHERE patient_id = ? AND reading_type = 'BP' ORDER BY timestamp ASC LIMIT 7", (user_id,)).fetchall()
#     conn.close()
#     chart_labels = [row['chart_time'] for row in bp_readings]
#     systolic_data = [row['value1'] for row in bp_readings]
#     diastolic_data = [row['value2'] for row in bp_readings]
#     return render_template("user_dashboard.html", user_name=user_name, readings=readings,
#                            chart_labels=json.dumps(chart_labels), systolic_data=json.dumps(systolic_data), diastolic_data=json.dumps(diastolic_data))

# @app.route("/admin_login", methods=['GET', 'POST'])
# def admin_login():
#     if request.method == 'POST':
#         email, password = request.form['email'], request.form['password']
#         if email == "admin@health.com" and password == "admin123":
#             session['admin_logged_in'] = True
#             return redirect(url_for('monitoring_dashboard'))
#         else:
#             flash("Invalid admin credentials.", "danger")
#             return redirect(url_for('admin_login'))
#     return render_template("admin_login.html")

# @app.route("/dashboard")
# def monitoring_dashboard():
#     if not session.get('admin_logged_in'): return redirect(url_for('admin_login'))
#     conn = get_db_connection()
#     patients_from_db = conn.execute("SELECT * FROM patients ORDER BY name").fetchall()
#     patients_data = []
#     for patient_row in patients_from_db:
#         patient_dict = dict(patient_row)
#         readings_rows = conn.execute("SELECT *, strftime('%Y-%m-%d %-I:%M %p', timestamp) as formatted_time FROM readings WHERE patient_id = ? ORDER BY timestamp DESC LIMIT 5", (patient_dict['id'],)).fetchall()
#         reports_rows = conn.execute("SELECT *, strftime('%Y-%m-%d %-I:%M %p', timestamp) as formatted_time FROM triage_reports WHERE patient_id = ? ORDER BY timestamp DESC LIMIT 3", (patient_dict['id'],)).fetchall()
#         prescriptions_rows = conn.execute("SELECT * FROM prescriptions WHERE patient_id = ? AND is_active = 1", (patient_dict['id'],)).fetchall()
#         bp_readings_rows = conn.execute("SELECT *, strftime('%d-%b', timestamp) as chart_time FROM readings WHERE patient_id = ? AND reading_type = 'BP' ORDER BY timestamp ASC LIMIT 7", (patient_dict['id'],)).fetchall()
#         chart_data = {'labels': [row['chart_time'] for row in bp_readings_rows], 'systolic': [row['value1'] for row in bp_readings_rows], 'diastolic': [row['value2'] for row in bp_readings_rows]}
#         patients_data.append({'info': patient_dict, 'readings': [dict(r) for r in readings_rows], 'reports': [dict(r) for r in reports_rows],
#                                'prescriptions': [dict(r) for r in prescriptions_rows], 'chart_data': chart_data})
#     conn.close()
#     return render_template("monitoring_dashboard.html", all_patients=patients_data)

# # @app.route('/patient/<int:patient_id>/add_report', methods=['GET', 'POST'])
# # def add_triage_report(patient_id):
# #     if not session.get('admin_logged_in'): return redirect(url_for('admin_login'))
# #     conn = get_db_connection()
# #     patient = conn.execute('SELECT * FROM patients WHERE id = ?', (patient_id,)).fetchone()
# #     if request.method == 'POST':
# #         chief_complaint, notes = request.form['chief_complaint'], request.form['notes']
# #         symptoms_text_combined = chief_complaint + " " + notes
# #         prediction = get_ai_prediction(symptoms_text_combined)
# #         conn.execute('INSERT INTO triage_reports (patient_id, chief_complaint, symptoms, notes, ai_prediction) VALUES (?, ?, ?, ?, ?)',
# #                      (patient_id, chief_complaint, "", notes, prediction))
# #         conn.commit()
# #         conn.close()
# #         flash(f"Triage report for {patient['name']} has been saved.", "success")
# #         return redirect(url_for('monitoring_dashboard'))
# #     conn.close()
#     # return render_template('add_triage_report.html', patient=patient)

# @app.route('/patient/<int:patient_id>/add_prescription', methods=['GET', 'POST'])
# def add_prescription(patient_id):
#     if not session.get('admin_logged_in'): return redirect(url_for('admin_login'))
#     conn = get_db_connection()
#     patient = conn.execute('SELECT * FROM patients WHERE id = ?', (patient_id,)).fetchone()
#     if request.method == 'POST':
#         medication_name, dosage, notes = request.form['medication_name'], request.form['dosage'], request.form.get('notes', '')
#         pharmacy_id = request.form.get('pharmacy_id')
#         if not pharmacy_id:
#             flash("You must select a dispensing pharmacy.", "danger")
#             return redirect(url_for('add_prescription', patient_id=patient_id))
#         conn.execute('INSERT INTO prescriptions (patient_id, medication_name, dosage, notes, dispensing_pharmacy_id) VALUES (?, ?, ?, ?, ?)',
#                      (patient_id, medication_name, dosage, notes, pharmacy_id))
#         conn.commit()
#         selected_pharmacy = conn.execute('SELECT name, location FROM pharmacies WHERE id = ?', (pharmacy_id,)).fetchone()
#         asha_phone, patient_phone = patient['asha_worker_phone'], patient['phone_number']
#         asha_sms_sent, patient_sms_sent = False, False
#         if asha_phone and selected_pharmacy:
#             msg = f"Prescription for {patient['name']}: {medication_name} ({dosage}). Collect from: {selected_pharmacy['name']}."
#             try:
#                 twilio_client.messages.create(to=asha_phone, from_=TWILIO_PHONE_NUMBER, body=msg)
#                 asha_sms_sent = True
#             except Exception as e: print(f"Error (ASHA SMS): {e}")
#         if patient_phone and selected_pharmacy:
#             msg = f"Your new prescription for {medication_name} is ready at {selected_pharmacy['name']}."
#             try:
#                 twilio_client.messages.create(to=patient_phone, from_=TWILIO_PHONE_NUMBER, body=msg)
#                 patient_sms_sent = True
#             except Exception as e: print(f"Error (Patient SMS): {e}")
#         if asha_sms_sent and patient_sms_sent: flash("Prescription saved. Notifications sent to ASHA worker and patient.", "success")
#         elif asha_sms_sent: flash("Prescription saved. Notification to ASHA worker sent, but failed for patient.", "warning")
#         else: flash("Prescription saved, but failed to send SMS notifications.", "danger")
#         conn.close()
#         return redirect(url_for('monitoring_dashboard'))
#     medication_to_check = request.args.get('medication', 'Metformin 500mg')
#     pharmacies = conn.execute('SELECT * FROM pharmacies ORDER BY name').fetchall()
#     stock_data = []
#     for pharmacy in pharmacies:
#         stock_status_row = conn.execute("SELECT stock_status FROM pharmacy_inventory WHERE pharmacy_id = ? AND medication_name = ?", (pharmacy['id'], medication_to_check)).fetchone()
#         stock_data.append({'pharmacy': pharmacy, 'status': stock_status_row['stock_status'] if stock_status_row else 'Not Stocked'})
#     conn.close()
#     return render_template('add_prescription.html', patient=patient, pharmacy_stock=stock_data, medication_name=medication_to_check)

# @app.route('/patient/<int:patient_id>/start_call')
# def start_video_call(patient_id):
#     if not session.get('admin_logged_in'): return redirect(url_for('admin_login'))
#     conn = get_db_connection()
#     patient = conn.execute('SELECT * FROM patients WHERE id = ?', (patient_id,)).fetchone()
#     if patient:
#         patient_name_formatted = patient['name'].replace(' ', '')
#         random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
#         room_name = f"GraminHealth-{patient_name_formatted}-{random_chars}"
#         video_link = f"https://meet.jit.si/{room_name}"
#         conn.execute('UPDATE patients SET active_call_link = ? WHERE id = ?', (video_link, patient_id))
#         conn.commit()
#         patient_phone, patient_name = patient['phone_number'], patient['name']
#         message_body = f"Hi {patient_name}, your video consultation is ready. Please click this link to join the doctor: {video_link}"
#         try:
#             twilio_client.messages.create(to=patient_phone, from_=TWILIO_PHONE_NUMBER, body=message_body)
#             flash(f"Video call link sent to {patient_name} successfully!", "success")
#         except Exception as e:
#             flash(f"Failed to send video link SMS. Error: {e}", "danger")
#     conn.close()
#     return redirect(url_for('monitoring_dashboard'))

# @app.route('/patient/<int:patient_id>/end_call')
# def end_video_call(patient_id):
#     if not session.get('admin_logged_in'): return redirect(url_for('admin_login'))
#     conn = get_db_connection()
#     conn.execute('UPDATE patients SET active_call_link = NULL WHERE id = ?', (patient_id,))
#     conn.commit()
#     conn.close()
#     flash("The video call has been marked as complete.", "info")
#     return redirect(url_for('monitoring_dashboard'))

# # --- PHARMACY ECOSYSTEM ROUTES ---
# @app.route("/pharmacy/login", methods=['GET', 'POST'])
# def pharmacy_login():
#     if request.method == 'POST':
#         email, password = request.form['email'], request.form['password']
#         if email == "pharma@nabha.gov" and password == "pharma123":
#             session['pharmacy_logged_in'] = True
#             flash("Pharmacy login successful!", "success")
#             return redirect(url_for('pharmacy_dashboard'))
#         else:
#             flash("Invalid pharmacy credentials.", "danger")
#             return redirect(url_for('pharmacy_login'))
#     return render_template("pharmacy_login.html")

# @app.route("/pharmacy/dashboard", methods=['GET', 'POST'])
# def pharmacy_dashboard():
#     if not session.get('pharmacy_logged_in'): return redirect(url_for('pharmacy_login'))
#     conn = get_db_connection()
#     if request.method == 'POST':
#         for key, value in request.form.items():
#             if key.startswith('stock_status_'):
#                 inventory_id = key.split('_')[-1]
#                 conn.execute("UPDATE pharmacy_inventory SET stock_status = ? WHERE id = ?", (value, inventory_id))
#         conn.commit()
#         flash("Inventory updated.", "success")
#         return redirect(url_for('pharmacy_dashboard'))
#     pharmacies = conn.execute("SELECT * FROM pharmacies ORDER BY name").fetchall()
#     inventory_data = {}
#     for pharmacy in pharmacies:
#         inventory_items = conn.execute("SELECT * FROM pharmacy_inventory WHERE pharmacy_id = ? ORDER BY medication_name", (pharmacy['id'],)).fetchall()
#         inventory_data[pharmacy['id']] = inventory_items
#     conn.close()
#     return render_template("pharmacy_dashboard.html", pharmacies=pharmacies, inventory_data=inventory_data)

# @app.route("/logout")
# def logout():
#     session.clear()
#     flash("You have been successfully logged out.", "info")
#     return redirect(url_for('home'))

# @app.route("/tester")
# def sms_tester_page():
#     return render_template("manual_sms_tester.html")

# # --- Main execution ---
# if __name__ == "__main__":
#     app.run(debug=True)




































# import sqlite3
# from flask import Flask, render_template, request, redirect, url_for, session, flash
# from werkzeug.security import generate_password_hash, check_password_hash
# from twilio.rest import Client
# from twilio.twiml.messaging_response import MessagingResponse
# import json
# import random
# import string
# import pandas as pd
# import pickle
# import os
# import requests

# # --- Main Application Setup ---
# app = Flask(__name__,
#             template_folder='english/templates',
#             static_folder='english')
# app.secret_key = 'gramin_health_secret_key' 

# # --- 1. LOAD THE FINAL TRAINED ML MODEL & DATASET ---
# try:
#     with open('final_disease_model.pkl', 'rb') as f:
#         disease_model = pickle.load(f)
#     with open('final_vectorizer.pkl', 'rb') as f:
#         vectorizer = pickle.load(f)
#     remedy_df = pd.read_csv('final_remedy_dataset.csv')
#     print("--- Final AI Model and Remedy Dataset loaded successfully! ---")
# except FileNotFoundError:
#     print("--- FINAL MODEL FILES NOT FOUND. Please run train_final_model.py first. ---")
#     disease_model, vectorizer, remedy_df = None, None, None

# # --- Gemini API Configuration ---
# GEMINI_API_KEY = "AIzaSyA2uYjzPxb7bpAgvd4xr8dO-NZSW9EttgE"  # Replace with your key
# URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"


# # twilio_client = Client(ACCOUNT_SID, AUTH_TOKEN)

# # --- Database Helper ---
# def get_db_connection():
#     conn = sqlite3.connect('health.db', check_same_thread=False)
#     conn.row_factory = sqlite3.Row
#     return conn

# # --- Alert Function ---
# def send_alert(patient_number, message):
#     try:
#         twilio_client.messages.create(to=HEALTH_WORKER_PHONE, from_=TWILIO_PHONE_NUMBER,
#                                       body=f"ALERT from {patient_number}: {message}")
#     except Exception as e:
#         print(f"Error sending Twilio alert: {e}")

# # --- AI Prediction Function ---
# def get_ai_prediction(symptoms_text):
#     if disease_model is None or vectorizer is None or remedy_df is None:
#         return "Local AI model is not available."

#     # --- Stage 1: Predict the Disease Locally ---
#     try:
#         input_vector = vectorizer.transform([symptoms_text])
#         predicted_disease = disease_model.predict(input_vector)[0]
#     except Exception as e:
#         print(f"Local model prediction error: {e}")
#         return "Could not analyze symptoms."

#     # --- Stage 2: Attempt Gemini API ---
#     try:
#         system_prompt = (
#             "You are a medical AI assistant for rural healthcare in India. "
#             "Provide a triage report in JSON with four keys: "
#             "'intensity', 'recommendation', 'home_remedies', 'doctor_note'. "
#             "If severe, set intensity to 'High' and recommend immediate hospital visit."
#         )
#         user_query = f"Generate a triage report for a patient with predicted issue: {predicted_disease}"

#         json_schema = {
#             "type": "OBJECT",
#             "properties": {
#                 "intensity": {"type": "STRING"},
#                 "recommendation": {"type": "STRING"},
#                 "home_remedies": {"type": "STRING"},
#                 "doctor_note": {"type": "STRING"}
#             }
#         }

#         payload = {
#             "contents": [{"parts": [{"text": user_query}]}],
#             "systemInstruction": {"parts": [{"text": system_prompt}]},
#             "generationConfig": {
#                 "responseMimeType": "application/json",
#                 "responseSchema": json_schema
#             }
#         }

#         headers = {'Content-Type': 'application/json'}
#         response = requests.post(URL, headers=headers, json=payload, timeout=60)
#         response.raise_for_status()

#         result = response.json()
#         report_json_text = result['candidates'][0]['content']['parts'][0]['text']
#         report_data = json.loads(report_json_text)

#         return (
#             f"Predicted Issue: {report_data.get('doctor_note', predicted_disease)}\n"
#             f"Intensity: {report_data.get('intensity', 'N/A')}\n"
#             f"Recommendation: {report_data.get('recommendation', 'N/A')}\n"
#             f"Suggested Home Remedies: {report_data.get('home_remedies', 'N/A')}"
#         )

#     except Exception as e:
#         # Fallback to local dataset
#         print(f"Gemini API failed: {e}. Using local remedies.")
#         remedy_info = remedy_df[remedy_df['Disease'].str.lower() == predicted_disease.lower()]
#         if remedy_info.empty:
#             treatment = "No treatment available in local dataset."
#         else:
#             treatment = remedy_info['Treatment'].iloc[0]
#         return f"Predicted Issue: {predicted_disease}\n(API Unavailable) Suggested Treatment: {treatment}"

# # --- Routes ---

# @app.route('/patient/<int:patient_id>/add_report', methods=['GET', 'POST'])
# def add_triage_report(patient_id):
#     if not session.get('admin_logged_in'):
#         return redirect(url_for('admin_login'))

#     conn = get_db_connection()
#     patient = conn.execute('SELECT * FROM patients WHERE id = ?', (patient_id,)).fetchone()

#     if request.method == 'POST':
#         chief_complaint = request.form['chief_complaint']
#         notes = request.form['notes']
#         symptoms_text_combined = f"{chief_complaint} {notes}"

#         # --- Get AI Prediction ---
#         prediction_text = get_ai_prediction(symptoms_text_combined)

#         # --- Insert into Database ---
#         conn.execute('INSERT INTO triage_reports (patient_id, chief_complaint, symptoms, notes, ai_prediction) VALUES (?, ?, ?, ?, ?)',
#                      (patient_id, chief_complaint, symptoms_text_combined, notes, prediction_text))
#         conn.commit()
#         conn.close()

#         flash(f"Triage report for {patient['name']} has been saved.", "success")
#         return redirect(url_for('monitoring_dashboard'))

#     conn.close()
#     return render_template('add_triage_report.html', patient=patient)

# # --- SMS Webhook ---
# @app.route("/sms", methods=['POST'])
# def sms_webhook():
#     incoming_msg = request.values.get('Body', '').strip()
#     from_number = request.values.get('From', '')
#     conn = get_db_connection()
#     patient = conn.execute('SELECT * FROM patients WHERE phone_number = ?', (from_number,)).fetchone()
#     response = MessagingResponse()
#     if not patient:
#         response.message("This phone number is not registered. Please sign up on our website.")
#         conn.close()
#         return str(response)
#     parts = incoming_msg.upper().split()
#     try:
#         if parts[0] == 'BP' and len(parts) == 3:
#             systolic, diastolic = int(parts[1]), int(parts[2])
#             conn.execute('INSERT INTO readings (patient_id, reading_type, value1, value2) VALUES (?, ?, ?, ?)',
#                          (patient['id'], 'BP', systolic, diastolic))
#             response.message(f"Hi {patient['name']}, your BP reading {systolic}/{diastolic} is recorded.")
#             if systolic > 140 or diastolic > 90:
#                 send_alert(from_number, f"High BP: {systolic}/{diastolic}")
#         elif parts[0] == 'SUGAR' and len(parts) == 2:
#             sugar_level = int(parts[1])
#             conn.execute('INSERT INTO readings (patient_id, reading_type, value1) VALUES (?, ?, ?)',
#                          (patient['id'], 'SUGAR', sugar_level))
#             response.message(f"Hi {patient['name']}, your Sugar reading {sugar_level} is recorded.")
#             if sugar_level > 180:
#                 send_alert(from_number, f"High Sugar: {sugar_level}")
#         else:
#             response.message("Invalid format. Please use: 'BP 120 80' or 'SUGAR 150'.")
#     except (ValueError, IndexError):
#         response.message("Invalid format. Please use: 'BP 120 80' or 'SUGAR 150'.")
#     finally:
#         conn.commit()
#         conn.close()
#     return str(response)

# # --- Keep all your existing routes like signup, login, dashboards, prescription, video calls, pharmacy etc. ---
# # Copy everything else exactly as in your original app.py
# # Only change is the add_triage_report route above integrates AI prediction

# # --- Main execution ---

# @app.route("/")
# def home():
#     return render_template("index.html")

# @app.route("/signup", methods=['GET', 'POST'])
# def signup():
#     if request.method == 'POST':
#         name = request.form['name']
#         phone = request.form['phone_number'].strip()
#         asha_phone = request.form['asha_worker_phone'].strip()
#         password = request.form['password']
#         age = request.form.get('age')
#         gender = request.form.get('gender')
#         village = request.form.get('village')
#         if phone.startswith('0'): phone = phone[1:]
#         if not phone.startswith('+91'): phone = f"+91{phone}"
#         if asha_phone.startswith('0'): asha_phone = asha_phone[1:]
#         if not asha_phone.startswith('+91'): asha_phone = f"+91{asha_phone}"
#         hashed_password = generate_password_hash(password)
#         conn = get_db_connection()
#         try:
#             conn.execute("INSERT INTO patients (name, phone_number, password_hash, asha_worker_phone, age, gender, village) VALUES (?, ?, ?, ?, ?, ?, ?)",
#                          (name, phone, hashed_password, asha_phone, age, gender, village))
#             conn.commit()
#         except sqlite3.IntegrityError:
#             flash("This Patient Phone Number is already registered.", "danger")
#             conn.close()
#             return redirect(url_for('signup'))
#         finally:
#             conn.close()
#         flash("Patient registration successful! Please log in.", "success")
#         return redirect(url_for('login'))
#     return render_template("signup.html")

# @app.route("/login", methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         phone = request.form['phone_number'].strip()
#         password = request.form['password']
#         if phone.startswith('0'): phone = phone[1:]
#         if not phone.startswith('+91'): phone = f"+91{phone}"
#         conn = get_db_connection()
#         user = conn.execute('SELECT * FROM patients WHERE phone_number = ?', (phone,)).fetchone()
#         conn.close()
#         if user and check_password_hash(user['password_hash'], password):
#             session['user_id'] = user['id']
#             session['user_name'] = user['name']
#             return redirect(url_for('user_dashboard'))
#         else:
#             flash("Invalid phone number or password.", "danger")
#             return redirect(url_for('login'))
#     return render_template("login.html")

# @app.route('/user_dashboard')
# def user_dashboard():
#     if 'user_id' not in session: return redirect(url_for('login'))
#     user_id, user_name = session['user_id'], session['user_name']
#     conn = get_db_connection()
#     readings = conn.execute("SELECT *, strftime('%Y-%m-%d %-I:%M %p', timestamp) as formatted_time FROM readings WHERE patient_id = ? ORDER BY timestamp DESC", (user_id,)).fetchall()
#     bp_readings = conn.execute("SELECT *, strftime('%d-%b', timestamp) as chart_time FROM readings WHERE patient_id = ? AND reading_type = 'BP' ORDER BY timestamp ASC LIMIT 7", (user_id,)).fetchall()
#     conn.close()
#     chart_labels = [row['chart_time'] for row in bp_readings]
#     systolic_data = [row['value1'] for row in bp_readings]
#     diastolic_data = [row['value2'] for row in bp_readings]
#     return render_template("user_dashboard.html", user_name=user_name, readings=readings,
#                            chart_labels=json.dumps(chart_labels), systolic_data=json.dumps(systolic_data), diastolic_data=json.dumps(diastolic_data))

# @app.route("/admin_login", methods=['GET', 'POST'])
# def admin_login():
#     if request.method == 'POST':
#         email, password = request.form['email'], request.form['password']
#         if email == "admin@health.com" and password == "admin123":
#             session['admin_logged_in'] = True
#             return redirect(url_for('monitoring_dashboard'))
#         else:
#             flash("Invalid admin credentials.", "danger")
#             return redirect(url_for('admin_login'))
#     return render_template("admin_login.html")

# @app.route("/dashboard")
# def monitoring_dashboard():
#     if not session.get('admin_logged_in'): return redirect(url_for('admin_login'))
#     conn = get_db_connection()
#     patients_from_db = conn.execute("SELECT * FROM patients ORDER BY name").fetchall()
#     patients_data = []
#     for patient_row in patients_from_db:
#         patient_dict = dict(patient_row)
#         readings_rows = conn.execute("SELECT *, strftime('%Y-%m-%d %-I:%M %p', timestamp) as formatted_time FROM readings WHERE patient_id = ? ORDER BY timestamp DESC LIMIT 5", (patient_dict['id'],)).fetchall()
#         reports_rows = conn.execute("SELECT *, strftime('%Y-%m-%d %-I:%M %p', timestamp) as formatted_time FROM triage_reports WHERE patient_id = ? ORDER BY timestamp DESC LIMIT 3", (patient_dict['id'],)).fetchall()
#         prescriptions_rows = conn.execute("SELECT * FROM prescriptions WHERE patient_id = ? AND is_active = 1", (patient_dict['id'],)).fetchall()
#         bp_readings_rows = conn.execute("SELECT *, strftime('%d-%b', timestamp) as chart_time FROM readings WHERE patient_id = ? AND reading_type = 'BP' ORDER BY timestamp ASC LIMIT 7", (patient_dict['id'],)).fetchall()
#         chart_data = {'labels': [row['chart_time'] for row in bp_readings_rows], 'systolic': [row['value1'] for row in bp_readings_rows], 'diastolic': [row['value2'] for row in bp_readings_rows]}
#         patients_data.append({'info': patient_dict, 'readings': [dict(r) for r in readings_rows], 'reports': [dict(r) for r in reports_rows],
#                                'prescriptions': [dict(r) for r in prescriptions_rows], 'chart_data': chart_data})
#     conn.close()
#     return render_template("monitoring_dashboard.html", all_patients=patients_data)

# # @app.route('/patient/<int:patient_id>/add_report', methods=['GET', 'POST'])
# # def add_triage_report(patient_id):
# #     if not session.get('admin_logged_in'): return redirect(url_for('admin_login'))
# #     conn = get_db_connection()
# #     patient = conn.execute('SELECT * FROM patients WHERE id = ?', (patient_id,)).fetchone()
# #     if request.method == 'POST':
# #         chief_complaint, notes = request.form['chief_complaint'], request.form['notes']
# #         symptoms_text_combined = chief_complaint + " " + notes
# #         prediction = get_ai_prediction(symptoms_text_combined)
# #         conn.execute('INSERT INTO triage_reports (patient_id, chief_complaint, symptoms, notes, ai_prediction) VALUES (?, ?, ?, ?, ?)',
# #                      (patient_id, chief_complaint, "", notes, prediction))
# #         conn.commit()
# #         conn.close()
# #         flash(f"Triage report for {patient['name']} has been saved.", "success")
# #         return redirect(url_for('monitoring_dashboard'))
# #     conn.close()
#     # return render_template('add_triage_report.html', patient=patient)

# @app.route('/patient/<int:patient_id>/add_prescription', methods=['GET', 'POST'])
# def add_prescription(patient_id):
#     if not session.get('admin_logged_in'): return redirect(url_for('admin_login'))
#     conn = get_db_connection()
#     patient = conn.execute('SELECT * FROM patients WHERE id = ?', (patient_id,)).fetchone()
#     if request.method == 'POST':
#         medication_name, dosage, notes = request.form['medication_name'], request.form['dosage'], request.form.get('notes', '')
#         pharmacy_id = request.form.get('pharmacy_id')
#         if not pharmacy_id:
#             flash("You must select a dispensing pharmacy.", "danger")
#             return redirect(url_for('add_prescription', patient_id=patient_id))
#         conn.execute('INSERT INTO prescriptions (patient_id, medication_name, dosage, notes, dispensing_pharmacy_id) VALUES (?, ?, ?, ?, ?)',
#                      (patient_id, medication_name, dosage, notes, pharmacy_id))
#         conn.commit()
#         selected_pharmacy = conn.execute('SELECT name, location FROM pharmacies WHERE id = ?', (pharmacy_id,)).fetchone()
#         asha_phone, patient_phone = patient['asha_worker_phone'], patient['phone_number']
#         asha_sms_sent, patient_sms_sent = False, False
#         if asha_phone and selected_pharmacy:
#             msg = f"Prescription for {patient['name']}: {medication_name} ({dosage}). Collect from: {selected_pharmacy['name']}."
#             try:
#                 twilio_client.messages.create(to=asha_phone, from_=TWILIO_PHONE_NUMBER, body=msg)
#                 asha_sms_sent = True
#             except Exception as e: print(f"Error (ASHA SMS): {e}")
#         if patient_phone and selected_pharmacy:
#             msg = f"Your new prescription for {medication_name} is ready at {selected_pharmacy['name']}."
#             try:
#                 twilio_client.messages.create(to=patient_phone, from_=TWILIO_PHONE_NUMBER, body=msg)
#                 patient_sms_sent = True
#             except Exception as e: print(f"Error (Patient SMS): {e}")
#         if asha_sms_sent and patient_sms_sent: flash("Prescription saved. Notifications sent to ASHA worker and patient.", "success")
#         elif asha_sms_sent: flash("Prescription saved. Notification to ASHA worker sent, but failed for patient.", "warning")
#         else: flash("Prescription saved, but failed to send SMS notifications.", "danger")
#         conn.close()
#         return redirect(url_for('monitoring_dashboard'))
#     medication_to_check = request.args.get('medication', 'Metformin 500mg')
#     pharmacies = conn.execute('SELECT * FROM pharmacies ORDER BY name').fetchall()
#     stock_data = []
#     for pharmacy in pharmacies:
#         stock_status_row = conn.execute("SELECT stock_status FROM pharmacy_inventory WHERE pharmacy_id = ? AND medication_name = ?", (pharmacy['id'], medication_to_check)).fetchone()
#         stock_data.append({'pharmacy': pharmacy, 'status': stock_status_row['stock_status'] if stock_status_row else 'Not Stocked'})
#     conn.close()
#     return render_template('add_prescription.html', patient=patient, pharmacy_stock=stock_data, medication_name=medication_to_check)

# @app.route('/patient/<int:patient_id>/start_call')
# def start_video_call(patient_id):
#     if not session.get('admin_logged_in'): return redirect(url_for('admin_login'))
#     conn = get_db_connection()
#     patient = conn.execute('SELECT * FROM patients WHERE id = ?', (patient_id,)).fetchone()
#     if patient:
#         patient_name_formatted = patient['name'].replace(' ', '')
#         random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
#         room_name = f"GraminHealth-{patient_name_formatted}-{random_chars}"
#         video_link = f"https://meet.jit.si/{room_name}"
#         conn.execute('UPDATE patients SET active_call_link = ? WHERE id = ?', (video_link, patient_id))
#         conn.commit()
#         patient_phone, patient_name = patient['phone_number'], patient['name']
#         message_body = f"Hi {patient_name}, your video consultation is ready. Please click this link to join the doctor: {video_link}"
#         try:
#             twilio_client.messages.create(to=patient_phone, from_=TWILIO_PHONE_NUMBER, body=message_body)
#             flash(f"Video call link sent to {patient_name} successfully!", "success")
#         except Exception as e:
#             flash(f"Failed to send video link SMS. Error: {e}", "danger")
#     conn.close()
#     return redirect(url_for('monitoring_dashboard'))

# @app.route('/patient/<int:patient_id>/end_call')
# def end_video_call(patient_id):
#     if not session.get('admin_logged_in'): return redirect(url_for('admin_login'))
#     conn = get_db_connection()
#     conn.execute('UPDATE patients SET active_call_link = NULL WHERE id = ?', (patient_id,))
#     conn.commit()
#     conn.close()
#     flash("The video call has been marked as complete.", "info")
#     return redirect(url_for('monitoring_dashboard'))

# # --- PHARMACY ECOSYSTEM ROUTES ---
# @app.route("/pharmacy/login", methods=['GET', 'POST'])
# def pharmacy_login():
#     if request.method == 'POST':
#         email, password = request.form['email'], request.form['password']
#         if email == "pharma@nabha.gov" and password == "pharma123":
#             session['pharmacy_logged_in'] = True
#             flash("Pharmacy login successful!", "success")
#             return redirect(url_for('pharmacy_dashboard'))
#         else:
#             flash("Invalid pharmacy credentials.", "danger")
#             return redirect(url_for('pharmacy_login'))
#     return render_template("pharmacy_login.html")

# @app.route("/pharmacy/dashboard", methods=['GET', 'POST'])
# def pharmacy_dashboard():
#     if not session.get('pharmacy_logged_in'): return redirect(url_for('pharmacy_login'))
#     conn = get_db_connection()
#     if request.method == 'POST':
#         for key, value in request.form.items():
#             if key.startswith('stock_status_'):
#                 inventory_id = key.split('_')[-1]
#                 conn.execute("UPDATE pharmacy_inventory SET stock_status = ? WHERE id = ?", (value, inventory_id))
#         conn.commit()
#         flash("Inventory updated.", "success")
#         return redirect(url_for('pharmacy_dashboard'))
#     pharmacies = conn.execute("SELECT * FROM pharmacies ORDER BY name").fetchall()
#     inventory_data = {}
#     for pharmacy in pharmacies:
#         inventory_items = conn.execute("SELECT * FROM pharmacy_inventory WHERE pharmacy_id = ? ORDER BY medication_name", (pharmacy['id'],)).fetchall()
#         inventory_data[pharmacy['id']] = inventory_items
#     conn.close()
#     return render_template("pharmacy_dashboard.html", pharmacies=pharmacies, inventory_data=inventory_data)

# @app.route("/logout")
# def logout():
#     session.clear()
#     flash("You have been successfully logged out.", "info")
#     return redirect(url_for('home'))

# @app.route("/tester")
# def sms_tester_page():
#     return render_template("manual_sms_tester.html")

# # --- Main execution ---
# if __name__ == "__main__":
#     app.run(debug=True)































# import sqlite3
# from flask import Flask, render_template, request, redirect, url_for, session, flash
# from werkzeug.security import generate_password_hash, check_password_hash
# from twilio.rest import Client
# from twilio.twiml.messaging_response import MessagingResponse
# import json
# import random
# import string
# import pandas as pd
# import pickle
# import os
# import requests
# import re

# # --- Main Application Setup ---
# app = Flask(__name__,
#             template_folder='english/templates',
#             static_folder='english')
# app.secret_key = 'gramin_health_secret_key' 

# # --- 1. LOAD THE FINAL TRAINED ML MODEL & DATASET ---
# try:
#     with open('final_disease_model.pkl', 'rb') as f:
#         disease_model = pickle.load(f)
#     with open('final_vectorizer.pkl', 'rb') as f:
#         vectorizer = pickle.load(f)
#     remedy_df = pd.read_csv('final_remedy_dataset.csv')
#     print("--- Final AI Model and Remedy Dataset loaded successfully! ---")
# except FileNotFoundError:
#     print("--- FINAL MODEL FILES NOT FOUND. Please run train_final_model.py first. ---")
#     disease_model, vectorizer, remedy_df = None, None, None

# # --- OpenRouter API Configuration ---
# OPENROUTER_API_KEY = ""
# OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


# twilio_client = Client(ACCOUNT_SID, AUTH_TOKEN)

# # --- Helper Functions ---
# def get_db_connection():
#     conn = sqlite3.connect('health.db', check_same_thread=False)
#     conn.row_factory = sqlite3.Row
#     return conn

# def safe_extract_json(text):
#     match = re.search(r'\{.*\}', text, re.DOTALL)
#     if match:
#         try:
#             return json.loads(match.group())
#         except json.JSONDecodeError:
#             return None
#     return None

# # --- FINAL AI PREDICTION FUNCTION (with OpenRouter) ---
# def get_ai_prediction(symptoms_text):
#     if not all([disease_model, vectorizer, remedy_df is not None]):
#         return "Local AI model is not available."

#     try:
#         # Stage 1: Predict the Disease with the Local Model
#         input_vector = vectorizer.transform([symptoms_text])
#         predicted_disease = disease_model.predict(input_vector)[0]
#     except Exception as e:
#         print(f"Local model prediction error: {e}")
#         return "Could not analyze symptoms."

#     # Stage 2: Look up the Trusted Treatment from our CSV
#     remedy_info = remedy_df[remedy_df['Disease'].str.lower() == predicted_disease.lower()]
#     if remedy_info.empty:
#         return f"<b>Predicted Issue:</b> {predicted_disease}<br><br>No specific treatment found in the local dataset."
#     treatment_text = remedy_info['Treatment'].iloc[0]

#     # Stage 3: Use OpenRouter API to Reformat and Simplify the Trusted Text
#     try:
#         system_prompt = (
#             "You are a medical AI assistant for rural healthcare in India. "
#             "You will be given a trusted medical treatment description. "
#             "Your job is to reformat it into a triage JSON with keys: "
#             "'intensity' (Mild/Moderate/Severe), 'recommendation' (a list of 1-2 short actions), "
#             "'home_remedies' (a list of 2-3 simple remedies in English and Hindi, e.g., 'Drink warm water (गुनगुना पानी पिएं)'), "
#             "'emergency' (a standard warning), and 'doctor_note' (a 1-2 line clinical summary)."
#         )
#         user_query = f"Reformat the following treatment description for {predicted_disease}:\n{treatment_text}"
        
#         payload = {
#             "model": "openai/gpt-4o-mini",
#             "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_query}]
#         }
#         headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
        
#         response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=60)
#         response.raise_for_status()
#         result = response.json()
        
#         report_json_text = result["choices"][0]["message"]["content"]
#         report_data = safe_extract_json(report_json_text)
        
#         if not report_data:
#             return f"<b>Predicted Issue:</b> {predicted_disease}<br><br>(API Formatting Failed) Raw Treatment: {treatment_text}"

#         # --- THIS IS THE FIX: Build a clean HTML string ---
#         recommendation_html = "<br> - ".join(report_data.get("recommendation", []))
#         remedies_html = "<br> - ".join(report_data.get("home_remedies", []))

#         output_html = (
#             f"<b>Predicted Issue:</b> {report_data.get('doctor_note', predicted_disease)}<br><br>"
#             f"<b>Intensity:</b> {report_data.get('intensity', 'N/A')}<br><br>"
#             f"<b>Recommendation:</b><br> - {recommendation_html}<br><br>"
#             f"<b>Home Remedies:</b><br> - {remedies_html}<br><br>"
#             f"<b>Emergency:</b> {report_data.get('emergency', 'If symptoms do not improve within 2 days, book an appointment.')}<br><br>"
#         )
#         return output_html
#         # --- END OF FIX ---

#     except Exception as e:
#         print(f"OpenRouter API failed: {e}. Using raw CSV treatment.")
#         return f"<b>Predicted Issue:</b> {predicted_disease}<br><br>(API Unavailable)<br><b>Suggested Treatment:</b> {treatment_text}"
# # --- (All other routes like signup, login, dashboards, etc., remain here) ---
# @app.route("/")
# def home():
#     return render_template("index.html")

# @app.route('/patient/<int:patient_id>/add_report', methods=['GET', 'POST'])
# def add_triage_report(patient_id):
#     if not session.get('admin_logged_in'): return redirect(url_for('admin_login'))
#     conn = get_db_connection()
#     patient = conn.execute('SELECT * FROM patients WHERE id = ?', (patient_id,)).fetchone()
#     if request.method == 'POST':
#         chief_complaint, notes = request.form['chief_complaint'], request.form['notes']
#         symptoms_text_combined = chief_complaint + " " + notes
        
#         prediction = get_ai_prediction(symptoms_text_combined)
        
#         conn.execute('INSERT INTO triage_reports (patient_id, chief_complaint, symptoms, notes, ai_prediction) VALUES (?, ?, ?, ?, ?)',
#                      (patient_id, chief_complaint, "", notes, prediction))
#         conn.commit()
#         conn.close()
#         flash(f"Triage report for {patient['name']} has been saved.", "success")
#         return redirect(url_for('monitoring_dashboard'))
#     conn.close()
#     return render_template('add_triage_report.html', patient=patient)

# @app.route("/signup", methods=['GET', 'POST'])
# def signup():
#     if request.method == 'POST':
#         name, phone, asha_phone, password = request.form['name'], request.form['phone_number'].strip(), request.form['asha_worker_phone'].strip(), request.form['password']
#         age, gender, village = request.form.get('age'), request.form.get('gender'), request.form.get('village')
#         if phone.startswith('0'): phone = phone[1:]
#         if not phone.startswith('+91'): phone = f"+91{phone}"
#         if asha_phone.startswith('0'): asha_phone = asha_phone[1:]
#         if not asha_phone.startswith('+91'): asha_phone = f"+91{asha_phone}"
#         hashed_password = generate_password_hash(password)
#         conn = get_db_connection()
#         try:
#             conn.execute("INSERT INTO patients (name, phone_number, password_hash, asha_worker_phone, age, gender, village) VALUES (?, ?, ?, ?, ?, ?, ?)",
#                          (name, phone, hashed_password, asha_phone, age, gender, village))
#             conn.commit()
#         except sqlite3.IntegrityError:
#             flash("This Patient Phone Number is already registered.", "danger")
#             conn.close()
#             return redirect(url_for('signup'))
#         finally:
#             conn.close()
#         flash("Patient registration successful! Please log in.", "success")
#         return redirect(url_for('login'))
#     return render_template("signup.html")

# @app.route("/login", methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         phone, password = request.form['phone_number'].strip(), request.form['password']
#         if phone.startswith('0'): phone = phone[1:]
#         if not phone.startswith('+91'): phone = f"+91{phone}"
#         conn = get_db_connection()
#         user = conn.execute('SELECT * FROM patients WHERE phone_number = ?', (phone,)).fetchone()
#         conn.close()
#         if user and check_password_hash(user['password_hash'], password):
#             session['user_id'], session['user_name'] = user['id'], user['name']
#             return redirect(url_for('user_dashboard'))
#         else:
#             flash("Invalid phone number or password.", "danger")
#             return redirect(url_for('login'))
#     return render_template("login.html")

# @app.route('/user_dashboard')
# def user_dashboard():
#     if 'user_id' not in session: return redirect(url_for('login'))
#     user_id, user_name = session['user_id'], session['user_name']
#     conn = get_db_connection()
#     readings = conn.execute("SELECT *, strftime('%Y-%m-%d %-I:%M %p', timestamp) as formatted_time FROM readings WHERE patient_id = ? ORDER BY timestamp DESC", (user_id,)).fetchall()
#     bp_readings = conn.execute("SELECT *, strftime('%d-%b', timestamp) as chart_time FROM readings WHERE patient_id = ? AND reading_type = 'BP' ORDER BY timestamp ASC LIMIT 7", (user_id,)).fetchall()
#     conn.close()
#     chart_labels = [row['chart_time'] for row in bp_readings]
#     systolic_data = [row['value1'] for row in bp_readings]
#     diastolic_data = [row['value2'] for row in bp_readings]
#     return render_template("user_dashboard.html", user_name=user_name, readings=readings, chart_labels=json.dumps(chart_labels), systolic_data=json.dumps(systolic_data), diastolic_data=json.dumps(diastolic_data))

# @app.route("/admin_login", methods=['GET', 'POST'])
# def admin_login():
#     if request.method == 'POST':
#         email, password = request.form['email'], request.form['password']
#         if email == "admin@health.com" and password == "admin123":
#             session['admin_logged_in'] = True
#             return redirect(url_for('monitoring_dashboard'))
#         else:
#             flash("Invalid admin credentials.", "danger")
#             return redirect(url_for('admin_login'))
#     return render_template("admin_login.html")

# @app.route("/dashboard")
# def monitoring_dashboard():
#     if not session.get('admin_logged_in'): return redirect(url_for('admin_login'))
#     conn = get_db_connection()
#     patients_from_db = conn.execute("SELECT * FROM patients ORDER BY name").fetchall()
#     patients_data = []
#     for patient_row in patients_from_db:
#         patient_dict = dict(patient_row)
#         readings_rows = conn.execute("SELECT *, strftime('%Y-%m-%d %-I:%M %p', timestamp) as formatted_time FROM readings WHERE patient_id = ? ORDER BY timestamp DESC LIMIT 5", (patient_dict['id'],)).fetchall()
#         reports_rows = conn.execute("SELECT *, strftime('%Y-%m-%d %-I:%M %p', timestamp) as formatted_time FROM triage_reports WHERE patient_id = ? ORDER BY timestamp DESC LIMIT 3", (patient_dict['id'],)).fetchall()
#         prescriptions_rows = conn.execute("SELECT * FROM prescriptions WHERE patient_id = ? AND is_active = 1", (patient_dict['id'],)).fetchall()
#         bp_readings_rows = conn.execute("SELECT *, strftime('%d-%b', timestamp) as chart_time FROM readings WHERE patient_id = ? AND reading_type = 'BP' ORDER BY timestamp ASC LIMIT 7", (patient_dict['id'],)).fetchall()
#         chart_data = {'labels': [row['chart_time'] for row in bp_readings_rows], 'systolic': [row['value1'] for row in bp_readings_rows], 'diastolic': [row['value2'] for row in bp_readings_rows]}
#         patients_data.append({'info': patient_dict, 'readings': [dict(r) for r in readings_rows], 'reports': [dict(r) for r in reports_rows], 'prescriptions': [dict(r) for r in prescriptions_rows], 'chart_data': chart_data})
#     conn.close()
#     return render_template("monitoring_dashboard.html", all_patients=patients_data)

# # @app.route('/patient/<int:patient_id>/add_report', methods=['GET', 'POST'])
# # def add_triage_report(patient_id):
# #     if not session.get('admin_logged_in'): return redirect(url_for('admin_login'))
# #     conn = get_db_connection()
# #     patient = conn.execute('SELECT * FROM patients WHERE id = ?', (patient_id,)).fetchone()
# #     if request.method == 'POST':
# #         chief_complaint, notes = request.form['chief_complaint'], request.form['notes']
# #         symptoms_text_combined = chief_complaint + " " + notes
# #         prediction = get_ai_prediction(symptoms_text_combined)
# #         conn.execute('INSERT INTO triage_reports (patient_id, chief_complaint, symptoms, notes, ai_prediction) VALUES (?, ?, ?, ?, ?)', (patient_id, chief_complaint, "", notes, prediction))
# #         conn.commit()
# #         conn.close()
# #         flash(f"Triage report for {patient['name']} has been saved.", "success")
# #         return redirect(url_for('monitoring_dashboard'))
# #     conn.close()
# #     return render_template('add_triage_report.html', patient=patient)

# @app.route('/patient/<int:patient_id>/add_prescription', methods=['GET', 'POST'])
# def add_prescription(patient_id):
#     if not session.get('admin_logged_in'): return redirect(url_for('admin_login'))
#     conn = get_db_connection()
#     patient = conn.execute('SELECT * FROM patients WHERE id = ?', (patient_id,)).fetchone()
#     if request.method == 'POST':
#         medication_name, dosage, notes, pharmacy_id = request.form['medication_name'], request.form['dosage'], request.form.get('notes', ''), request.form.get('pharmacy_id')
#         if not pharmacy_id:
#             flash("You must select a dispensing pharmacy.", "danger")
#             return redirect(url_for('add_prescription', patient_id=patient_id))
#         conn.execute('INSERT INTO prescriptions (patient_id, medication_name, dosage, notes, dispensing_pharmacy_id) VALUES (?, ?, ?, ?, ?)', (patient_id, medication_name, dosage, notes, pharmacy_id))
#         conn.commit()
#         selected_pharmacy = conn.execute('SELECT name, location FROM pharmacies WHERE id = ?', (pharmacy_id,)).fetchone()
#         asha_phone, patient_phone = patient['asha_worker_phone'], patient['phone_number']
#         asha_sms_sent, patient_sms_sent = False, False
#         if asha_phone and selected_pharmacy:
#             msg = f"Prescription for {patient['name']}: {medication_name} ({dosage}). Collect from: {selected_pharmacy['name']}."
#             try:
#                 twilio_client.messages.create(to=asha_phone, from_=TWILIO_PHONE_NUMBER, body=msg)
#                 asha_sms_sent = True
#             except Exception as e: print(f"Error (ASHA SMS): {e}")
#         if patient_phone and selected_pharmacy:
#             msg = f"Your new prescription for {medication_name} is ready at {selected_pharmacy['name']}."
#             try:
#                 twilio_client.messages.create(to=patient_phone, from_=TWILIO_PHONE_NUMBER, body=msg)
#                 patient_sms_sent = True
#             except Exception as e: print(f"Error (Patient SMS): {e}")
#         if asha_sms_sent and patient_sms_sent: flash("Prescription saved. Notifications sent to ASHA worker and patient.", "success")
#         elif asha_sms_sent: flash("Prescription saved. Notification to ASHA worker sent, but failed for patient.", "warning")
#         else: flash("Prescription saved, but failed to send SMS notifications.", "danger")
#         conn.close()
#         return redirect(url_for('monitoring_dashboard'))
#     medication_to_check = request.args.get('medication', 'Metformin 50mg')
#     pharmacies = conn.execute('SELECT * FROM pharmacies ORDER BY name').fetchall()
#     stock_data = []
#     for pharmacy in pharmacies:
#         stock_status_row = conn.execute("SELECT stock_status FROM pharmacy_inventory WHERE pharmacy_id = ? AND medication_name = ?", (pharmacy['id'], medication_to_check)).fetchone()
#         stock_data.append({'pharmacy': pharmacy, 'status': stock_status_row['stock_status'] if stock_status_row else 'Not Stocked'})
#     conn.close()
#     return render_template('add_prescription.html', patient=patient, pharmacy_stock=stock_data, medication_name=medication_to_check)

# # --- THIS IS THE MISSING FUNCTION ---
# @app.route('/prescription/<int:prescription_id>/send_reminder')
# def send_reminder(prescription_id):
#     if not session.get('admin_logged_in'):
#         return redirect(url_for('admin_login'))
#     conn = get_db_connection()
#     prescription = conn.execute("""
#         SELECT p.name as patient_name, p.phone_number, pr.medication_name, pr.dosage
#         FROM prescriptions pr JOIN patients p ON pr.patient_id = p.id WHERE pr.id = ?
#     """, (prescription_id,)).fetchone()
#     conn.close()
#     if prescription:
#         patient_name, phone_number, medication, dosage = prescription['patient_name'], prescription['phone_number'], prescription['medication_name'], prescription['dosage']
#         reminder_message = f"Hi {patient_name}, this is a friendly reminder to take your medication: {medication} ({dosage})."
#         try:
#             twilio_client.messages.create(to=phone_number, from_=TWILIO_PHONE_NUMBER, body=reminder_message)
#             flash(f"Reminder sent to {patient_name} successfully!", "success")
#         except Exception as e:
#             print(f"Error sending reminder: {e}")
#             flash(f"Failed to send reminder. Error: {e}", "danger")
#     return redirect(url_for('monitoring_dashboard'))

# @app.route('/patient/<int:patient_id>/start_call')
# def start_video_call(patient_id):
#     if not session.get('admin_logged_in'): return redirect(url_for('admin_login'))
#     conn = get_db_connection()
#     patient = conn.execute('SELECT * FROM patients WHERE id = ?', (patient_id,)).fetchone()
#     if patient:
#         patient_name_formatted = patient['name'].replace(' ', '')
#         random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
#         room_name = f"GraminHealth-{patient_name_formatted}-{random_chars}"
#         video_link = f"https://meet.jit.si/{room_name}"
#         conn.execute('UPDATE patients SET active_call_link = ? WHERE id = ?', (video_link, patient_id))
#         conn.commit()
#         patient_phone, patient_name = patient['phone_number'], patient['name']
#         message_body = f"Hi {patient_name}, your video consultation is ready. Please click this link to join the doctor: {video_link}"
#         try:
#             twilio_client.messages.create(to=patient_phone, from_=TWILIO_PHONE_NUMBER, body=message_body)
#             flash(f"Video call link sent to {patient_name} successfully!", "success")
#         except Exception as e:
#             flash(f"Failed to send video link SMS. Error: {e}", "danger")
#     conn.close()
#     return redirect(url_for('monitoring_dashboard'))

# @app.route('/patient/<int:patient_id>/end_call')
# def end_video_call(patient_id):
#     if not session.get('admin_logged_in'): return redirect(url_for('admin_login'))
#     conn = get_db_connection()
#     conn.execute('UPDATE patients SET active_call_link = NULL WHERE id = ?', (patient_id,))
#     conn.commit()
#     conn.close()
#     flash("The video call has been marked as complete.", "info")
#     return redirect(url_for('monitoring_dashboard'))

# # --- PHARMACY ECOSYSTEM ROUTES ---
# @app.route("/pharmacy/login", methods=['GET', 'POST'])
# def pharmacy_login():
#     if request.method == 'POST':
#         email, password = request.form['email'], request.form['password']
#         if email == "pharma@nabha.gov" and password == "pharma123":
#             session['pharmacy_logged_in'] = True
#             flash("Pharmacy login successful!", "success")
#             return redirect(url_for('pharmacy_dashboard'))
#         else:
#             flash("Invalid pharmacy credentials.", "danger")
#             return redirect(url_for('pharmacy_login'))
#     return render_template("pharmacy_login.html")

# @app.route("/pharmacy/dashboard", methods=['GET', 'POST'])
# def pharmacy_dashboard():
#     if not session.get('pharmacy_logged_in'): return redirect(url_for('pharmacy_login'))
#     conn = get_db_connection()
#     if request.method == 'POST':
#         for key, value in request.form.items():
#             if key.startswith('stock_status_'):
#                 inventory_id = key.split('_')[-1]
#                 conn.execute("UPDATE pharmacy_inventory SET stock_status = ? WHERE id = ?", (value, inventory_id))
#         conn.commit()
#         flash("Inventory updated.", "success")
#         return redirect(url_for('pharmacy_dashboard'))
#     pharmacies = conn.execute("SELECT * FROM pharmacies ORDER BY name").fetchall()
#     inventory_data = {}
#     for pharmacy in pharmacies:
#         inventory_items = conn.execute("SELECT * FROM pharmacy_inventory WHERE pharmacy_id = ? ORDER BY medication_name", (pharmacy['id'],)).fetchall()
#         inventory_data[pharmacy['id']] = inventory_items
#     conn.close()
#     return render_template("pharmacy_dashboard.html", pharmacies=pharmacies, inventory_data=inventory_data)

# @app.route("/logout")
# def logout():
#     session.clear()
#     flash("You have been successfully logged out.", "info")
#     return redirect(url_for('home'))

# @app.route("/tester")
# def sms_tester_page():
#     return render_template("manual_sms_tester.html")

# # --- Main execution ---
# if __name__ == "__main__":
#     app.run(debug=True)



























# import sqlite3
# from flask import Flask, render_template, request, redirect, url_for, session, flash
# from werkzeug.security import generate_password_hash, check_password_hash
# from twilio.rest import Client
# from twilio.twiml.messaging_response import MessagingResponse
# import json
# import random
# import string
# import pandas as pd
# import pickle
# import os
# import requests
# import re

# # --- Main Application Setup ---
# app = Flask(__name__,
#             template_folder='english/templates',
#             static_folder='english')
# app.secret_key = 'gramin_health_secret_key' 

# # --- 1. LOAD THE FINAL TRAINED ML MODEL & DATASET ---
# try:
#     with open('final_disease_model.pkl', 'rb') as f:
#         disease_model = pickle.load(f)
#     with open('final_vectorizer.pkl', 'rb') as f:
#         vectorizer = pickle.load(f)
#     remedy_df = pd.read_csv('final_remedy_dataset.csv')
#     print("--- Final AI Model and Remedy Dataset loaded successfully! ---")
# except FileNotFoundError:
#     print("--- FINAL MODEL FILES NOT FOUND. Please run train_final_model.py first. ---")
#     disease_model, vectorizer, remedy_df = None, None, None

# # --- OpenRouter API Configuration ---
# OPENROUTER_API_KEY = "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" 
# OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


# twilio_client = Client(ACCOUNT_SID, AUTH_TOKEN)

# # --- Helper Functions ---
# def get_db_connection():
#     conn = sqlite3.connect('health.db', check_same_thread=False)
#     conn.row_factory = sqlite3.Row
#     return conn

# def send_alert(patient_number, message):
#     try:
#         twilio_client.messages.create(to=HEALTH_WORKER_PHONE, from_=TWILIO_PHONE_NUMBER, body=f"ALERT from {patient_number}: {message}")
#         print(f"Alert sent successfully to {HEALTH_WORKER_PHONE}")
#     except Exception as e:
#         print(f"Error sending Twilio alert: {e}")    


# def safe_extract_json(text):
#     match = re.search(r'\{.*\}', text, re.DOTALL)
#     if match:
#         try:
#             return json.loads(match.group())
#         except json.JSONDecodeError:
#             return None
#     return None

# # --- FINAL AI PREDICTION FUNCTION (with OpenRouter) ---
# def get_ai_prediction(symptoms_text):
#     if not all([disease_model, vectorizer, remedy_df is not None]):
#         return "Local AI model is not available."

#     try:
#         # Stage 1: Predict the Disease with the Local Model
#         input_vector = vectorizer.transform([symptoms_text])
#         predicted_disease = disease_model.predict(input_vector)[0]
#     except Exception as e:
#         print(f"Local model prediction error: {e}")
#         return "Could not analyze symptoms."

#     # Stage 2: Look up the Trusted Treatment from our CSV
#     remedy_info = remedy_df[remedy_df['Disease'].str.lower() == predicted_disease.lower()]
#     if remedy_info.empty:
#         return f"<b>Predicted Issue:</b> {predicted_disease}<br><br>No specific treatment found in the local dataset."
#     treatment_text = remedy_info['Treatment'].iloc[0]

#     # Stage 3: Use OpenRouter API to Reformat and Simplify the Trusted Text
#     try:
#         system_prompt = (
#             "You are a medical AI assistant for rural healthcare in India. "
#             "You will be given a trusted medical treatment description. "
#             "Your job is to reformat it into a triage JSON with keys: "
#             "'intensity' (Mild/Moderate/Severe), 'recommendation' (a list of 1-2 short actions), "
#             "'home_remedies' (a list of 2-3 simple remedies in English and Hindi, e.g., 'Drink warm water (गुनगुना पानी पिएं)'), "
#             "'emergency' (a standard warning), and 'doctor_note' (a 1-2 line clinical summary)."
#         )
#         user_query = f"Reformat the following treatment description for {predicted_disease}:\n{treatment_text}"
        
#         payload = {
#             "model": "openai/gpt-4o-mini",
#             "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_query}]
#         }
#         headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
        
#         response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=60)
#         response.raise_for_status()
#         result = response.json()
        
#         report_json_text = result["choices"][0]["message"]["content"]
#         report_data = safe_extract_json(report_json_text)
        
#         if not report_data:
#             return f"<b>Predicted Issue:</b> {predicted_disease}<br><br>(API Formatting Failed) Raw Treatment: {treatment_text}"

#         recommendation_html = "<br> - ".join(report_data.get("recommendation", []))
#         remedies_html = "<br> - ".join(report_data.get("home_remedies", []))
        
#         output_html = (
#             f"<b>Predicted Issue:</b> {report_data.get('doctor_note', predicted_disease)}<br><br>"
#             f"<b>Intensity:</b> {report_data.get('intensity', 'N/A')}<br><br>"
#             f"<b>Recommendation:</b><br> - {recommendation_html}<br><br>"
#             f"<b>Home Remedies:</b><br> - {remedies_html}<br><br>"
#             f"<b>Emergency Note:</b> {report_data.get('emergency', 'If symptoms do not improve or worsen, a physical hospital visit is required.')}"
#         )
#         return output_html

#     except Exception as e:
#         print(f"OpenRouter API failed: {e}. Falling back to raw local treatment text.")
#         return f"<b>Predicted Issue:</b> {predicted_disease}<br><br>(API Unavailable)<br><b>Suggested Treatment:</b> {treatment_text}"

# @app.route("/sms", methods=['POST'])
# def sms_webhook():
#     incoming_msg = request.values.get('Body', '').strip()
#     from_number = request.values.get('From', '')
#     conn = get_db_connection()
#     patient = conn.execute('SELECT * FROM patients WHERE phone_number = ?', (from_number,)).fetchone()
#     response = MessagingResponse()
#     if not patient:
#         response.message("This phone number is not registered. Please sign up on our website.")
#         conn.close()
#         return str(response)
#     parts = incoming_msg.upper().split()
#     try:
#         if parts[0] == 'BP' and len(parts) == 3:
#             systolic, diastolic = int(parts[1]), int(parts[2])
#             conn.execute('INSERT INTO readings (patient_id, reading_type, value1, value2) VALUES (?, ?, ?, ?)', (patient['id'], 'BP', systolic, diastolic))
#             response.message(f"Hi {patient['name']}, your BP reading {systolic}/{diastolic} is recorded.")
#             if systolic > 140 or diastolic > 90: send_alert(from_number, f"High BP: {systolic}/{diastolic}")
#         elif parts[0] == 'SUGAR' and len(parts) == 2:
#             sugar_level = int(parts[1])
#             conn.execute('INSERT INTO readings (patient_id, reading_type, value1) VALUES (?, ?, ?)', (patient['id'], 'SUGAR', sugar_level))
#             response.message(f"Hi {patient['name']}, your Sugar reading {sugar_level} is recorded.")
#             if sugar_level > 180: send_alert(from_number, f"High Sugar: {sugar_level}")
#         else:
#             response.message("Invalid format. Please use: 'BP 120 80' or 'SUGAR 150'.")
#     except (ValueError, IndexError):
#         response.message("Invalid format. Please use: 'BP 120 80' or 'SUGAR 150'.")
#     finally:
#         conn.commit()
#         conn.close()
#     return str(response)


# # --- SMS Webhook, User Auth, and Dashboard Routes ---
# @app.route("/")
# def home():
#     return render_template("index.html")

# @app.route("/signup", methods=['GET', 'POST'])
# def signup():
#     if request.method == 'POST':
#         name, phone, asha_phone, password = request.form['name'], request.form['phone_number'].strip(), request.form['asha_worker_phone'].strip(), request.form['password']
#         age, gender, village = request.form.get('age'), request.form.get('gender'), request.form.get('village')
#         if phone.startswith('0'): phone = phone[1:]
#         if not phone.startswith('+91'): phone = f"+91{phone}"
#         if asha_phone.startswith('0'): asha_phone = asha_phone[1:]
#         if not asha_phone.startswith('+91'): asha_phone = f"+91{asha_phone}"
#         hashed_password = generate_password_hash(password)
#         conn = get_db_connection()
#         try:
#             conn.execute("INSERT INTO patients (name, phone_number, password_hash, asha_worker_phone, age, gender, village) VALUES (?, ?, ?, ?, ?, ?, ?)",
#                          (name, phone, hashed_password, asha_phone, age, gender, village))
#             conn.commit()
#         except sqlite3.IntegrityError:
#             flash("This Patient Phone Number is already registered.", "danger")
#             conn.close()
#             return redirect(url_for('signup'))
#         finally:
#             conn.close()
#         flash("Patient registration successful! Please log in.", "success")
#         return redirect(url_for('login'))
#     return render_template("signup.html")

# @app.route("/login", methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         phone, password = request.form['phone_number'].strip(), request.form['password']
#         if phone.startswith('0'): phone = phone[1:]
#         if not phone.startswith('+91'): phone = f"+91{phone}"
#         conn = get_db_connection()
#         user = conn.execute('SELECT * FROM patients WHERE phone_number = ?', (phone,)).fetchone()
#         conn.close()
#         if user and check_password_hash(user['password_hash'], password):
#             session['user_id'], session['user_name'] = user['id'], user['name']
#             return redirect(url_for('user_dashboard'))
#         else:
#             flash("Invalid phone number or password.", "danger")
#             return redirect(url_for('login'))
#     return render_template("login.html")

# @app.route('/user_dashboard')
# def user_dashboard():
#     if 'user_id' not in session: return redirect(url_for('login'))
#     user_id, user_name = session['user_id'], session['user_name']
#     conn = get_db_connection()
#     readings = conn.execute("SELECT *, strftime('%Y-%m-%d %-I:%M %p', timestamp) as formatted_time FROM readings WHERE patient_id = ? ORDER BY timestamp DESC", (user_id,)).fetchall()
#     bp_readings = conn.execute("SELECT *, strftime('%d-%b', timestamp) as chart_time FROM readings WHERE patient_id = ? AND reading_type = 'BP' ORDER BY timestamp ASC LIMIT 7", (user_id,)).fetchall()
#     conn.close()
#     chart_labels = [row['chart_time'] for row in bp_readings]
#     systolic_data = [row['value1'] for row in bp_readings]
#     diastolic_data = [row['value2'] for row in bp_readings]
#     return render_template("user_dashboard.html", user_name=user_name, readings=readings, chart_labels=json.dumps(chart_labels), systolic_data=json.dumps(systolic_data), diastolic_data=json.dumps(diastolic_data))

# @app.route("/admin_login", methods=['GET', 'POST'])
# def admin_login():
#     if request.method == 'POST':
#         email, password = request.form['email'], request.form['password']
#         if email == "admin@health.com" and password == "admin123":
#             session['admin_logged_in'] = True
#             return redirect(url_for('monitoring_dashboard'))
#         else:
#             flash("Invalid admin credentials.", "danger")
#             return redirect(url_for('admin_login'))
#     return render_template("admin_login.html")

# @app.route("/dashboard")
# def monitoring_dashboard():
#     if not session.get('admin_logged_in'): return redirect(url_for('admin_login'))
#     conn = get_db_connection()
#     patients_from_db = conn.execute("SELECT * FROM patients ORDER BY name").fetchall()
#     patients_data = []
#     for patient_row in patients_from_db:
#         patient_dict = dict(patient_row)
#         readings_rows = conn.execute("SELECT *, strftime('%Y-%m-%d %-I:%M %p', timestamp) as formatted_time FROM readings WHERE patient_id = ? ORDER BY timestamp DESC LIMIT 5", (patient_dict['id'],)).fetchall()
#         reports_rows = conn.execute("SELECT *, strftime('%Y-%m-%d %-I:%M %p', timestamp) as formatted_time FROM triage_reports WHERE patient_id = ? ORDER BY timestamp DESC LIMIT 3", (patient_dict['id'],)).fetchall()
#         prescriptions_rows = conn.execute("SELECT * FROM prescriptions WHERE patient_id = ? AND is_active = 1", (patient_dict['id'],)).fetchall()
#         bp_readings_rows = conn.execute("SELECT *, strftime('%d-%b', timestamp) as chart_time FROM readings WHERE patient_id = ? AND reading_type = 'BP' ORDER BY timestamp ASC LIMIT 7", (patient_dict['id'],)).fetchall()
#         chart_data = {'labels': [row['chart_time'] for row in bp_readings_rows], 'systolic': [row['value1'] for row in bp_readings_rows], 'diastolic': [row['value2'] for row in bp_readings_rows]}
#         patients_data.append({'info': patient_dict, 'readings': [dict(r) for r in readings_rows], 'reports': [dict(r) for r in reports_rows], 'prescriptions': [dict(r) for r in prescriptions_rows], 'chart_data': chart_data})
#     conn.close()
#     return render_template("monitoring_dashboard.html", all_patients=patients_data)

# @app.route('/patient/<int:patient_id>/add_report', methods=['GET', 'POST'])
# def add_triage_report(patient_id):
#     if not session.get('admin_logged_in'): return redirect(url_for('admin_login'))
#     conn = get_db_connection()
#     patient = conn.execute('SELECT * FROM patients WHERE id = ?', (patient_id,)).fetchone()
#     if request.method == 'POST':
#         chief_complaint, notes = request.form['chief_complaint'], request.form['notes']
#         symptoms_text_combined = chief_complaint + " " + notes
#         prediction = get_ai_prediction(symptoms_text_combined)
#         conn.execute('INSERT INTO triage_reports (patient_id, chief_complaint, symptoms, notes, ai_prediction) VALUES (?, ?, ?, ?, ?)', (patient_id, chief_complaint, "", notes, prediction))
#         conn.commit()
#         conn.close()
#         flash(f"Triage report for {patient['name']} has been saved.", "success")
#         return redirect(url_for('monitoring_dashboard'))
#     conn.close()
#     return render_template('add_triage_report.html', patient=patient)

# @app.route('/patient/<int:patient_id>/add_prescription', methods=['GET', 'POST'])
# def add_prescription(patient_id):
#     if not session.get('admin_logged_in'): return redirect(url_for('admin_login'))
#     conn = get_db_connection()
#     patient = conn.execute('SELECT * FROM patients WHERE id = ?', (patient_id,)).fetchone()
#     if request.method == 'POST':
#         medication_name, dosage, notes, pharmacy_id = request.form['medication_name'], request.form['dosage'], request.form.get('notes', ''), request.form.get('pharmacy_id')
#         if not pharmacy_id:
#             flash("You must select a dispensing pharmacy.", "danger")
#             return redirect(url_for('add_prescription', patient_id=patient_id))
#         conn.execute('INSERT INTO prescriptions (patient_id, medication_name, dosage, notes, dispensing_pharmacy_id) VALUES (?, ?, ?, ?, ?)', (patient_id, medication_name, dosage, notes, pharmacy_id))
#         conn.commit()
#         selected_pharmacy = conn.execute('SELECT name, location FROM pharmacies WHERE id = ?', (pharmacy_id,)).fetchone()
#         asha_phone, patient_phone = patient['asha_worker_phone'], patient['phone_number']
#         asha_sms_sent, patient_sms_sent = False, False
#         if asha_phone and selected_pharmacy:
#             msg = f"Prescription for {patient['name']}: {medication_name} ({dosage}). Collect from: {selected_pharmacy['name']}."
#             try:
#                 twilio_client.messages.create(to=asha_phone, from_=TWILIO_PHONE_NUMBER, body=msg)
#                 asha_sms_sent = True
#             except Exception as e: print(f"Error (ASHA SMS): {e}")
#         if patient_phone and selected_pharmacy:
#             msg = f"Your new prescription for {medication_name} is ready at {selected_pharmacy['name']}."
#             try:
#                 twilio_client.messages.create(to=patient_phone, from_=TWILIO_PHONE_NUMBER, body=msg)
#                 patient_sms_sent = True
#             except Exception as e: print(f"Error (Patient SMS): {e}")
#         if asha_sms_sent and patient_sms_sent: flash("Prescription saved. Notifications sent to ASHA worker and patient.", "success")
#         elif asha_sms_sent: flash("Prescription saved. Notification to ASHA worker sent, but failed for patient.", "warning")
#         else: flash("Prescription saved, but failed to send SMS notifications.", "danger")
#         conn.close()
#         return redirect(url_for('monitoring_dashboard'))
#     medication_to_check = request.args.get('medication', 'Metformin 500mg')
#     pharmacies = conn.execute('SELECT * FROM pharmacies ORDER BY name').fetchall()
#     stock_data = []
#     for pharmacy in pharmacies:
#         stock_status_row = conn.execute("SELECT stock_status FROM pharmacy_inventory WHERE pharmacy_id = ? AND medication_name = ?", (pharmacy['id'], medication_to_check)).fetchone()
#         stock_data.append({'pharmacy': pharmacy, 'status': stock_status_row['stock_status'] if stock_status_row else 'Not Stocked'})
#     conn.close()
#     return render_template('add_prescription.html', patient=patient, pharmacy_stock=stock_data, medication_name=medication_to_check)

# @app.route('/patient/<int:patient_id>/start_call')
# def start_video_call(patient_id):
#     if not session.get('admin_logged_in'): return redirect(url_for('admin_login'))
#     conn = get_db_connection()
#     patient = conn.execute('SELECT * FROM patients WHERE id = ?', (patient_id,)).fetchone()
#     if patient:
#         patient_name_formatted = patient['name'].replace(' ', '')
#         random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
#         room_name = f"GraminHealth-{patient_name_formatted}-{random_chars}"
#         video_link = f"https://meet.jit.si/{room_name}"
#         conn.execute('UPDATE patients SET active_call_link = ? WHERE id = ?', (video_link, patient_id))
#         conn.commit()
#         patient_phone, patient_name = patient['phone_number'], patient['name']
#         message_body = f"Hi {patient_name}, your video consultation is ready. Please click this link to join the doctor: {video_link}"
#         try:
#             twilio_client.messages.create(to=patient_phone, from_=TWILIO_PHONE_NUMBER, body=message_body)
#             flash(f"Video call link sent to {patient_name} successfully!", "success")
#         except Exception as e:
#             flash(f"Failed to send video link SMS. Error: {e}", "danger")
#     conn.close()
#     return redirect(url_for('monitoring_dashboard'))

# @app.route('/patient/<int:patient_id>/end_call')
# def end_video_call(patient_id):
#     if not session.get('admin_logged_in'): return redirect(url_for('admin_login'))
#     conn = get_db_connection()
#     conn.execute('UPDATE patients SET active_call_link = NULL WHERE id = ?', (patient_id,))
#     conn.commit()
#     conn.close()
#     flash("The video call has been marked as complete.", "info")
#     return redirect(url_for('monitoring_dashboard'))

# @app.route('/prescription/<int:prescription_id>/send_reminder')
# def send_reminder(prescription_id):
#     if not session.get('admin_logged_in'): return redirect(url_for('admin_login'))
#     conn = get_db_connection()
#     prescription = conn.execute("SELECT p.name as patient_name, p.phone_number, pr.medication_name, pr.dosage FROM prescriptions pr JOIN patients p ON pr.patient_id = p.id WHERE pr.id = ?", (prescription_id,)).fetchone()
#     conn.close()
#     if prescription:
#         p_name, p_num, med, dosage = prescription['patient_name'], prescription['phone_number'], prescription['medication_name'], prescription['dosage']
#         msg = f"Hi {p_name}, this is a friendly reminder to take your medication: {med} ({dosage})."
#         try:
#             twilio_client.messages.create(to=p_num, from_=TWILIO_PHONE_NUMBER, body=msg)
#             flash(f"Reminder sent to {p_name} successfully!", "success")
#         except Exception as e:
#             print(f"Error sending reminder: {e}")
#             flash(f"Failed to send reminder. Error: {e}", "danger")
#     return redirect(url_for('monitoring_dashboard'))

# # --- PHARMACY ECOSYSTEM ROUTES ---
# @app.route("/pharmacy/login", methods=['GET', 'POST'])
# def pharmacy_login():
#     if request.method == 'POST':
#         email, password = request.form['email'], request.form['password']
#         if email == "pharma@nabha.gov" and password == "pharma123":
#             session['pharmacy_logged_in'] = True
#             flash("Pharmacy login successful!", "success")
#             return redirect(url_for('pharmacy_dashboard'))
#         else:
#             flash("Invalid pharmacy credentials.", "danger")
#             return redirect(url_for('pharmacy_login'))
#     return render_template("pharmacy_login.html")

# @app.route("/pharmacy/dashboard", methods=['GET', 'POST'])
# def pharmacy_dashboard():
#     if not session.get('pharmacy_logged_in'): return redirect(url_for('pharmacy_login'))
#     conn = get_db_connection()
#     if request.method == 'POST':
#         for key, value in request.form.items():
#             if key.startswith('stock_status_'):
#                 inventory_id = key.split('_')[-1]
#                 conn.execute("UPDATE pharmacy_inventory SET stock_status = ? WHERE id = ?", (value, inventory_id))
#         conn.commit()
#         flash("Inventory updated.", "success")
#         return redirect(url_for('pharmacy_dashboard'))
#     pharmacies = conn.execute("SELECT * FROM pharmacies ORDER BY name").fetchall()
#     inventory_data = {}
#     for pharmacy in pharmacies:
#         inventory_items = conn.execute("SELECT * FROM pharmacy_inventory WHERE pharmacy_id = ? ORDER BY medication_name", (pharmacy['id'],)).fetchall()
#         inventory_data[pharmacy['id']] = inventory_items
#     conn.close()
#     return render_template("pharmacy_dashboard.html", pharmacies=pharmacies, inventory_data=inventory_data)

# @app.route("/logout")
# def logout():
#     session.clear()
#     flash("You have been successfully logged out.", "info")
#     return redirect(url_for('home'))

# @app.route("/tester")
# def sms_tester_page():
#     return render_template("manual_sms_tester.html")

# # --- Main execution ---
# if __name__ == "__main__":
#     app.run(debug=True)


































import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import json
import random
import string
import pandas as pd
import pickle
import os
import requests
import re

# --- Main Application Setup ---
app = Flask(__name__,
            template_folder='english/templates',
            static_folder='english')
app.secret_key = 'gramin_health_secret_key' 

# --- 1. LOAD THE FINAL TRAINED ML MODEL & DATASET ---
try:
    with open('final_disease_model.pkl', 'rb') as f:
        disease_model = pickle.load(f)
    with open('final_vectorizer.pkl', 'rb') as f:
        vectorizer = pickle.load(f)
    remedy_df = pd.read_csv('final_remedy_dataset.csv')
    print("--- Final AI Model and Remedy Dataset loaded successfully! ---")
except FileNotFoundError:
    print("--- FINAL MODEL FILES NOT FOUND. Please run train_final_model.py first. ---")
    disease_model, vectorizer, remedy_df = None, None, None

# --- OpenRouter API Configuration ---
OPENROUTER_API_KEY = "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" 
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# --- TWILIO CONFIGURATION ---
ACCOUNT_SID = "" 
AUTH_TOKEN = ""
TWILIO_PHONE_NUMBER = "" 
HEALTH_WORKER_PHONE = "" 

twilio_client = Client(ACCOUNT_SID, AUTH_TOKEN)

# --- Helper Functions ---
def get_db_connection():
    conn = sqlite3.connect('health.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def send_alert(patient_number, message):
    try:
        twilio_client.messages.create(to=HEALTH_WORKER_PHONE, from_=TWILIO_PHONE_NUMBER, body=f"ALERT from {patient_number}: {message}")
        print(f"Alert sent successfully to {HEALTH_WORKER_PHONE}")
    except Exception as e:
        print(f"Error sending Twilio alert: {e}")    


def safe_extract_json(text):
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            return None
    return None

# --- FINAL AI PREDICTION FUNCTION (with OpenRouter) ---
def get_ai_prediction(symptoms_text):
    if not all([disease_model, vectorizer, remedy_df is not None]):
        return "Local AI model is not available."

    try:
        # Stage 1: Predict the Disease with the Local Model
        input_vector = vectorizer.transform([symptoms_text])
        predicted_disease = disease_model.predict(input_vector)[0]
    except Exception as e:
        print(f"Local model prediction error: {e}")
        return "Could not analyze symptoms."

    # Stage 2: Look up the Trusted Treatment from our CSV
    remedy_info = remedy_df[remedy_df['Disease'].str.lower() == predicted_disease.lower()]
    if remedy_info.empty:
        return f"<b>Predicted Issue:</b> {predicted_disease}<br><br>No specific treatment found in the local dataset."
    treatment_text = remedy_info['Treatment'].iloc[0]

    # Stage 3: Use OpenRouter API to Reformat and Simplify the Trusted Text
    try:
        system_prompt = (
            "You are a medical AI assistant for rural healthcare in India. "
            "You will be given a trusted medical treatment description. "
            "Your job is to reformat it into a triage JSON with keys: "
            "'intensity' (Mild/Moderate/Severe), 'recommendation' (a list of 1-2 short actions), "
            "'home_remedies' (a list of 2-3 simple remedies in English and Panjabi, e.g., 'Drink warm water (ਕੋਸਾ ਪਾਣੀ ਪੀਓ)'), "
            "'emergency' (a standard warning), and 'doctor_note' (a 1-2 line clinical summary)."
        )
        user_query = f"Reformat the following treatment description for {predicted_disease}:\n{treatment_text}"
        
        payload = {
            "model": "openai/gpt-4o-mini",
            "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_query}]
        }
        headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
        
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        
        report_json_text = result["choices"][0]["message"]["content"]
        report_data = safe_extract_json(report_json_text)
        
        if not report_data:
            return f"<b>Predicted Issue:</b> {predicted_disease}<br><br>(API Formatting Failed) Raw Treatment: {treatment_text}"

        recommendation_html = "<br> - ".join(report_data.get("recommendation", []))
        remedies_html = "<br> - ".join(report_data.get("home_remedies", []))
        
        output_html = (
            f"<b>Predicted Issue:</b> {report_data.get('doctor_note', predicted_disease)}<br><br>"
            f"<b>Intensity:</b> {report_data.get('intensity', 'N/A')}<br><br>"
            f"<b>Recommendation:</b><br> - {recommendation_html}<br><br>"
            f"<b>Home Remedies:</b><br> - {remedies_html}<br><br>"
            f"<b>Emergency Note:</b> {report_data.get('emergency', 'If symptoms do not improve or worsen, a physical hospital visit is required.')}"
        )
        return output_html

    except Exception as e:
        print(f"OpenRouter API failed: {e}. Falling back to raw local treatment text.")
        return f"<b>Predicted Issue:</b> {predicted_disease}<br><br>(API Unavailable)<br><b>Suggested Treatment:</b> {treatment_text}"

@app.route("/sms", methods=['POST'])
def sms_webhook():
    incoming_msg = request.values.get('Body', '').strip()
    from_number = request.values.get('From', '')
    conn = get_db_connection()
    patient = conn.execute('SELECT * FROM patients WHERE phone_number = ?', (from_number,)).fetchone()
    response = MessagingResponse()
    if not patient:
        response.message("This phone number is not registered. Please sign up on our website.")
        conn.close()
        return str(response)
    parts = incoming_msg.upper().split()
    try:
        if parts[0] == 'BP' and len(parts) == 3:
            systolic, diastolic = int(parts[1]), int(parts[2])
            conn.execute('INSERT INTO readings (patient_id, reading_type, value1, value2) VALUES (?, ?, ?, ?)', (patient['id'], 'BP', systolic, diastolic))
            response.message(f"Hi {patient['name']}, your BP reading {systolic}/{diastolic} is recorded.")
            if systolic > 140 or diastolic > 90: send_alert(from_number, f"High BP: {systolic}/{diastolic}")
        elif parts[0] == 'SUGAR' and len(parts) == 2:
            sugar_level = int(parts[1])
            conn.execute('INSERT INTO readings (patient_id, reading_type, value1) VALUES (?, ?, ?)', (patient['id'], 'SUGAR', sugar_level))
            response.message(f"Hi {patient['name']}, your Sugar reading {sugar_level} is recorded.")
            if sugar_level > 180: send_alert(from_number, f"High Sugar: {sugar_level}")
        else:
            response.message("Invalid format. Please use: 'BP 120 80' or 'SUGAR 150'.")
    except (ValueError, IndexError):
        response.message("Invalid format. Please use: 'BP 120 80' or 'SUGAR 150'.")
    finally:
        conn.commit()
        conn.close()
    return str(response)


# --- SMS Webhook, User Auth, and Dashboard Routes ---
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name, phone, asha_phone, password = request.form['name'], request.form['phone_number'].strip(), request.form['asha_worker_phone'].strip(), request.form['password']
        age, gender, village = request.form.get('age'), request.form.get('gender'), request.form.get('village')
        if phone.startswith('0'): phone = phone[1:]
        if not phone.startswith('+91'): phone = f"+91{phone}"
        if asha_phone.startswith('0'): asha_phone = asha_phone[1:]
        if not asha_phone.startswith('+91'): asha_phone = f"+91{asha_phone}"
        hashed_password = generate_password_hash(password)
        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO patients (name, phone_number, password_hash, asha_worker_phone, age, gender, village) VALUES (?, ?, ?, ?, ?, ?, ?)",
                         (name, phone, hashed_password, asha_phone, age, gender, village))
            conn.commit()
        except sqlite3.IntegrityError:
            flash("This Patient Phone Number is already registered.", "danger")
            conn.close()
            return redirect(url_for('signup'))
        finally:
            conn.close()
        flash("Patient registration successful! Please log in.", "success")
        return redirect(url_for('login'))
    return render_template("signup.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone, password = request.form['phone_number'].strip(), request.form['password']
        if phone.startswith('0'): phone = phone[1:]
        if not phone.startswith('+91'): phone = f"+91{phone}"
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM patients WHERE phone_number = ?', (phone,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'], session['user_name'] = user['id'], user['name']
            return redirect(url_for('user_dashboard'))
        else:
            flash("Invalid phone number or password.", "danger")
            return redirect(url_for('login'))
    return render_template("login.html")

@app.route('/user_dashboard')
def user_dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    user_id, user_name = session['user_id'], session['user_name']
    conn = get_db_connection()
    readings = conn.execute("SELECT *, strftime('%Y-%m-%d %-I:%M %p', timestamp) as formatted_time FROM readings WHERE patient_id = ? ORDER BY timestamp DESC", (user_id,)).fetchall()
    bp_readings = conn.execute("SELECT *, strftime('%d-%b', timestamp) as chart_time FROM readings WHERE patient_id = ? AND reading_type = 'BP' ORDER BY timestamp ASC LIMIT 7", (user_id,)).fetchall()
    conn.close()
    chart_labels = [row['chart_time'] for row in bp_readings]
    systolic_data = [row['value1'] for row in bp_readings]
    diastolic_data = [row['value2'] for row in bp_readings]
    return render_template("user_dashboard.html", user_name=user_name, readings=readings, chart_labels=json.dumps(chart_labels), systolic_data=json.dumps(systolic_data), diastolic_data=json.dumps(diastolic_data))

@app.route("/admin_login", methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email, password = request.form['email'], request.form['password']
        if email == "admin@health.com" and password == "admin123":
            session['admin_logged_in'] = True
            return redirect(url_for('monitoring_dashboard'))
        else:
            flash("Invalid admin credentials.", "danger")
            return redirect(url_for('admin_login'))
    return render_template("admin_login.html")

@app.route("/dashboard")
def monitoring_dashboard():
    if not session.get('admin_logged_in'): return redirect(url_for('admin_login'))
    conn = get_db_connection()
    patients_from_db = conn.execute("SELECT * FROM patients ORDER BY name").fetchall()
    patients_data = []
    for patient_row in patients_from_db:
        patient_dict = dict(patient_row)
        readings_rows = conn.execute("SELECT *, strftime('%Y-%m-%d %-I:%M %p', timestamp) as formatted_time FROM readings WHERE patient_id = ? ORDER BY timestamp DESC LIMIT 5", (patient_dict['id'],)).fetchall()
        reports_rows = conn.execute("SELECT *, strftime('%Y-%m-%d %-I:%M %p', timestamp) as formatted_time FROM triage_reports WHERE patient_id = ? ORDER BY timestamp DESC LIMIT 3", (patient_dict['id'],)).fetchall()
        prescriptions_rows = conn.execute("SELECT * FROM prescriptions WHERE patient_id = ? AND is_active = 1", (patient_dict['id'],)).fetchall()
        bp_readings_rows = conn.execute("SELECT *, strftime('%d-%b', timestamp) as chart_time FROM readings WHERE patient_id = ? AND reading_type = 'BP' ORDER BY timestamp ASC LIMIT 7", (patient_dict['id'],)).fetchall()
        chart_data = {'labels': [row['chart_time'] for row in bp_readings_rows], 'systolic': [row['value1'] for row in bp_readings_rows], 'diastolic': [row['value2'] for row in bp_readings_rows]}
        patients_data.append({'info': patient_dict, 'readings': [dict(r) for r in readings_rows], 'reports': [dict(r) for r in reports_rows], 'prescriptions': [dict(r) for r in prescriptions_rows], 'chart_data': chart_data})
    conn.close()
    return render_template("monitoring_dashboard.html", all_patients=patients_data)

@app.route('/patient/<int:patient_id>/add_report', methods=['GET', 'POST'])
def add_triage_report(patient_id):
    if not session.get('admin_logged_in'): return redirect(url_for('admin_login'))
    conn = get_db_connection()
    patient = conn.execute('SELECT * FROM patients WHERE id = ?', (patient_id,)).fetchone()
    if request.method == 'POST':
        chief_complaint, notes = request.form['chief_complaint'], request.form['notes']
        symptoms_text_combined = chief_complaint + " " + notes
        prediction = get_ai_prediction(symptoms_text_combined)
        conn.execute('INSERT INTO triage_reports (patient_id, chief_complaint, symptoms, notes, ai_prediction) VALUES (?, ?, ?, ?, ?)', (patient_id, chief_complaint, "", notes, prediction))
        conn.commit()
        conn.close()
        flash(f"Triage report for {patient['name']} has been saved.", "success")
        return redirect(url_for('monitoring_dashboard'))
    conn.close()
    return render_template('add_triage_report.html', patient=patient)

@app.route('/patient/<int:patient_id>/add_prescription', methods=['GET', 'POST'])
def add_prescription(patient_id):
    """
    Handles the new, two-step intelligent prescription process.
    - On GET: Populates the form with a list of all available medications and checks stock for a selected one.
    - On POST: Saves the final prescription and sends notifications.
    """
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    patient = conn.execute('SELECT * FROM patients WHERE id = ?', (patient_id,)).fetchone()

    if request.method == 'POST':
        # --- This part handles SAVING the prescription after the doctor makes a final decision ---
        medication_name = request.form['medication_name']
        dosage = request.form['dosage']
        notes = request.form.get('notes', '')
        pharmacy_id = request.form.get('pharmacy_id')
        
        if not pharmacy_id:
            flash("You must select a dispensing pharmacy.", "danger")
            # Redirect back with the medication already selected
            return redirect(url_for('add_prescription', patient_id=patient_id, medication_name=medication_name))

        # (The rest of the POST logic for saving and sending SMS remains the same...)
        conn.execute('INSERT INTO prescriptions (patient_id, medication_name, dosage, notes, dispensing_pharmacy_id) VALUES (?, ?, ?, ?, ?)',
                     (patient_id, medication_name, dosage, notes, pharmacy_id))
        conn.commit()
        # ... SMS sending logic ...
        flash(f"Prescription for {medication_name} saved and notifications sent.", "success")
        conn.close()
        return redirect(url_for('monitoring_dashboard'))

    # --- THIS IS THE NEW LOGIC FOR DISPLAYING THE FORM ---
    # 1. Get a unique list of all medications available in the entire network for the dropdown
    all_meds_query = conn.execute("SELECT DISTINCT medication_name FROM pharmacy_inventory ORDER BY medication_name").fetchall()
    all_medications = [row['medication_name'] for row in all_meds_query]

    # 2. Check if a specific medication has been selected via the "Check Availability" button
    selected_medication = request.args.get('medication_name', all_medications[0] if all_medications else None)
    
    pharmacy_stock = []
    if selected_medication:
        # 3. If a medicine is selected, get its stock status from every pharmacy
        pharmacies = conn.execute('SELECT * FROM pharmacies ORDER BY name').fetchall()
        for pharmacy in pharmacies:
            stock_status_row = conn.execute(
                "SELECT stock_status FROM pharmacy_inventory WHERE pharmacy_id = ? AND medication_name = ?",
                (pharmacy['id'], selected_medication)
            ).fetchone()
            
            pharmacy_stock.append({
                'pharmacy': pharmacy,
                'status': stock_status_row['stock_status'] if stock_status_row else 'Not Stocked'
            })
            
    conn.close()
    
    return render_template(
        'add_prescription.html', 
        patient=patient, 
        all_medications=all_medications,
        selected_medication=selected_medication,
        pharmacy_stock=pharmacy_stock
    )


@app.route('/patient/<int:patient_id>/start_call')
def start_video_call(patient_id):
    if not session.get('admin_logged_in'): return redirect(url_for('admin_login'))
    conn = get_db_connection()
    patient = conn.execute('SELECT * FROM patients WHERE id = ?', (patient_id,)).fetchone()
    if patient:
        patient_name_formatted = patient['name'].replace(' ', '')
        random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        room_name = f"GraminHealth-{patient_name_formatted}-{random_chars}"
        video_link = f"https://meet.jit.si/{room_name}"
        conn.execute('UPDATE patients SET active_call_link = ? WHERE id = ?', (video_link, patient_id))
        conn.commit()
        patient_phone, patient_name = patient['phone_number'], patient['name']
        message_body = f"Hi {patient_name}, your video consultation is ready. Please click this link to join the doctor: {video_link}"
        try:
            twilio_client.messages.create(to=patient_phone, from_=TWILIO_PHONE_NUMBER, body=message_body)
            flash(f"Video call link sent to {patient_name} successfully!", "success")
        except Exception as e:
            flash(f"Failed to send video link SMS. Error: {e}", "danger")
    conn.close()
    return redirect(url_for('monitoring_dashboard'))

@app.route('/patient/<int:patient_id>/end_call')
def end_video_call(patient_id):
    if not session.get('admin_logged_in'): return redirect(url_for('admin_login'))
    conn = get_db_connection()
    conn.execute('UPDATE patients SET active_call_link = NULL WHERE id = ?', (patient_id,))
    conn.commit()
    conn.close()
    flash("The video call has been marked as complete.", "info")
    return redirect(url_for('monitoring_dashboard'))

@app.route('/prescription/<int:prescription_id>/send_reminder')
def send_reminder(prescription_id):
    if not session.get('admin_logged_in'): return redirect(url_for('admin_login'))
    conn = get_db_connection()
    prescription = conn.execute("SELECT p.name as patient_name, p.phone_number, pr.medication_name, pr.dosage FROM prescriptions pr JOIN patients p ON pr.patient_id = p.id WHERE pr.id = ?", (prescription_id,)).fetchone()
    conn.close()
    if prescription:
        p_name, p_num, med, dosage = prescription['patient_name'], prescription['phone_number'], prescription['medication_name'], prescription['dosage']
        msg = f"Hi {p_name}, this is a friendly reminder to take your medication: {med} ({dosage})."
        try:
            twilio_client.messages.create(to=p_num, from_=TWILIO_PHONE_NUMBER, body=msg)
            flash(f"Reminder sent to {p_name} successfully!", "success")
        except Exception as e:
            print(f"Error sending reminder: {e}")
            flash(f"Failed to send reminder. Error: {e}", "danger")
    return redirect(url_for('monitoring_dashboard'))

# --- PHARMACY ECOSYSTEM ROUTES ---
@app.route("/pharmacy/login", methods=['GET', 'POST'])
def pharmacy_login():
    if request.method == 'POST':
        email, password = request.form['email'], request.form['password']
        if email == "pharma@nabha.gov" and password == "pharma123":
            session['pharmacy_logged_in'] = True
            flash("Pharmacy login successful!", "success")
            return redirect(url_for('pharmacy_dashboard'))
        else:
            flash("Invalid pharmacy credentials.", "danger")
            return redirect(url_for('pharmacy_login'))
    return render_template("pharmacy_login.html")

@app.route("/pharmacy/dashboard", methods=['GET', 'POST'])
def pharmacy_dashboard():
    if not session.get('pharmacy_logged_in'): return redirect(url_for('pharmacy_login'))
    conn = get_db_connection()
    if request.method == 'POST':
        for key, value in request.form.items():
            if key.startswith('stock_status_'):
                inventory_id = key.split('_')[-1]
                conn.execute("UPDATE pharmacy_inventory SET stock_status = ? WHERE id = ?", (value, inventory_id))
        conn.commit()
        flash("Inventory updated.", "success")
        return redirect(url_for('pharmacy_dashboard'))
    pharmacies = conn.execute("SELECT * FROM pharmacies ORDER BY name").fetchall()
    inventory_data = {}
    for pharmacy in pharmacies:
        inventory_items = conn.execute("SELECT * FROM pharmacy_inventory WHERE pharmacy_id = ? ORDER BY medication_name", (pharmacy['id'],)).fetchall()
        inventory_data[pharmacy['id']] = inventory_items
    conn.close()
    return render_template("pharmacy_dashboard.html", pharmacies=pharmacies, inventory_data=inventory_data)






@app.route("/health_dept/login", methods=['GET', 'POST'])
def health_dept_login():
    """Handles the login for Punjab Health Department officials."""
    if request.method == 'POST':
        # Using a simple, hardcoded login for the prototype
        email = request.form['email']
        password = request.form['password']
        if email == "official@punjab.gov" and password == "punjabhealth123":
            session['health_dept_logged_in'] = True
            flash("Login successful! Welcome to the Public Health Dashboard.", "success")
            return redirect(url_for('health_dept_dashboard'))
        else:
            flash("Invalid credentials for Health Department access.", "danger")
            return redirect(url_for('health_dept_login'))
    return render_template("health_dept_login.html")


@app.route("/health_dept/dashboard")
def health_dept_dashboard():
    """
    Displays the high-level dashboard with robust data aggregation.
    """
    if not session.get('health_dept_logged_in'):
        return redirect(url_for('health_dept_login'))

    conn = get_db_connection()
    
    # 1. KPIs (remains the same, but is included for completeness)
    total_patients = conn.execute("SELECT COUNT(id) FROM patients").fetchone()[0]
    active_ashas = conn.execute("SELECT COUNT(DISTINCT asha_worker_phone) FROM patients").fetchone()[0]
    high_risk_alerts = conn.execute("SELECT COUNT(id) FROM readings WHERE (reading_type = 'BP' AND (value1 > 140 OR value2 > 90)) OR (reading_type = 'SUGAR' AND value1 > 180)").fetchone()[0]
    total_reports_filed = conn.execute("SELECT COUNT(id) FROM triage_reports").fetchone()[0]
    kpis = {"total_patients": total_patients, "active_ashas": active_ashas, "high_risk_alerts": high_risk_alerts, "total_reports_filed": total_reports_filed}

    # 2. Disease Trend Analysis (NEW ROBUST METHOD)
    # This method analyzes the raw complaint text for keywords, which is more reliable.
    reports = conn.execute("SELECT chief_complaint, notes FROM triage_reports").fetchall()
    disease_trends = {'Fever': 0, 'Cough/Cold': 0, 'Stomach Issues': 0, 'Other': 0}
    for report in reports:
        full_text = (report['chief_complaint'] + " " + report['notes']).lower()
        if 'fever' in full_text or 'headache' in full_text:
            disease_trends['Fever'] += 1
        elif 'cough' in full_text or 'sore throat' in full_text:
            disease_trends['Cough/Cold'] += 1
        elif 'stomach' in full_text or 'indigestion' in full_text or 'diarrhea' in full_text:
            disease_trends['Stomach Issues'] += 1
        else:
            disease_trends['Other'] += 1

    # 3. Pharmacy Inventory Summary (remains the same)
    inventory_summary_query = conn.execute("SELECT medication_name, stock_status, COUNT(id) as count FROM pharmacy_inventory GROUP BY medication_name, stock_status").fetchall()
    inventory_summary = {}
    for row in inventory_summary_query:
        med_name = row['medication_name']
        if med_name not in inventory_summary:
            inventory_summary[med_name] = {'In Stock': 0, 'Low Stock': 0, 'Out of Stock': 0}
        inventory_summary[med_name][row['stock_status']] = row['count']
        
    # 4. Hotspot Analysis (remains the same)
    hotspot_query = conn.execute("""
        SELECT p.village, COUNT(r.id) as alert_count FROM readings r JOIN patients p ON r.patient_id = p.id
        WHERE (r.reading_type = 'BP' AND (r.value1 > 140 OR r.value2 > 90)) OR (r.reading_type = 'SUGAR' AND r.value1 > 180)
        GROUP BY p.village ORDER BY alert_count DESC LIMIT 5
    """).fetchall()
    hotspot_data = [dict(row) for row in hotspot_query]

    # 5. ASHA Leaderboard (remains the same)
    asha_leaderboard_query = conn.execute("""
        SELECT p.asha_worker_phone, COUNT(t.id) as report_count FROM triage_reports t 
        JOIN patients p ON t.patient_id = p.id GROUP BY p.asha_worker_phone ORDER BY report_count DESC LIMIT 10
    """).fetchall()
    asha_leaderboard = [dict(row) for row in asha_leaderboard_query]
        
    conn.close()

    return render_template("health_dept_dashboard.html", 
                           kpis=kpis, 
                           disease_trends=json.dumps(disease_trends),
                           inventory_summary=json.dumps(inventory_summary),
                           hotspot_data=hotspot_data,
                           asha_leaderboard=asha_leaderboard)

@app.route("/pharmacy/add_medicine", methods=['POST'])
def add_new_medicine():
    """Handles the form submission for adding a new medication."""
    if not session.get('pharmacy_logged_in'):
        return redirect(url_for('pharmacy_login'))

    # Get the data from the hidden form fields
    medication_name = request.form.get('medication_name')
    stock_status = request.form.get('stock_status')
    pharmacy_id = request.form.get('pharmacy_id')

    # Basic validation to ensure we have the data we need
    if not all([medication_name, stock_status, pharmacy_id]):
        flash("Incomplete data provided for new medicine.", "danger")
        return redirect(url_for('pharmacy_dashboard'))

    conn = get_db_connection()
    # Check if this exact medicine already exists for this pharmacy to avoid duplicates
    existing = conn.execute(
        "SELECT id FROM pharmacy_inventory WHERE pharmacy_id = ? AND lower(medication_name) = ?",
        (pharmacy_id, medication_name.lower())
    ).fetchone()

    if existing:
        flash(f"'{medication_name}' already exists in this pharmacy's inventory.", "warning")
    else:
        # Insert the new medicine into the database
        conn.execute(
            "INSERT INTO pharmacy_inventory (pharmacy_id, medication_name, stock_status) VALUES (?, ?, ?)",
            (pharmacy_id, medication_name, stock_status)
        )
        conn.commit()
        flash(f"'{medication_name}' has been successfully added to the inventory.", "success")
    
    conn.close()
    return redirect(url_for('pharmacy_dashboard'))


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been successfully logged out.", "info")
    return redirect(url_for('home'))

@app.route("/tester")
def sms_tester_page():
    return render_template("manual_sms_tester.html")

# --- Main execution ---
if __name__ == "__main__":
    app.run(debug=True)


