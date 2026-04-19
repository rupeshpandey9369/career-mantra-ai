import os
import json
import hashlib
import random
import string
from datetime import datetime, date, timedelta

from flask import (
    Flask, request, render_template, render_template_string,
    session, redirect, url_for, jsonify
)
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_migrate import Migrate
import google.generativeai as genai

from socket_handlers import init_handlers
from app_templates import _LOGIN_HTML, _ROOM_CREATED_HTML, _INTERVIEW_ROOM_HTML, _SCORECARD_HTML, _STUDENT_DASHBOARD_HTML
from app_templates2 import _JOIN_INTERVIEW_HTML, _PRACTICE_HTML, _AI_INTERVIEW_HTML, _AI_CHATBOT_HTML, _PERFORMANCE_HTML, _COMPANY_QUESTIONS_HTML, _ERROR_HTML




# ── App factory ───────────────────────────────────────────────────────────────

app = Flask(__name__)

app.secret_key        = os.environ.get("SECRET_KEY", "CareerMantraAI_2026_Rupesh")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///careermantra.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SOCKETIO_SERVER_URL"] = os.environ.get("SOCKETIO_SERVER_URL", "")

db      = SQLAlchemy(app)
migrate = Migrate(app, db)

# async_mode=None lets eventlet/gevent auto-detect; falls back to threading in dev.
socketio = SocketIO(app, cors_allowed_origins="*", async_mode=None)

genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))


# ── Models ────────────────────────────────────────────────────────────────────
# Keeping these inline for a single-file deployment. Split into models.py once
# the project grows beyond ~5 tables.

class User(db.Model):
    __tablename__ = "users"

    id            = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__("uuid").uuid4()))
    username      = db.Column(db.String(64), unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name     = db.Column(db.String(120), nullable=True)
    role          = db.Column(db.String(20), nullable=False, default="candidate")  # candidate | interviewer
    is_active     = db.Column(db.Boolean, default=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    last_login    = db.Column(db.DateTime, nullable=True)

    profile       = db.relationship("CandidateProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")


class CandidateProfile(db.Model):
    __tablename__ = "candidate_profiles"

    id                 = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__("uuid").uuid4()))
    user_id            = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False, unique=True)
    current_level      = db.Column(db.Integer, default=1)
    questions_solved   = db.Column(db.Integer, default=0)
    interviews_attended= db.Column(db.Integer, default=0)
    ai_interviews      = db.Column(db.Integer, default=0)
    streak_days        = db.Column(db.Integer, default=0)
    last_active_date   = db.Column(db.Date, nullable=True)
    overall_score      = db.Column(db.Float, default=0.0)
    dsa_score          = db.Column(db.Float, default=0.0)
    system_design_score= db.Column(db.Float, default=0.0)
    behavioral_score   = db.Column(db.Float, default=0.0)
    resume_url         = db.Column(db.String(512), nullable=True)
    target_companies   = db.Column(db.Text, default="[]")   # JSON list

    user = db.relationship("User", back_populates="profile")


class InterviewRoom(db.Model):
    __tablename__ = "interview_rooms"

    id               = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__("uuid").uuid4()))
    room_code        = db.Column(db.String(8), unique=True, nullable=False, index=True)
    passcode_hash    = db.Column(db.String(256), nullable=False)
    interviewer_id   = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    candidate_id     = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=True)
    status           = db.Column(db.String(20), default="scheduled")  # scheduled | active | ended
    room_type        = db.Column(db.String(20), default="mixed")
    position         = db.Column(db.String(120), nullable=True)
    scheduled_at     = db.Column(db.DateTime, nullable=True)
    started_at       = db.Column(db.DateTime, nullable=True)
    ended_at         = db.Column(db.DateTime, nullable=True)
    duration_minutes = db.Column(db.Integer, default=60)
    job_description  = db.Column(db.Text, nullable=True)
    livekit_room_name= db.Column(db.String(128), nullable=True)
    recording_url    = db.Column(db.String(512), nullable=True)
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)

    live_session = db.relationship("LiveSession", back_populates="room", uselist=False, cascade="all, delete-orphan")
    messages     = db.relationship("ChatMessage", back_populates="room", cascade="all, delete-orphan")
    scorecard    = db.relationship("InterviewScorecard", back_populates="room", uselist=False, cascade="all, delete-orphan")


