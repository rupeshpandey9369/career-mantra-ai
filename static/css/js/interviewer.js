// ========================================
// CareerMantra AI - Live Interviewer Rooms
// Mock Interview + Timer + Feedback System
// ========================================

class InterviewRoom {
    constructor() {
        this.currentQuestion = 0;
        this.timeLeft = 300; // 5 minutes per question
        this.questions = [
            {
                id: 1,
                question: "Explain the difference between let, const, and var in JavaScript. When would you use each?",
                category: "JavaScript Fundamentals",
                time: 300,
                difficulty: "Easy"
            },
            {
                id: 2,
                question: "How does the event loop work in JavaScript? Explain call stack, callback queue, and microtasks.",
                category: "JavaScript Advanced",
                time: 420,
                difficulty: "Medium"
            },
            {
                id: 3,
                question: "Design a URL shortener system. What data structures would you use and why?",
                category: "System Design",
                time: 600,
                difficulty: "Hard"
            },
            {
                id: 4,
                question: "Explain React Hooks. Implement useDebounce custom hook from scratch.",
                category: "React",
                time: 360,
                difficulty: "Medium"
            },
            {
                id: 5,
                question: "What are the differences between Redux Toolkit and Zustand? When to use each?",
                category: "State Management",
                time: 300,
                difficulty: "Medium"
            }
        ];
        this.answers = [];
        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
    }

    // 🎯 Start Interview Session
    startInterview(role = 'frontend') {
        document.getElementById('room-setup').classList.add('hidden');
        document.getElementById('interview-active').classList.remove('hidden');
        this.loadQuestion();
        this.startTimer();
    }

    // ❓ Load Current Question
    loadQuestion() {
        if (this.currentQuestion >= this.questions.length) {
            this.endInterview();
            return;
        }

        const q = this.questions[this.currentQuestion];
        document.getElementById('question-text').innerHTML = `
            <div class="text-center">
                <div class="text-3xl font-bold text-gray-800 mb-4">Q${this.currentQuestion + 1}/5</div>
                <div class="w-full bg-gray-200 rounded-full h-2 mb-6">
                    <div class="bg-gradient-to-r from-orange-500 to-red-500 h-2 rounded-full transition-all" 
                         style="width: ${((this.currentQuestion + 1) / 5) * 100}%"></div>
                </div>
                <div class="bg-gradient-to-r from-orange-50 to-red-50 p-8 rounded-3xl border-4 border-orange-200 shadow-2xl">
                    <div class="text-sm font-semibold text-orange-600 uppercase tracking-wide mb-4">${q.category}</div>
                    <h2 class="text-2xl md:text-3xl font-black text-gray-900 leading-tight mb-6">${q.question}</h2>
                    <div class="text-sm text-gray-500">Difficulty: <span class="font-bold text-orange-600">${q.difficulty}</span></div>
                </div>
            </div>
        `;

        document.getElementById('current-time').textContent = this.formatTime(q.time);
        this.timeLeft = q.time;
    }

    // ⏱️ Timer Management
    startTimer() {
        this.timer = setInterval(() => {
            this.timeLeft--;
            document.getElementById('current-time').textContent = this.formatTime(this.timeLeft);
            
            if (this.timeLeft <= 0) {
                this.nextQuestion();
            }
        }, 1000);
    }

    formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    // ▶️ Record Answer
    async startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaRecorder = new MediaRecorder(stream);
            this.audioChunks = [];

            this.mediaRecorder.ondataavailable = (event) => {
                this.audioChunks.push(event.data);
            };

            this.mediaRecorder.onstop = () => {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
                const url = URL.createObjectURL(audioBlob);
                document.getElementById('recorded-answer').src = url;
                document.getElementById('audio-preview').classList.remove('hidden');
            };

