/**
 * Game Edukasi Sekolah Rakyat — Game2
 * Frontend Game Logic
 *
 * Features:
 * - Login & profile system
 * - Topic selection by kelas (10/11/12)
 * - Quiz with timer, streak tracking, & animated feedback
 * - Leaderboard & achievements
 */

// ========================
// STATE
// ========================

const STATE = {
    studentId: null,
    nama: '',
    kelas: 10,
    currentTopic: null,
    currentContent: null,
    currentImageUrl: null,
    selectedAnswer: null,
    timerInterval: null,
    timerStart: null,
    answered: false,
    points: 0,
    streak: 0,
    topicsData: {},
};

// Topic image mapping (mirrors backend TOPIC_IMAGES)
const TOPIC_IMAGES = {
    'Besaran dan Satuan': 'besaran.png',
    'Vektor': 'vektor.png',
    'Gerak Lurus (GLB & GLBB)': 'gerak_lurus.png',
    'Gerak Parabola': 'gerak_parabola.png',
    'Hukum Newton': 'hukum_newton.png',
    'Usaha dan Energi': 'usaha_energi.png',
    'Momentum dan Impuls': 'momentum.png',
    'Gerak Melingkar': 'rotasi.png',
    'Gravitasi': 'gravitasi.png',
    'Getaran dan Gelombang': 'gelombang.png',
    'Kinematika Gerak Lurus Lanjutan': 'gerak_lurus.png',
    'Dinamika Rotasi': 'rotasi.png',
    'Kesetimbangan Benda Tegar': 'rotasi.png',
    'Fluida Statis': 'fluida.png',
    'Fluida Dinamis': 'fluida.png',
    'Termodinamika': 'termodinamika.png',
    'Teori Kinetik Gas': 'termodinamika.png',
    'Gelombang Mekanik': 'gelombang.png',
    'Gelombang Bunyi': 'gelombang.png',
    'Optik Geometri': 'optik.png',
    'Alat-alat Optik': 'optik.png',
    'Listrik Statis': 'listrik.png',
    'Listrik Dinamis': 'listrik.png',
    'Medan Magnet': 'magnet.png',
    'Induksi Elektromagnetik': 'magnet.png',
    'Rangkaian Arus Bolak-Balik': 'listrik.png',
    'Radiasi Elektromagnetik': 'kuantum.png',
    'Fisika Kuantum': 'kuantum.png',
    'Fisika Inti dan Radioaktivitas': 'kuantum.png',
    'Relativitas Khusus': 'relativitas.png',
};

function getTopicImage(topicName) {
    if (TOPIC_IMAGES[topicName]) return `/static/images/${TOPIC_IMAGES[topicName]}`;
    for (const [key, img] of Object.entries(TOPIC_IMAGES)) {
        if (topicName.includes(key) || key.includes(topicName)) return `/static/images/${img}`;
    }
    return null;
}

// ========================
// API HELPERS
// ========================

async function api(endpoint, method = 'GET', body = null) {
    const opts = {
        method,
        headers: { 'Content-Type': 'application/json' },
    };
    if (body) opts.body = JSON.stringify(body);

    const res = await fetch(endpoint, opts);
    return res.json();
}

// ========================
// SCREEN MANAGEMENT
// ========================

function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    const screen = document.getElementById(screenId);
    if (screen) screen.classList.add('active');
}

// ========================
// LOGIN / START
// ========================

async function startGame() {
    const nama = document.getElementById('input-nama').value.trim();
    if (!nama) {
        document.getElementById('input-nama').focus();
        document.getElementById('input-nama').style.borderColor = '#ef4444';
        return;
    }

    const kelas = parseInt(document.getElementById('input-kelas').value);
    STATE.kelas = kelas;
    STATE.nama = nama;

    // Create profile — pass kelas for deduplication
    const data = await api('/api/profile', 'POST', {
        nama: nama,
        jenjang: 'SMA',
        jurusan: 'IPA',
        kelas: kelas,
    });

    STATE.studentId = data.student_id;
    STATE.points = data.profile.points || 0;
    STATE.streak = data.profile.current_streak || 0;

    // Show header stats
    document.getElementById('header-stats').style.display = 'flex';
    updateHeaderStats(data.profile);

    // Load topics
    await loadTopics();

    showScreen('screen-topics');
}