class LiveSession(db.Model):
    __tablename__ = "live_sessions"

    id                      = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__("uuid").uuid4()))
    room_id                 = db.Column(db.String(36), db.ForeignKey("interview_rooms.id"), nullable=False, unique=True)
    current_stage           = db.Column(db.Integer, default=0)
    current_question        = db.Column(db.Text, nullable=True)
    code_snapshot           = db.Column(db.Text, nullable=True)
    code_language           = db.Column(db.String(32), default="python")
    whiteboard_data         = db.Column(db.Text, nullable=True)
    ai_suggestions          = db.Column(db.Text, default="[]")
    interviewer_notes       = db.Column(db.Text, nullable=True)
    candidate_tab_switches  = db.Column(db.Integer, default=0)
    candidate_fullscreen_exits = db.Column(db.Integer, default=0)
    updated_at              = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    room = db.relationship("InterviewRoom", back_populates="live_session")


class ChatMessage(db.Model):
    __tablename__ = "chat_messages"

    id           = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__("uuid").uuid4()))
    room_id      = db.Column(db.String(36), db.ForeignKey("interview_rooms.id"), nullable=False)
    sender_id    = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    message_type = db.Column(db.String(20), default="text")  # text | system | ai_hint
    content      = db.Column(db.Text, nullable=False)
    is_private   = db.Column(db.Boolean, default=False)
    sent_at      = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    room   = db.relationship("InterviewRoom", back_populates="messages")
    sender = db.relationship("User")


class InterviewScorecard(db.Model):
    __tablename__ = "interview_scorecards"

    id               = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__("uuid").uuid4()))
    room_id          = db.Column(db.String(36), db.ForeignKey("interview_rooms.id"), nullable=False, unique=True)
    candidate_id     = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    problem_solving  = db.Column(db.Integer, default=0)
    communication    = db.Column(db.Integer, default=0)
    code_quality     = db.Column(db.Integer, default=0)
    system_thinking  = db.Column(db.Integer, default=0)
    behavioral_fit   = db.Column(db.Integer, default=0)
    overall_score    = db.Column(db.Float, default=0.0)
    recommendation   = db.Column(db.String(20), nullable=True)  # hire | no_hire | maybe
    ai_summary       = db.Column(db.Text, nullable=True)
    interviewer_notes= db.Column(db.Text, nullable=True)
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)

    room = db.relationship("InterviewRoom", back_populates="scorecard")


class PracticeSession(db.Model):
    __tablename__ = "practice_sessions"

    id               = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__("uuid").uuid4()))
    candidate_id     = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    session_type     = db.Column(db.String(20), default="ai_mock")  # ai_mock | level | chatbot
    topic_tag        = db.Column(db.String(64), nullable=True)
    level            = db.Column(db.Integer, nullable=True)
    score            = db.Column(db.Float, nullable=True)
    ai_feedback      = db.Column(db.Text, nullable=True)
    duration_seconds = db.Column(db.Integer, nullable=True)
    tab_switches     = db.Column(db.Integer, default=0)
    completed_at     = db.Column(db.DateTime, default=datetime.utcnow, index=True)


# ── Init ──────────────────────────────────────────────────────────────────────

with app.app_context():
    db.create_all()
    # Seed the default interviewer account if it doesn't exist yet.
    if not User.query.filter_by(username="rupesh").first():
        interviewer = User(
            username      = "rupesh",
            password_hash = hashlib.sha256("rupesh123".encode()).hexdigest(),
            full_name     = "Rupesh Pandey",
            role          = "interviewer",
        )
        db.session.add(interviewer)
        db.session.commit()

init_handlers(socketio, db, InterviewRoom, LiveSession, ChatMessage, User)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_or_create_candidate(username: str) -> tuple[User, CandidateProfile]:
    """Upsert a candidate user row on first login."""
    user = User.query.filter_by(username=username).first()
    if not user:
        user = User(
            username      = username,
            password_hash = "",   # no password for quick-join candidates
            role          = "candidate",
        )
        db.session.add(user)
        db.session.flush()  # get user.id before creating profile

    if not user.profile:
        profile = CandidateProfile(user_id=user.id)
        db.session.add(profile)

    user.last_login = datetime.utcnow()
    db.session.commit()
    return user, user.profile


