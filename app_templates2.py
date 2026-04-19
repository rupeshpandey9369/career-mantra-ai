_JOIN_INTERVIEW_HTML = '''<!DOCTYPE html>
<html><head><title>Join Interview - CareerMantra</title>
<meta name="viewport" content="width=device-width">
<style>*{margin:0;padding:0;box-sizing:border-box}body{background:linear-gradient(135deg,#060b18,#0f2040);min-height:100vh;font-family:system-ui;display:flex;align-items:center;justify-content:center;padding:2rem;color:white}.card{background:rgba(255,255,255,.05);backdrop-filter:blur(24px);border:1px solid rgba(255,255,255,.08);border-radius:24px;padding:3rem;max-width:420px;width:100%;text-align:center}h1{font-size:1.8rem;font-weight:700;margin-bottom:.5rem}input{width:100%;padding:1rem;margin:.5rem 0;border:1px solid rgba(255,255,255,.1);border-radius:12px;background:rgba(255,255,255,.07);color:white;font-size:1rem;text-align:center;letter-spacing:.1em;outline:none;text-transform:uppercase}input:focus{border-color:#6366f1}.btn{width:100%;padding:1rem;background:linear-gradient(135deg,#6366f1,#22d3ee);color:white;border:none;border-radius:12px;font-size:1rem;font-weight:600;cursor:pointer;margin-top:1rem}.back{display:block;margin-top:1.5rem;color:#475569;text-decoration:none;font-size:.85rem}</style>
</head><body>
<div class="card">
<h1>Join Live Interview</h1>
<p style="color:#64748b;margin-bottom:1.5rem;font-size:.9rem">Enter the room code your interviewer shared</p>
<form method="POST" action="/join_with_code">
<input name="room_code" placeholder="ROOM CODE" maxlength="8" required autocomplete="off">
<input name="passcode" placeholder="PASSCODE (if required)" maxlength="10" autocomplete="off">
<button class="btn">Join Room</button>
</form>
<a href="/student_dashboard" class="back">← Back to dashboard</a>
</div>
</body></html>'''


_PRACTICE_HTML = '''<!DOCTYPE html>
<html><head><title>Practice - CareerMantra</title>
<meta name="viewport" content="width=device-width">
<script src="https://cdn.tailwindcss.com"></script>
<style>body{font-family:system-ui;background:linear-gradient(135deg,#060b18,#0f2040);min-height:100vh;color:#e2e8f0;padding:2rem}.glass{background:rgba(15,20,40,.7);backdrop-filter:blur(20px);border:1px solid rgba(255,255,255,.08);border-radius:16px}</style>
</head><body>
<div style="max-width:900px;margin:0 auto">
<h1 style="font-size:2rem;font-weight:700;background:linear-gradient(135deg,#6366f1,#22d3ee);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:1.5rem">
  Practice Questions — Level {{ level }}
</h1>
<div class="space-y-4">
{% for q, placeholder in [
  ("Tell me about yourself (2 mins)", "I am a software engineer with..."),
  ("Two Sum: nums=[2,7,11,15], target=9", "def two_sum(nums, target):&#10;    ..."),
] %}
<div class="glass p-6">
  <div class="font-semibold text-slate-200 mb-3">{{ q }}</div>
  <textarea id="ans{{ loop.index }}" rows="5"
    class="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-slate-200 font-mono text-sm outline-none focus:border-indigo-500/50 resize-none"
    placeholder="{{ placeholder }}"></textarea>
  <button onclick="submitPractice({{ loop.index }}, `{{ q }}`)"
    class="mt-3 px-5 py-2 rounded-xl text-sm font-medium"
    style="background:linear-gradient(135deg,#6366f1,#22d3ee);color:white">
    Get Feedback
  </button>
  <div id="fb{{ loop.index }}" class="mt-3 text-sm text-slate-300 leading-relaxed hidden"></div>
</div>
{% endfor %}
</div>
<a href="/student_dashboard" style="display:inline-block;margin-top:2rem;color:#475569;text-decoration:none;font-size:.85rem">← Dashboard</a>
</div>
<script>
function submitPractice(n, q) {
  var ans = document.getElementById("ans"+n).value.trim();
  if (!ans) { alert("Write your answer first."); return; }
  var fb = document.getElementById("fb"+n);
  fb.textContent = "Evaluating..."; fb.classList.remove("hidden");
  fetch("/chat", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({question: q, user_answer: ans})
  }).then(r => r.json()).then(d => { fb.textContent = d.reply; });
}
</script>
</body></html>'''