function updateHeaderStats(profile) {
    document.getElementById('header-points').textContent = profile.points || 0;
    document.getElementById('header-streak').textContent = profile.current_streak || 0;

    STATE.points = profile.points || 0;
    STATE.streak = profile.current_streak || 0;

    // Difficulty display
    if (profile.difficulty_info) {
        const diffEl = document.getElementById('stat-difficulty');
        diffEl.style.display = 'flex';
        document.getElementById('header-diff-emoji').textContent = profile.difficulty_info.emoji || '';
        document.getElementById('header-diff-label').textContent = profile.difficulty_info.label || '';
    }
}

// ========================
// TOPIC LOADING & DISPLAY
// ========================

async function loadTopics() {
    const data = await api('/api/subjects?jenjang=SMA&jurusan=IPA');

    // Find Fisika
    const fisika = data.subjects.find(s => s.name === 'Fisika');
    if (fisika && fisika.kelas) {
        STATE.topicsData = fisika.kelas;
    }

    renderTopics(STATE.kelas);
}

function renderTopics(kelas) {
    const grid = document.getElementById('topic-grid');
    let topics;

    if (kelas === 'all') {
        topics = [];
        for (const [k, t] of Object.entries(STATE.topicsData)) {
            t.forEach(topic => topics.push({ name: topic, kelas: k }));
        }
        document.getElementById('topic-subtitle').textContent = `Semua kelas — ${topics.length} topik tersedia`;
    } else {
        const key = `Kelas ${kelas}`;
        topics = (STATE.topicsData[key] || []).map(t => ({ name: t, kelas: key }));
        document.getElementById('topic-subtitle').textContent = `${key} — ${topics.length} topik tersedia`;
    }

    const topicIcons = {
        'Besaran': '📏', 'Vektor': '↗️', 'Gerak': '🏃', 'Parabola': '🏀',
        'Newton': '🍎', 'Usaha': '💪', 'Energi': '💪', 'Momentum': '💥',
        'Impuls': '💥', 'Melingkar': '🔄', 'Gravitasi': '🌍', 'Getaran': '〰️',
        'Gelombang': '🌊', 'Kinematika': '📊', 'Rotasi': '⚙️', 'Kesetimbangan': '⚖️',
        'Fluida': '💧', 'Termodinamika': '🌡️', 'Kinetik Gas': '💨',
        'Bunyi': '🔊', 'Optik': '🔭', 'Alat': '🔬', 'Listrik': '⚡',
        'Magnet': '🧲', 'Induksi': '🔌', 'Arus Bolak': '〽️',
        'Radiasi': '📡', 'Kuantum': '⚛️', 'Inti': '☢️', 'Radioaktivitas': '☢️',
        'Relativitas': '🚀', 'Digital': '💻',
    };

    function getIcon(name) {
        for (const [key, icon] of Object.entries(topicIcons)) {
            if (name.includes(key)) return icon;
        }
        return '⚡';
    }

    grid.innerHTML = topics.map(t => {
        const imgUrl = getTopicImage(t.name);
        const imgHtml = imgUrl ? `<img src="${imgUrl}" alt="${t.name}" class="topic-card-img">` : `<div class="topic-icon">${getIcon(t.name)}</div>`;
        return `
            <div class="topic-card" onclick="selectTopic('${t.name.replace(/'/g, "\\'")}')"> 
                ${imgHtml}
                <div class="topic-name">${t.name}</div>
                <div class="topic-meta">${t.kelas} · Klik untuk mulai kuis</div>
            </div>
        `;
    }).join('');
}

function switchKelas(kelas) {
    STATE.kelas = kelas;

    // Update tabs
    document.querySelectorAll('.kelas-tab').forEach(tab => {
        const tabKelas = tab.dataset.kelas;
        tab.classList.toggle('active', tabKelas === String(kelas));
    });

    renderTopics(kelas);
}

// ========================
// MAIN TABS (Quiz / Leaderboard / Achievements)
// ========================

function switchMainTab(tab) {
    // Update tab buttons
    document.querySelectorAll('.nav-tab').forEach((t, i) => {
        t.classList.toggle('active', i === ['quiz', 'leaderboard', 'achievements'].indexOf(tab));
    });

    document.getElementById('tab-quiz').style.display = tab === 'quiz' ? 'block' : 'none';
    document.getElementById('tab-leaderboard').style.display = tab === 'leaderboard' ? 'block' : 'none';
    document.getElementById('tab-achievements').style.display = tab === 'achievements' ? 'block' : 'none';

    if (tab === 'leaderboard') loadLeaderboard();
    if (tab === 'achievements') loadAchievements();
}

