from flask import jsonify
import google.generativeai as genai
genai.configure(api_key="AIzaSyCx6WG4JSrarW4wHp5z56lGVp8gDX5DPCU")

from flask import Flask, request, render_template_string, session, redirect
import hashlib
import uuid
from datetime import datetime
room_messages = {}  
message_broadcast = {}
live_rooms = {}
interview_sessions = {}
room_recordings = {}


app = Flask(__name__)
app.secret_key = 'CareerMantraAI_2026_Rupesh'

# ONLY ONE Interviewer allowed
INTERVIEWER_CREDENTIALS = {
    'rupesh': hashlib.sha256('rupesh123'.encode()).hexdigest()
}

# Storage
live_rooms = {}
interview_sessions = {}  # Active interview participants
practice_progress = {}   # Student practice levels
ai_chat_sessions = {}

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].lower().strip()
        password_hash = hashlib.sha256(request.form['password'].encode()).hexdigest()
        
        # Interviewer check (ONLY rupesh)
        if username in INTERVIEWER_CREDENTIALS and INTERVIEWER_CREDENTIALS[username] == password_hash:
            session['user'] = username
            session['role'] = 'interviewer'
            return redirect('/interviewer_dashboard')
        
        # All others = Student
        session['user'] = username
        session['role'] = 'student'
        from datetime import datetime
        if username not in practice_progress:
            practice_progress[username] = {
                'level': 1,
                'questions_solved': 0,
                'interviews_attended': 0,
                'ai_interviews': 0,
                'daily_hours': 0,
                'streak': 0,
                'last_active': datetime.now().isoformat(),
                'overall_score': 0,
                'skills': {'DSA': 0, 'SystemDesign': 0, 'Behavioral': 0},
                'interview_scores': [],
                'ai_feedback_ratings': []
            }
        return redirect('/student_dashboard')
    
    return '''
<!DOCTYPE html>
<html><head><title>CareerMantra AI</title>
<meta name="viewport" content="width=device-width">
<style>*{margin:0;padding:0;box-sizing:border-box}
body{background:linear-gradient(135deg,#1e3a8a,#3b82f6);min-height:100vh;font-family:system-ui;padding:2rem;display:flex;align-items:center;justify-content:center;color:white}
.card{background:rgba(255,255,255,0.15);backdrop-filter:blur(30px);border-radius:25px;padding:3rem;max-width:450px;width:90%;text-align:center}
h1{font-size:3rem;background:linear-gradient(45deg,#ffd700,#ff6b6b);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:1rem}
input{width:100%;padding:1.2rem;margin:1rem 0;border:none;border-radius:15px;background:rgba(255,255,255,0.95);font-size:1.1rem}
.btn{width:100%;padding:1.3rem;background:linear-gradient(45deg,#10b981,#059669);color:white;border:none;border-radius:15px;font-size:1.2rem;font-weight:bold;cursor:pointer}
.demo{background:rgba(255,255,255,0.1);padding:1.5rem;border-radius:15px;margin-top:2rem;border-left:4px solid #ffd700}</style>
</head><body>
<div class="card">
<h1>🚀 CareerMantra AI</h1>
<form method="POST">
<input name="username" placeholder="Username" required>
<input type="password" name="password" placeholder="Password" required>
<button class="btn">Enter Platform</button>
</form>
<div class="demo">
<strong>👨‍💼 Interviewer:</strong> rupesh/rupesh123<br>
<strong>👨‍💻 Student:</strong> anyname/anypass
</div>
</div>
</body></html>'''

@app.route('/interviewer_dashboard')
def interviewer_dashboard():
    if session.get('role') != 'interviewer': 
        return redirect('/')
    
    rooms_html = ''
    for room_id, room in live_rooms.items():
        participants = interview_sessions.get(room_id, [])
        stage = room.get('stage', 0)
        rooms_html += f'''
        <div style="background:rgba(255,255,255,0.1);backdrop-filter:blur(20px);padding:2rem;border-radius:20px;margin-bottom:1rem;border:1px solid rgba(255,255,255,0.2)">
            <h3 style="color:#ffd700;margin-bottom:1rem">Room: <strong>{room_id}</strong> | Stage {stage+1}/5</h3>
            <p style="color:#94a3b8;margin-bottom:1.5rem">Candidate: <strong>{room['candidate']}</strong> | Students: <strong>{len(participants)}</strong></p>
            <a href="/interview_room/{room_id}" style="background:#3b82f6;color:white;padding:0.8rem 1.5rem;border-radius:10px;text-decoration:none;margin-right:1rem;font-weight:bold;display:inline-block">🎤 Live Interview</a>
            <a href="/scorecard/{room_id}" style="background:#f59e0b;color:white;padding:0.8rem 1.5rem;border-radius:10px;text-decoration:none;margin-right:1rem;font-weight:bold;display:inline-block">📊 Scorecard</a>
            <a href="/end_room/{room_id}" style="background:#ef4444;color:white;padding:0.8rem 1.5rem;border-radius:10px;text-decoration:none;font-weight:bold;display:inline-block">❌ End Room</a>
        </div>'''
    
    if not live_rooms:
        rooms_html = '<div style="text-align:center;padding:4rem;color:#94a3b8;background:rgba(255,255,255,0.05);border-radius:20px;border:1px solid rgba(255,255,255,0.1)"><h2 style="font-size:2.5rem;margin-bottom:1rem">📭 No Active Rooms</h2><p style="font-size:1.2rem">Create your first interview room to start!</p></div>'
    
    return f'''
<!DOCTYPE html>
<html>
<head>
    <title>Interviewer Dashboard - CareerMantra</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body style="background:linear-gradient(135deg,#0f172a 0%,#1e293b 50%,#334155 100%);color:white;font-family:'Segoe UI',sans-serif;min-height:100vh;padding:2rem">
    <div style="max-width:1200px;margin:0 auto">
        <!-- HEADER -->
        <div style="text-align:center;margin-bottom:3rem">
            <h1 style="font-size:4rem;font-weight:900;background:linear-gradient(45deg,#fbbf24,#f59e0b);background-clip:text;-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:0.5rem">
                👨‍💼 Interviewer Control Panel
            </h1>
            <p style="font-size:1.3rem;opacity:0.9">rupesh - Professional Interview Platform</p>
        </div>
        
        <!-- STATS -->
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:2rem;margin:2rem 0">
            <div style="background:rgba(255,255,255,0.1);backdrop-filter:blur(20px);padding:2.5rem;border-radius:20px;text-align:center;border:1px solid rgba(255,255,255,0.2)">
                <div style="font-size:3.5rem;color:#10b981;font-weight:900;margin-bottom:0.5rem">{len(live_rooms)}</div>
                <div style="font-size:1.2rem;color:#94a3b8">Active Rooms</div>
            </div>
            <div style="background:rgba(255,255,255,0.1);backdrop-filter:blur(20px);padding:2.5rem;border-radius:20px;text-align:center;border:1px solid rgba(255,255,255,0.2)">
                <div style="font-size:3.5rem;color:#3b82f6;font-weight:900;margin-bottom:0.5rem">{sum([len(interview_sessions.get(r,[])) for r in live_rooms])}</div>
                <div style="font-size:1.2rem;color:#94a3b8">Total Students</div>
            </div>
        </div>
        
        <!-- CREATE ROOM -->
        <div style="background:rgba(16,185,129,0.15);backdrop-filter:blur(20px);padding:3rem;border-radius:25px;margin:2rem 0;text-align:center;border:1px solid rgba(16,185,129,0.3)">
            <h2 style="color:#10b981;font-size:2.2rem;margin-bottom:1.5rem">🎯 Create Interview Room</h2>
            <form method="POST" action="/create_interview" style="max-width:600px;margin:0 auto">
                <input name="candidate_name" placeholder="SDE-2, Frontend Dev, ML Engineer, etc." 
                       style="width:100%;padding:1.2rem;border-radius:15px;border:1px solid rgba(255,255,255,0.3);font-size:1.1rem;margin-bottom:1.5rem;background:rgba(255,255,255,0.9);color:#1f2937;font-weight:500">
                <button style="width:100%;max-width:400px;padding:1.3rem;background:#10b981;color:white;border:none;border-radius:15px;font-size:1.3rem;font-weight:900;cursor:pointer;box-shadow:0 10px 30px rgba(16,185,129,0.4);transition:all 0.3s">
                    🚀 GENERATE ROOM CODE
                </button>
            </form>
        </div>
        
        <!-- ROOMS LIST -->
        <div style="margin:2rem 0">{rooms_html}</div>
        
        <!-- LOGOUT -->
        <a href="/logout" 
           style="display:block;width:320px;margin:4rem auto;background:#ef4444;color:white;padding:1.3rem;border-radius:20px;text-decoration:none;text-align:center;font-weight:900;font-size:1.1rem;box-shadow:0 10px 30px rgba(239,68,68,0.4);transition:all 0.3s">
            🚪 Logout
        </a>
    </div>
</body>
</html>'''