_AI_INTERVIEW_HTML = '''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width"><title>AI Mock Interview - CareerMantra</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{background:linear-gradient(135deg,#0f172a,#1e293b);color:#fff;font-family:"Segoe UI",system-ui,sans-serif;min-height:100vh;padding:1.5rem}.wrapper{max-width:1400px;margin:0 auto}.header{text-align:center;margin-bottom:2rem}.header h1{font-size:2.5rem;background:linear-gradient(45deg,#60a5fa,#34d399);-webkit-background-clip:text;-webkit-text-fill-color:transparent}.main{display:grid;grid-template-columns:1.5fr 1fr;gap:1.5rem}@media(max-width:768px){.main{grid-template-columns:1fr}}.panel{background:rgba(30,41,59,.8);backdrop-filter:blur(10px);border:1px solid rgba(148,163,184,.15);border-radius:16px;padding:2rem}.q-num{font-size:.8rem;color:#64748b;text-transform:uppercase;letter-spacing:1px;margin-bottom:.5rem}.q-text{font-size:1.4rem;font-weight:600;color:#60a5fa;margin-bottom:1.5rem;line-height:1.4}textarea{width:100%;padding:1rem;background:rgba(15,23,42,.8);border:1px solid rgba(100,116,139,.4);border-radius:12px;color:#e2e8f0;font-family:inherit;font-size:.95rem;resize:vertical;min-height:140px;outline:none}textarea:focus{border-color:#60a5fa}.btns{display:flex;gap:.75rem;flex-wrap:wrap;margin-top:1rem}.btn{padding:.7rem 1.4rem;border:none;border-radius:10px;font-size:.9rem;font-weight:600;cursor:pointer;transition:all .2s}.btn-blue{background:linear-gradient(135deg,#3b82f6,#2563eb);color:white}.btn-green{background:linear-gradient(135deg,#10b981,#059669);color:white}.btn-gray{background:rgba(100,116,139,.4);color:#e2e8f0;border:1px solid rgba(148,163,184,.3)}.nav-list{list-style:none;display:flex;flex-wrap:wrap;gap:.4rem;margin-top:1.2rem}.nav-item{background:rgba(100,116,139,.2);border:1px solid rgba(148,163,184,.2);border-radius:8px;padding:.45rem .75rem;cursor:pointer;font-size:.8rem;transition:all .2s}.nav-item:hover{background:rgba(100,116,139,.4)}.nav-item.active{background:linear-gradient(135deg,#10b981,#059669);border-color:#10b981}.feedback-panel{display:flex;flex-direction:column;min-height:500px}.feedback-content{flex:1;overflow-y:auto;padding:1rem;background:rgba(15,23,42,.5);border-radius:10px;border:1px solid rgba(148,163,184,.15)}.score-line{background:linear-gradient(90deg,#10b981,#34d399);padding:.6rem 1rem;border-radius:8px;font-weight:600;color:#0f172a;margin-bottom:.75rem}.feedback-line{color:#fbbf24;font-weight:600;margin-bottom:.4rem}.answer-line{color:#60a5fa;font-weight:600;margin-bottom:.4rem}.tip-line{color:#f87171;font-weight:600;margin-bottom:.4rem}.empty{color:#64748b;font-style:italic;text-align:center;padding:2rem}</style>
</head><body>
<div class="wrapper">
<div class="header"><h1>AI Mock Interview</h1><p style="color:#94a3b8">{{ username }} — get AI-powered feedback on each answer</p></div>
<div class="main">
<div class="panel">
  <div class="q-num" id="qNum">Question 1 of {{ questions|length }}</div>
  <div class="q-text" id="qText">{{ questions[0] }}</div>
  <textarea id="answerInput" placeholder="Type your answer here... (2-3 sentences minimum)"></textarea>
  <div class="btns">
    <button class="btn btn-blue" onclick="submitAnswer()">Submit Answer</button>
    <button class="btn btn-green" onclick="submitAnswer()">Get AI Feedback</button>
    <button class="btn btn-gray" onclick="nextQ()">Next →</button>
  </div>
  <ul class="nav-list" id="navList">
    {% for q in questions %}
    <li class="nav-item{% if loop.first %} active{% endif %}" onclick="goTo({{ loop.index0 }})">
      <strong>Q{{ loop.index }}</strong> {{ q[:25] }}{% if q|length > 25 %}…{% endif %}
    </li>
    {% endfor %}
  </ul>
</div>
<div class="panel feedback-panel">
  <div style="font-size:1rem;font-weight:600;color:#60a5fa;text-transform:uppercase;letter-spacing:1px;margin-bottom:1rem">AI Feedback</div>
  <div class="feedback-content" id="aiResponse"><div class="empty">Submit your answer to get feedback here</div></div>
</div>
</div>
<div style="text-align:center;margin-top:1.5rem">
<a href="/student_dashboard" style="display:inline-block;padding:.7rem 2rem;background:rgba(100,116,139,.3);color:#94a3b8;text-decoration:none;border-radius:10px;border:1px solid rgba(148,163,184,.2)">← Back to Dashboard</a>
</div>
</div>
<script>
var questions = {{ questions | tojson }};
var idx = 0;

function updateUI() {
  document.getElementById("qNum").textContent  = "Question " + (idx+1) + " of " + questions.length;
  document.getElementById("qText").textContent = questions[idx];
  document.getElementById("answerInput").value = "";
  document.querySelectorAll(".nav-item").forEach((el, i) => el.classList.toggle("active", i === idx));
}
function nextQ()  { idx = (idx+1) % questions.length; updateUI(); }
function goTo(i)  { idx = i; updateUI(); }

function submitAnswer() {
  var ans = document.getElementById("answerInput").value.trim();
  if (!ans) { alert("Write your answer first."); return; }
  var fb = document.getElementById("aiResponse");
  fb.innerHTML = "<div class='empty'>Evaluating...</div>";
  fetch("/chat", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({question: questions[idx], user_answer: ans})
  }).then(r=>r.json()).then(d => {
    var html = "";
    (d.reply||"").split("\\n").forEach(line => {
      line = line.trim(); if (!line) return;
      if (line.startsWith("Score:"))          html += "<div class='score-line'>"+line+"</div>";
      else if (line.startsWith("Feedback:"))  html += "<div class='feedback-line'>"+line+"</div>";
      else if (line.startsWith("Correct Answer:")) html += "<div class='answer-line'>"+line+"</div>";
      else if (line.startsWith("Tip:"))       html += "<div class='tip-line'>"+line+"</div>";
      else html += "<div>"+line+"</div>";
    });
    fb.innerHTML = html || "<div class='empty'>No feedback received</div>";
  });
}
</script>
</body></html>'''


