"""
App - Flask Web Server
Game Edukasi Sekolah Rakyat (Tim 4) — Game2

Enhanced quiz game with gamification, leaderboard, and score export API.
Pipeline modes: PIPELINE_MODE=mock (default) | local | api
"""

import sys
import os
import uuid
from flask import Flask, render_template, request, jsonify

# Add game2 directory to path
sys.path.insert(0, os.path.dirname(__file__))

from data.curriculum_data import (
    get_jenjang_list, get_jurusan_list, get_subjects,
    get_topics, get_physics_topics_by_kelas,
    ACHIEVEMENTS, DIFFICULTY_TIERS
)
from data.physics_content import get_question_count, get_all_topics_for_subject
from backend.game_engine import get_or_create_session, ScoringEngine
from backend.storage import (
    get_profile, get_all_profiles, get_leaderboard,
    create_profile, export_all_scores, get_analytics_summary
)

app = Flask(__name__)
app.secret_key = "sekolah-rakyat-game2-2026-secret"


# ========================
# Frontend Routes
# ========================

@app.route("/")
def index():
    """Serve halaman utama game."""
    return render_template("index.html")


# ========================
# Profile API
# ========================

@app.route("/api/profile", methods=["POST"])
def api_create_profile():
    """Buat atau ambil profil siswa."""
    data = request.json
    nama = data.get("nama", "Siswa")
    jenjang = data.get("jenjang", "SMA")
    jurusan = data.get("jurusan", "IPA")
    kelas = data.get("kelas", 10)

    student_id = data.get("student_id") or str(uuid.uuid4())[:8]
    profile, actual_id = create_profile(student_id, nama, jenjang, jurusan, kelas)

    return jsonify({
        "profile": profile,
        "student_id": actual_id,
    })


@app.route("/api/profile/<student_id>", methods=["GET"])
def api_get_profile(student_id):
    """Ambil profil siswa."""
    profile = get_profile(student_id)
    if not profile:
        return jsonify({"error": "Profil tidak ditemukan"}), 404

    scoring = ScoringEngine()
    profile["difficulty_info"] = scoring.get_difficulty_info(profile["points"])

    return jsonify({"profile": profile})


# ========================
# Curriculum API
# ========================

@app.route("/api/subjects", methods=["GET"])
def api_subjects():
    """Return daftar mata pelajaran."""
    jenjang = request.args.get("jenjang", "SMA")
    jurusan = request.args.get("jurusan", "IPA")

    subjects = get_subjects(jenjang, jurusan)

    subject_list = []
    for name, data in subjects.items():
        subject_list.append({
            "name": name,
            "icon": data.get("icon", "📚"),
            "topics": data.get("topik", []),
            "kelas": data.get("kelas", {}),
        })

    return jsonify({
        "jenjang": jenjang,
        "jurusan": jurusan,
        "subjects": subject_list,
    })


@app.route("/api/physics-topics", methods=["GET"])
def api_physics_topics():
    """Return topik fisika, opsional filter by kelas."""
    kelas = request.args.get("kelas")
    if kelas:
        kelas = int(kelas)
    topics = get_physics_topics_by_kelas(kelas)
    return jsonify({
        "kelas": kelas,
        "topics": topics,
        "total": len(topics),
    })


# ========================
# Game API
# ========================

@app.route("/api/generate", methods=["POST"])
def api_generate():
    """Generate konten game (narasi + kuis)."""
    data = request.json
    student_id = data.get("student_id")
    subject = data.get("subject", "Fisika")
    topic = data.get("topic")

    if not all([student_id, topic]):
        return jsonify({"error": "Missing student_id or topic"}), 400

    session = get_or_create_session(student_id)
    result = session.generate_content(subject, topic)

    if not result:
        return jsonify({"error": "Gagal generate konten"}), 500

    return jsonify(result)


@app.route("/api/answer", methods=["POST"])
def api_answer():
    """Submit jawaban kuis."""
    data = request.json
    student_id = data.get("student_id")
    selected_answer = data.get("answer")

    if not all([student_id, selected_answer]):
        return jsonify({"error": "Missing required fields"}), 400

    session = get_or_create_session(student_id)
    result = session.submit_answer(selected_answer)

    if "error" in result:
        return jsonify(result), 400

    return jsonify(result)