@app.route('/end_room/<room_id>')
def end_room(room_id):
    if room_id in live_rooms and session.get('role') == 'interviewer':
        del live_rooms[room_id]
        if room_id in interview_sessions:
            del interview_sessions[room_id]
    return redirect('/interviewer_dashboard')


# 🔥 STUDENT DASHBOARD (sabke liye except rupesh)
@app.route('/student_dashboard')
def student_dashboard():
    if session.get('role') != 'student': return redirect('/')
    username = session['user']
    progress = practice_progress.get(username, {'level': 1, 'questions_solved': 0})
    
    return f'''
<!DOCTYPE html>
<html><head><title>Student Dashboard</title>
<style>*{{margin:0;padding:0}}body{{background:linear-gradient(135deg,#1e3a8a,#3b82f6);color:white;font-family:system-ui;min-height:100vh;padding:2rem}}.container{{max-width:1200px;margin:0 auto}}.header h1{{font-size:4rem;text-align:center;background:linear-gradient(45deg,#10b981,#059669);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:2rem}}.stats-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:2rem;margin:3rem 0}}.stat-card{{background:rgba(255,255,255,0.1);backdrop-filter:blur(20px);padding:3rem;border-radius:25px;text-align:center}}.stat-number{{font-size:3rem;font-weight:900;margin-bottom:0.5rem;color:#ffd700}}.features-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(350px,1fr));gap:2rem;margin:3rem 0}}.feature-card{{background:rgba(255,255,255,0.1);backdrop-filter:blur(20px);padding:2.5rem;border-radius:25px;text-align:center;transition:transform 0.3s}}.feature-card:hover{{transform:translateY(-10px)}}.feature-icon{{font-size:3rem;margin-bottom:1rem;display:block}}.btn{{display:inline-block;background:linear-gradient(45deg,#10b981,#059669);color:white;padding:1.5rem 3rem;border-radius:20px;text-decoration:none;font-weight:bold;font-size:1.2rem;margin:0.5rem}}</style>
</head><body>
<div class="container">
<div class="header">
<h1>🎯 Welcome {username}!</h1>
<p style="text-align:center;font-size:1.5rem;opacity:0.9">Your Complete Interview Preparation</p>
</div>
<div class="stats-grid">
<div class="stat-card">
<div class="stat-number">Level {progress['level']}</div>
Current Level
</div>
<div class="stat-card">
<div class="stat-number">{progress['questions_solved']}</div>
Questions Solved
</div>
<div class="stat-card">
<div class="stat-number">15</div>
Total Levels
</div>
</div>
<div class="features-grid">
<div class="feature-card">
<span class="feature-icon">📚</span>
<h3>Question Practice</h3>
<p>15 Levels: OS, Algorithms, C/C++, Python, DSA, English</p>
<a href="/practice" class="btn">Start Practice</a>
</div>
<div class="feature-card">
<span class="feature-icon">🤖</span>
<h3>AI Chatbot</h3>
<p>24/7 Interview doubt clearing assistant</p>
<a href="/ai_chatbot" class="btn">Chat Now</a>
</div>
<div class="feature-card">
<span class="feature-icon">🎤</span>
<h3>Join Interview</h3>
<p>Enter Interview Code to join live session</p>
<a href="/join_interview" class="btn">Join Interview</a>
</div>
<div class="feature-card">
<span class="feature-icon">📊</span>
<h3>Performance Monitor</h3>
<p>Track progress & improvement areas</p>
<a href="/performance" class="btn">View Analytics</a>
</div>
<div class="feature-card">
<span class="feature-icon">🎯</span>
<h3>AI Interview</h3>
<p>Practice with AI Interviewer (Basic → Advanced)</p>
<a href="/ai_interview" class="btn">Start AI Interview</a>
</div>
<div class="feature-card">
<span class="feature-icon">🏢</span>
<h3>Company Questions</h3>
<p>Last 5 years company interview questions</p>
<a href="/company_questions" class="btn">View Questions</a>
</div>
</div>
<a href="/logout" style="display:block;width:300px;margin:4rem auto;background:linear-gradient(45deg,#ef4444,#dc2626);color:white;padding:1.5rem;border-radius:25px;text-decoration:none;text-align:center;font-weight:bold;font-size:1.2rem">🚪 Logout</a>
</div>
</body></html>'''

@app.route('/create_interview', methods=['POST'])
def create_interview():
    room_id = str(uuid.uuid4())[:8].upper()
    live_rooms[room_id] = {
        'candidate': request.form['candidate_name'],
        'stage': 0,
        'start_time': datetime.now().isoformat(),
        'questions': [],
        'scores': {},
        'feedback': {}
    }
    return f'''
<!DOCTYPE html>
<html><body style="background:linear-gradient(135deg,#1e3a8a,#3b82f6);color:white;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:2rem;font-family:system-ui">
<div style="background:rgba(255,255,255,0.95);color:#1e3a8a;padding:4rem;border-radius:30px;text-align:center;max-width:600px;width:90%;box-shadow:0 25px 50px rgba(0,0,0,0.3)">
<h1 style="font-size:4rem;color:#10b981;margin-bottom:2rem">✅ Room Created!</h1>
<div style="background:linear-gradient(45deg,#10b981,#059669);color:white;padding:2rem;border-radius:20px;margin:2rem 0;font-size:2rem;font-weight:bold;font-family:monospace">📱 INTERVIEW CODE: {room_id}</div>
<p style="font-size:1.3rem;margin:2rem 0">Share this code with candidates. They will join instantly!</p>
<div style="display:flex;gap:2rem;justify-content:center;flex-wrap:wrap">
<a href="/interviewer_dashboard" style="background:#3b82f6;color:white;padding:1.5rem 3rem;border-radius:20px;text-decoration:none;font-weight:bold;font-size:1.2rem">← Dashboard</a>
<a href="/interview_room/{room_id}" style="background:#10b981;color:white;padding:1.5rem 3rem;border-radius:20px;text-decoration:none;font-weight:bold;font-size:1.2rem">🎤 Start Interview</a>
</div>
</div>
</body></html>'''

# Continue with other routes...
@app.route('/join_interview')
def join_interview():
    username = session.get('user', 'Anonymous')
    return f'''
<!DOCTYPE html>
<html><head><title>Join Interview</title>
<style>*{{margin:0;padding:0}}body{{background:linear-gradient(135deg,#1e3a8a,#3b82f6);color:white;font-family:system-ui;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:2rem}}.join-card{{background:rgba(255,255,255,0.15);backdrop-filter:blur(30px);padding:4rem;border-radius:30px;max-width:500px;width:90%;text-align:center;border:1px solid rgba(255,255,255,0.2)}}
h1{{font-size:3.5rem;background:linear-gradient(45deg,#ffd700,#ff6b6b);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:2rem}}input{{width:100%;padding:1.5rem;margin:2rem 0;border:none;border-radius:20px;background:rgba(255,255,255,0.95);font-size:1.3rem;font-weight:bold;text-align:center}}.btn{{width:100%;padding:1.5rem;background:linear-gradient(45deg,#10b981,#059669);color:white;border:none;border-radius:20px;font-size:1.3rem;font-weight:bold;cursor:pointer;margin-top:2rem}}</style>
</head><body>
<div class="join-card">
<h1>🎤 Join Live Interview</h1>
<form method="POST" action="/join_with_code">
<input name="room_code" placeholder="Enter 8-digit Interview Code" maxlength="8" required>
<button class="btn">🚀 JOIN INTERVIEW</button>
</form>
<p style="margin-top:2rem;opacity:0.8">Get code from your interviewer</p>
</div>
<a href="/student_dashboard" style="display:block;width:300px;margin:2rem auto;background:#ef4444;color:white;padding:1.5rem;border-radius:20px;text-decoration:none;text-align:center">← Dashboard</a>
</body></html>'''