_AI_CHATBOT_HTML = '''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width"><title>AI Coach - CareerMantra</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{background:linear-gradient(135deg,#0f172a,#1e293b);color:#fff;font-family:"Segoe UI",system-ui,sans-serif;height:100vh;display:flex;flex-direction:column}.header{background:rgba(15,23,42,.9);backdrop-filter:blur(10px);border-bottom:1px solid rgba(148,163,184,.15);padding:1.2rem 1.5rem;text-align:center}.header h1{font-size:1.6rem;background:linear-gradient(45deg,#60a5fa,#34d399);-webkit-background-clip:text;-webkit-text-fill-color:transparent}.messages{flex:1;overflow-y:auto;padding:1.5rem;display:flex;flex-direction:column;gap:.8rem}.msg{display:flex}.msg.bot{justify-content:flex-start}.msg.user{justify-content:flex-end}.bubble{max-width:70%;padding:.9rem 1.1rem;border-radius:12px;line-height:1.5;font-size:.9rem}.bubble.bot{background:linear-gradient(135deg,rgba(96,165,250,.15),rgba(52,211,153,.08));border:1px solid rgba(96,165,250,.25)}.bubble.user{background:linear-gradient(135deg,#3b82f6,#2563eb)}.dot{width:7px;height:7px;background:#60a5fa;border-radius:50%;animation:b 1.4s infinite}.dot:nth-child(2){animation-delay:.2s}.dot:nth-child(3){animation-delay:.4s}@keyframes b{0%,80%,100%{transform:translateY(0)}40%{transform:translateY(-8px)}}.input-row{background:rgba(30,41,59,.8);border-top:1px solid rgba(148,163,184,.15);padding:1rem 1.5rem;display:flex;gap:.75rem}.input-row input{flex:1;background:rgba(15,23,42,.6);border:1px solid rgba(100,116,139,.4);color:#e2e8f0;padding:.85rem 1rem;border-radius:10px;font-size:.9rem;outline:none}.input-row input:focus{border-color:#60a5fa}.send-btn{padding:.75rem 1.5rem;background:linear-gradient(135deg,#10b981,#059669);color:white;border:none;border-radius:10px;font-weight:600;cursor:pointer;text-transform:uppercase;font-size:.8rem;letter-spacing:.4px}</style>
</head><body>
<div class="header"><h1>AI Coach</h1><p style="color:#94a3b8;font-size:.85rem">Ask anything about DSA, behavioral, system design, or career prep</p></div>
<div class="messages" id="msgs">
<div class="msg bot"><div class="bubble bot">Hi {{ username }}! I can help with DSA, HR questions, system design, and career advice. What would you like to work on?</div></div>
</div>
<div class="input-row">
<input id="inp" placeholder="Ask your question..." onkeypress="if(event.key==='Enter') send()">
<button class="send-btn" onclick="send()">Send</button>
</div>
<div style="text-align:center;padding:.75rem;border-top:1px solid rgba(148,163,184,.1)">
<a href="/student_dashboard" style="color:#475569;text-decoration:none;font-size:.8rem">← Dashboard</a>
</div>
<script>
var msgs = document.getElementById("msgs");
function send() {
  var inp = document.getElementById("inp");
  var txt = inp.value.trim(); if (!txt) return;
  addMsg(txt, "user"); inp.value = "";
  var typing = addMsg('<div style="display:flex;gap:.3rem;align-items:center"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>', "bot");
  fetch("/chat", {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:txt})})
    .then(r=>r.json()).then(d=>{
      typing.querySelector(".bubble").innerHTML = "<strong>AI Coach:</strong><br>" + (d.reply||"").replace(/\\n/g,"<br>");
      msgs.scrollTop = msgs.scrollHeight;
    }).catch(()=>{ typing.querySelector(".bubble").textContent = "Connection error. Try again."; });
}
function addMsg(content, role) {
  var wrap = document.createElement("div"); wrap.className = "msg " + role;
  var bubble = document.createElement("div"); bubble.className = "bubble " + role;
  bubble.innerHTML = content; wrap.appendChild(bubble); msgs.appendChild(wrap);
  msgs.scrollTop = msgs.scrollHeight; return wrap;
}
document.getElementById("inp").focus();
</script>
</body></html>'''


