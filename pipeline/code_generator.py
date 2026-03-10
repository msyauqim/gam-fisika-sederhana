"""
Code Generator — Stage 2: Game Code Generation from Spec
Game Edukasi Sekolah Rakyat (Tim 4) — Game2

Menggunakan Qwen-Coder (atau Qwen2.5-7B-Instruct) untuk menghasilkan
program web lengkap (HTML+CSS+JS) dari game specification.
"""

import json
import os
import re

from huggingface_hub import InferenceClient


CODE_GEN_SYSTEM_PROMPT = """Kamu adalah AI Web Game Developer yang sangat ahli.
Tugasmu adalah membuat program game web LENGKAP dalam satu file HTML berdasarkan spesifikasi game yang diberikan.

ATURAN OUTPUT:
1. Output HARUS berupa satu file HTML lengkap yang self-contained
2. Semua CSS di dalam tag <style> di <head>
3. Semua JavaScript di dalam tag <script> di akhir <body>
4. Game harus INTERAKTIF dan bisa langsung dimainkan di browser
5. Design harus PREMIUM dengan dark theme, gradien, dan animasi smooth
6. HARUS ada mekanisme scoring yang mengirim skor ke parent window via postMessage
7. Gunakan Canvas API atau DOM manipulation untuk visual game
8. Harus responsive dan berjalan di mobile/desktop
9. JANGAN gunakan library eksternal (tidak ada CDN) — murni HTML+CSS+JS vanilla

FORMAT postMessage untuk komunikasi dengan parent container:
```javascript
// Kirim skor ke parent saat game selesai
window.parent.postMessage({
    type: 'game_complete',
    score: totalScore,
    maxScore: maxPossibleScore,
    timeSpent: elapsedSeconds,
    correct: correctAnswers,
    total: totalQuestions
}, '*');

// Kirim update progres selama game
window.parent.postMessage({
    type: 'game_progress',
    currentScore: score,
    progress: percentComplete
}, '*');
```

JANGAN masukkan teks atau penjelasan di luar tag HTML.
Output HANYA kode HTML lengkap dari <!DOCTYPE html> sampai </html>."""