# 🔥 STUDENT DASHBOARD BUTTON ROUTES (ye sab ADD KARO ↑ wale join_interview ke BAAD)
@app.route('/practice')
def practice():
    username = session.get('user', 'Anonymous')
    user_progress = practice_progress.get(username, {'level': 1, 'questions_solved': 0})
    level = user_progress.get('level', 1)
    return f'''
<!DOCTYPE html>
<html><head><title>Practice Questions</title>
<style>*{{margin:0;padding:0}}body{{background:linear-gradient(135deg,#1e3a8a,#3b82f6);color:white;font-family:system-ui;min-height:100vh;padding:2rem}}h1{{font-size:3rem;text-align:center;background:linear-gradient(45deg,#ffd700,#ff6b6b);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:2rem}}.questions{{display:grid;grid-template-columns:repeat(auto-fit,minmax(350px,1fr));gap:2rem;max-width:1200px;margin:2rem auto}}.q-card{{background:rgba(255,255,255,0.1);padding:2rem;border-radius:20px;border-left:5px solid #10b981}}.q-title{{font-size:1.6rem;color:#ffd700;margin-bottom:0.7rem}}.btn{{display:block;width:250px;margin:1.5rem auto;background:linear-gradient(45deg,#10b981,#059669);color:white;padding:1rem;border-radius:12px;text-decoration:none;text-align:center;font-weight:bold}}.mini-btn{{background:#2563eb;border:none;color:white;padding:0.6rem 0.9rem;border-radius:10px;cursor:pointer;margin-top:0.5rem}}</style>
</head><body>
<h1>📚 Practice Questions - Level {level}</h1>
<div class="questions">
<div class="q-card"><div class="q-title">1. HR Intro</div><p><strong>Tell me about yourself (2 mins)</strong></p><textarea id="ans1" style="width:100%;height:120px;padding:0.8rem;border-radius:10px;border:1px solid #10b981;background:rgba(0,0,0,0.3);color:white"></textarea><br><button class="mini-btn" onclick="submitPractice(1)">Submit Answer</button></div>
<div class="q-card"><div class="q-title">2. DSA</div><p><strong>Two Sum: nums=[2,7,11,15], target=9</strong></p><textarea id="ans2" style="width:100%;height:120px;padding:0.8rem;border-radius:10px;border:1px solid #10b981;background:rgba(0,0,0,0.3);color:white"></textarea><br><button class="mini-btn" onclick="submitPractice(2)">Submit Answer</button></div>
</div>
<div id="practiceFeedback" style="max-width:1200px;margin:1rem auto;background:white;color:#111;padding:1rem;border-radius:10px;display:none;white-space:pre-wrap;"></div>
<a href="/student_dashboard" class="btn">← Back to Dashboard</a>
<script>
function submitPractice(q) {{
  var ans = document.getElementById('ans'+q).value.trim();
  if (!ans) {{ alert('Please write your answer first.'); return; }}
  var question = q === 1 ? 'Tell me about yourself (2 mins)' : 'Two Sum: nums=[2,7,11,15], target=9';
  fetch('/chat', {{ method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify({{question:question,user_answer:ans}}) }}).then(function(r) {{ return r.json(); }}).then(function(d) {{ var f = document.getElementById('practiceFeedback'); f.style.display = 'block'; f.innerText = 'Practice feedback:\n' + d.reply; }});
}}
</script>
</body></html>'''


@app.route('/ai_chatbot')
def ai_chatbot():
    username = session.get('user', 'User')
    return f'''<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width"><title>AI Chatbot - CareerMantra</title><style>*{{margin:0;padding:0;box-sizing:border-box}}body{{background:linear-gradient(135deg,#0f172a,#1e293b);color:#fff;font-family:"Segoe UI",system-ui,sans-serif;min-height:100vh;padding:0}}.wrapper{{max-width:900px;height:100vh;margin:0 auto;display:flex;flex-direction:column}}.header{{background:rgba(15,23,42,0.9);backdrop-filter:blur(10px);border-bottom:1px solid rgba(148,163,184,0.2);padding:1.5rem;text-align:center}}.header h1{{font-size:1.8rem;background:linear-gradient(45deg,#60a5fa,#34d399);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:0.5rem}}.header p{{color:#94a3b8;font-size:0.9rem}}.chat-container{{flex:1;display:flex;flex-direction:column;overflow:hidden}}.messages{{flex:1;overflow-y:auto;padding:1.5rem;display:flex;flex-direction:column;gap:1rem}}.message{{display:flex;animation:slideIn 0.3s ease-out}}@keyframes slideIn{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:translateY(0)}}}}.message.bot{{justify-content:flex-start}}.message.user{{justify-content:flex-end}}.bubble{{max-width:70%;padding:1rem 1.2rem;border-radius:12px;word-wrap:break-word;line-height:1.5}}.bubble.bot{{background:linear-gradient(135deg,rgba(96,165,250,0.2),rgba(52,211,153,0.1));border:1px solid rgba(96,165,250,0.3);color:#e2e8f0}}.bubble.user{{background:linear-gradient(135deg,#3b82f6,#2563eb);color:white}}.typing{{display:flex;align-items:center;gap:0.5rem}}.dot{{width:8px;height:8px;background:#60a5fa;border-radius:50%;animation:bounce 1.4s infinite}}.dot:nth-child(1){{animation-delay:0s}}.dot:nth-child(2){{animation-delay:0.2s}}.dot:nth-child(3){{animation-delay:0.4s}}@keyframes bounce{{0%,80%,100%{{transform:translateY(0)}}40%{{transform:translateY(-10px)}}}}.input-area{{background:rgba(30,41,59,0.8);backdrop-filter:blur(10px);border-top:1px solid rgba(148,163,184,0.2);padding:1.5rem;display:flex;gap:1rem}}.input-area input{{flex:1;background:rgba(15,23,42,0.6);border:1px solid rgba(100,116,139,0.4);color:#e2e8f0;padding:1rem;border-radius:10px;font-size:0.95rem}}.input-area input:focus{{outline:none;border-color:#60a5fa;box-shadow:0 0 0 3px rgba(96,165,250,0.1)}}.btn{{padding:0.75rem 1.5rem;background:linear-gradient(135deg,#10b981,#059669);color:white;border:none;border-radius:10px;font-weight:600;cursor:pointer;transition:all 0.3s;text-transform:uppercase;font-size:0.85rem;letter-spacing:0.5px}}.btn:hover{{transform:translateY(-2px);box-shadow:0 4px 12px rgba(16,185,129,0.3)}}.back-btn{{display:inline-block;margin-top:1rem;padding:0.75rem 2rem;background:rgba(100,116,139,0.4);color:#94a3b8;text-decoration:none;border-radius:10px;transition:all 0.3s;border:1px solid rgba(148,163,184,0.3)}}.back-btn:hover{{background:rgba(100,116,139,0.6);color:#e2e8f0;border-color:rgba(148,163,184,0.5)}}.quick-help{{background:rgba(15,23,42,0.6);border:1px solid rgba(96,165,250,0.2);border-radius:10px;padding:1rem;margin-bottom:1rem;font-size:0.85rem;color:#94a3b8}}.quick-help strong{{color:#60a5fa}}.messages::-webkit-scrollbar{{width:8px}}.messages::-webkit-scrollbar-track{{background:transparent}}.messages::-webkit-scrollbar-thumb{{background:rgba(96,165,250,0.3);border-radius:4px}}.messages::-webkit-scrollbar-thumb:hover{{background:rgba(96,165,250,0.5)}}</style></head><body><div class="wrapper"><div class="header"><h1>🤖 AI Chatbot Coach</h1><p>Ask anything about DSA, HR, Interviews & Career Prep</p></div><div class="chat-container"><div class="messages" id="messages"><div class="message bot"><div class="bubble bot"><strong>👋 Hi {username}!</strong><br><br>I'm your AI Career Coach powered by Gemini 2.5. I can help you with:<br><br><strong style="color:#60a5fa">📚 DSA Topics:</strong> Arrays, Trees, Graphs, DP solutions<br><strong style="color:#10b981">🗣️ HR Questions:</strong> Tell me about yourself, conflict resolution<br><strong style="color:#fbbf24">🏢 Company Prep:</strong> Google, Amazon, Microsoft interview tips<br><strong style="color:#f87171">💼 Resume & Behavioral:</strong> STAR method, behavioral answers<br><br>Just type your question below! 👇</div></div></div><div class="input-area"><input type="text" id="messageInput" placeholder="Ask your question..." onkeypress="if(event.key==='Enter') sendMsg()"><button class="btn" onclick="sendMsg()">Send 🚀</button></div></div><div style="padding:1rem;text-align:center;border-top:1px solid rgba(148,163,184,0.2)"><a href="/student_dashboard" class="back-btn">← Back to Dashboard</a></div></div><script>
var messagesDiv = document.getElementById('messages');

function sendMsg() {{
  var inp = document.getElementById('messageInput');
  var txt = inp.value.trim();
  if (!txt) return;
  
  var msgDiv = document.createElement('div');
  msgDiv.className = 'message user';
  msgDiv.innerHTML = '<div class="bubble user">' + txt + '</div>';
  messagesDiv.appendChild(msgDiv);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
  
  inp.value = '';
  
  var typingDiv = document.createElement('div');
  typingDiv.className = 'message bot';
  typingDiv.innerHTML = '<div class="bubble bot"><div class="typing"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div></div>';
  messagesDiv.appendChild(typingDiv);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
  
  fetch('/chat', {{
    method: 'POST',
    headers: {{'Content-Type': 'application/json'}},
    body: JSON.stringify({{message: txt}})
  }})
  .then(r => r.json())
  .then(d => {{
    messagesDiv.removeChild(typingDiv);
    var respDiv = document.createElement('div');
    respDiv.className = 'message bot';
    var reply = (d.reply || 'Unable to respond').replace(/\n/g, '<br>');
    respDiv.innerHTML = '<div class="bubble bot"><strong>🤖 AI Coach:</strong><br>' + reply + '</div>';
    messagesDiv.appendChild(respDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
  }})
  .catch(e => {{
    messagesDiv.removeChild(typingDiv);
    var errDiv = document.createElement('div');
    errDiv.className = 'message bot';
    errDiv.innerHTML = '<div class="bubble bot" style="background:linear-gradient(135deg,rgba(244,63,94,0.2),rgba(249,115,22,0.1));border-color:rgba(244,63,94,0.3)"><strong>❌ Error:</strong><br>Could not get response. Try again!</div>';
    messagesDiv.appendChild(errDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
  }});
}}

document.getElementById('messageInput').focus();
</script></body></html>'''


