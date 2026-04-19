"""
socket_handlers.py — Real-time room logic for CareerMantra AI.
 
Register by calling init_handlers(socketio, db) from your app factory
after flask_socketio is initialized. All room state lives in the DB;
Redis can back the message_queue dict if you scale to multiple workers.
"""
 
import json
import hashlib
from datetime import datetime
from functools import wraps
 
from flask import request, session
from flask_socketio import emit, join_room, leave_room, disconnect
 
import google.generativeai as genai
 
 
# In-memory buffer for code sync — debounce DB writes to every 5s.
# Key: room_code, Value: {"code": str, "dirty_since": datetime}
# TODO: swap this for Redis if you deploy multiple SocketIO workers.
_code_buffer = {}
 
# Tracks socket_id → {room_code, user_id, role} for disconnect cleanup.
_connections = {}
 
 
def init_handlers(socketio, db, Room, LiveSession, ChatMessage, User):
    """Wire up all SocketIO event handlers. Called once from app factory."""
 
    def require_auth(f):
        """Reject events from unauthenticated sockets immediately."""
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not session.get("user"):
                disconnect()
                return
            return f(*args, **kwargs)
        return wrapper
 
    # ------------------------------------------------------------------ #
    #  CONNECTION LIFECYCLE                                              #
    # ------------------------------------------------------------------ #
 
    @socketio.on("connect")
    @require_auth
    def on_connect():
        # Nothing to do on bare connect — the client joins a room explicitly.
        # Keeping this handler so we can add rate-limiting here later.
        pass
 
    @socketio.on("disconnect")
    def on_disconnect():
        meta = _connections.pop(request.sid, None)
        if not meta:
            return
 
        room_code = meta["room_code"]
        role = meta["role"]
 
        emit("participant_left", {"user": meta["username"], "role": role}, room=room_code)
 
        # Flush any buffered code snapshot to DB on disconnect so we don't
        # lose the candidate's last state if the tab closes mid-interview.
        _flush_code_to_db(room_code, db, LiveSession, Room)
 
    # ------------------------------------------------------------------ #
    #  JOINING & LEAVING ROOMS                                           #
    # ------------------------------------------------------------------ #
 
    @socketio.on("join_room")
    @require_auth
    def on_join(data):
        room_code = data.get("room_code", "").upper().strip()
        passcode  = data.get("passcode", "")
 
        room = Room.query.filter_by(room_code=room_code).first()
        if not room:
            emit("error", {"msg": "Room not found."})
            return
 
        if room.status == "ended":
            emit("error", {"msg": "This interview has already ended."})
            return
 
        # Verify passcode — interviewers skip this check.
        user = User.query.filter_by(username=session["user"]).first()
        if user.role == "candidate":
            passcode_hash = hashlib.sha256(passcode.encode()).hexdigest()
            if passcode_hash != room.passcode_hash:
                emit("error", {"msg": "Incorrect passcode."})
                return
            # Bind candidate to room on first valid join.
            if not room.candidate_id:
                room.candidate_id = user.id
                db.session.commit()
 
        join_room(room_code)
        _connections[request.sid] = {
            "room_code": room_code,
            "user_id":   str(user.id),
            "username":  user.full_name or user.username,
            "role":      user.role,
        }
 
        # Send the candidate the current editor state so they're in sync.
        live = LiveSession.query.filter_by(room_id=room.id).first()
        emit("room_state", {
            "stage":         live.current_stage if live else 0,
            "code":          live.code_snapshot or "",
            "language":      live.code_language or "python",
            "current_q":     live.current_question or "",
            "ai_suggestions": json.loads(live.ai_suggestions or "[]"),
        })
 
        emit("participant_joined", {
            "user": user.full_name or user.username,
            "role": user.role,
        }, room=room_code)
 
    @socketio.on("leave_room")
    @require_auth
    def on_leave(data):
        room_code = data.get("room_code", "").upper()
        leave_room(room_code)
        meta = _connections.pop(request.sid, None)
        if meta:
            emit("participant_left", {"user": meta["username"], "role": meta["role"]}, room=room_code)
 
    # ------------------------------------------------------------------ #
    #  CHAT MESSAGES                                                     #
    # ------------------------------------------------------------------ #
 
    @socketio.on("chat_message")
    @require_auth
    def on_chat(data):
        room_code = data.get("room_code", "").upper()
        content   = (data.get("content") or "").strip()
        is_private = bool(data.get("is_private", False))  # interviewer-only notes
 
        if not content or len(content) > 4000:
            return
 
        room = Room.query.filter_by(room_code=room_code).first()
        if not room or room.status != "active":
            return
 
        user = User.query.filter_by(username=session["user"]).first()
 
        msg = ChatMessage(
            room_id    = room.id,
            sender_id  = user.id,
            content    = content,
            is_private = is_private,
            sent_at    = datetime.utcnow(),
        )
        db.session.add(msg)
        db.session.commit()
 
        payload = {
            "id":         str(msg.id),
            "sender":     user.full_name or user.username,
            "role":       user.role,
            "content":    content,
            "is_private": is_private,
            "sent_at":    msg.sent_at.isoformat(),
        }
 
        if is_private:
            # Private notes only go back to the interviewer's socket.
            emit("chat_message", payload)
        else:
            emit("chat_message", payload, room=room_code)
 
    # ------------------------------------------------------------------ #
    #  CODE EDITOR SYNC                                                  #
    # ------------------------------------------------------------------ #
 
    @socketio.on("code_change")
    @require_auth
    def on_code_change(data):
        room_code = data.get("room_code", "").upper()
        code      = data.get("code", "")
        language  = data.get("language", "python")
 
        # Broadcast to everyone else in the room immediately so the interviewer
        # sees keystrokes in real-time. skip_sid prevents echoing back to sender.
        emit("code_update", {"code": code, "language": language},
             room=room_code, skip_sid=request.sid)
 
        # Buffer the write — we only hit the DB every 5s to avoid thrashing
        # on rapid keystrokes. _flush_code_to_db is triggered on a schedule
        # by the heartbeat or on disconnect.
        buf = _code_buffer.setdefault(room_code, {})
        buf["code"]        = code
        buf["language"]    = language
        buf["dirty_since"] = buf.get("dirty_since") or datetime.utcnow()
 
        # Flush if the buffer has been dirty for >5 seconds.
        age = (datetime.utcnow() - buf["dirty_since"]).total_seconds()
        if age >= 5:
            _flush_code_to_db(room_code, db, LiveSession, Room)
 
    @socketio.on("language_change")
    @require_auth
    def on_language_change(data):
        room_code = data.get("room_code", "").upper()
        language  = data.get("language", "python")
        emit("language_update", {"language": language}, room=room_code, skip_sid=request.sid)
 
    # ------------------------------------------------------------------ #
    #  WHITEBOARD                                                        #
    # ------------------------------------------------------------------ #
 
    @socketio.on("whiteboard_stroke")
    @require_auth
    def on_stroke(data):
        room_code = data.get("room_code", "").upper()
        # Just relay — the full canvas state is persisted via whiteboard_save.
        emit("whiteboard_stroke", data, room=room_code, skip_sid=request.sid)
 
    @socketio.on("whiteboard_save")
    @require_auth
    def on_whiteboard_save(data):
        """Persist canvas JSON periodically (client sends this every 10s)."""
        room_code    = data.get("room_code", "").upper()
        canvas_data  = data.get("canvas_data")  # JSON-serializable stroke list
 
        room = Room.query.filter_by(room_code=room_code).first()
        if not room:
            return
 
        live = LiveSession.query.filter_by(room_id=room.id).first()
        if live:
            live.whiteboard_data = json.dumps(canvas_data)
            db.session.commit()
 
    @socketio.on("whiteboard_clear")
    @require_auth
    def on_whiteboard_clear(data):
        room_code = data.get("room_code", "").upper()
        emit("whiteboard_cleared", {}, room=room_code)
 
    # ------------------------------------------------------------------ #
    #  INTERVIEW STAGE CONTROL (interviewer only)                        #
    # ------------------------------------------------------------------ #
 
    @socketio.on("set_stage")
    @require_auth
    def on_set_stage(data):
        if session.get("role") != "interviewer":
            return
 
        room_code = data.get("room_code", "").upper()
        stage     = int(data.get("stage", 0))
        question  = data.get("question", "")
 
        room = Room.query.filter_by(room_code=room_code).first()
        if not room:
            return
 
        live = LiveSession.query.filter_by(room_id=room.id).first()
        if live:
            live.current_stage    = stage
            live.current_question = question
            db.session.commit()
 
        emit("stage_changed", {"stage": stage, "question": question}, room=room_code)
 
    @socketio.on("set_question")
    @require_auth
    def on_set_question(data):
        """Interviewer pushes a new question to the candidate's screen."""
        if session.get("role") != "interviewer":
            return
 
        room_code = data.get("room_code", "").upper()
        question  = (data.get("question") or "").strip()
 
        room = Room.query.filter_by(room_code=room_code).first()
        if not room:
            return
 
        live = LiveSession.query.filter_by(room_id=room.id).first()
        if live:
            live.current_question = question
            db.session.commit()
 
        emit("question_set", {"question": question}, room=room_code)
 
    # ------------------------------------------------------------------ #
    #  PROCTORING (candidate-side, auto-reported by the browser)         #
    # ------------------------------------------------------------------ #
 
    @socketio.on("proctoring_event")
    @require_auth
    def on_proctor_event(data):
        event_type = data.get("type")  # "tab_switch" | "fullscreen_exit"
        room_code  = data.get("room_code", "").upper()
 
        room = Room.query.filter_by(room_code=room_code).first()
        if not room:
            return
 
        live = LiveSession.query.filter_by(room_id=room.id).first()
        if not live:
            return
 
        if event_type == "tab_switch":
            live.candidate_tab_switches = (live.candidate_tab_switches or 0) + 1
        elif event_type == "fullscreen_exit":
            live.candidate_fullscreen_exits = (live.candidate_fullscreen_exits or 0) + 1
 
        db.session.commit()
 
        # Alert the interviewer in real time.
        user = User.query.filter_by(username=session["user"]).first()
        emit("proctor_alert", {
            "type":      event_type,
            "candidate": user.full_name or user.username,
            "tab_switches":       live.candidate_tab_switches,
            "fullscreen_exits":   live.candidate_fullscreen_exits,
        }, room=room_code)
 
    # ------------------------------------------------------------------ #
    #  AI CO-PILOT (interviewer triggers, Gemini responds)               #
    # ------------------------------------------------------------------ #
 
    @socketio.on("request_ai_suggestions")
    @require_auth
    def on_ai_suggestions(data):
        if session.get("role") != "interviewer":
            return
 
        room_code     = data.get("room_code", "").upper()
        asked_so_far  = data.get("asked_questions", [])
 
        room = Room.query.filter_by(room_code=room_code).first()
        if not room:
            return
 
        live      = LiveSession.query.filter_by(room_id=room.id).first()
        candidate = User.query.get(room.candidate_id) if room.candidate_id else None
        
        # Build context — gracefully degrade when resume/JD is missing.
        resume_text = "No resume uploaded."  # Fallback for now until resume feature added
        jd_text     = "Software Engineer"    # Fallback job description
        stage_names = ["intro", "coding", "system_design", "behavioral", "closing"]
        stage       = stage_names[min(live.current_stage, 4)] if live else "intro"
 
        prompt = f"""You are an expert technical interviewer assistant for CareerMantra AI.
RESUME: {{resume_text}}
JOB_DESC: {{jd_text}}
STAGE: {{stage}}
ASKED_QUESTIONS: {{json.dumps(asked_so_far)}}
 
Suggest exactly 3 tailored interview questions for the interviewer to ask RIGHT NOW.
Respond ONLY in JSON format:
{{
  "questions": [
    {{"q": "...", "why": "...", "follow_up": "..."}},
    {{"q": "...", "why": "...", "follow_up": "..."}},
    {{"q": "...", "why": "...", "follow_up": "..."}}
  ],
  "stage_tip": "..."
}}"""
 
        try:
            model    = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            raw      = response.text.strip().lstrip("```json").rstrip("```").strip()
            result   = json.loads(raw)
        except Exception as e:
            emit("ai_suggestions_error", {"msg": f"Gemini error: {str(e)}"})
            return
 
        if live:
            live.ai_suggestions = json.dumps(result.get("questions", []))
            db.session.commit()
 
        emit("ai_suggestions", result)
 
    # ------------------------------------------------------------------ #
    #  ROOM END                                                          #
    # ------------------------------------------------------------------ #
 
    @socketio.on("end_interview")
    @require_auth
    def on_end_interview(data):
        if session.get("role") != "interviewer":
            return
 
        room_code = data.get("room_code", "").upper()
        room = Room.query.filter_by(room_code=room_code).first()
        if not room:
            return
 
        room.status   = "ended"
        db.session.commit()
 
        _flush_code_to_db(room_code, db, LiveSession, Room)
        emit("interview_ended", {"room_code": room_code}, room=room_code)
 
 
# ------------------------------------------------------------------ #
#  HELPERS                                                           #
# ------------------------------------------------------------------ #
 
def _flush_code_to_db(room_code, db, LiveSession, Room):
    """Write buffered code snapshot to DB and clear the dirty flag."""
    buf = _code_buffer.pop(room_code, None)
    if not buf or not buf.get("code"):
        return
 
    room = Room.query.filter_by(room_code=room_code).first()
    if not room:
        return
 
    live = LiveSession.query.filter_by(room_id=room.id).first()
    if live:
        live.code_snapshot = buf["code"]
        live.code_language = buf.get("language", "python")
        db.session.commit()
