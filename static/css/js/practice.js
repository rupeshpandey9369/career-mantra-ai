// ========================================
// CareerMantra AI - Practice Quiz Logic
// OpenTDB API + Smooth UX + Auto-Next
// ========================================

let currentLevel = 1;
let questions = [];
let currentQuestion = 0;
let score = 0;
let isAnswered = false;

const decodeHtml = (str) => {
    const map = {
        '&quot;': '"',
        '&#039;': "'",
        '&amp;': '&',
        '&lt;': '<',
        '&gt;': '>',
        '&nbsp;': ' ',
        '&#x27;': "'"
    };
    return str.replace(/([&quot;&#039;&amp;&lt;&gt;&nbsp;&#x27;])/g, (match) => map[match]);
};

// 🎯 Load Level + Fetch Questions
async function loadLevel(level) {
    currentLevel = level;
    
    // Disable all buttons + loading state
    document.querySelectorAll('.level-btn').forEach(btn => {
        btn.disabled = true;
        btn.classList.add('loading');
    });
    
    try {
        // Fetch from WORKING API
        const response = await fetch(`/api/questions/${level}`);
        if (!response.ok) throw new Error('API failed');
        
        const data = await response.json();
        questions = data;
        currentQuestion = 0;
        score = 0;
        isAnswered = false;
        
        // Update UI
        document.getElementById('current-level').textContent = `Level ${level}`;
        document.getElementById('score').textContent = 'Score: 0/10';
        document.getElementById('questions-container').classList.remove('hidden');
        
        // Auto show first question
        setTimeout(() => showQuestion(), 500);
        
    } catch (error) {
        console.error('API Error:', error);
        document.getElementById('questions').innerHTML = `
            <div class="text-center p-16">
                <div class="text-6xl mb-6">❌</div>
                <h2 class="text-3xl font-bold text-red-600 mb-4">Questions Failed to Load</h2>
                <p class="text-xl text-gray-600 mb-8">API Error - Check console (F12)</p>
                <button onclick="location.reload()" class="px-8 py-4 bg-blue-600 text-white rounded-2xl font-bold shadow-xl hover:shadow-2xl transition-all">
                    🔄 Try Again
                </button>
            </div>
        `;
    } finally {
        // Re-enable level buttons
        document.querySelectorAll('.level-btn').forEach(btn => {
            btn.disabled = false;
            btn.classList.remove('loading');
        });
    }
}

// 📝 Show Current Question
function showQuestion() {
    if (currentQuestion >= questions.length) {
        showResults();
        return;
    }

    const q = questions[currentQuestion];
    const allAnswers = [...q.incorrect_answers, q.correct_answer].sort(() => Math.random() - 0.5);
    isAnswered = false;

    document.getElementById('questions').innerHTML = `
        <div class="max-w-3xl mx-auto animate-in fade-in duration-500">
            <!-- Progress Bar -->
            <div class="flex justify-between items-center mb-8">
                <div class="text-2xl font-bold text-gray-800">
                    Q${currentQuestion + 1}/10
                </div>
                <div class="w-64 bg-gray-200 rounded-full h-3">
                    <div class="bg-gradient-to-r from-blue-500 to-indigo-600 h-3 rounded-full transition-all duration-1000" 
                         style="width: ${(currentQuestion / questions.length) * 100}%"></div>
                </div>
            </div>
            
            <!-- Question Card -->
            <div class="bg-gradient-to-r from-blue-50 to-indigo-50 p-8 rounded-3xl shadow-2xl border-l-8 border-blue-500 mb-8">
                <h3 class="text-2xl font-bold text-gray-800 mb-8 leading-relaxed">${decodeHtml(q.question)}</h3>
                
                <!-- Answer Buttons -->
                <div class="grid md:grid-cols-2 gap-4">
                    ${allAnswers.map((answer, index) => `
                        <button onclick="selectAnswer('${decodeHtml(q.correct_answer)}', '${decodeHtml(answer)}', this, ${index})" 
                                class="answer-btn option-btn p-6 bg-white border-2 border-gray-200 rounded-2xl text-left hover:shadow-xl hover:border-blue-300 hover:-translate-y-1 transition-all duration-300 h-24 flex items-center text-lg font-medium group">
                            <span class="block truncate">${decodeHtml(answer)}</span>
                            <div class="opacity-0 group-hover:opacity-100 transition-opacity w-6 h-6 ml-3 rounded-full border-2 border-gray-300 flex items-center justify-center text-xs font-bold">
                                ${index + 1}
                            </div>
                        </button>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
}

// ✅ Answer Selection + Auto-Next
function selectAnswer(correct, selected, btn, index) {
    if (isAnswered) return;
    isAnswered = true;

    // Disable all buttons
    document.querySelectorAll('.answer-btn').forEach(b => b.disabled = true);

    // Feedback animation
    setTimeout(() => {
        if (correct === selected) {
            // ✅ Correct
            btn.classList.add('correct');
            score++;
            btn.innerHTML += ' <span class="ml-3 px-3 py-1 bg-green-500 text-white text-xs font-bold rounded-full animate-pulse">✅ +1</span>';
        } else {
            // ❌ Wrong
            btn.classList.add('incorrect');
            btn.innerHTML += ' <span class="ml-3 px-3 py-1 bg-red-500 text-white text-xs font-bold rounded-full">❌</span>';
            
            // Show correct answer
            document.querySelectorAll('.answer-btn').forEach(b => {
                if (b.textContent.includes(correct)) {
                    b.classList.add('correct');
                    b.innerHTML += ' <span class="ml-3 px-3 py-1 bg-green-500 text-white text-xs font-bold rounded-full animate-pulse">✅</span>';
                }
            });
        }

        // Update score
        document.getElementById('score').textContent = `Score: ${score}/10`;

        // Auto next after 2.5s
        setTimeout(() => {
            currentQuestion++;
            showQuestion();
        }, 2500);

    }, 200);
}

// 🏆 Results Screen
function showResults() {
    const percentage = Math.round((score / 10) * 100);
    const rating = getRating(percentage);
    
    document.getElementById('questions').innerHTML = `
        <div class="text-center p-20 animate-in fade-in">
            <div class="text-8xl mb-8">${getEmoji(rating)}</div>
            <h2 class="text-6xl font-black bg-gradient-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent mb-8">
                Level ${currentLevel} Complete!
            </h2>
            <div class="text-7xl font-black text-gray-800 mb-12">${score}/10</div>
            <div class="text-4xl font-bold text-gray-600 mb-16">${percentage}%</div>
            
            <div class="max-w-2xl mx-auto mb-12">
                <div class="text-2xl font-bold text-white mb-6">${rating.toUpperCase()} PERFORMANCE</div>
                <div class="grid md:grid-cols-2 gap-6 text-lg">
                    <div class="bg-white/20 p-6 rounded-2xl backdrop-blur-xl">
                        <div class="text-3xl font-bold text-emerald-400 mb-2">${score}/10</div>
                        <div class="text-white/80">Correct Answers</div>
                    </div>
                    <div class="bg-white/20 p-6 rounded-2xl backdrop-blur-xl">
                        <div class="text-3xl font-bold text-blue-400 mb-2">Level ${currentLevel}</div>
                        <div class="text-white/80">Difficulty</div>
                    </div>
                </div>
            </div>
            
            <div class="flex flex-col sm:flex-row gap-4 justify-center">
                <button onclick="loadLevel(${currentLevel})" class="px-12 py-4 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-3xl text-xl font-bold shadow-2xl hover:shadow-3xl hover:scale-105 transition-all">
                    🔄 Replay Level
                </button>
                <a href="/practice" class="px-12 py-4 bg-gray-600 text-white rounded-3xl text-xl font-bold shadow-2xl hover:shadow-3xl hover:bg-gray-700 transition-all text-center flex-1 py-4">
                    ← All Levels
                </a>
                <a href="/" class="px-12 py-4 bg-emerald-600 text-white rounded-3xl text-xl font-bold shadow-2xl hover:shadow-3xl hover:bg-emerald-700 transition-all">
                    🎯 Dashboard
                </a>
            </div>
        </div>
    `;
}

function getRating(percentage) {
    if (percentage >= 90) return 'EXCELLENT';
    if (percentage >= 80) return 'GREAT';
    if (percentage >= 70) return 'GOOD';
    if (percentage >= 60) return 'FAIR';
    return 'NEEDS WORK';
}

function getEmoji(rating) {
    const ratings = {
        'EXCELLENT': '🥇',
        'GREAT': '🥈', 
        'GOOD': '🥉',
        'FAIR': '⚡',
        'NEEDS WORK': '💪'
    };
    return ratings[rating] || '📊';
}

// Keyboard support
document.addEventListener('DOMContentLoaded', () => {
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !isAnswered) {
            const activeBtn = document.activeElement;
            if (activeBtn.classList.contains('answer-btn')) {
                activeBtn.click();
            }
        }
    });
});