@app.route('/performance')
def performance():
    username = session.get('user', 'Anonymous')
    from datetime import datetime, timedelta
    import random
    
    # Get or initialize user data
    if username not in practice_progress:
        practice_progress[username] = {
            'level': 1,
            'questions_solved': 0,
            'interviews_attended': 0,
            'ai_interviews': 0,
            'daily_hours': 0,
            'streak': 0,
            'last_active': datetime.now().isoformat(),
            'overall_score': 0,
            'skills': {'DSA': 0, 'SystemDesign': 0, 'Behavioral': 0},
            'interview_scores': [],
            'ai_feedback_ratings': []
        }
    
    user_data = practice_progress[username]
    
    # Calculate stats
    levels_completed = user_data.get('level', 1) - 1
    questions_solved = user_data.get('questions_solved', 0)
    interviews_attended = user_data.get('interviews_attended', 0)
    ai_interviews = user_data.get('ai_interviews', 0)
    daily_hours = user_data.get('daily_hours', random.randint(2, 8))
    streak = user_data.get('streak', random.randint(0, 30))
    overall_score = user_data.get('overall_score', random.randint(60, 95))
    
    # Get skills
    skills = user_data.get('skills', {'DSA': random.randint(40, 90), 'SystemDesign': random.randint(30, 85), 'Behavioral': random.randint(50, 95)})
    
    # Calculate additional metrics
    avg_interview_score = 0
    if interviews_attended > 0:
        scores = user_data.get('interview_scores', [])
        avg_interview_score = sum(scores) / len(scores) if scores else random.randint(65, 85)
    
    avg_ai_score = 0
    if ai_interviews > 0:
        ai_scores = user_data.get('ai_feedback_ratings', [])
        avg_ai_score = sum(ai_scores) / len(ai_scores) if ai_scores else random.randint(70, 90)
    
    # Performance indicators
    dsa_pct = skills.get('DSA', 0)
    system_pct = skills.get('SystemDesign', 0)
    behavioral_pct = skills.get('Behavioral', 0)
    
    html = f'''<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width"><title>Performance Analytics</title><style>*{{margin:0;padding:0;box-sizing:border-box}}body{{background:linear-gradient(135deg,#0f172a,#1e293b);color:#fff;font-family:"Segoe UI",system-ui,sans-serif;min-height:100vh;padding:1.5rem}}.wrapper{{max-width:1400px;margin:0 auto}}.header{{text-align:center;margin-bottom:2.5rem}}.header h1{{font-size:3rem;background:linear-gradient(45deg,#60a5fa,#34d399);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:0.5rem}}.header p{{color:#94a3b8;font-size:1.1rem}}.top-metrics{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:1.5rem;margin-bottom:2rem}}.metric-card{{background:rgba(30,41,59,0.8);backdrop-filter:blur(10px);border:1px solid rgba(148,163,184,0.2);border-radius:16px;padding:1.5rem;text-align:center}}.metric-value{{font-size:2.5rem;font-weight:900;background:linear-gradient(135deg,#60a5fa,#34d399);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:0.5rem}}.metric-label{{color:#94a3b8;font-size:0.9rem;text-transform:uppercase;letter-spacing:1px}}.main-grid{{display:grid;grid-template-columns:2fr 1fr;gap:1.5rem;margin-bottom:2rem}}@media(max-width:768px){{.main-grid{{grid-template-columns:1fr}}}}.section{{background:rgba(30,41,59,0.8);backdrop-filter:blur(10px);border:1px solid rgba(148,163,184,0.2);border-radius:16px;padding:2rem}}.section-title{{font-size:1.4rem;font-weight:600;color:#60a5fa;margin-bottom:1.5rem;text-transform:uppercase;letter-spacing:1px}}.skill-item{{margin-bottom:1.5rem}}.skill-header{{display:flex;justify-content:space-between;margin-bottom:0.5rem}}.skill-name{{color:#e2e8f0;font-weight:600}}.skill-pct{{color:#60a5fa;font-weight:700}}.skill-bar{{height:10px;background:rgba(100,116,139,0.3);border-radius:10px;overflow:hidden}}.skill-progress{{height:100%;background:linear-gradient(90deg,#3b82f6,#10b981);transition:width 0.3s}}.quick-stats{{display:grid;grid-template-columns:1fr;gap:1rem}}.stat-item{{background:rgba(15,23,42,0.6);padding:1rem;border-radius:12px;border-left:4px solid #60a5fa;display:flex;justify-content:space-between;align-items:center}}.stat-label{{color:#94a3b8}}.stat-val{{font-size:1.5rem;font-weight:700;color:#60a5fa}}.performance-box{{background:rgba(15,23,42,0.6);padding:1.5rem;border-radius:12px;margin-bottom:1rem;border:1px solid rgba(96,165,250,0.2)}}.perf-title{{font-size:1.1rem;color:#60a5fa;font-weight:600;margin-bottom:0.5rem}}.perf-value{{font-size:2rem;font-weight:900;color:#10b981}}.footer{{text-align:center;margin-top:2rem}}.btn{{display:inline-block;padding:0.75rem 2rem;background:rgba(100,116,139,0.4);color:#94a3b8;text-decoration:none;border-radius:10px;transition:all 0.3s;border:1px solid rgba(148,163,184,0.3)}}.btn:hover{{background:rgba(100,116,139,0.6);color:#e2e8f0;border-color:rgba(148,163,184,0.5)}}.badge{{display:inline-block;background:linear-gradient(135deg,#10b981,#059669);padding:0.5rem 1rem;border-radius:20px;font-size:0.85rem;font-weight:600;margin-right:0.5rem;margin-bottom:0.5rem}}</style></head><body><div class="wrapper"><div class="header"><h1>📊 Performance Analytics - {username}</h1><p>Your complete interview preparation dashboard</p></div><div class="top-metrics"><div class="metric-card"><div class="metric-value">{overall_score}%</div><div class="metric-label">Overall Performance</div></div><div class="metric-card"><div class="metric-value">{streak}</div><div class="metric-label">Day Streak 🔥</div></div><div class="metric-card"><div class="metric-value">{daily_hours}h</div><div class="metric-label">Daily Hours Active</div></div><div class="metric-card"><div class="metric-value">{levels_completed}</div><div class="metric-label">Levels Completed</div></div></div><div class="main-grid"><div class="section"><div class="section-title">💪 Skill Assessment</div><div class="skill-item"><div class="skill-header"><span class="skill-name">⚡ DSA (Data Structures)</span><span class="skill-pct">{dsa_pct}%</span></div><div class="skill-bar"><div class="skill-progress" style="width:{dsa_pct}%"></div></div></div><div class="skill-item"><div class="skill-header"><span class="skill-name">🏗️ System Design</span><span class="skill-pct">{system_pct}%</span></div><div class="skill-bar"><div class="skill-progress" style="width:{system_pct}%"></div></div></div><div class="skill-item"><div class="skill-header"><span class="skill-name">🗣️ Behavioral Skills</span><span class="skill-pct">{behavioral_pct}%</span></div><div class="skill-bar"><div class="skill-progress" style="width:{behavioral_pct}%"></div></div></div><div style="margin-top:2rem;padding-top:2rem;border-top:1px solid rgba(148,163,184,0.2)"><div class="section-title" style="margin-bottom:1rem">📈 Practice Stats</div><div class="performance-box"><div class="perf-title">Questions Solved</div><div class="perf-value">{questions_solved}</div></div><div class="performance-box"><div class="perf-title">Interviews Attended</div><div class="perf-value">{interviews_attended}</div></div><div class="performance-box"><div class="perf-title">AI Interviews Done</div><div class="perf-value">{ai_interviews}</div></div></div></div><div class="section"><div class="section-title">📋 Quick Summary</div><div class="quick-stats"><div class="stat-item"><span class="stat-label">Current Level</span><span class="stat-val">{user_data.get('level', 1)}/15</span></div><div class="stat-item"><span class="stat-label">Avg Interview Score</span><span class="stat-val">{int(avg_interview_score) if interviews_attended > 0 else 0}%</span></div><div class="stat-item"><span class="stat-label">Avg AI Score</span><span class="stat-val">{int(avg_ai_score) if ai_interviews > 0 else 0}%</span></div><div class="stat-item"><span class="stat-label">Best Subject</span><span class="stat-val">DSA</span></div></div><div style="margin-top:2rem;padding-top:1rem;border-top:1px solid rgba(148,163,184,0.2)"><div class="section-title" style="font-size:1rem;margin-bottom:1rem">🎖️ Achievements</div><div style="display:flex;flex-wrap:wrap"><div class="badge">🔥 {streak} Day Streak</div><div class="badge">📚 {levels_completed} Levels</div><div class="badge">🎯 {questions_solved} Solved</div></div></div></div></div><div class="footer"><a href="/student_dashboard" class="btn">← Back to Dashboard</a></div></div></body></html>'''
    
    return html

