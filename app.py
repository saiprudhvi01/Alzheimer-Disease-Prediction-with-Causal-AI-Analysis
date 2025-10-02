from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import json
import os
import uuid
from datetime import datetime, timedelta
import random
import hashlib
import sqlite3
from functools import wraps
import re
import threading
import time
from collections import defaultdict, deque
import statistics
import math

# Import compatible packages for Python 3.13
# import googletrans  # For multi-language support - REMOVED due to Python 3.13 compatibility issues
from reportlab.pdfgen import canvas  # For PDF generation
from reportlab.lib.pagesizes import letter
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Database setup
DATABASE = 'alzheimer_app.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.route('/reset_db')
def reset_db():
    """Reset database (for development purposes)"""
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
    init_db()
    return "Database reset successfully"

# Risk factors and scoring
RISK_FACTORS = {
    'memory_loss': {'None': 0, 'Mild': 10, 'Moderate': 20, 'Severe': 30},
    'age_group': {'Below 60': 5, '60-70': 10, '70-80': 15, 'Above 80': 20},
    'problem_solving': {'No': 0, 'Yes': 15},
    'disorientation': {'No': 0, 'Yes': 15},
    'mood_swings': {'No': 0, 'Yes': 10},
    'family_history': {'No': 0, 'Yes': 10},
    'poor_judgment': {'No': 0, 'Yes': 10}
}

# Causal AI templates for dynamic descriptions
CAUSAL_TEMPLATES = {
    'memory_loss': {
        'causes': [
            "Memory impairment often stems from {factor1} and {factor2}, creating a cascade of cognitive challenges.",
            "The combination of {factor1} and neurological changes contributes significantly to memory difficulties.",
            "Progressive memory loss typically results from {factor1} combined with {factor2}, affecting daily functioning."
        ],
        'reduction': [
            "Memory training exercises like puzzles and brain games can help maintain cognitive function.",
            "Regular mental stimulation through reading and learning new skills preserves memory capacity.",
            "Structured routines and memory aids such as calendars and reminders can compensate for memory challenges."
        ],
        'consequences': [
            "Untreated memory loss may lead to increased dependency and reduced quality of life over time.",
            "Without intervention, memory impairment can progress, making daily tasks increasingly difficult.",
            "Progressive memory loss may result in social withdrawal and diminished independence if not addressed."
        ]
    },
    'age': {
        'causes': [
            "Age-related cognitive changes combined with {factor1} accelerate brain function decline.",
            "Natural aging processes interact with {factor1} to impact cognitive reserve and brain health.",
            "Advanced age amplifies the effects of {factor1}, making brain cells more vulnerable to damage."
        ],
        'reduction': [
            "Regular cardiovascular exercise maintains brain blood flow and supports cognitive health in older adults.",
            "A Mediterranean-style diet rich in antioxidants and omega-3s helps protect against age-related decline.",
            "Lifelong learning and social engagement build cognitive reserve against age-related changes."
        ],
        'consequences': [
            "Age-related cognitive decline may progress more rapidly without proper lifestyle interventions.",
            "Advanced age combined with risk factors can lead to accelerated functional impairment.",
            "Without preventive measures, age-related brain changes may significantly impact independence."
        ]
    },
    'family_history': {
        'causes': [
            "Genetic predisposition from {factor1} creates inherited vulnerabilities in brain cell function.",
            "Family history indicates genetic factors that interact with {factor1} to affect cognitive processes.",
            "Inherited genetic traits combined with {factor1} increase susceptibility to cognitive decline."
        ],
        'reduction': [
            "While genetic factors can't be changed, lifestyle modifications can significantly reduce overall risk.",
            "Regular health screenings and early intervention can help manage genetic predispositions effectively.",
            "Healthy lifestyle choices provide the best defense against genetic vulnerabilities."
        ],
        'consequences': [
            "Genetic predispositions may accelerate cognitive decline when combined with other risk factors.",
            "Family history suggests increased vulnerability that requires proactive risk management.",
            "Without intervention, genetic factors may contribute to more rapid cognitive deterioration."
        ]
    },
    'mood_disorders': {
        'causes': [
            "Mood disturbances and {factor1} create a complex interplay affecting cognitive function.",
            "Neurological inflammation from mood issues combined with {factor1} impacts brain cell communication.",
            "Chronic stress and mood changes interact with {factor1} to affect memory and cognitive processes."
        ],
        'reduction': [
            "Stress management techniques like meditation and mindfulness can improve mood and cognitive function.",
            "Regular exercise and social connections help stabilize mood and support brain health.",
            "Professional counseling and therapy can address underlying mood issues affecting cognition."
        ],
        'consequences': [
            "Untreated mood disorders may exacerbate cognitive decline and reduce treatment effectiveness.",
            "Chronic mood disturbances can accelerate brain changes and functional impairment.",
            "Without mood management, cognitive symptoms may worsen and become more resistant to intervention."
        ]
    }
}

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/assessment')
def assessment():
    # For demo purposes, allow assessment without login
    # In production, you would require authentication
    return render_template('assessment.html')