def _update_streak(profile: CandidateProfile):
    today = date.today()
    if profile.last_active_date == today:
        return
    if profile.last_active_date == today - timedelta(days=1):
        profile.streak_days += 1
    else:
        profile.streak_days = 1
    profile.last_active_date = today


def _generate_room_code() -> str:
    chars = string.ascii_uppercase + string.digits
    while True:
        code = "".join(random.choices(chars, k=8))
        if not InterviewRoom.query.filter_by(room_code=code).first():
            return code


def _require_role(*roles):
    """Decorator factory — redirects to login if session role not in roles."""
    from functools import wraps
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if session.get("role") not in roles:
                return redirect("/")
            return f(*args, **kwargs)
        return wrapper
    return decorator


# ── Auth ──────────────────────────────────────────────────────────────────────

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].lower().strip()
        pw_hash  = hashlib.sha256(request.form["password"].encode()).hexdigest()

        interviewer = User.query.filter_by(username=username, role="interviewer").first()
        if interviewer and interviewer.password_hash == pw_hash:
            session["user"] = username
            session["role"] = "interviewer"
            interviewer.last_login = datetime.utcnow()
            db.session.commit()
            return redirect("/interviewer_dashboard")

        # Any username/password combo creates a candidate account on the spot.
        # This mirrors the old behavior; swap for a real registration flow later.
        user, profile = _get_or_create_candidate(username)
        _update_streak(profile)
        db.session.commit()

        session["user"] = username
        session["role"] = "candidate"
        return redirect("/student_dashboard")

    return render_template_string(_LOGIN_HTML)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ── Interviewer routes ────────────────────────────────────────────────────────

@app.route("/interviewer_dashboard")
@_require_role("interviewer")
def interviewer_dashboard():
    me = User.query.filter_by(username=session["user"]).first()

    active_rooms = InterviewRoom.query.filter_by(
        interviewer_id=me.id, status="active"
    ).all()

    # Stats for the header cards
    total_candidates = sum(1 for r in active_rooms if r.candidate_id)

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    completed_today = InterviewRoom.query.filter(
        InterviewRoom.interviewer_id == me.id,
        InterviewRoom.status == "ended",
        InterviewRoom.ended_at >= today_start,
    ).count()

    scores = [r.scorecard.overall_score for r in active_rooms if r.scorecard]
    avg_score = round(sum(scores) / len(scores), 1) if scores else None

    # interviewer_dashboard.html expects a live_rooms dict-like context;
    # pass a list and let Jinja handle it — the template was built for this.
    return render_template(
        "interviewer_dashboard.html",
        live_rooms       = {r.room_code: _room_to_dict(r) for r in active_rooms},
        interview_sessions = {},   # handled by SocketIO now, not needed in template
        total_candidates = total_candidates,
        completed_today  = completed_today,
        avg_score        = avg_score,
        config           = app.config,
    )


@app.route("/create_interview", methods=["POST"])
@_require_role("interviewer")
def create_interview():
    me       = User.query.filter_by(username=session["user"]).first()
    passcode = request.form.get("passcode", "").strip() or _generate_room_code()[:6]

    room = InterviewRoom(
        room_code       = _generate_room_code(),
        passcode_hash   = hashlib.sha256(passcode.encode()).hexdigest(),
        interviewer_id  = me.id,
        status          = "active",   # open immediately so candidates can join
        room_type       = request.form.get("room_type", "mixed"),
        position        = request.form.get("position", ""),
        job_description = request.form.get("job_description", ""),
        duration_minutes= int(request.form.get("duration_minutes") or 60),
    )
    raw_dt = request.form.get("scheduled_at")
    if raw_dt:
        try:
            room.scheduled_at = datetime.fromisoformat(raw_dt)
        except ValueError:
            pass

    db.session.add(room)
    db.session.flush()

    live = LiveSession(room_id=room.id)
    db.session.add(live)
    db.session.commit()

    # Candidate name field is cosmetic metadata stored on the position field
    # if the user typed a name rather than a role title.
    candidate_label = request.form.get("candidate_name", "").strip()
    if candidate_label and not room.position:
        room.position = candidate_label
        db.session.commit()

    return render_template_string(_ROOM_CREATED_HTML, room=room, passcode=passcode)