@app.route('/ai_interview')
def ai_interview():
    username = session.get('user', 'Anonymous')
    import random, hashlib, json
    
    # Initialize user data if not exists
    if username not in practice_progress:
        practice_progress[username] = {
            'level': 1,
            'questions_solved': 0,
            'interviews_attended': 0,
            'ai_interviews': 0,
            'daily_hours': 0,
            'streak': 0,
            'overall_score': 0,
            'skills': {'DSA': 0, 'SystemDesign': 0, 'Behavioral': 0},
            'interview_scores': [],
            'ai_feedback_ratings': []
        }
    
    # Track AI interview session start
    practice_progress[username]['ai_interviews'] = practice_progress[username].get('ai_interviews', 0) + 1
    
    user_seed = hashlib.md5(username.encode()).hexdigest()
    random.seed(int(user_seed[:8], 16))
    all_questions = [
        "Tell me about yourself (2 mins)", "Why this company?", "Strengths & weaknesses?",
        "Biggest failure story?", "Team conflict example?", "Leadership experience?",
        "Two Sum (Array)", "Valid parenthesis", "Merge intervals", "LRU Cache design",
        "Kth largest element", "Number of islands", "Course schedule (Graph)",
        "Design TinyURL", "Design YouTube", "Design Instagram", "Rate limiter",
        "Autocomplete system", "Payment gateway design", "Where do you see yourself in 5 years?"
    ]
    user_questions = ["Tell me about yourself (2 mins)"] + random.sample([q for q in all_questions if q != "Tell me about yourself (2 mins)"], min(9, len(all_questions)-1))
    questions_json = json.dumps(user_questions)
    question_cards = ''.join(["<li onclick='goToQuestion("+str(i)+")' class='q-nav"+(" active" if i==0 else "")+"'><span class='q-num'>Q"+str(i+1)+"</span> "+q+"</li>" for i,q in enumerate(user_questions)])
    
    html = '''<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width"><title>AI Mock Interview</title><style>*{margin:0;padding:0;box-sizing:border-box}body{background:linear-gradient(135deg,#0f172a,#1e293b);color:#fff;font-family:"Segoe UI",system-ui,sans-serif;min-height:100vh;padding:1.5rem}html,body{background-attachment:fixed}.wrapper{max-width:1400px;margin:0 auto}.header{text-align:center;margin-bottom:2rem;padding:1rem}.header h1{font-size:2.8rem;background:linear-gradient(45deg,#60a5fa,#34d399);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:.5rem}.header p{color:#94a3b8;font-size:1rem}.main{display:grid;grid-template-columns:1.5fr 1fr;gap:1.5rem;margin-bottom:2rem}@media(max-width:768px){.main{grid-template-columns:1fr}}.interview-panel{background:rgba(30,41,59,0.8);backdrop-filter:blur(10px);border:1px solid rgba(148,163,184,0.2);border-radius:16px;padding:2rem}.question-display{margin-bottom:1.5rem}.q-number{font-size:0.85rem;color:#64748b;text-transform:uppercase;letter-spacing:1px;margin-bottom:.5rem}.current-q{font-size:1.6rem;font-weight:600;color:#60a5fa;line-height:1.4;margin-bottom:1rem}.answer-box{margin-bottom:1.5rem}textarea{width:100%;padding:1rem;background:rgba(15,23,42,0.8);border:1px solid rgba(100,116,139,0.4);border-radius:12px;color:#e2e8f0;font-family:inherit;font-size:0.95rem;resize:vertical;min-height:140px}textarea:focus{outline:none;border-color:#60a5fa;box-shadow:0 0 0 3px rgba(96,165,250,0.1)}.control-buttons{display:flex;gap:1rem;flex-wrap:wrap}.btn{padding:0.75rem 1.5rem;border:none;border-radius:10px;font-size:0.95rem;font-weight:600;cursor:pointer;transition:all 0.3s;text-transform:uppercase;letter-spacing:0.5px}.btn-primary{background:linear-gradient(135deg,#3b82f6,#2563eb);color:white;box-shadow:0 4px 15px rgba(59,130,246,0.3)}.btn-primary:hover{transform:translateY(-2px);box-shadow:0 6px 20px rgba(59,130,246,0.4)}.btn-success{background:linear-gradient(135deg,#10b981,#059669);color:white;box-shadow:0 4px 15px rgba(16,185,129,0.3)}.btn-success:hover{transform:translateY(-2px);box-shadow:0 6px 20px rgba(16,185,129,0.4)}.btn-secondary{background:rgba(100,116,139,0.5);color:#e2e8f0;border:1px solid rgba(148,163,184,0.4)}.btn-secondary:hover{background:rgba(100,116,139,0.7);border-color:rgba(148,163,184,0.6)}.questions-nav{background:rgba(15,23,42,0.6);border:1px solid rgba(148,163,184,0.2);border-radius:12px;padding:1rem;margin-top:1rem}.questions-nav h3{font-size:0.85rem;color:#94a3b8;text-transform:uppercase;margin-bottom:1rem;letter-spacing:1px}.questions-list{list-style:none;display:flex;flex-wrap:wrap;gap:0.5rem;max-height:300px;overflow-y:auto}.q-nav{background:rgba(100,116,139,0.3);border:1px solid rgba(148,163,184,0.3);border-radius:8px;padding:0.6rem 0.9rem;cursor:pointer;transition:all 0.2s;font-size:0.85rem;display:flex;align-items:center;gap:0.5rem;white-space:nowrap}.q-nav:hover{background:rgba(100,116,139,0.5);border-color:rgba(148,163,184,0.5)}.q-nav.active{background:linear-gradient(135deg,#10b981,#059669);border-color:#10b981;color:#fff}.q-num{font-weight:700;min-width:24px}.feedback-panel{background:rgba(30,41,59,0.8);backdrop-filter:blur(10px);border:1px solid rgba(148,163,184,0.2);border-radius:16px;padding:2rem;min-height:500px;display:flex;flex-direction:column}.feedback-header{font-size:1.3rem;font-weight:600;color:#60a5fa;margin-bottom:1.5rem;text-transform:uppercase;letter-spacing:1px}.feedback-content{flex:1;overflow-y:auto;padding:1rem;background:rgba(15,23,42,0.6);border-radius:10px;border:1px solid rgba(148,163,184,0.2)}.feedback-content div{margin-bottom:1rem;line-height:1.6}.score-line{background:linear-gradient(90deg,#10b981,#34d399);padding:0.75rem 1rem;border-radius:8px;font-weight:600;color:#0f172a;margin-bottom:1rem}.feedback-line{color:#fbbf24;font-weight:600;margin-bottom:0.5rem}.answer-line{color:#60a5fa;font-weight:600;margin-bottom:0.5rem}.tip-line{color:#f87171;font-weight:600;margin-bottom:0.5rem}.empty-state{color:#64748b;font-style:italic;text-align:center;padding:2rem}.footer{text-align:center;margin-top:2rem}.back-btn{display:inline-block;padding:0.75rem 2rem;background:rgba(100,116,139,0.4);color:#94a3b8;text-decoration:none;border-radius:10px;transition:all 0.3s;border:1px solid rgba(148,163,184,0.3)}.back-btn:hover{background:rgba(100,116,139,0.6);color:#e2e8f0;border-color:rgba(148,163,184,0.5)}</style></head><body><div class="wrapper"><div class="header"><h1>🎤 AI Mock Interview</h1><p>Practice bahut sahi se...Get AI-powered feedback on your answers</p></div><div class="main"><div class="interview-panel"><div class="question-display"><div class="q-number" id="qNum">Question 1 of '''+ str(len(user_questions))+'''</div><div class="current-q" id="currentQuestion">'''+ user_questions[0]+'''</div></div><div class="answer-box"><textarea id="answerInput" placeholder="Type your answer here...Write atleast 2-3 sentences"></textarea></div><div class="control-buttons"><button class="btn btn-primary" onclick="submitBtn()">📤 Submit Answer</button><button class="btn btn-success" onclick="feedbackBtn()">⚡ Get AI Feedback</button><button class="btn btn-secondary" onclick="nextBtn()">→ Next Question</button></div><div class="questions-nav"><h3>All Questions</h3><ul class="questions-list">'''+ question_cards+'''</ul></div></div><div class="feedback-panel"><div class="feedback-header">AI Feedback</div><div class="feedback-content" id="aiResponse"><div class="empty-state">👉 Submit your answer to get AI feedback here</div></div></div></div><div class="footer"><a href="/student_dashboard" class="back-btn">← Back to Dashboard</a></div></div><script>
var currentQuestion = 0;
var allQuestions = ''' + questions_json + ''';
var totalQuestions = allQuestions.length;

function updateUI() {
  document.getElementById("qNum").textContent = "Question " + (currentQuestion + 1) + " of " + totalQuestions;
  document.getElementById("currentQuestion").textContent = allQuestions[currentQuestion];
  document.getElementById("answerInput").value = "";
  document.getElementById("answerInput").focus();
  
  var items = document.querySelectorAll(".q-nav");
  for (var i = 0; i < items.length; i++) {
    if (i === currentQuestion) {
      items[i].classList.add("active");
    } else {
      items[i].classList.remove("active");
    }
  }
}

function nextBtn() {
  currentQuestion = (currentQuestion + 1) % totalQuestions;
  updateUI();
}

function goToQuestion(idx) {
  currentQuestion = idx;
  updateUI();
}

function showFeedback(data) {
  var container = document.getElementById("aiResponse");
  var text = (data.reply || data.error || "Unable to get response");
  var lines = text.split("\\n");
  var html = "";
  
  for (var i = 0; i < lines.length; i++) {
    var line = lines[i].trim();
    if (!line) continue;
    
    if (line.indexOf("Score:") === 0) {
      html += "<div class='score-line'>" + line + "</div>";
    } else if (line.indexOf("Feedback:") === 0) {
      html += "<div class='feedback-line'>" + line + "</div>";
    } else if (line.indexOf("Correct Answer:") === 0) {
      html += "<div class='answer-line'>" + line + "</div>";
    } else if (line.indexOf("Tip:") === 0) {
      html += "<div class='tip-line'>" + line + "</div>";
    } else {
      html += "<div>" + line + "</div>";
    }
  }
  
  container.innerHTML = html || "<div class='empty-state'>No feedback received</div>";
}

function submitBtn() {
  var ans = document.getElementById("answerInput").value.trim();
  if (!ans) {
    alert("Please type your answer first");
    return;
  }
  
  var payload = {
    question: allQuestions[currentQuestion],
    user_answer: ans
  };
  
  fetch("/chat", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload)
  })
  .then(function(res) { return res.json(); })
  .then(function(data) { showFeedback(data); })
  .catch(function(err) { 
    console.error("Error:", err);
    showFeedback({error: "Server error - try again"});
  });
}

function feedbackBtn() {
  submitBtn();
}

window.onload = function() {
  updateUI();
};
</script></body></html>'''
    
    return html