class GameCodeGenerator:
    """
    Stage 2: Generate HTML/CSS/JS game code dari game specification.
    """

    def __init__(self):
        hf_token = os.environ.get("HF_TOKEN", "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")
        # Gunakan Qwen2.5-Coder jika tersedia, fallback ke Qwen2.5-7B
        self._model = os.environ.get("CODE_GEN_MODEL", "Qwen/Qwen2.5-7B-Instruct")
        self._client = InferenceClient(
            model=self._model,
            token=hf_token,
            timeout=120,  # Code gen lebih lama
        )
        print(f"🔧 Code Generator ready: {self._model}")

    def generate_code(self, spec):
        """
        Generate HTML/CSS/JS dari game specification.

        Args:
            spec: dict — Game specification dari Stage 1

        Returns:
            str: Complete HTML code, or fallback HTML if failed
        """
        try:
            messages = self._build_prompt(spec)

            response = self._client.chat_completion(
                messages=messages,
                max_tokens=4096,
                temperature=0.4,   # Lebih deterministik untuk code gen
                top_p=0.95,
            )

            content = response.choices[0].message.content
            html_code = self._extract_html(content)

            if html_code and self._validate_html(html_code):
                print(f"✅ [Stage 2] Code generated: {len(html_code)} chars")
                return html_code
            else:
                print("⚠️ [Stage 2] Invalid HTML output, using fallback")
                return self._fallback_html(spec)

        except Exception as e:
            print(f"❌ [Stage 2] Error: {e}")
            return self._fallback_html(spec)

    def _build_prompt(self, spec):
        """Build code generation prompt dari spec."""
        spec_json = json.dumps(spec, ensure_ascii=False, indent=2)

        user_prompt = f"""Buatkan program game web LENGKAP berdasarkan spesifikasi berikut:

```json
{spec_json}
```

DETAIL IMPLEMENTASI:
1. Judul game: "{spec.get('title', 'Mini Game')}"
2. Tipe game: {spec.get('game_type', 'quiz_interactive')}
3. Visual theme: dark premium dengan warna {spec.get('visual_style', {}).get('colors', ['#1a1a2e', '#e94560'])}
4. Waktu maksimal: {spec.get('scoring_rules', {}).get('max_time_seconds', 60)} detik
5. Soal kuis yang harus dimasukkan: {json.dumps(spec.get('quiz_questions', []), ensure_ascii=False)}

FITUR WAJIB:
- Layar mulai dengan judul dan tombol "Mulai Game"
- Timer countdown
- Animasi dan transisi smooth
- Tampilkan skor real-time
- Layar akhir dengan total skor dan tombol "Main Lagi"
- postMessage ke parent saat game selesai (type: 'game_complete')

Output HANYA kode HTML lengkap, mulai dari <!DOCTYPE html>."""

        return [
            {"role": "system", "content": CODE_GEN_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]

    def _extract_html(self, content):
        """Extract HTML code dari LLM response."""
        # Coba cari code block ```html ... ```
        code_block = re.search(r'```(?:html)?\s*(<!DOCTYPE.*?</html>)\s*```', content, re.DOTALL | re.IGNORECASE)
        if code_block:
            return code_block.group(1).strip()

        # Coba cari <!DOCTYPE ... </html> langsung
        html_match = re.search(r'(<!DOCTYPE\s+html.*?</html>)', content, re.DOTALL | re.IGNORECASE)
        if html_match:
            return html_match.group(1).strip()

        # Coba cari <html> ... </html>
        html_match2 = re.search(r'(<html.*?</html>)', content, re.DOTALL | re.IGNORECASE)
        if html_match2:
            return "<!DOCTYPE html>\n" + html_match2.group(1).strip()

        return None

    def _validate_html(self, html):
        """Validasi dasar bahwa HTML mengandung komponen yang diperlukan."""
        checks = [
            "<html" in html.lower(),
            "<head" in html.lower(),
            "<body" in html.lower(),
            "<style" in html.lower(),
            "<script" in html.lower(),
            "postmessage" in html.lower() or "postMessage" in html,
        ]
        return sum(checks) >= 4  # Minimal 4 dari 6 check harus pass

    def _fallback_html(self, spec):
        """Generate fallback HTML game yang simpel tapi fungsional."""
        title = spec.get("title", "Mini Game Fisika")
        description = spec.get("description", "Game edukasi fisika interaktif")
        questions = spec.get("quiz_questions", [])
        colors = spec.get("visual_style", {}).get("colors", ["#1a1a2e", "#16213e", "#0f3460", "#e94560"])
        max_time = spec.get("scoring_rules", {}).get("max_time_seconds", 60)

        # Build questions JS array
        q_js = json.dumps(questions, ensure_ascii=False)

        return f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, {colors[0]}, {colors[1]});
            color: #e0e0e0;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .container {{
            max-width: 600px;
            width: 90%;
            padding: 2rem;
            background: rgba(255,255,255,0.06);
            border-radius: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
            box-shadow: 0 8px 32px rgba(0,0,0,0.4);
        }}
        h1 {{
            text-align: center;
            font-size: 1.8rem;
            margin-bottom: 0.5rem;
            background: linear-gradient(90deg, {colors[2]}, {colors[3]});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .subtitle {{ text-align: center; color: #999; margin-bottom: 1.5rem; font-size: 0.9rem; }}
        .screen {{ display: none; }}
        .screen.active {{ display: block; animation: fadeIn 0.3s ease; }}
        @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        .btn {{
            display: block;
            width: 100%;
            padding: 14px;
            margin: 8px 0;
            border: none;
            border-radius: 12px;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.2s;
            background: rgba(255,255,255,0.08);
            color: #e0e0e0;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .btn:hover {{ background: rgba(255,255,255,0.15); transform: translateY(-2px); }}
        .btn-primary {{
            background: linear-gradient(135deg, {colors[2]}, {colors[3]});
            color: white;
            font-weight: bold;
            font-size: 1.1rem;
        }}
        .btn-primary:hover {{ transform: translateY(-2px); box-shadow: 0 4px 20px rgba(233,69,96,0.3); }}
        .btn.correct {{ background: rgba(46,204,113,0.3) !important; border-color: #2ecc71 !important; }}
        .btn.wrong {{ background: rgba(231,76,60,0.3) !important; border-color: #e74c3c !important; }}
        .timer {{
            text-align: center;
            font-size: 2rem;
            font-weight: bold;
            color: {colors[3]};
            margin: 1rem 0;
        }}
        .score-display {{ text-align: center; font-size: 1.2rem; margin: 0.5rem 0; color: #aaa; }}
        .question {{ font-size: 1.1rem; margin: 1.5rem 0; line-height: 1.5; padding: 1rem; background: rgba(0,0,0,0.2); border-radius: 12px; }}
        .explanation {{
            margin-top: 1rem;
            padding: 1rem;
            background: rgba(46,204,113,0.1);
            border-radius: 12px;
            border-left: 3px solid #2ecc71;
            display: none;
        }}
        .result-emoji {{ font-size: 4rem; text-align: center; margin: 1rem 0; }}
        .progress-bar {{
            width: 100%;
            height: 6px;
            background: rgba(255,255,255,0.1);
            border-radius: 3px;
            margin: 1rem 0;
            overflow: hidden;
        }}
        .progress-bar .fill {{
            height: 100%;
            background: linear-gradient(90deg, {colors[2]}, {colors[3]});
            border-radius: 3px;
            transition: width 0.3s;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Start Screen -->
        <div id="screen-start" class="screen active">
            <h1>🎮 {title}</h1>
            <p class="subtitle">{description}</p>
            <div style="text-align:center; margin: 2rem 0;">
                <div style="font-size: 3rem;">🚀</div>
            </div>
            <button class="btn btn-primary" onclick="startGame()">Mulai Game</button>
        </div>

        <!-- Game Screen -->
        <div id="screen-game" class="screen">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div class="score-display">Skor: <span id="score">0</span></div>
                <div class="timer" id="timer">{max_time}s</div>
                <div class="score-display">Q: <span id="q-num">1</span>/<span id="q-total">?</span></div>
            </div>
            <div class="progress-bar"><div class="fill" id="progress" style="width:0%"></div></div>
            <div class="question" id="question-text"></div>
            <div id="options-container"></div>
            <div class="explanation" id="explanation"></div>
            <button class="btn btn-primary" id="btn-next" style="display:none" onclick="nextQuestion()">Soal Berikutnya →</button>
        </div>

        <!-- End Screen -->
        <div id="screen-end" class="screen">
            <div class="result-emoji" id="result-emoji">🏆</div>
            <h1 id="result-title">Selesai!</h1>
            <p class="subtitle" id="result-subtitle"></p>
            <div style="text-align:center; margin:1.5rem 0;">
                <div style="font-size:2.5rem; font-weight:bold; color:{colors[3]}" id="final-score">0</div>
                <div style="color:#999">poin</div>
            </div>
            <button class="btn btn-primary" onclick="restartGame()">Main Lagi 🔄</button>
        </div>
    </div>

    <script>
        const QUESTIONS = {q_js};
        const MAX_TIME = {max_time};
        let currentQ = 0, score = 0, timer = MAX_TIME, timerInterval = null, answered = false;

        function showScreen(id) {{
            document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
            document.getElementById(id).classList.add('active');
        }}

        function startGame() {{
            currentQ = 0; score = 0; timer = MAX_TIME; answered = false;
            document.getElementById('q-total').textContent = QUESTIONS.length;
            showScreen('screen-game');
            loadQuestion();
            startTimer();
            window.parent.postMessage({{ type: 'game_progress', currentScore: 0, progress: 0 }}, '*');
        }}

        function startTimer() {{
            clearInterval(timerInterval);
            timer = MAX_TIME;
            timerInterval = setInterval(() => {{
                timer--;
                document.getElementById('timer').textContent = timer + 's';
                if (timer <= 10) document.getElementById('timer').style.color = '#e74c3c';
                if (timer <= 0) {{ clearInterval(timerInterval); endGame(); }}
            }}, 1000);
        }}

        function loadQuestion() {{
            if (currentQ >= QUESTIONS.length) {{ endGame(); return; }}
            answered = false;
            const q = QUESTIONS[currentQ];
            document.getElementById('q-num').textContent = currentQ + 1;
            document.getElementById('question-text').textContent = q.question;
            document.getElementById('explanation').style.display = 'none';
            document.getElementById('btn-next').style.display = 'none';
            document.getElementById('score').textContent = score;
            document.getElementById('progress').style.width = ((currentQ / QUESTIONS.length) * 100) + '%';

            const container = document.getElementById('options-container');
            container.innerHTML = '';
            const shuffled = [...q.options].sort(() => Math.random() - 0.5);
            shuffled.forEach(opt => {{
                const btn = document.createElement('button');
                btn.className = 'btn';
                btn.textContent = opt;
                btn.onclick = () => selectAnswer(btn, opt, q);
                container.appendChild(btn);
            }});
        }}

        function selectAnswer(btn, selected, q) {{
            if (answered) return;
            answered = true;
            const correct = selected === q.answer;
            const buttons = document.querySelectorAll('#options-container .btn');
            buttons.forEach(b => {{
                b.style.pointerEvents = 'none';
                if (b.textContent === q.answer) b.classList.add('correct');
                if (b === btn && !correct) b.classList.add('wrong');
            }});
            if (correct) score += 10;
            else score = Math.max(0, score - 2);
            document.getElementById('score').textContent = score;
            document.getElementById('explanation').textContent = '💡 ' + q.explanation;
            document.getElementById('explanation').style.display = 'block';
            document.getElementById('btn-next').style.display = 'block';
            window.parent.postMessage({{
                type: 'game_progress',
                currentScore: score,
                progress: Math.round(((currentQ + 1) / QUESTIONS.length) * 100)
            }}, '*');
        }}

        function nextQuestion() {{ currentQ++; loadQuestion(); }}

        function endGame() {{
            clearInterval(timerInterval);
            showScreen('screen-end');
            const percent = Math.round((score / (QUESTIONS.length * 10)) * 100);
            document.getElementById('final-score').textContent = score;
            document.getElementById('result-emoji').textContent = percent >= 80 ? '🏆' : percent >= 50 ? '⭐' : '💪';
            document.getElementById('result-title').textContent = percent >= 80 ? 'Luar Biasa!' : percent >= 50 ? 'Bagus!' : 'Terus Berlatih!';
            document.getElementById('result-subtitle').textContent = 'Kamu menjawab ' + Math.round(score/10) + ' dari ' + QUESTIONS.length + ' soal dengan benar';
            window.parent.postMessage({{
                type: 'game_complete',
                score: score,
                maxScore: QUESTIONS.length * 10,
                timeSpent: MAX_TIME - timer,
                correct: Math.round(score/10),
                total: QUESTIONS.length
            }}, '*');
        }}

        function restartGame() {{ startGame(); }}
    </script>
</body>
</html>"""


# Singleton
_code_generator = None

def get_code_generator():
    global _code_generator
    if _code_generator is None:
        _code_generator = GameCodeGenerator()
    return _code_generator