@app.route("/interview_room/<room_code>")
@_require_role("interviewer", "candidate")
def interview_room(room_code):
    room = InterviewRoom.query.filter_by(room_code=room_code.upper()).first_or_404()
    if room.status == "ended":
        return redirect(f"/scorecard/{room_code}")

    recent_msgs = (
        ChatMessage.query
        .filter_by(room_id=room.id, is_private=False)
        .order_by(ChatMessage.sent_at.desc())
        .limit(50)
        .all()
    )[::-1]

    return render_template_string(
        _INTERVIEW_ROOM_HTML,
        room=room,
        messages=recent_msgs,
        role=session.get("role"),
        username=session.get("user"),
    )


@app.route("/end_room/<room_code>")
@_require_role("interviewer")
def end_room(room_code):
    room = InterviewRoom.query.filter_by(room_code=room_code.upper()).first()
    if room:
        room.status   = "ended"
        room.ended_at = datetime.utcnow()
        db.session.commit()
    return redirect("/interviewer_dashboard")


@app.route("/scorecard/<room_code>")
@_require_role("interviewer", "candidate")
def scorecard(room_code):
    room  = InterviewRoom.query.filter_by(room_code=room_code.upper()).first_or_404()
    card  = room.scorecard
    live  = room.live_session
    msgs  = ChatMessage.query.filter_by(room_id=room.id).order_by(ChatMessage.sent_at).all()

    # Auto-generate scorecard via Gemini if one doesn't exist yet.
    if not card and room.status == "ended":
        card = _generate_ai_scorecard(room, live, msgs)

    return render_template_string(
        _SCORECARD_HTML,
        room=room,
        card=card,
        live=live,
    )


# ── Candidate routes ──────────────────────────────────────────────────────────

@app.route("/student_dashboard")
@_require_role("candidate")
def student_dashboard():
    user    = User.query.filter_by(username=session["user"]).first()
    profile = user.profile if user else None
    return render_template_string(_STUDENT_DASHBOARD_HTML, user=user, p=profile)


@app.route("/join_interview")
@_require_role("candidate")
def join_interview():
    return render_template_string(_JOIN_INTERVIEW_HTML)


@app.route("/join_with_code", methods=["POST"])
@_require_role("candidate")
def join_with_code():
    code = request.form.get("room_code", "").upper().strip()
    room = InterviewRoom.query.filter_by(room_code=code).first()
    if not room or room.status == "ended":
        return render_template_string(_ERROR_HTML, msg="Room not found or already ended.", back="/join_interview")

    session["current_room"] = code
    if room.status == "scheduled":
        room.status = "active"
        db.session.commit()

    return redirect(f"/interview_room/{code}")


@app.route("/practice")
@_require_role("candidate")
def practice():
    user    = User.query.filter_by(username=session["user"]).first()
    profile = user.profile if user else None
    level   = profile.current_level if profile else 1
    return render_template_string(_PRACTICE_HTML, level=level, username=session["user"])


@app.route("/ai_interview")
@_require_role("candidate")
def ai_interview():
    user    = User.query.filter_by(username=session["user"]).first()
    profile = user.profile
    if profile:
        profile.ai_interviews = (profile.ai_interviews or 0) + 1
        db.session.commit()

    all_questions = [
        "Tell me about yourself (2 mins)", "Why this company?", "Strengths & weaknesses?",
        "Biggest failure story?", "Team conflict example?", "Leadership experience?",
        "Two Sum (Array)", "Valid parenthesis", "Merge intervals", "LRU Cache design",
        "Kth largest element", "Number of islands", "Course schedule (Graph)",
        "Design TinyURL", "Design YouTube", "Design Instagram", "Rate limiter",
        "Autocomplete system", "Payment gateway design", "Where do you see yourself in 5 years?",
    ]
    seed_val  = int(hashlib.md5(session["user"].encode()).hexdigest()[:8], 16)
    rng       = random.Random(seed_val)
    questions = ["Tell me about yourself (2 mins)"] + rng.sample(
        [q for q in all_questions if q != "Tell me about yourself (2 mins)"], 9
    )
    return render_template_string(_AI_INTERVIEW_HTML, questions=questions, username=session["user"])


@app.route("/ai_chatbot")
@_require_role("candidate")
def ai_chatbot():
    return render_template_string(_AI_CHATBOT_HTML, username=session.get("user", "there"))


