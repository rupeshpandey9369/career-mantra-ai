_LOGIN_HTML = '''<!DOCTYPE html>
<html><head><title>CareerMantra AI</title>
<meta name="viewport" content="width=device-width">
<style>*{margin:0;padding:0;box-sizing:border-box}
body{background:linear-gradient(135deg,#060b18,#0f2040);min-height:100vh;font-family:"DM Sans",system-ui,sans-serif;display:flex;align-items:center;justify-content:center;padding:2rem;color:white}
.card{background:rgba(255,255,255,0.05);backdrop-filter:blur(24px);border:1px solid rgba(255,255,255,0.08);border-radius:24px;padding:3rem;max-width:420px;width:100%;text-align:center}
h1{font-size:2.5rem;font-weight:700;background:linear-gradient(135deg,#6366f1,#22d3ee);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:.5rem;letter-spacing:-.02em}
.tagline{color:#64748b;font-size:.9rem;margin-bottom:2.5rem}
input{width:100%;padding:1rem 1.25rem;margin:.6rem 0;border:1px solid rgba(255,255,255,0.1);border-radius:12px;background:rgba(255,255,255,0.07);color:white;font-size:.95rem;outline:none;transition:border-color .2s}
input:focus{border-color:#6366f1}
input::placeholder{color:#475569}
.btn{width:100%;padding:1rem;background:linear-gradient(135deg,#6366f1,#22d3ee);color:white;border:none;border-radius:12px;font-size:1rem;font-weight:600;cursor:pointer;margin-top:1rem;transition:opacity .2s,transform .15s}
.btn:hover{opacity:.9;transform:translateY(-1px)}
.demo{background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.06);padding:1.25rem;border-radius:12px;margin-top:2rem;text-align:left;font-size:.82rem;color:#64748b;line-height:1.8}
.demo strong{color:#94a3b8}
</style></head><body>
<div class="card">
<h1>CareerMantra AI</h1>
<p class="tagline">Interview preparation & live interview platform</p>
<form method="POST">
<input name="username" placeholder="Username" required autocomplete="username">
<input type="password" name="password" placeholder="Password" required autocomplete="current-password">
<button class="btn">Sign In</button>
</form>
<div class="demo">
<strong>Interviewer:</strong> rupesh / rupesh123<br>
<strong>Candidate:</strong> any username / any password
</div>
</div>
</body></html>'''


_ROOM_CREATED_HTML = '''<!DOCTYPE html>
<html><head><title>Room Created - CareerMantra</title>
<meta name="viewport" content="width=device-width">
<style>*{margin:0;padding:0;box-sizing:border-box}body{background:linear-gradient(135deg,#060b18,#0f2040);min-height:100vh;font-family:system-ui;display:flex;align-items:center;justify-content:center;padding:2rem;color:white}.card{background:rgba(255,255,255,0.05);backdrop-filter:blur(24px);border:1px solid rgba(255,255,255,0.08);border-radius:24px;padding:3rem;max-width:500px;width:100%;text-align:center}.code{font-family:monospace;font-size:2rem;font-weight:700;background:linear-gradient(135deg,#6366f1,#22d3ee);-webkit-background-clip:text;-webkit-text-fill-color:transparent;letter-spacing:.1em;margin:1rem 0}.passcode{font-family:monospace;font-size:1.2rem;background:rgba(255,255,255,0.07);padding:.6rem 1.5rem;border-radius:10px;display:inline-block;color:#94a3b8;margin:.5rem 0}.btn{display:inline-block;padding:.9rem 2rem;border-radius:12px;text-decoration:none;font-weight:600;font-size:.9rem;margin:.4rem;transition:all .2s}.btn-primary{background:linear-gradient(135deg,#6366f1,#22d3ee);color:white}.btn-ghost{background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.1);color:#94a3b8}</style>
</head><body>
<div class="card">
<h1 style="font-size:1.8rem;margin-bottom:.5rem">Room Created</h1>
<p style="color:#64748b;margin-bottom:1.5rem">Share this code with your candidate</p>
<div class="code">{{ room.room_code }}</div>
<div>Passcode: <span class="passcode">{{ passcode }}</span></div>
<p style="color:#475569;font-size:.82rem;margin:1rem 0">{{ room.position or "Interview session" }} · {{ room.duration_minutes }} minutes</p>
<div style="margin-top:2rem">
<a href="/interviewer_dashboard" class="btn btn-ghost">← Dashboard</a>
<a href="/interview_room/{{ room.room_code }}" class="btn btn-primary">Enter Room →</a>
</div>
</div>
</body></html>'''