@app.route('/calculate_risk', methods=['POST'])
def calculate_risk():
    # For demo purposes, allow calculation without authentication
    # In production, you would require proper authentication
    user_id = session.get('user_id', 1)  # Default to user ID 1 for demo

    data = request.get_json()
    print(f"DEBUG: Received data: {data}")  # Debug log

    if not data:
        print("DEBUG: No data provided")
        return jsonify({'error': 'No data provided'}), 400

    risk_score = 0

    # Calculate risk score based on factors (excluding wellness data)
    risk_factor_keys = ['memory_loss', 'age_group', 'problem_solving', 'disorientation', 'mood_swings', 'family_history', 'poor_judgment']

    for factor in risk_factor_keys:
        value = data.get(factor)
        print(f"DEBUG: Processing {factor} = {value}")
        if value and factor in RISK_FACTORS and value in RISK_FACTORS[factor]:
            risk_score += RISK_FACTORS[factor][value]
            print(f"DEBUG: Added {RISK_FACTORS[factor][value]} points for {factor}")

    # Ensure risk score never exceeds 100
    risk_score = min(risk_score, 100)
    print(f"DEBUG: Final risk score: {risk_score}")

    # Determine risk level
    if risk_score <= 30:
        risk_level = "Low Risk"
    elif risk_score <= 60:
        risk_level = "Moderate Risk"
    else:
        risk_level = "High Risk"

    # Calculate wellness score
    wellness_data = data.get('wellness', {})
    sleep_quality = int(wellness_data.get('sleep_quality', 1))
    mood_level = int(wellness_data.get('mood_level', 1))
    social_engagement = wellness_data.get('social_engagement', 'None')

    social_scores = {'None': 1, 'Rarely': 2, 'Often': 3}
    wellness_score = (sleep_quality * 2) + (mood_level * 2) + social_scores.get(social_engagement, 1)

    # Ensure wellness score never exceeds 20
    wellness_score = min(wellness_score, 20)

    if wellness_score <= 7:
        wellness_level = "Low Wellness"
    elif wellness_score <= 14:
        wellness_level = "Moderate Wellness"
    else:
        wellness_level = "High Wellness"

    # Generate causal analysis
    causal_analysis = generate_causal_analysis(data, risk_score)

    # Store assessment in database (only if user is logged in)
    if 'user_id' in session:
        db = get_db()
        db.execute('''
            INSERT INTO assessments (user_id, risk_score, risk_level, wellness_score, wellness_level, assessment_data, causal_analysis)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (session['user_id'], risk_score, risk_level, wellness_score, wellness_level, json.dumps(data), json.dumps(causal_analysis)))
        db.commit()

    print(f"DEBUG: Sending response: risk_score={risk_score}, wellness_score={wellness_score}")
    return jsonify({
        'risk_score': risk_score,
        'risk_level': risk_level,
        'wellness_score': wellness_score,
        'wellness_level': wellness_level,
        'causal_analysis': causal_analysis
    })

def generate_causal_analysis(data, risk_score):
    """Generate dynamic causal analysis based on risk factors"""
    primary_factors = []
    causal_lines = []

    # Identify primary risk factors
    if data.get('memory_loss') in ['Moderate', 'Severe']:
        primary_factors.append('memory_loss')
    if data.get('age_group') in ['70-80', 'Above 80']:
        primary_factors.append('age')
    if data.get('family_history') == 'Yes':
        primary_factors.append('family_history')
    if data.get('mood_swings') == 'Yes' or data.get('disorientation') == 'Yes':
        primary_factors.append('mood_disorders')

    # Generate 6-line causal analysis
    if primary_factors:
        primary = primary_factors[0]
        template = CAUSAL_TEMPLATES.get(primary, CAUSAL_TEMPLATES['memory_loss'])

        # Line 1-2: Causes
        factor1 = data.get('age_group', 'lifestyle factors')
        factor2 = data.get('family_history', 'environmental factors') if data.get('family_history') == 'Yes' else 'lifestyle factors'

        causal_lines.append(template['causes'][0].format(factor1=factor1, factor2=factor2))
        causal_lines.append(template['causes'][1].format(factor1=factor1, factor2=factor2))

        # Line 3-4: Reduction strategies
        causal_lines.append(template['reduction'][0])
        causal_lines.append(template['reduction'][1])

        # Line 5-6: Consequences
        causal_lines.append(template['consequences'][0])
        causal_lines.append(template['consequences'][1])
    else:
        # Default analysis for no major factors
        causal_lines = [
            "General lifestyle factors combined with normal aging processes contribute to baseline cognitive health considerations.",
            "Regular health monitoring and maintaining an active lifestyle help preserve cognitive function across all age groups.",
            "A balanced diet rich in brain-healthy nutrients supports optimal cognitive performance throughout life.",
            "Regular physical exercise and mental stimulation build cognitive reserve against future challenges.",
            "Without regular health monitoring, subtle changes in cognitive function may go unnoticed over time.",
            "Maintaining social connections and stress management contributes to long-term brain health preservation."
        ]

    return causal_lines

@app.route('/chatbot', methods=['POST'])
def chatbot():
    """Simple chatbot for health queries"""
    user_message = request.get_json().get('message', '').lower()

    responses = {
        'memory': "Memory training exercises like puzzles, reading, and learning new skills can help maintain cognitive function. Regular mental stimulation is important for brain health.",
        'medicine': "Please consult with your healthcare provider about medication schedules and reminders. I recommend setting up a daily routine with alarms or pill organizers.",
        'exercise': "Regular physical activity is crucial for brain health. Aim for 30 minutes of moderate exercise most days, such as walking, swimming, or yoga.",
        'diet': "A brain-healthy diet includes fatty fish, berries, leafy greens, nuts, and whole grains. Stay hydrated and limit processed foods and excessive sugar.",
        'sleep': "Quality sleep is essential for cognitive function. Aim for 7-9 hours per night and maintain a consistent sleep schedule.",
        'stress': "Stress management techniques like meditation, deep breathing, and mindfulness can help protect cognitive health and improve overall well-being."
    }

    response = "I'm here to help with general health guidance. For personalized medical advice, please consult with healthcare professionals."

    for keyword, reply in responses.items():
        if keyword in user_message:
            response = reply
            break

    return jsonify({'response': response})

@app.route('/anomaly_detection', methods=['POST'])
def anomaly_detection():
    """Detect anomalies in user data"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.get_json()

    # Simple anomaly detection based on sudden changes
    anomalies = []

    # Check for sudden weight changes
    current_weight = data.get('current_weight')
    previous_weight = data.get('previous_weight')

    if current_weight and previous_weight:
        weight_change = abs(current_weight - previous_weight)
        if weight_change > 10:  # More than 10kg change
            anomalies.append({
                'type': 'weight_change',
                'message': f'Significant weight change detected: {weight_change}kg difference from previous reading',
                'severity': 'high' if weight_change > 20 else 'medium'
            })

    # Check for memory score changes
    current_memory = data.get('current_memory_score')
    previous_memory = data.get('previous_memory_score')

    if current_memory and previous_memory:
        memory_change = abs(current_memory - previous_memory)
        if memory_change > 15:  # Significant memory score change
            anomalies.append({
                'type': 'memory_change',
                'message': f'Significant memory score change detected: {memory_change} point difference',
                'severity': 'high' if memory_change > 25 else 'medium'
            })

    return jsonify({'anomalies': anomalies})

@app.route('/predictive_alerts', methods=['POST'])
def predictive_alerts():
    """Generate predictive risk forecasts"""
    # For demo purposes, allow without authentication
    user_id = session.get('user_id', 1)  # Default to user ID 1 for demo

    data = request.get_json()
    current_risk = data.get('current_risk', 0)

    # Simple trend prediction based on current risk score
    if current_risk >= 80:
        predicted_increase = 15
        timeframe = "2 years"
        urgency = "High"
    elif current_risk >= 60:
        predicted_increase = 25
        timeframe = "3 years"
        urgency = "Medium"
    elif current_risk >= 40:
        predicted_increase = 15
        timeframe = "5 years"
        urgency = "Low"
    else:
        predicted_increase = 5
        timeframe = "7 years"
        urgency = "Very Low"

    alerts = []
    if current_risk > 60:
        alerts.append({
            'type': 'high_risk_trend',
            'message': f'If current lifestyle continues, risk may increase by {predicted_increase}% in {timeframe}',
            'recommendation': 'Consider consulting healthcare provider for comprehensive evaluation',
            'urgency': urgency
        })
    elif current_risk > 30:
        alerts.append({
            'type': 'moderate_risk_trend',
            'message': f'With lifestyle improvements, you can maintain low risk for the next {timeframe}',
            'recommendation': 'Continue healthy habits and regular check-ups',
            'urgency': urgency
        })

    return jsonify({
        'alerts': alerts,
        'predicted_increase': predicted_increase,
        'timeframe': timeframe,
        'urgency': urgency
    })

@app.route('/translate', methods=['POST'])
def translate():
    """Translate text to different languages"""
    data = request.get_json()
    text = data.get('text', '')
    target_lang = data.get('target_lang', 'en')

    try:
        translator = googletrans.Translator()
        translated = translator.translate(text, dest=target_lang)
        return jsonify({'translated_text': translated.text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/emergency_contact', methods=['POST'])
def emergency_contact():
    """Handle emergency contact notifications"""
    # For demo purposes, allow without authentication
    user_id = session.get('user_id', 1)  # Default to user ID 1 for demo

    data = request.get_json()
    emergency_type = data.get('emergency_type', 'general')

    # In a real application, this would send actual notifications
    # For demo purposes, we'll just log the emergency
    if 'user_id' in session:
        db = get_db()
        db.execute('''
            INSERT INTO emergency_logs (user_id, emergency_type, timestamp, location_data)
            VALUES (?, ?, ?, ?)
        ''', (session['user_id'], emergency_type, datetime.now(), json.dumps(data.get('location', {}))))
        db.commit()

    return jsonify({
        'success': True,
        'message': 'Emergency contact notified successfully',
        'emergency_id': 'generated_id_here'  # In real app, this would be actual notification ID
    })

@app.route('/mood_tracking', methods=['POST'])
def mood_tracking():
    """Track daily mood and emotions"""
    # For demo purposes, allow without authentication
    user_id = session.get('user_id', 1)  # Default to user ID 1 for demo

    data = request.get_json()
    mood = data.get('mood')  # Happy, Neutral, Sad, Anxious
    notes = data.get('notes', '')

    # Store in database (only if user is logged in)
    if 'user_id' in session:
        db = get_db()
        db.execute('''
            INSERT INTO mood_logs (user_id, mood, notes, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (session['user_id'], mood, notes, datetime.now()))
        db.commit()

        # Analyze mood trends
        cursor = db.execute('''
            SELECT mood, COUNT(*) as count FROM mood_logs
            WHERE user_id = ? AND timestamp >= date('now', '-30 days')
            GROUP BY mood
        ''', (session['user_id'],))

        mood_trends = dict(cursor.fetchall())

    return jsonify({
        'success': True,
        'mood_trends': {'Happy': 5, 'Neutral': 3, 'Sad': 1},  # Demo data
        'message': 'Mood logged successfully'
    })

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['user_type'] = user['user_type']

            if user['user_type'] == 'doctor':
                return redirect(url_for('doctor_dashboard'))
            else:
                return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')

@app.route('/doctor_dashboard')
def doctor_dashboard():
    if 'user_id' not in session or session.get('user_type') != 'doctor':
        return redirect(url_for('login'))

    return render_template('doctor_dashboard.html', username=session.get('username'))

@app.route('/doctor_patients')
def doctor_patients():
    """Get patients and their recent assessments for doctors"""
    if 'user_id' not in session or session.get('user_type') != 'doctor':
        return jsonify({'error': 'Unauthorized'}), 401

    db = get_db()

    # Get all patients with their recent assessments
    patients = db.execute('''
        SELECT u.id, u.username, u.email,
               a.risk_score, a.risk_level, a.wellness_score, a.wellness_level, a.created_at as last_assessment,
               COUNT(a.id) as total_assessments
        FROM users u
        LEFT JOIN assessments a ON u.id = a.user_id
        WHERE u.user_type = 'patient'
        GROUP BY u.id, u.username, u.email
        ORDER BY a.created_at DESC
    ''').fetchall()

    patients_data = []
    for patient in patients:
        patient_dict = dict(patient)
        patient_dict['last_assessment'] = patient['last_assessment'] or 'No assessments'
        patients_data.append(patient_dict)

    return jsonify(patients_data)

@app.route('/doctor_appointments')
def doctor_appointments():
    """Get appointment requests for doctors to approve/reject"""
    if 'user_id' not in session or session.get('user_type') != 'doctor':
        return jsonify({'error': 'Unauthorized'}), 401

    db = get_db()

    appointments = db.execute('''
        SELECT a.*, u.username as patient_name, u.email as patient_email
        FROM appointments a
        JOIN users u ON a.user_id = u.id
        WHERE a.status = 'pending'
        ORDER BY a.created_at DESC
    ''').fetchall()

    return jsonify([dict(appointment) for appointment in appointments])

@app.route('/update_appointment_status', methods=['POST'])
def update_appointment_status():
    """Allow doctors to approve/reject appointments"""
    if 'user_id' not in session or session.get('user_type') != 'doctor':
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    appointment_id = data.get('appointment_id')
    status = data.get('status')  # 'approved' or 'rejected'

    if not appointment_id or status not in ['approved', 'rejected']:
        return jsonify({'error': 'Invalid data'}), 400

    try:
        db = get_db()
        db.execute('UPDATE appointments SET status = ? WHERE id = ?', (status, appointment_id))
        db.commit()

        return jsonify({'success': True, 'message': f'Appointment {status} successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    user_type = data.get('user_type', 'patient')

    if not all([username, email, password]):
        return jsonify({'error': 'All fields are required'}), 400

    # Check if user already exists
    db = get_db()
    existing_user = db.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, email)).fetchone()

    if existing_user:
        return jsonify({'error': 'Username or email already exists'}), 400

    # Hash password using pbkdf2:sha256 method (compatible with Werkzeug)
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    # Insert new user
    db.execute('''
        INSERT INTO users (username, password, email, user_type)
        VALUES (?, ?, ?, ?)
    ''', (username, hashed_password, email, user_type))
    db.commit()

    return jsonify({'success': True, 'message': 'Account created successfully'})

@app.route('/dashboard_data')
def dashboard_data():
    """Get dashboard data for the current user"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    user_id = session['user_id']
    db = get_db()

    # Get latest assessment
    latest_assessment = db.execute('''
        SELECT risk_score, risk_level, wellness_score, wellness_level, created_at
        FROM assessments
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 1
    ''', (user_id,)).fetchone()

    # Get recent assessments (last 5)
    recent_assessments = db.execute('''
        SELECT risk_score, risk_level, wellness_score, wellness_level, created_at
        FROM assessments
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 5
    ''', (user_id,)).fetchall()

    # Get mood trends (last 30 days)
    mood_trends = db.execute('''
        SELECT mood, COUNT(*) as count
        FROM mood_logs
        WHERE user_id = ? AND timestamp >= date('now', '-30 days')
        GROUP BY mood
        ORDER BY count DESC
    ''', (user_id,)).fetchall()

    # Get recent mood logs (last 7 days)
    recent_moods = db.execute('''
        SELECT mood, notes, timestamp
        FROM mood_logs
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT 7
    ''', (user_id,)).fetchall()

    # Format data for frontend
    dashboard_info = {
        'latest_assessment': dict(latest_assessment) if latest_assessment else None,
        'recent_assessments': [dict(assessment) for assessment in recent_assessments],
        'mood_trends': {mood['mood']: mood['count'] for mood in mood_trends},
        'recent_moods': [dict(mood) for mood in recent_moods]
    }

    return jsonify(dashboard_info)

@app.route('/get_notifications')
def get_notifications():
    """Get user notifications"""
    if 'user_id' not in session:
        return jsonify([])

    # In a real app, these would be dynamic based on user data and schedules
    notifications = [
        {
            'type': 'appointment',
            'icon': 'exclamation-triangle text-warning',
            'message': 'Schedule your monthly check-up',
            'priority': 'medium'
        },
        {
            'type': 'tips',
            'icon': 'info-circle text-info',
            'message': 'New wellness tips available',
            'priority': 'low'
        },
        {
            'type': 'training',
            'icon': 'calendar text-success',
            'message': 'Memory training session tomorrow',
            'priority': 'high'
        }
    ]

@app.route('/schedule_appointment', methods=['POST'])
def schedule_appointment():
    """Schedule a doctor appointment"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.get_json()
    appointment_type = data.get('appointment_type')
    preferred_date = data.get('preferred_date')
    notes = data.get('notes', '')

    if not all([appointment_type, preferred_date]):
        return jsonify({'error': 'Appointment type and date are required'}), 400

    try:
        db = get_db()
        db.execute('''
            INSERT INTO appointments (user_id, appointment_type, preferred_date, notes)
            VALUES (?, ?, ?, ?)
        ''', (session['user_id'], appointment_type, preferred_date, notes))
        db.commit()

        return jsonify({
            'success': True,
            'message': 'Appointment request submitted successfully',
            'appointment_id': 'generated_id_here'  # In real app, return actual ID
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_user_appointments')
def get_user_appointments():
    """Get user's appointments"""
    if 'user_id' not in session:
        return jsonify([])

    user_id = session['user_id']
    db = get_db()

    appointments = db.execute('''
        SELECT * FROM appointments
        WHERE user_id = ?
        ORDER BY preferred_date DESC
        LIMIT 10
    ''', (user_id,)).fetchall()

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_type', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db()
    app.run(debug=True)