@app.route("/performance")
@_require_role("candidate")
def performance():
    user    = User.query.filter_by(username=session["user"]).first()
    profile = user.profile if user else None

    sessions = PracticeSession.query.filter_by(candidate_id=user.id).order_by(
        PracticeSession.completed_at.desc()
    ).limit(100).all()

    topic_scores: dict = {}
    for s in sessions:
        if s.topic_tag and s.score is not None:
            topic_scores.setdefault(s.topic_tag, []).append(s.score)

    topic_avgs = {tag: round(sum(v)/len(v), 1) for tag, v in topic_scores.items()}

    return render_template_string(
        _PERFORMANCE_HTML,
        profile   = profile,
        username  = session["user"],
        topic_avgs= topic_avgs,
    )


@app.route("/company_questions")
@_require_role("candidate")
def company_questions():
    return render_template_string(_COMPANY_QUESTIONS_HTML, companies=_COMPANY_DATA)


# ── API endpoints ─────────────────────────────────────────────────────────────

@app.route("/chat", methods=["POST"])
def chat():
    data         = request.get_json(silent=True) or {}
    question     = (data.get("question") or "").strip()
    user_message = (data.get("user_answer") or data.get("message") or "").strip()
    username     = session.get("user", "Student")

    if not user_message:
        return jsonify({"reply": "Please type your question or message!"})

    if question and question != "Interview question":
        prompt = f"""You are CareerMantra AI Interview Coach.
Question: {question}
User Answer: {user_message}
Evaluate and respond EXACTLY in this format:
Score: XX%
Feedback: ...
Correct Answer: ...
Tip: ...
User: {username}"""
    else:
        prompt = f"""You are CareerMantra AI — expert career coach for top tech interviews.
Help with DSA, behavioral, system design, and career advice.
User message: {user_message}
Respond helpfully and concisely."""

    try:
        model    = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        reply    = response.text

        # If this was a scored answer, parse it and persist the session.
        user = User.query.filter_by(username=username).first()
        if user and user.profile and question:
            score_line = next((l for l in reply.splitlines() if l.startswith("Score:")), None)
            score_val  = None
            if score_line:
                try:
                    score_val = float(score_line.split(":")[1].strip().replace("%", ""))
                except (ValueError, IndexError):
                    pass

            tag = _infer_topic_tag(question)
            ps  = PracticeSession(
                candidate_id = user.id,
                session_type = "ai_mock",
                topic_tag    = tag,
                score        = score_val,
                ai_feedback  = reply,
            )
            db.session.add(ps)
            _refresh_skill_scores(user.profile)
            db.session.commit()

        return jsonify({"reply": reply})

    except Exception as e:
        app.logger.error("Gemini error: %s", e)
        return jsonify({"reply": "I'm having trouble connecting. Try again in a moment!"})


@app.route("/get_messages/<room_code>")
def get_messages(room_code):
    """Legacy polling endpoint — kept for backward compat with old student_interview page."""
    room = InterviewRoom.query.filter_by(room_code=room_code.upper()).first()
    if not room:
        return jsonify({"messages": []})

    msgs = (
        ChatMessage.query
        .filter_by(room_id=room.id, is_private=False)
        .order_by(ChatMessage.sent_at.desc())
        .limit(20)
        .all()
    )
    return jsonify({"messages": [
        {"user": m.sender.username, "role": m.sender.role, "text": m.content,
         "time": m.sent_at.strftime("%H:%M")}
        for m in reversed(msgs)
    ]})


@app.route("/send_message/<room_code>", methods=["POST"])
def send_message_http(room_code):
    """Legacy HTTP fallback for rooms not yet on SocketIO."""
    data    = request.get_json(silent=True) or {}
    user    = User.query.filter_by(username=session.get("user", "")).first()
    room    = InterviewRoom.query.filter_by(room_code=room_code.upper()).first()

    if not user or not room:
        return jsonify({"status": "error"})

    msg = ChatMessage(
        room_id  = room.id,
        sender_id= user.id,
        content  = (data.get("text") or "").strip(),
    )
    db.session.add(msg)
    db.session.commit()
    return jsonify({"status": "sent"})


@app.route("/next_stage/<room_code>", methods=["POST"])
@_require_role("interviewer")
def next_stage(room_code):
    room = InterviewRoom.query.filter_by(room_code=room_code.upper()).first()
    if room and room.live_session and room.live_session.current_stage < 4:
        room.live_session.current_stage += 1
        db.session.commit()
    return jsonify({"status": "updated"})