// ========================
// QUIZ FLOW
// ========================

async function selectTopic(topicName) {
    STATE.currentTopic = topicName;
    STATE.answered = false;
    STATE.selectedAnswer = null;
    STATE.currentImageUrl = null;

    showScreen('screen-quiz');

    // Reset UI
    document.getElementById('result-container').style.display = 'none';
    document.getElementById('btn-next').style.display = 'none';
    document.getElementById('answer-options').innerHTML = '<div class="spinner"></div>';
    document.getElementById('quiz-topic-label').textContent = topicName;
    document.getElementById('narasi-text').textContent = 'Loading...';
    document.getElementById('question-text').textContent = '';
    document.getElementById('narasi-image-container').style.display = 'none';

    // Fetch question
    const data = await api('/api/generate', 'POST', {
        student_id: STATE.studentId,
        subject: 'Fisika',
        topic: topicName,
    });

    if (data.error) {
        document.getElementById('narasi-text').textContent = 'Gagal memuat soal. Silakan coba lagi.';
        return;
    }

    STATE.currentContent = data.content;
    STATE.currentImageUrl = data.image_url;
    renderQuiz(data.content, data.image_url);

    // Update difficulty info
    if (data.student_info) {
        updateDifficultyDisplay(data.student_info);
    }

    // Start timer
    startTimer();
}

function renderQuiz(content, imageUrl) {
    document.getElementById('narasi-text').textContent = content.narasi;
    document.getElementById('question-text').textContent = content.kuis.pertanyaan;

    // Show topic illustration image
    const imgContainer = document.getElementById('narasi-image-container');
    const imgEl = document.getElementById('narasi-image');
    if (imageUrl) {
        imgEl.src = imageUrl;
        imgEl.alt = content.materi_inti || 'Ilustrasi Fisika';
        imgContainer.style.display = 'block';
    } else {
        imgContainer.style.display = 'none';
    }

    const letters = ['A', 'B', 'C', 'D', 'E'];
    const optionsHtml = content.kuis.pilihan.map((opt, i) => `
        <button class="answer-btn" id="answer-${i}" onclick="selectAnswer(${i}, '${opt.replace(/'/g, "\\'")}')">
            <span class="letter">${letters[i]}</span>
            <span>${opt}</span>
        </button>
    `).join('');

    document.getElementById('answer-options').innerHTML = optionsHtml;
}

function startTimer() {
    STATE.timerStart = Date.now();
    const timerEl = document.getElementById('quiz-timer');

    if (STATE.timerInterval) clearInterval(STATE.timerInterval);

    STATE.timerInterval = setInterval(() => {
        const elapsed = (Date.now() - STATE.timerStart) / 1000;
        timerEl.textContent = `⏱️ ${elapsed.toFixed(1)}s`;

        // Color coding
        timerEl.classList.remove('fast', 'medium', 'slow');
        if (elapsed < 5) timerEl.classList.add('fast');
        else if (elapsed < 15) timerEl.classList.add('medium');
        else timerEl.classList.add('slow');
    }, 100);
}

function stopTimer() {
    if (STATE.timerInterval) {
        clearInterval(STATE.timerInterval);
        STATE.timerInterval = null;
    }
}

async function selectAnswer(index, answer) {
    if (STATE.answered) return;
    STATE.answered = true;
    STATE.selectedAnswer = answer;

    stopTimer();

    // Disable all buttons
    document.querySelectorAll('.answer-btn').forEach(btn => btn.classList.add('disabled'));

    // Highlight selected
    document.getElementById(`answer-${index}`).classList.add('selected');

    // Submit answer
    const data = await api('/api/answer', 'POST', {
        student_id: STATE.studentId,
        answer: answer,
    });

    if (data.error) {
        alert('Error: ' + data.error);
        return;
    }

    // Show correct/wrong on buttons
    const content = STATE.currentContent;
    document.querySelectorAll('.answer-btn').forEach((btn, i) => {
        const optText = content.kuis.pilihan[i];
        if (optText === data.correct_answer) {
            btn.classList.add('correct');
        } else if (i === index && !data.is_correct) {
            btn.classList.add('wrong');
        }
    });

    // Update state
    STATE.points = data.new_points;
    STATE.streak = data.streak;

    // Update header
    document.getElementById('header-points').textContent = data.new_points;
    document.getElementById('header-streak').textContent = data.streak;

    if (data.difficulty) {
        updateDifficultyDisplay(data.difficulty);
    }

    // Show result
    showResult(data);

    // Show confetti for correct answers
    if (data.is_correct) {
        spawnConfetti();
    }
}