_PERFORMANCE_HTML = '''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width"><title>Performance - CareerMantra</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>body{font-family:system-ui;background:linear-gradient(135deg,#0f172a,#1e293b);min-height:100vh;color:#e2e8f0;padding:1.5rem}
.glass{background:rgba(30,41,59,.8);backdrop-filter:blur(10px);border:1px solid rgba(148,163,184,.15);border-radius:16px;padding:1.5rem}
.bar-wrap{height:10px;background:rgba(100,116,139,.25);border-radius:99px;overflow:hidden;margin-top:.4rem}
.bar{height:100%;background:linear-gradient(90deg,#3b82f6,#10b981);border-radius:99px}</style>
</head>
<body>
<div style="max-width:1200px;margin:0 auto">
<h1 style="font-size:2.5rem;font-weight:700;background:linear-gradient(45deg,#60a5fa,#34d399);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:2rem;text-align:center">
  Performance Analytics — {{ username }}
</h1>

<!-- Top metrics -->
<div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
{% for label, val, color in [
  ("Overall Score", (profile.overall_score|round(0)|int|string + "%") if profile and profile.overall_score else "—", "#10b981"),
  ("Streak", (profile.streak_days|string + " days") if profile else "0 days", "#f59e0b"),
  ("Level", profile.current_level if profile else 1, "#6366f1"),
  ("Questions Solved", profile.questions_solved if profile else 0, "#22d3ee"),
] %}
<div class="glass text-center">
  <div style="font-size:2.2rem;font-weight:800;color:{{ color }}">{{ val }}</div>
  <div class="text-xs text-slate-500 uppercase tracking-widest mt-1">{{ label }}</div>
</div>
{% endfor %}
</div>

<!-- Skill bars -->
<div class="glass mb-6">
<div class="text-sm font-semibold text-slate-300 uppercase tracking-widest mb-4">Skill Assessment</div>
{% for label, val in [
  ("DSA", profile.dsa_score if profile else 0),
  ("System Design", profile.system_design_score if profile else 0),
  ("Behavioral", profile.behavioral_score if profile else 0),
] %}
<div class="mb-4">
  <div class="flex justify-between text-sm text-slate-400 mb-1"><span>{{ label }}</span><span>{{ val|round(0)|int }}%</span></div>
  <div class="bar-wrap"><div class="bar" style="width:{{ val }}%"></div></div>
</div>
{% endfor %}
</div>

{% if topic_avgs %}
<div class="glass mb-6">
<div class="text-sm font-semibold text-slate-300 uppercase tracking-widest mb-4">Topic Breakdown</div>
<div class="grid grid-cols-2 md:grid-cols-4 gap-3">
{% for tag, avg in topic_avgs.items() %}
<div style="background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.07);border-radius:12px;padding:1rem;text-align:center">
  <div style="font-size:1.4rem;font-weight:700;color:#60a5fa">{{ avg }}</div>
  <div class="text-xs text-slate-500 mt-0.5">{{ tag }}</div>
</div>
{% endfor %}
</div>
</div>
{% endif %}

<div style="text-align:center;margin-top:2rem">
<a href="/student_dashboard" style="display:inline-block;padding:.7rem 2rem;background:rgba(100,116,139,.3);color:#94a3b8;text-decoration:none;border-radius:10px;border:1px solid rgba(148,163,184,.2)">← Dashboard</a>
</div>
</div>
</body></html>'''