@app.route("/upload_audio", methods=["POST"])
def upload_audio():
    # TODO: pipe this to Whisper or Google STT for live transcription
    return jsonify({"status": "success"})


@app.route("/api/rooms/<room_code>/end", methods=["POST"])
@_require_role("interviewer")
def api_end_room(room_code):
    room = InterviewRoom.query.filter_by(room_code=room_code.upper()).first_or_404()
    room.status   = "ended"
    room.ended_at = datetime.utcnow()
    db.session.commit()
    return jsonify({"status": "ended"})


# ── Internal helpers ──────────────────────────────────────────────────────────

def _room_to_dict(room: InterviewRoom) -> dict:
    return {
        "candidate": room.position or "Candidate",
        "position":  room.position or "",
        "stage":     room.live_session.current_stage if room.live_session else 0,
        "status":    room.status,
    }


def _infer_topic_tag(question: str) -> str:
    q = question.lower()
    if any(k in q for k in ["design", "system", "scalab", "architect"]):
        return "SystemDesign"
    if any(k in q for k in ["tell me", "conflict", "failure", "strength", "weakness", "why", "behavior", "star"]):
        return "Behavioral"
    return "DSA"


def _refresh_skill_scores(profile: CandidateProfile):
    """Recalculate aggregate skill scores from the last 20 sessions per topic."""
    for tag, col in [("DSA", "dsa_score"), ("SystemDesign", "system_design_score"), ("Behavioral", "behavioral_score")]:
        recent = (
            PracticeSession.query
            .filter_by(candidate_id=profile.user_id, topic_tag=tag)
            .order_by(PracticeSession.completed_at.desc())
            .limit(20)
            .all()
        )
        scores = [s.score for s in recent if s.score is not None]
        if scores:
            setattr(profile, col, round(sum(scores) / len(scores), 1))


def _generate_ai_scorecard(room, live, msgs):
    if not msgs and not (live and live.code_snapshot):
        return None

    transcript = ""
    for m in msgs:
        if not m.is_private:
            transcript += f"[{m.sender.role}] {m.sender.username}: {m.content}\n"
    notes = live.interviewer_notes if live else ""

    prompt = f"""You are a senior engineering hiring manager generating an interview assessment.
TRANSCRIPT:
{transcript[:6000]}
INTERVIEWER_NOTES: {notes or 'None'}
CODE_SNAPSHOT: {(live.code_snapshot or '')[:2000]}

Respond ONLY in JSON:
{{"problem_solving":0,"communication":0,"code_quality":0,"system_thinking":0,"behavioral_fit":0,
"recommendation":"maybe","ai_summary":"","candidate_feedback":""}}"""

    try:
        model  = genai.GenerativeModel("gemini-1.5-flash")
        raw    = model.generate_content(prompt).text.strip().lstrip("```json").rstrip("```").strip()
        data   = json.loads(raw)
    except Exception as e:
        app.logger.error("Scorecard generation failed: %s", e)
        return None

    scores = [data.get(k, 0) for k in ("problem_solving","communication","code_quality","system_thinking","behavioral_fit")]
    card = InterviewScorecard(
        room_id          = room.id,
        candidate_id     = room.candidate_id or "",
        problem_solving  = data.get("problem_solving", 0),
        communication    = data.get("communication", 0),
        code_quality     = data.get("code_quality", 0),
        system_thinking  = data.get("system_thinking", 0),
        behavioral_fit   = data.get("behavioral_fit", 0),
        overall_score    = round(sum(scores) / len(scores), 1),
        recommendation   = data.get("recommendation", "maybe"),
        ai_summary       = data.get("ai_summary", ""),
        interviewer_notes= data.get("candidate_feedback", ""),
    )
    db.session.add(card)
    db.session.commit()
    return card


# ── Static company data ───────────────────────────────────────────────────────

_COMPANY_DATA = {
    "Google":   ["Why Google?","Rate DSA 1-10","System Design YouTube","2nd highest salary SQL","LRU Cache"],
    "Amazon":   ["Leadership Principles?","Design TinyURL","LRU Cache","Kth largest element","Top K frequent"]
}

# ── Entrypoint ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)

# Gunicorn / Vercel WSGI entrypoint
application = app