# ========================
# Leaderboard API
# ========================

@app.route("/api/leaderboard", methods=["GET"])
def api_leaderboard():
    """Ambil leaderboard, opsional filter by kelas."""
    kelas = request.args.get("kelas")
    if kelas:
        kelas = int(kelas)
    limit = int(request.args.get("limit", 20))

    leaderboard = get_leaderboard(kelas, limit)
    return jsonify({
        "leaderboard": leaderboard,
        "filter_kelas": kelas,
    })


# ========================
# Achievements API
# ========================

@app.route("/api/achievements/<student_id>", methods=["GET"])
def api_achievements(student_id):
    """Return achievements siswa."""
    profile = get_profile(student_id)
    if not profile:
        return jsonify({"error": "Profil tidak ditemukan"}), 404

    unlocked = profile.get("achievements", [])

    all_achievements = []
    for ach_id, ach in ACHIEVEMENTS.items():
        all_achievements.append({
            "id": ach_id,
            "name": ach["name"],
            "description": ach["description"],
            "points_reward": ach["points_reward"],
            "unlocked": ach_id in unlocked,
        })

    return jsonify({
        "achievements": all_achievements,
        "unlocked_count": len(unlocked),
        "total_count": len(ACHIEVEMENTS),
    })


# ========================
# Score Export API (for MVP Team)
# ========================

@app.route("/api/scores/export", methods=["GET"])
def api_scores_export():
    """Export semua score data untuk Tim MVP."""
    return jsonify(export_all_scores())


@app.route("/api/scores/student/<student_id>", methods=["GET"])
def api_scores_student(student_id):
    """Detail score per student untuk Tim MVP."""
    profile = get_profile(student_id)
    if not profile:
        return jsonify({"error": "Student not found"}), 404

    accuracy = 0
    if profile["total_answered"] > 0:
        accuracy = round(profile["total_correct"] / profile["total_answered"] * 100, 1)

    return jsonify({
        "student_id": student_id,
        "nama": profile["nama"],
        "points": profile["points"],
        "difficulty": profile["difficulty"],
        "total_correct": profile["total_correct"],
        "total_wrong": profile["total_wrong"],
        "total_answered": profile["total_answered"],
        "accuracy": accuracy,
        "best_streak": profile.get("best_streak", 0),
        "achievements": profile.get("achievements", []),
        "unique_topics": profile.get("unique_topics", []),
        "history": profile.get("history", [])[-20:],  # 20 terakhir
    })


@app.route("/api/analytics/summary", methods=["GET"])
def api_analytics():
    """Summary analytics untuk Tim MVP dashboard."""
    return jsonify(get_analytics_summary())


# ========================
# Game Stats
# ========================

@app.route("/api/stats", methods=["GET"])
def api_stats():
    """Stats umum game."""
    return jsonify({
        "total_questions": get_question_count(),
        "physics_questions": get_question_count("Fisika"),
        "available_topics": get_all_topics_for_subject("Fisika"),
        "difficulty_tiers": DIFFICULTY_TIERS,
        "total_achievements": len(ACHIEVEMENTS),
    })


if __name__ == "__main__":
    pipeline_mode = os.environ.get("PIPELINE_MODE", "mock")
    print("=" * 50)
    print("🎮 Game Edukasi Sekolah Rakyat — Game2")
    print("=" * 50)
    print(f"📊 Total soal Fisika: {get_question_count('Fisika')}")
    print(f"📚 Total topik: {len(get_all_topics_for_subject('Fisika'))}")
    print(f"🏆 Total achievements: {len(ACHIEVEMENTS)}")
    print(f"🔧 Pipeline mode: {pipeline_mode}")
    print(f"🌐 Server: http://localhost:5051")
    print("=" * 50)
    print("💡 Tip: Set PIPELINE_MODE=local atau api untuk pakai LLM")
    print("=" * 50)
    app.run(debug=True, host="0.0.0.0", port=5051)