_INTERVIEW_ROOM_HTML = '''<!DOCTYPE html>
<html lang="en"><head><title>Interview Room {{ room.room_code }} - CareerMantra</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=DM+Mono:wght@400;500&display=swap');
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:"DM Sans",system-ui,sans-serif;background:#060b18;color:#e2e8f0;min-height:100vh}
.glass{background:rgba(15,20,40,.7);backdrop-filter:blur(20px);border:1px solid rgba(255,255,255,.07)}
.badge{font-size:.7rem;font-weight:600;padding:3px 10px;border-radius:99px;letter-spacing:.04em;text-transform:uppercase}
::-webkit-scrollbar{width:5px}::-webkit-scrollbar-thumb{background:rgba(255,255,255,.1);border-radius:3px}
.msg-interviewer{background:rgba(99,102,241,.15);border:1px solid rgba(99,102,241,.25);border-radius:12px 12px 4px 12px}
.msg-candidate{background:rgba(34,211,238,.08);border:1px solid rgba(34,211,238,.15);border-radius:12px 12px 12px 4px}
</style>
</head>
<body class="flex flex-col h-screen">

<!-- Topbar -->
<nav class="glass flex items-center justify-between px-5 py-3 sticky top-0 z-30" style="border-top:none;border-left:none;border-right:none">
  <div class="flex items-center gap-3">
    <span class="font-semibold text-sm">CareerMantra AI</span>
    <span class="text-slate-600 text-xs">/</span>
    <span class="font-mono text-xs text-indigo-300">{{ room.room_code }}</span>
    <span class="badge" style="background:rgba(16,185,129,.15);color:#10b981">Live</span>
  </div>
  <div class="flex items-center gap-2 text-xs text-slate-400">
    <i class="fas fa-clock"></i>
    <span id="timer">00:00</span>
    {% if role == "interviewer" %}
    <a href="/end_room/{{ room.room_code }}"
       class="ml-3 px-3 py-1.5 rounded-lg text-rose-400 border border-rose-500/20 hover:bg-rose-500/10 transition-colors"
       onclick="return confirm('End this interview?')">End</a>
    {% endif %}
  </div>
</nav>

<!-- Main layout -->
<div class="flex flex-1 overflow-hidden">

  <!-- Left: question + code editor placeholder -->
  <div class="flex flex-col flex-1 overflow-hidden">
    <!-- Current question banner -->
    <div id="question-banner" class="px-5 py-3 text-sm text-slate-400 border-b border-white/5"
         style="min-height:48px;background:rgba(99,102,241,.05)">
      {% if room.live_session and room.live_session.current_question %}
        <span class="text-slate-200">{{ room.live_session.current_question }}</span>
      {% else %}
        <span class="text-slate-600">Waiting for question...</span>
      {% endif %}
    </div>

    <!-- Code area (swap for Monaco Editor script block in next step) -->
    <div class="flex-1 p-4">
      <div class="glass rounded-2xl h-full flex flex-col">
        <div class="flex items-center gap-3 px-4 py-2.5 border-b border-white/5">
          <span class="text-xs text-slate-500 font-medium">Code Editor</span>
          <select id="lang-select" class="ml-auto text-xs bg-transparent text-slate-400 border border-white/10 rounded-lg px-2 py-1 outline-none">
            <option value="python">Python</option>
            <option value="javascript">JavaScript</option>
            <option value="java">Java</option>
            <option value="cpp">C++</option>
          </select>
        </div>
        <textarea id="code-editor"
                  class="flex-1 bg-transparent text-sm font-mono text-slate-200 p-4 resize-none outline-none leading-relaxed"
                  placeholder="Write your solution here...&#10;&#10;def two_sum(nums, target):&#10;    ..."></textarea>
      </div>
    </div>
  </div>

  <!-- Right: chat panel -->
  <div class="glass flex flex-col w-80 flex-shrink-0" style="border-top:none;border-right:none;border-bottom:none">
    <div class="px-4 py-3 border-b border-white/5 text-xs font-medium text-slate-400 uppercase tracking-widest">
      Chat
    </div>
    <div id="chat-messages" class="flex-1 overflow-y-auto p-3 space-y-2">
      {% for msg in messages %}
      <div class="p-2.5 {{ 'msg-interviewer' if msg.sender.role == 'interviewer' else 'msg-candidate' }}">
        <div class="text-xs text-slate-500 mb-1">{{ msg.sender.username }}</div>
        <div class="text-sm text-slate-200">{{ msg.content }}</div>
      </div>
      {% endfor %}
    </div>
    <div class="p-3 border-t border-white/5 flex gap-2">
      <input id="chat-input" type="text"
             class="flex-1 text-sm bg-white/5 border border-white/10 rounded-xl px-3 py-2 text-slate-200 outline-none focus:border-indigo-500/50"
             placeholder="Message...">
      <button onclick="sendMsg()"
              class="px-3 py-2 rounded-xl text-indigo-300 border border-indigo-500/20 hover:bg-indigo-500/10 transition-colors text-sm">
        <i class="fas fa-paper-plane text-xs"></i>
      </button>
    </div>

    {% if role == "interviewer" %}
    <div class="p-3 border-t border-white/5 space-y-2">
      <div class="text-xs text-slate-600 uppercase tracking-widest mb-2">Stage</div>
      <div class="grid grid-cols-5 gap-1">
        {% for s in ["Intro","Code","Sys","Behav","Close"] %}
        <button onclick="setStage({{ loop.index0 }})"
                class="stage-btn text-xs py-1.5 rounded-lg border border-white/10 text-slate-500 hover:text-indigo-300 hover:border-indigo-500/30 transition-all"
                data-s="{{ loop.index0 }}">{{ s }}</button>
        {% endfor %}
      </div>
    </div>
    {% endif %}
  </div>
</div>

<script>
const ROOM   = "{{ room.room_code }}";
const ROLE   = "{{ role }}";
const ME     = "{{ username }}";
const socket = io("{{ config.get('SOCKETIO_SERVER_URL', '') }}" || undefined);

// Join the SocketIO room immediately on page load.
socket.on("connect", () => {
  socket.emit("join_room", { room_code: ROOM, passcode: "" });
});

socket.on("room_state", (state) => {
  if (state.code) document.getElementById("code-editor").value = state.code;
  if (state.current_q) setQuestionBanner(state.current_q);
  if (state.language) document.getElementById("lang-select").value = state.language;
});

socket.on("code_update", (data) => {
  const el = document.getElementById("code-editor");
  // Only update if we didn't send it (skip_sid handles this server-side,
  // but we guard here too to avoid cursor jump on slow networks).
  if (data.code !== el.value) el.value = data.code;
});

socket.on("chat_message", (msg) => {
  if (!msg.is_private || ROLE === "interviewer") appendMsg(msg);
});

socket.on("question_set", (data) => setQuestionBanner(data.question));

socket.on("stage_changed", (data) => {
  if (data.question) setQuestionBanner(data.question);
  document.querySelectorAll(".stage-btn").forEach((b, i) => {
    b.classList.toggle("text-indigo-300", i === data.stage);
    b.classList.toggle("border-indigo-500/40", i === data.stage);
  });
});

socket.on("interview_ended", () => {
  window.location.href = "/scorecard/" + ROOM;
});

// Code sync — debounced by socket_handlers on the server side too.
let syncTimer;
document.getElementById("code-editor").addEventListener("input", (e) => {
  clearTimeout(syncTimer);
  syncTimer = setTimeout(() => {
    socket.emit("code_change", {
      room_code: ROOM,
      code: e.target.value,
      language: document.getElementById("lang-select").value,
    });
  }, 150);
});

document.getElementById("lang-select").addEventListener("change", (e) => {
  socket.emit("language_change", { room_code: ROOM, language: e.target.value });
});

function sendMsg() {
  const el  = document.getElementById("chat-input");
  const txt = el.value.trim();
  if (!txt) return;
  socket.emit("chat_message", { room_code: ROOM, content: txt });
  el.value = "";
}

document.getElementById("chat-input").addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendMsg();
});

function appendMsg(msg) {
  const wrap = document.getElementById("chat-messages");
  const div  = document.createElement("div");
  div.className = "p-2.5 " + (msg.role === "interviewer" ? "msg-interviewer" : "msg-candidate");
  div.innerHTML = `<div class="text-xs text-slate-500 mb-1">${msg.sender}</div>
                   <div class="text-sm text-slate-200">${msg.content}</div>`;
  wrap.appendChild(div);
  wrap.scrollTop = wrap.scrollHeight;
}

function setQuestionBanner(q) {
  const el = document.getElementById("question-banner");
  el.innerHTML = `<span class="text-slate-200">${q}</span>`;
}

function setStage(idx) {
  socket.emit("set_stage", { room_code: ROOM, stage: idx });
}

// Timer
let secs = 0;
setInterval(() => {
  secs++;
  const m = String(Math.floor(secs / 60)).padStart(2, "0");
  const s = String(secs % 60).padStart(2, "0");
  document.getElementById("timer").textContent = `${m}:${s}`;
}, 1000);

// Proctoring — candidate only. Fires events that the server logs and
// forwards to the interviewer as alerts.
{% if role == "candidate" %}
document.addEventListener("visibilitychange", () => {
  if (document.hidden) {
    socket.emit("proctoring_event", { room_code: ROOM, type: "tab_switch" });
  }
});
document.addEventListener("fullscreenchange", () => {
  if (!document.fullscreenElement) {
    socket.emit("proctoring_event", { room_code: ROOM, type: "fullscreen_exit" });
  }
});
{% endif %}
</script>
</body></html>'''