            this.mediaRecorder.start();
            this.isRecording = true;
            document.getElementById('record-btn').innerHTML = '⏹️ Stop Recording';
            document.getElementById('record-btn').classList.add('bg-red-500', 'hover:bg-red-600');
            
        } catch (err) {
            showToast('Microphone access denied', 'error');
        }
    }

    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            document.getElementById('record-btn').innerHTML = '🎤 Record Answer';
            document.getElementById('record-btn').classList.remove('bg-red-500', 'hover:bg-red-600');
        }
    }

    // ➡️ Next Question
    nextQuestion() {
        this.stopRecording();
        clearInterval(this.timer);
        this.answers.push({
            question: this.questions[this.currentQuestion].question,
            timeUsed: this.questions[this.currentQuestion].time - this.timeLeft,
            recorded: this.audioChunks.length > 0
        });
        this.currentQuestion++;
        setTimeout(() => this.loadQuestion(), 500);
        setTimeout(() => this.startTimer(), 1000);
    }

    // 🏁 End Interview + Show Results
    endInterview() {
        clearInterval(this.timer);
        document.getElementById('interview-active').classList.add('hidden');
        document.getElementById('interview-results').classList.remove('hidden');

        const totalTime = this.questions.reduce((sum, q) => sum + q.time, 0);
        const avgTimePerQuestion = totalTime / 5;
        
        document.getElementById('results').innerHTML = `
            <div class="text-center">
                <div class="text-6xl mb-8">🎤</div>
                <h2 class="text-5xl font-black bg-gradient-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent mb-8">
                    Interview Complete!
                </h2>
                <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12 max-w-4xl mx-auto">
                    <div class="bg-gradient-to-br from-orange-500 to-red-500 text-white p-8 rounded-3xl shadow-2xl">
                        <div class="text-4xl font-black mb-2">${this.currentQuestion}/5</div>
                        <div class="text-lg opacity-90">Questions Answered</div>
                    </div>
                    <div class="bg-gradient-to-br from-emerald-500 to-teal-500 text-white p-8 rounded-3xl shadow-2xl">
                        <div class="text-4xl font-black mb-2">${Math.round(avgTimePerQuestion)}s</div>
                        <div class="text-lg opacity-90">Avg Response Time</div>
                    </div>
                    <div class="bg-gradient-to-br from-blue-500 to-indigo-500 text-white p-8 rounded-3xl shadow-2xl">
                        <div class="text-4xl font-black mb-2">${this.answers.filter(a => a.recorded).length}</div>
                        <div class="text-lg opacity-90">Recordings Saved</div>
                    </div>
                </div>
                
                <div class="max-w-3xl mx-auto space-y-4 mb-12">
                    ${this.answers.map((answer, idx) => `
                        <div class="flex items-center justify-between p-6 bg-white/50 backdrop-blur-xl rounded-2xl border border-white/30 hover:shadow-xl transition-all group">
                            <div>
                                <div class="font-bold text-lg text-gray-800 mb-1">Q${idx + 1}</div>
                                <div class="text-sm text-gray-500">Time: ${answer.timeUsed}s</div>
                            </div>
                            <div class="flex items-center gap-3">
                                ${answer.recorded ? '🎵 Recorded' : '📝 Text Only'}
                                <button onclick="interviewRoom.replayAnswer(${idx})" class="px-4 py-2 bg-orange-500 text-white rounded-xl text-sm font-bold hover:bg-orange-600 transition-all">
                                    Review
                                </button>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    // 🔄 Replay Answer
    replayAnswer(index) {
        document.getElementById('audio-preview').classList.remove('hidden');
        // In production, load saved audio blob from answers array
        showToast('Audio playback feature coming soon!', 'info');
    }
}

// 🎮 Global Interview Room Instance
const interviewRoom = new InterviewRoom();

// 🎤 Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Room selection
    document.querySelectorAll('.room-card').forEach(card => {
        card.addEventListener('click', () => {
            document.querySelectorAll('.room-card').forEach(c => c.classList.remove('ring-4', 'ring-orange-400'));
            card.classList.add('ring-4', 'ring-orange-400');
            document.getElementById('start-interview-btn').dataset.role = card.dataset.role;
        });
    });

    // Start interview
    document.getElementById('start-interview-btn').addEventListener('click', () => {
        const role = document.getElementById('start-interview-btn').dataset.role;
        if (role) {
            interviewRoom.startInterview(role);
        }
    });

    // Record controls
    document.getElementById('record-btn').addEventListener('click', () => {
        if (interviewRoom.isRecording) {
            interviewRoom.stopRecording();
        } else {
            interviewRoom.startRecording();
        }
    });
});

// 🔔 Utility Functions
function showToast(message, type = 'success') {
    // Use main.js toast system
    if (window.showToast) {
        window.showToast(message, type);
    } else {
        console.log(`Toast: ${message}`);
    }
}