function showResult(data) {
    const container = document.getElementById('result-container');

    let bonusHtml = '';
    if (data.bonus > 0) {
        bonusHtml += `<span class="bonus-badge">✨ +${data.bonus} bonus</span>`;
    }
    if (data.streak >= 3) {
        bonusHtml += `<span class="streak-indicator">🔥 ${data.streak} Streak!</span>`;
    }
    if (data.answer_time && data.answer_time < 5) {
        bonusHtml += `<span class="bonus-badge">⚡ Speed bonus!</span>`;
    }

    // Achievement popups
    let achievementsHtml = '';
    if (data.new_achievements && data.new_achievements.length > 0) {
        achievementsHtml = data.new_achievements.map(ach => `
            <div class="achievement-popup">
                <span class="ach-icon">🎖️</span>
                <div class="ach-text">
                    <h4>🏆 Achievement Unlocked: ${ach.name}</h4>
                    <p>${ach.description} (+${ach.points_reward} poin)</p>
                </div>
            </div>
        `).join('');
    }

    const emoji = data.is_correct ? '🎉' : '😢';
    const title = data.is_correct ? 'Benar!' : 'Salah!';
    const pointText = data.point_change >= 0 ? `+${data.point_change}` : `${data.point_change}`;

    container.innerHTML = `
        ${achievementsHtml}
        <div class="result-card ${data.is_correct ? 'correct' : 'wrong'}">
            <div class="result-header">
                <span class="result-emoji">${emoji}</span>
                <div>
                    <div class="result-title">${title}</div>
                    <div class="result-points">${pointText} poin ${bonusHtml}</div>
                </div>
            </div>
            <div class="result-explanation">
                <strong>Penjelasan:</strong> ${data.penjelasan}
            </div>
            <div class="result-stats">
                <div class="result-stat">
                    <div class="value">${data.new_points}</div>
                    <div class="label">Total Poin</div>
                </div>
                <div class="result-stat">
                    <div class="value">${data.streak}</div>
                    <div class="label">Streak</div>
                </div>
                <div class="result-stat">
                    <div class="value">${data.stats.accuracy}%</div>
                    <div class="label">Akurasi</div>
                </div>
                <div class="result-stat">
                    <div class="value">${data.answer_time || '-'}s</div>
                    <div class="label">Waktu</div>
                </div>
            </div>
        </div>
    `;

    container.style.display = 'block';
    document.getElementById('btn-next').style.display = 'inline-flex';

    // Scroll to result
    container.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function updateDifficultyDisplay(info) {
    const diffEl = document.getElementById('stat-difficulty');
    diffEl.style.display = 'flex';
    document.getElementById('header-diff-emoji').textContent = info.emoji || '';
    document.getElementById('header-diff-label').textContent = info.label || '';
}

async function nextQuestion() {
    // Get a random topic from current kelas or keep same topic
    STATE.answered = false;
    STATE.selectedAnswer = null;

    await selectTopic(STATE.currentTopic);
}

function backToTopics() {
    stopTimer();
    showScreen('screen-topics');

    // Refresh profile
    refreshProfile();
}

async function refreshProfile() {
    if (!STATE.studentId) return;
    const data = await api(`/api/profile/${STATE.studentId}`);
    if (data.profile) {
        updateHeaderStats(data.profile);
    }
}

// ========================
// LEADERBOARD
// ========================

async function loadLeaderboard(filterKelas) {
    // Default to current player's kelas
    const kelas = filterKelas !== undefined ? filterKelas : STATE.kelas;

    // Update tab buttons
    document.querySelectorAll('.lb-kelas-tab').forEach(tab => {
        const tabKelas = tab.dataset.kelas;
        if (tabKelas === 'all') {
            tab.classList.toggle('active', kelas === null);
        } else {
            tab.classList.toggle('active', parseInt(tabKelas) === kelas);
        }
    });

    const url = kelas !== null ? `/api/leaderboard?kelas=${kelas}&limit=20` : '/api/leaderboard?limit=20';
    const data = await api(url);
    const tbody = document.getElementById('leaderboard-body');

    const kelasLabel = kelas !== null ? `Kelas ${kelas}` : 'Semua Kelas';
    document.getElementById('lb-kelas-label').textContent = kelasLabel;

    if (!data.leaderboard || data.leaderboard.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:var(--text-muted); padding:2rem;">Belum ada data untuk ${kelasLabel}. Mainkan kuis untuk muncul di leaderboard!</td></tr>`;
        return;
    }

    tbody.innerHTML = data.leaderboard.map((entry, i) => {
        const rank = i + 1;
        let rankClass = 'rank-other';
        if (rank === 1) rankClass = 'rank-1';
        else if (rank === 2) rankClass = 'rank-2';
        else if (rank === 3) rankClass = 'rank-3';

        const isMe = entry.student_id === STATE.studentId;
        const highlight = isMe ? 'style="background: rgba(99,102,241,0.08);"' : '';

        let level = 'Pemula';
        const pts = entry.points || 0;
        if (pts > 900) level = 'Expert 👑';
        else if (pts > 500) level = 'Sulit 💪';
        else if (pts > 200) level = 'Menengah 🔥';
        else level = 'Pemula 🌱';

        const entryKelas = entry.kelas ? `Kelas ${entry.kelas}` : '-';

        return `
            <tr ${highlight}>
                <td><span class="rank-badge ${rankClass}">${rank <= 3 ? ['🥇', '🥈', '🥉'][rank - 1] : rank}</span></td>
                <td><strong>${entry.nama}</strong>${isMe ? ' (kamu)' : ''}</td>
                <td>${entryKelas}</td>
                <td><span class="points-display">${pts}</span></td>
                <td>${level}</td>
            </tr>
        `;
    }).join('');
}

// ========================
// ACHIEVEMENTS
// ========================

async function loadAchievements() {
    if (!STATE.studentId) return;

    const data = await api(`/api/achievements/${STATE.studentId}`);

    document.getElementById('ach-subtitle').textContent =
        `${data.unlocked_count} / ${data.total_count} unlocked`;

    const grid = document.getElementById('achievements-grid');

    grid.innerHTML = data.achievements.map(ach => {
        const status = ach.unlocked ? 'unlocked' : 'locked';
        const lockIcon = ach.unlocked ? '' : '🔒 ';

        return `
            <div class="ach-card ${status}">
                <span class="ach-emoji">${ach.unlocked ? '🏆' : '🔒'}</span>
                <div class="ach-info">
                    <h4>${lockIcon}${ach.name}</h4>
                    <p>${ach.description}</p>
                </div>
                <span class="ach-reward">+${ach.points_reward}</span>
            </div>
        `;
    }).join('');
}

// ========================
// CONFETTI EFFECT
// ========================

function spawnConfetti() {
    const container = document.getElementById('confetti-container');
    const colors = ['#6366f1', '#8b5cf6', '#22c55e', '#f59e0b', '#ef4444', '#3b82f6', '#ec4899'];

    for (let i = 0; i < 30; i++) {
        const confetti = document.createElement('div');
        confetti.className = 'confetti';
        confetti.style.left = Math.random() * 100 + '%';
        confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        confetti.style.borderRadius = Math.random() > 0.5 ? '50%' : '2px';
        confetti.style.width = (Math.random() * 8 + 4) + 'px';
        confetti.style.height = (Math.random() * 8 + 4) + 'px';
        confetti.style.animationDuration = (Math.random() * 1.5 + 1) + 's';
        confetti.style.animationDelay = (Math.random() * 0.5) + 's';
        container.appendChild(confetti);

        setTimeout(() => confetti.remove(), 3000);
    }
}

// ========================
// KEYBOARD SHORTCUTS
// ========================

document.addEventListener('keydown', (e) => {
    // Enter to start
    if (e.key === 'Enter' && document.getElementById('screen-login').classList.contains('active')) {
        startGame();
        return;
    }

    // A-E to select answers
    if (STATE.currentContent && !STATE.answered) {
        const keyMap = { 'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4 };
        const idx = keyMap[e.key.toLowerCase()];
        if (idx !== undefined && STATE.currentContent.kuis.pilihan[idx]) {
            selectAnswer(idx, STATE.currentContent.kuis.pilihan[idx]);
        }
    }

    // Enter/Space for next question
    if (e.key === 'Enter' && STATE.answered) {
        nextQuestion();
    }
});

// ========================
// INIT
// ========================

// Auto-focus name input
window.addEventListener('load', () => {
    document.getElementById('input-nama').focus();
});