_SCORECARD_HTML = '''<!DOCTYPE html>
<html lang="en"><head><title>Scorecard - CareerMantra</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<script src="https://cdn.tailwindcss.com"></script>
<style>*{box-sizing:border-box}body{font-family:system-ui,sans-serif;background:linear-gradient(135deg,#060b18,#0f2040);min-height:100vh;color:#e2e8f0;padding:2rem}
.glass{background:rgba(15,20,40,.7);backdrop-filter:blur(20px);border:1px solid rgba(255,255,255,.07);border-radius:20px}
.score-bar{height:8px;background:rgba(255,255,255,.08);border-radius:99px;overflow:hidden}
.score-fill{height:100%;background:linear-gradient(90deg,#6366f1,#22d3ee);border-radius:99px;transition:width .8s ease}
</style></head>
<body>
<div style="max-width:860px;margin:0 auto">
  <div class="text-center mb-10">
    <h1 style="font-size:2.5rem;font-weight:700;background:linear-gradient(135deg,#6366f1,#22d3ee);-webkit-background-clip:text;-webkit-text-fill-color:transparent">
      Interview Scorecard
    </h1>
    <p class="text-slate-500 mt-1">{{ room.room_code }} · {{ room.position or "Interview Session" }}</p>
  </div>

  {% if card %}
  <div class="glass p-8 mb-6">
    <div class="flex items-center justify-between mb-6">
      <div>
        <div style="font-size:3rem;font-weight:700;{% if card.overall_score >= 7 %}color:#10b981{% elif card.overall_score >= 5 %}color:#f59e0b{% else %}color:#f43f5e{% endif %}">
          {{ card.overall_score }}/10
        </div>
        <div class="text-slate-400 text-sm">Overall Score</div>
      </div>
      <div class="text-right">
        <div class="text-lg font-semibold" style="{% if card.recommendation == 'hire' %}color:#10b981{% elif card.recommendation == 'no_hire' %}color:#f43f5e{% else %}color:#f59e0b{% endif %}">
          {{ card.recommendation | upper if card.recommendation else "PENDING" }}
        </div>
        <div class="text-slate-500 text-xs mt-0.5">Recommendation</div>
      </div>
    </div>

    {% for label, val in [("Problem Solving", card.problem_solving), ("Communication", card.communication), ("Code Quality", card.code_quality), ("System Thinking", card.system_thinking), ("Behavioral Fit", card.behavioral_fit)] %}
    <div class="mb-4">
      <div class="flex justify-between text-sm text-slate-400 mb-1.5">
        <span>{{ label }}</span><span>{{ val }}/10</span>
      </div>
      <div class="score-bar"><div class="score-fill" style="width:{{ val * 10 }}%"></div></div>
    </div>
    {% endfor %}
  </div>

  {% if card.ai_summary %}
  <div class="glass p-6 mb-6">
    <div class="text-xs text-slate-500 uppercase tracking-widest mb-3 font-medium">AI Summary</div>
    <p class="text-slate-300 leading-relaxed text-sm">{{ card.ai_summary }}</p>
  </div>
  {% endif %}

  {% if live %}
  <div class="glass p-6 mb-6">
    <div class="text-xs text-slate-500 uppercase tracking-widest mb-3 font-medium">Proctoring Log</div>
    <div class="grid grid-cols-2 gap-4 text-sm">
      <div>Tab switches: <span class="text-slate-200">{{ live.candidate_tab_switches or 0 }}</span></div>
      <div>Fullscreen exits: <span class="text-slate-200">{{ live.candidate_fullscreen_exits or 0 }}</span></div>
    </div>
  </div>
  {% endif %}

  {% else %}
  <div class="glass p-10 text-center text-slate-500">
    <p class="text-lg mb-2">Scorecard not available yet.</p>
    <p class="text-sm">End the interview to generate the AI scorecard.</p>
  </div>
  {% endif %}

  <div class="flex gap-3 justify-center mt-8">
    <a href="/interviewer_dashboard" class="px-6 py-2.5 rounded-xl border border-white/10 text-slate-400 hover:bg-white/5 transition-colors text-sm">← Dashboard</a>
  </div>
</div>
</body></html>'''


