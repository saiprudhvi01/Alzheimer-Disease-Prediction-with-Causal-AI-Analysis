# Alzheimer's Care AI - Comprehensive Health Monitoring Platform

A comprehensive Flask-based web application for Alzheimer's disease risk assessment, wellness tracking, and causal AI analysis with multiple advanced features.

## 🚀 Features

### Core Features
- **Risk Assessment**: Comprehensive evaluation based on 7 key factors (memory loss, age, problem solving, disorientation, mood swings, family history, poor judgment)
- **Wellness Score**: Tracks sleep quality, mood level, and social engagement (max 20 points)
- **Causal AI Analysis**: Dynamic 6-line personalized descriptions explaining disease causes, prevention strategies, and consequences

### Advanced Features
- **24/7 AI Chatbot**: Natural language processing for health queries and medication reminders
- **Anomaly Detection**: Identifies unusual data patterns (sudden weight changes, memory score fluctuations)
- **Data Privacy & Security**: HIPAA-compliant authentication with encrypted data storage
- **Doctor Integration**: PDF report generation and multi-patient doctor dashboards
- **Predictive Alerts**: Risk forecasting and trend analysis (e.g., "risk may increase by 20% in 5 years")
- **Multi-language Support**: Supports Hindi, Telugu, Tamil using googletrans library
- **Offline Mode**: Local storage with sync capabilities for rural connectivity
- **Mood & Emotion Tracking**: Daily check-ins with trend analysis
- **Emergency Contact**: One-click location sharing with instant caregiver alerts

## 🧠 Causal AI System

The application features a sophisticated causal analysis engine that generates dynamic, personalized explanations:

**Dynamic Analysis Based On:**
- Memory Loss → Memory Impairment Analysis
- Age 70+ → Age-Related Changes
- Family History → Genetic Risk Analysis
- Mood/Disorientation → Neurological Health Assessment

**6-Line Structure:**
1. **Cause Analysis**: Explains why the disease is occurring based on specific factors
2. **Cause Analysis**: Provides additional context on contributing factors
3. **Prevention Strategy**: Recommends specific interventions
4. **Prevention Strategy**: Offers additional protective measures
5. **Consequence Warning**: Describes potential outcomes without intervention
6. **Consequence Warning**: Emphasizes importance of proactive management

## 📊 Risk Scoring System

### Risk Factors (0-100 points):
- **Memory Loss**: None(0) | Mild(10) | Moderate(20) | Severe(30)
- **Age Group**: Below 60(5) | 60-70(10) | 70-80(15) | Above 80(20)
- **Problem Solving**: No(0) | Yes(15)
- **Disorientation**: No(0) | Yes(15)
- **Mood Swings**: No(0) | Yes(10)
- **Family History**: No(0) | Yes(10)
- **Poor Judgment**: No(0) | Yes(10)

### Risk Levels:
- **0-30 points**: Low Risk
- **31-60 points**: Moderate Risk
- **61-100 points**: High Risk

### Wellness Score (Max 20 points):
- **Sleep Quality**: (1-5) × 2 points
- **Mood Level**: (1-5) × 2 points
- **Social Engagement**: None(1) | Rarely(2) | Often(3)

## 🛠️ Installation & Setup

1. **Clone or download** the project files
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Initialize database**:
   ```python
   python app.py
   ```
   (Database will be created automatically on first run)

4. **Run the application**:
   ```python
   python app.py
   ```

5. **Access the application**:
   - Open browser and navigate to `http://localhost:5000`
   - Default credentials:
     - **Patient**: `patient1` / `password123`
     - **Doctor**: `doctor1` / `password123`
     - **Admin**: `admin` / `password123`

## 📁 Project Structure

```
AlzheimerCare-AI/
├── app.py                 # Main Flask application
├── schema.sql             # Database schema
├── requirements.txt       # Python dependencies
├── templates/             # HTML templates
│   ├── index.html         # Landing page
│   ├── login.html         # Authentication
│   ├── dashboard.html     # User dashboard
│   └── assessment.html    # Risk assessment form
├── static/                # Static assets
│   └── styles.css         # Additional CSS
└── README.md              # This file
```

## 🔧 Technical Specifications

### Compatible Technologies (Python 3.13+):
- **Flask 2.3.3**: Web framework
- **googletrans 4.0.0rc1**: Multi-language support
- **reportlab 4.0.7**: PDF generation
- **Werkzeug 2.3.7**: Security utilities

### Database:
- **SQLite3**: Local database with user authentication, assessments, mood logs, and emergency tracking

### Security Features:
- Password hashing with Werkzeug
- Session management
- Input validation and sanitization
- CSRF protection

## 🎯 Demo Credentials

| User Type | Username | Password | Access Level |
|-----------|----------|----------|--------------|
| Patient | patient1 | password123 | Full assessment access |
| Doctor | doctor1 | password123 | Patient management |
| Admin | admin | password123 | System administration |

## 🌟 Key Innovations

1. **Causal AI Engine**: Dynamic analysis that adapts explanations based on individual risk factors
2. **Multi-modal Interface**: Chatbot, emergency alerts, mood tracking integration
3. **Predictive Analytics**: Risk forecasting with timeline projections
4. **Offline-First Design**: Local storage with background sync capabilities
5. **Multi-language Support**: Regional language accessibility for diverse populations

## 📈 Risk Assessment Example

**Sample Input:**
- Memory Loss: Mild (10 pts)
- Age Group: 60-70 (10 pts)
- Problem Solving: No (0 pts)
- Disorientation: No (0 pts)
- Mood Swings: No (0 pts)
- Family History: No (0 pts)
- Poor Judgment: No (0 pts)
- Sleep Quality: 3 (6 pts)
- Mood Level: 3 (6 pts)
- Social Engagement: Rarely (2 pts)

**Output:**
- **Risk Score**: 20 points → **Low Risk**
- **Wellness Score**: 14 points → **Moderate Wellness**
- **Causal Analysis**: 6-line personalized explanation with prevention strategies

## 🚨 Emergency Features

- One-click emergency button with GPS location sharing
- Automatic caregiver notification system
- Emergency contact logging and history tracking
- Integration with local emergency services (configurable)

## 🔮 Future Enhancements

- Machine learning model integration for improved risk prediction
- Wearable device data integration (Fitbit, Apple Health)
- Advanced chatbot with medical knowledge base
- Telemedicine consultation scheduling
- Community support group integration

## 📝 License

This project is developed for educational and healthcare innovation purposes. Please ensure compliance with local healthcare regulations when deploying in production environments.

---

**Built with ❤️ for Alzheimer's care and research**