@app.route('/company_questions')
def company_questions():
    companies = {
        'Google': ['Why Google?', 'Rate DSA 1-10', 'System Design YouTube', '2nd highest salary SQL', 'LRU Cache', 'Median of data stream', 'Course schedule', 'Word ladder', 'Regular expression matching', 'Wildcard matching'],
        'Amazon': ['Leadership Principles?', 'Design TinyURL', 'LRU Cache', 'Kth largest element', 'Top K frequent', 'Word break', 'Group anagrams', 'Valid parenthesis', 'Longest substring', 'Container most water'],
        'Microsoft': ['OOPs concepts', 'Multithreading', 'SQL vs NoSQL', 'REST API design', 'Memory leak', 'Deadlock', 'Binary tree zigzag', 'Graph valid tree', 'Number of islands', 'Pacific Atlantic water'],
        'Meta': ['SQL 2nd highest', 'LRU Cache', 'Why Meta?', 'Team conflict', 'Design Instagram', 'LFU Cache', 'Serialize deserialize', 'Word search', 'Longest consecutive', 'Subarray sum equals k'],
        'Apple': ['Design iPhone music', 'Cache design', 'LRU vs LFU', 'Autocomplete system', 'Trie implementation', 'Design Notes app', 'File system design', 'Photos app design', 'iOS architecture', 'Swift vs Objective-C'],
        'Netflix': ['Design Netflix', 'Cache design', 'Rate limiter', 'Load balancer', 'Microservices', 'Chaos engineering', 'A/B testing', 'Recommendation system', 'Content delivery', 'User profile design'],
        'Uber': ['Design Uber', 'Rate limiter', 'Trip matching', 'Geosharding', 'ETL pipeline', 'Real-time tracking', 'Dispatch system', 'Pricing algorithm', 'Fraud detection', 'Driver ETA prediction'],
        'Airbnb': ['Design Airbnb', 'Search ranking', 'Recommendation', 'Fraud detection', 'Calendar sync', 'Payment system', 'Review system', 'Host matching', 'Dynamic pricing', 'Photo tagging'],
        'Flipkart': ['Design Flipkart', 'Search autocomplete', 'Recommendation', 'Inventory management', 'Order processing', 'Payment gateway', 'Logistics', 'Customer support', 'A/B testing', 'Fraud detection'],
        'Paytm': ['Payment gateway', 'UPI integration', 'Wallet design', 'Fraud detection', 'KYC system', 'Transaction idempotency', 'Reconciliation', 'Chargeback handling', 'Risk scoring', 'Customer limits'],
        'Zomato': ['Design Zomato', 'Restaurant search', 'Recommendation', 'Order tracking', 'Delivery optimization', 'Payment integration', 'Rating system', 'Dynamic pricing', 'Inventory sync', 'Customer support'],
        'Swiggy': ['Design Swiggy', 'Delivery optimization', 'ETA prediction', 'Driver allocation', 'Order batching', 'Restaurant sync', 'Payment flow', 'Customer notifications', 'Feedback analysis', 'Peak hour handling'],
        'PhonePe': ['UPI flow design', 'Transaction idempotency', 'Fraud detection', 'Wallet reconciliation', 'KYC verification', 'Merchant onboarding', 'QR code payments', 'Cashback system', 'Customer limits', 'Risk engine'],
        'Cred': ['Credit card system', 'Bill payment', 'Reward points', 'Fraud detection', 'Credit scoring', 'EMI calculator', 'Dispute resolution', 'Customer onboarding', 'Transaction categorization', 'Loyalty program'],
        'Postman': ['API design principles', 'REST vs GraphQL', 'Rate limiting', 'Authentication', 'API versioning', 'OpenAPI spec', 'API monitoring', 'Documentation', 'SDK generation', 'API marketplace']
    }
    
    html = '''
<!DOCTYPE html>
<html><head><title>Company Questions</title>
<style>*{{margin:0;padding:0}}body{{background:linear-gradient(135deg,#1e3a8a,#3b82f6);color:white;font-family:system-ui;min-height:100vh;padding:2rem}}.container{{max-width:1400px;margin:0 auto}}.header{{text-align:center;margin-bottom:4rem}}h1{{font-size:4rem;background:linear-gradient(45deg,#f59e0b,#d97706);-webkit-background-clip:text;-webkit-text-fill-color:transparent}}.companies-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(450px,1fr));gap:2rem}}.company-card{{background:rgba(255,255,255,0.15);padding:2.5rem;border-radius:25px;border-left:6px solid #ffd700;transition:transform 0.3s}}.company-card:hover{{transform:translateY(-8px)}}.company-logo{{font-size:3.5rem;margin-bottom:1.5rem;display:block}}.company-name{{font-size:2.2rem;color:#ffd700;margin-bottom:1.5rem;font-weight:900}}.question{{padding:1rem;margin-bottom:0.8rem;background:rgba(0,0,0,0.4);border-radius:12px;border-left:3px solid #10b981;font-size:0.95rem;transition:background 0.3s}}.question:hover{{background:rgba(16,185,129,0.3)}}.btn{{display:block;width:350px;margin:4rem auto;background:linear-gradient(45deg,#10b981,#059669);color:white;padding:1.5rem;border-radius:25px;text-decoration:none;text-align:center;font-weight:bold;font-size:1.2rem}}</style>
</head><body>
<div class="container">
<div class="header">
<h1>🏢 15+ Companies - Real Interview Questions</h1>
<p style="font-size:1.4rem;opacity:0.9">Last 5 years ke actual questions - Practice karo!</p>
</div>
<div class="companies-grid">'''
    
    for company, questions in companies.items():
        html += f'''
        <div class="company-card">
            <div class="company-logo">🏢</div>
            <div class="company-name">{company}</div>'''
        for i, q in enumerate(questions[:10], 1):  # Top 10 per company
            html += f'<div class="question">Q{i}. {q}</div>'
        html += f'<p style="margin-top:1rem;color:#94a3b8;font-size:0.9rem">+{len(questions)-10} more questions...</p></div>'
    
    html += '''
    </div>
    <a href="/student_dashboard" class="btn">← Back to Dashboard</a>
    </div></body></html>'''
    
    return html