_STUDENT_DASHBOARD_HTML = '''<!DOCTYPE html>
<html><head><title>Dashboard - CareerMantra AI</title>
<meta name="viewport" content="width=device-width">
<script src="https://cdn.tailwindcss.com"></script>
<style>@import url("https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap");
*{box-sizing:border-box;margin:0;padding:0}body{font-family:"DM Sans",system-ui,sans-serif;background:linear-gradient(135deg,#060b18,#0f2040);min-height:100vh;color:#e2e8f0;padding:2rem}
.glass{background:rgba(15,20,40,.7);backdrop-filter:blur(20px);border:1px solid rgba(255,255,255,.08);border-radius:20px}
.card{border-radius:20px;padding:2rem;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.07);transition:transform .25s,border-color .25s}
.card:hover{transform:translateY(-4px);border-color:rgba(99,102,241,.4)}
.btn{display:inline-block;padding:.85rem 1.75rem;border-radius:12px;font-weight:600;text-decoration:none;font-size:.9rem;text-align:center;transition:all .2s}
.btn-primary{background:linear-gradient(135deg,#6366f1,#22d3ee);color:white}
.btn-ghost{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.08);color:#94a3b8}
.btn-ghost:hover{background:rgba(255,255,255,.1);color:#e2e8f0}
</style>
</head>
<body>
<div style="max-width:1200px;margin:0 auto">
  <div class="flex items-center justify-between mb-8">
    <div>
      <h1 style="font-size:2rem;font-weight:700;background:linear-gradient(135deg,#6366f1,#22d3ee);-webkit-background-clip:text;-webkit-text-fill-color:transparent">
        CareerMantra AI
      </h1>
      <p class="text-slate-400 text-sm mt-0.5">Welcome back, {{ user.username if user else "there" }}</p>
    </div>
    <a href="/logout" class="btn btn-ghost text-sm">Logout</a>
  </div>

  <!-- Stats -->
  <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
    {% set vals = [
      ("Level",    p.current_level if p else 1,      "#6366f1"),
      ("Solved",   p.questions_solved if p else 0,   "#22d3ee"),
      ("Streak",   (p.streak_days|string + " days") if p else "0 days", "#10b981"),
      ("Score",    (p.overall_score|round(0)|int|string + "%") if p and p.overall_score else "—", "#f59e0b"),
    ] %}
    {% for label, val, color in vals %}
    <div class="glass p-5 text-center">
      <div style="font-size:2rem;font-weight:700;color:{{ color }}">{{ val }}</div>
      <div class="text-xs text-slate-500 uppercase tracking-widest mt-1">{{ label }}</div>
    </div>
    {% endfor %}
  </div>

  <!-- Feature cards -->
  <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
    {% for icon, title, desc, href in [
      ("🎤", "AI Mock Interview", "Practice with AI. Voice-to-voice feedback.", "/ai_interview"),
      ("🏋️", "Practice Questions", "15 levels of DSA, behavioral & system design.", "/practice"),
      ("🤖", "AI Coach", "Ask anything. Get instant expert guidance.", "/ai_chatbot"),
      ("📊", "Performance", "Deep analytics on your progress and weak spots.", "/performance"),
      ("🏢", "Company Questions", "Real questions from 15+ top companies.", "/company_questions"),
      ("🎯", "Join Live Interview", "Enter a live room with your interviewer.", "/join_interview"),
    ] %}
    <a href="{{ href }}" class="card" style="text-decoration:none">
      <div style="font-size:2.2rem;margin-bottom:.75rem">{{ icon }}</div>
      <div class="font-semibold text-white mb-1">{{ title }}</div>
      <div class="text-sm text-slate-400">{{ desc }}</div>
    </a>
    {% endfor %}
  </div>
</div>
</body></html>'''