_COMPANY_QUESTIONS_HTML = '''<!DOCTYPE html>
<html><head><title>Company Questions - CareerMantra</title>
<meta name="viewport" content="width=device-width">
<style>*{margin:0;padding:0;box-sizing:border-box}body{background:linear-gradient(135deg,#060b18,#0f2040);color:#e2e8f0;font-family:system-ui;min-height:100vh;padding:2rem}
h1{font-size:2.5rem;text-align:center;background:linear-gradient(45deg,#f59e0b,#d97706);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:2.5rem}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:1.5rem}
.card{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.07);border-radius:16px;padding:2rem;border-left:4px solid #6366f1;transition:transform .25s}
.card:hover{transform:translateY(-4px)}
.company{font-size:1.5rem;color:#fbbf24;font-weight:700;margin-bottom:1.2rem}
.q{padding:.75rem 1rem;margin-bottom:.5rem;background:rgba(0,0,0,.3);border-radius:10px;border-left:3px solid #10b981;font-size:.9rem;transition:background .2s}
.q:hover{background:rgba(16,185,129,.15)}
</style>
</head><body>
<h1>Company Interview Questions</h1>
<div class="grid">
{% for company, questions in companies.items() %}
<div class="card">
  <div class="company">{{ company }}</div>
  {% for q in questions[:10] %}
  <div class="q">{{ loop.index }}. {{ q }}</div>
  {% endfor %}
</div>
{% endfor %}
</div>
<div style="text-align:center;margin-top:3rem">
<a href="/student_dashboard" style="display:inline-block;padding:.9rem 2.5rem;background:linear-gradient(135deg,#6366f1,#22d3ee);color:white;text-decoration:none;border-radius:12px;font-weight:600">← Back to Dashboard</a>
</div>
</body></html>'''


_ERROR_HTML = '''<!DOCTYPE html>
<html><head><title>Error - CareerMantra</title>
<style>*{margin:0;padding:0}body{background:linear-gradient(135deg,#060b18,#0f2040);min-height:100vh;display:flex;align-items:center;justify-content:center;font-family:system-ui;color:white;padding:2rem}.card{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.08);border-radius:20px;padding:3rem;text-align:center;max-width:480px}.title{font-size:1.6rem;color:#f43f5e;margin-bottom:1rem}.msg{color:#94a3b8;margin-bottom:2rem}.btn{display:inline-block;padding:.85rem 2rem;background:linear-gradient(135deg,#6366f1,#22d3ee);color:white;text-decoration:none;border-radius:12px;font-weight:600}</style>
</head><body>
<div class="card">
<div class="title">Something went wrong</div>
<div class="msg">{{ msg }}</div>
<a href="{{ back }}" class="btn">Go Back</a>
</div>
</body></html>'''