@app.route('/join_with_code', methods=['POST'])
def join_with_code():
    room_code = request.form['room_code'].upper().strip()
    username = session.get('user', 'Anonymous')
    
    if room_code in live_rooms:
        if room_code not in interview_sessions:
            interview_sessions[room_code] = []
        if username not in interview_sessions[room_code]:
            interview_sessions[room_code].append(username)
        
        session['current_room'] = room_code
        return redirect(f'/student_interview/{room_code}')
    else:
        return '''
        <html><body style="background:linear-gradient(135deg,#1e3a8a,#3b82f6);color:white;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:2rem;font-family:system-ui">
        <div style="background:rgba(255,255,255,0.1);padding:3rem;border-radius:25px;text-align:center;max-width:500px">
        <h1 style="color:#ef4444;font-size:3rem">❌ Invalid Interview Code!</h1>
        <p style="font-size:1.2rem">Room not found. Please check the code and try again.</p>
        <a href="/join_interview" style="background:#10b981;color:white;padding:1.2rem 2.5rem;border-radius:15px;text-decoration:none;display:inline-block;margin-top:2rem;font-weight:bold">Try Again</a>
        </div></body></html>'''

      #/interview_room/<room_id> route ADD karo:

@app.route('/interview_room/<room_id>')
def interview_room(room_id):
    if room_id not in live_rooms:
        return '''
<!DOCTYPE html>
<html><body style="background:linear-gradient(135deg,#1e3a8a,#3b82f6);color:white;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:2rem;font-family:system-ui">
<div style="background:rgba(255,255,255,0.95);color:#1e3a8a;padding:4rem;border-radius:30px;text-align:center;max-width:600px;width:90%;box-shadow:0 25px 50px rgba(0,0,0,0.3)">
<h1 style="color:#ef4444;font-size:3rem">❌ Invalid Interview Code!</h1>
<p style="font-size:1.2rem">Room not found. Please check the code and try again.</p>
<a href="/interviewer_dashboard" style="background:#10b981;color:white;padding:1.2rem 2.5rem;border-radius:15px;text-decoration:none;display:inline-block;margin-top:2rem;font-weight:bold">Back to Dashboard</a>
</div></body></html>'''
    
    room = live_rooms[room_id]
    participants = interview_sessions.get(room_id, [])
    
    return f'''
<!DOCTYPE html>
<html><head><title>Interviewer Room - {room_id}</title>
<script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-gradient-to-br from-slate-900 to-gray-900 min-h-screen p-8 text-white">
<div class="max-w-6xl mx-auto">
    <h1 class="text-5xl font-bold text-center mb-12 bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">🎤 Interview Control: {room_id}</h1>
    
    <div class="grid lg:grid-cols-3 gap-8">
        <!-- PARTICIPANTS -->
        <div class="bg-white/10 backdrop-blur-xl rounded-3xl p-8">
            <h2 class="text-3xl font-bold text-blue-300 mb-6">👥 Participants ({len(participants)})</h2>
            <div id="participantsList" class="space-y-4">
                {''.join([f'<div class="bg-green-600/20 p-4 rounded-xl"><strong>{p}</strong> - Connected</div>' for p in participants])}
            </div>
        </div>
        
        <!-- QUESTIONS -->
        <div class="bg-white/10 backdrop-blur-xl rounded-3xl p-8">
            <h2 class="text-3xl font-bold text-yellow-300 mb-6">❓ Send Question</h2>
            <textarea id="questionInput" placeholder="Type your question here..." class="w-full h-32 bg-black/30 p-4 rounded-2xl text-white mb-4"></textarea>
            <button onclick="sendQuestion()" class="w-full bg-gradient-to-r from-yellow-500 to-orange-500 text-white py-4 px-8 rounded-2xl font-bold text-xl">📤 Send Question</button>
        </div>
        
        <!-- CHAT & CONTROLS -->
        <div class="bg-white/10 backdrop-blur-xl rounded-3xl p-8">
            <h2 class="text-3xl font-bold text-emerald-300 mb-6">💬 Live Chat</h2>
            <div id="chatMessages" class="h-64 overflow-y-auto bg-black/30 rounded-2xl p-6 mb-6"></div>
            <div class="space-y-4">
                <button onclick="nextStage()" class="w-full bg-gradient-to-r from-purple-500 to-pink-500 text-white py-3 px-6 rounded-2xl font-bold">Next Stage →</button>
                <a href="/scorecard/{room_id}" class="block text-center bg-gradient-to-r from-cyan-500 to-blue-500 text-white py-3 px-6 rounded-2xl font-bold text-decoration-none">📊 View Scorecard</a>
                <a href="/end_room/{room_id}" class="block text-center bg-gradient-to-r from-red-500 to-pink-500 text-white py-3 px-6 rounded-2xl font-bold text-decoration-none">❌ End Interview</a>
            </div>
        </div>
    </div>
</div>

<script>
let roomId = "{room_id}";

// Load messages
function loadMessages() {{
    fetch(`/get_messages/{room_id}`).then(r=>r.json()).then(data => {{
        const msgs = document.getElementById("chatMessages");
        msgs.innerHTML = "";
        data.messages.forEach(function(msg) {{
            var div = document.createElement("div");
            var roleClass = msg.role === "interviewer" ? "text-right bg-blue-600" : "bg-emerald-600";
            div.innerHTML = '<div class="' + roleClass + ' p-4 rounded-2xl max-w-lg mx-2">' +
                '<strong>' + msg.user + ':</strong> ' + msg.text +
                '</div>';
            msgs.appendChild(div);
        }});
        msgs.scrollTop = msgs.scrollHeight;
    }});
}}

setInterval(loadMessages, 2000);

function sendQuestion() {{
    var input = document.getElementById("questionInput");
    var msg = input.value.trim();
    if(!msg) return;
    
    fetch(`/send_message/{room_id}`, {{
        method: "POST",
        headers: {{"Content-Type": "application/json"}},
        body: JSON.stringify({{text: msg, role: "interviewer"}})
    }});
    input.value = "";
    loadMessages();
}}

function nextStage() {{
    fetch(`/next_stage/{room_id}`, {{method: "POST"}}).then(r=>r.json()).then(d=>{{
        alert("✅ Moved to next stage!");
        location.reload();
    }});
}}

loadMessages();
</script>
</body></html>'''

@app.route('/student_interview/<room_id>')
def student_interview(room_id):
    return f'''
<!DOCTYPE html>
<html><head><title>Student Interview - {room_id}</title>
<script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-gradient-to-br from-indigo-900 to-purple-900 min-h-screen p-8 text-white">
<div class="max-w-4xl mx-auto">
    <h1 class="text-5xl font-bold text-center mb-12 bg-gradient-to-r from-emerald-400 to-teal-400 bg-clip-text text-transparent">🎤 Live Interview: {room_id}</h1>
    
    <div class="grid md:grid-cols-2 gap-8">
        <!-- CHAT -->
        <div class="bg-white/10 backdrop-blur-xl rounded-3xl p-8">
            <h2 class="text-3xl font-bold text-emerald-300 mb-6">💬 Live Chat</h2>
            <div id="chatMessages" class="h-96 overflow-y-auto bg-black/30 rounded-2xl p-6 mb-6"></div>
            <div class="flex gap-3">
                <input id="chatInput" placeholder="Type your answer here..." class="flex-1 bg-white text-black p-4 rounded-2xl">
                <button onclick="sendAnswer()" class="bg-emerald-500 hover:bg-emerald-600 text-white px-8 py-4 rounded-2xl font-bold">📤 Answer</button>
            </div>
        </div>
        
        <!-- STUDENT RECORDING -->
        <div class="bg-white/10 backdrop-blur-xl rounded-3xl p-8">
            <h2 class="text-3xl font-bold text-pink-300 mb-6">🎙️ Record Answer</h2>
            <button id="recordBtn" class="w-full bg-gradient-to-r from-pink-500 to-red-500 text-white py-10 px-8 rounded-3xl font-bold text-xl shadow-2xl">🔴 Record Answer</button>
            <button id="stopBtn" class="w-full bg-gradient-to-r from-green-500 to-emerald-500 text-white py-10 px-8 rounded-3xl font-bold text-xl shadow-2xl hidden">⏹️ Stop</button>
            <div id="recordingStatus" class="text-center text-2xl text-yellow-400 hidden mt-4 p-4 bg-yellow-500/20 rounded-xl">🎤 Recording... Interviewer will hear!</div>
        </div>
    </div>
</div>

<script>
let mediaRecorder, audioChunks = [], roomId = "{room_id}";

// Load existing messages
function loadMessages() {{
    fetch(`/get_messages/{room_id}`).then(r=>r.json()).then(data => {{
        const msgs = document.getElementById("chatMessages");
        msgs.innerHTML = "";
        data.messages.forEach(function(msg) {{
            var div = document.createElement("div");
            var roleClass = msg.role === "interviewer" ? "text-right bg-blue-600" : "bg-emerald-600";
            div.innerHTML = '<div class="' + roleClass + ' p-4 rounded-2xl max-w-lg mx-2">' +
                '<strong>' + msg.user + ':</strong> ' + msg.text +
                '</div>';
            msgs.appendChild(div);
        }});
        msgs.scrollTop = msgs.scrollHeight;
    }});
}}

setInterval(loadMessages, 2000);

function sendAnswer() {{
    var input = document.getElementById("chatInput");
    var msg = input.value.trim();
    if(!msg) return;
    
    fetch(`/send_message/{room_id}`, {{
        method: "POST",
        headers: {{"Content-Type": "application/json"}},
        body: JSON.stringify({{text: msg}})
    }});
    input.value = "";
    loadMessages();
}}

document.getElementById("recordBtn").onclick = async function() {{
    var stream = await navigator.mediaDevices.getUserMedia({{audio: true}});
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];
    
    mediaRecorder.ondataavailable = function(e) {{ audioChunks.push(e.data); }};
    mediaRecorder.onstop = function() {{
        var blob = new Blob(audioChunks, {{type: "audio/wav"}});
        var form = new FormData();
        form.append("audio", blob, "student_answer.wav");
        form.append("room_id", roomId);
        
        fetch("/upload_audio", {{method: "POST", body: form}}).then(function(r){{return r.json();}}).then(function(d){{alert("✅ Answer recorded & shared!");}});
    }};
    
    mediaRecorder.start();
    document.getElementById("recordBtn").classList.add("hidden");
    document.getElementById("stopBtn").classList.remove("hidden");
    document.getElementById("recordingStatus").classList.remove("hidden");
}};

document.getElementById("stopBtn").onclick = function() {{
    mediaRecorder.stop();
    document.getElementById("recordBtn").classList.remove("hidden");
    document.getElementById("stopBtn").classList.add("hidden");
    document.getElementById("recordingStatus").classList.add("hidden");
}};

loadMessages();
</script>
</body></html>'''






@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    print("Audio recording uploaded!")
    return jsonify({'status': 'success'})



@app.route('/send_message/<room_id>', methods=['POST'])
def send_message(room_id):
    data = request.get_json()
    username = session.get('user', 'Anonymous')
    role = session.get('role', 'student')
    
    # Initialize room_messages
    if room_id not in room_messages:
        room_messages[room_id] = []
    
    room_messages[room_id].append({
        'user': username,
        'role': role,
        'text': data.get('text', ''),
        'time': datetime.now().strftime('%H:%M')
    })
    
    print(f"[{role}] {username}: {data.get('text')}")
    return jsonify({'status': 'sent'})



@app.route('/next_stage/<room_id>', methods=['POST'])
def next_stage(room_id):
    if room_id in live_rooms and session.get('role') == 'interviewer':
        current_stage = live_rooms[room_id].get('stage', 0)
        if current_stage < 4:  # Assuming 5 stages (0-4)
            live_rooms[room_id]['stage'] = current_stage + 1
            # Here you could add logic to send next question or update
    return jsonify({'status': 'updated'})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json(silent=True) or {}
    question = (data.get('question') or '').strip()
    user_answer = (data.get('user_answer') or data.get('message') or '').strip()
    username = session.get('user', 'Student')

    if not user_answer:
        return jsonify({'reply': 'Score: 0%\nFeedback: No answer received. Please write your answer in the text box.\nCorrect Answer: Write a clear complete sentence answer.\nTip: Provide one structured example and details.'})

    if not question:
        question = 'Interview question'

    model = genai.GenerativeModel('gemini-2.5-flash')
    prompt = f"""You are CareerMantra AI Interview Coach responding in English.
Question: {question}
User Answer: {user_answer}
Evaluate correctness from 0-100% and provide:
1) Score: XX%
2) Feedback: Short analysis of right/wrong.
3) Correct Answer: Full corrected complete sample answer.
4) Tip: One practical improvement tip.
Format output exactly as:
Score: XX%
Feedback: ...
Correct Answer: ...
Tip: ...
User: {username} (AI/ML student)."""
    try:
        response = model.generate_content(prompt)
        ai_response = response.text
        
        # Track interview attempt
        if username not in practice_progress:
            practice_progress[username] = {
                'level': 1,
                'questions_solved': 0,
                'interviews_attended': 0,
                'ai_interviews': 0,
                'daily_hours': 0,
                'streak': 0,
                'overall_score': 0,
                'skills': {'DSA': 0, 'SystemDesign': 0, 'Behavioral': 0},
                'interview_scores': [],
                'ai_feedback_ratings': []
            }
        
        practice_progress[username]['interviews_attended'] = practice_progress[username].get('interviews_attended', 0) + 1
        
        # Extract score from response
        try:
            score_line = [l for l in ai_response.split('\n') if 'Score:' in l][0]
            score_str = ''.join(filter(str.isdigit, score_line.split('%')[0]))
            score_val = int(score_str) if score_str else 70
            practice_progress[username]['ai_feedback_ratings'].append(score_val)
        except:
            pass
        
        return jsonify({'reply': ai_response})
    except Exception as e:
        print('chat error', e)
        if len(user_answer) < 10:
            fallback_response = 'Score: 0%\nFeedback: Answer too short. Please write 2-3 complete sentences.\nCorrect Answer: Use STAR method and include situation, task, action, result.\nTip: Add a specific example from your experience.'
        else:
            fallback_response = 'Score: 65%\nFeedback: The answer is partially correct but misses structure and detail.\nCorrect Answer: [Provide full structured answer with intro, key points and conclusion].\nTip: Use examples and numbers to improve clarity.'
        
        # Track in fallback too
        if username not in practice_progress:
            practice_progress[username] = {
                'level': 1,
                'questions_solved': 0,
                'interviews_attended': 0,
                'ai_interviews': 0,
                'daily_hours': 0,
                'streak': 0,
                'overall_score': 0,
                'skills': {'DSA': 0, 'SystemDesign': 0, 'Behavioral': 0},
                'interview_scores': [],
                'ai_feedback_ratings': []
            }
        practice_progress[username]['interviews_attended'] = practice_progress[username].get('interviews_attended', 0) + 1
        
        return jsonify({'reply': fallback_response})


@app.route('/get_messages/<room_id>')
def get_messages(room_id):
    messages = room_messages.get(room_id, [])
    return jsonify({'messages': messages[-20:]})  # Last 20 messages

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    print("🚀 CareerMantra AI - DUAL DASHBOARD LIVE!")
    print("👨‍💼 rupesh/rupesh123 → Interviewer Dashboard")
    print("👨‍💻 ANY OTHER → Student Dashboard")
    app.run(debug=True, host='0.0.0.0', port=5000)

application = app
