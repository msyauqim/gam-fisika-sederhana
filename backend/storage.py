"""
Storage - JSON-based Data Persistence
Game Edukasi Sekolah Rakyat (Tim 4) — Game2

Menyimpan student profiles, leaderboard, dan score export.
Enhanced with analytics support for MVP team.
"""

import json
import os
from datetime import datetime

# Path untuk data storage
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "game_data")
PROFILES_FILE = os.path.join(DATA_DIR, "profiles.json")
LEADERBOARD_FILE = os.path.join(DATA_DIR, "leaderboard.json")


def _ensure_data_dir():
    """Pastikan directory data ada."""
    os.makedirs(DATA_DIR, exist_ok=True)


def _load_json(filepath, default=None):
    """Load data dari file JSON."""
    if default is None:
        default = {}
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError):
        pass
    return default


def _save_json(filepath, data):
    """Simpan data ke file JSON."""
    _ensure_data_dir()
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ========================
# Student Profile CRUD
# ========================

def create_profile(student_id, nama, jenjang, jurusan=None, kelas=None):
    """Buat profil siswa baru, atau return existing jika nama+kelas sama."""
    profiles = _load_json(PROFILES_FILE)

    # Cek apakah sudah ada profil dengan nama + kelas yang sama
    for existing_id, existing_profile in profiles.items():
        if (existing_profile.get("nama", "").lower() == nama.lower() and
            existing_profile.get("kelas") == kelas):
            # Return existing profile, update last login
            existing_profile["last_played"] = datetime.now().isoformat()
            _save_json(PROFILES_FILE, profiles)
            return existing_profile, existing_id

    if student_id in profiles:
        return profiles[student_id], student_id

    profile = {
        "student_id": student_id,
        "nama": nama,
        "jenjang": jenjang,
        "jurusan": jurusan,
        "kelas": kelas,
        "points": 0,
        "difficulty": "Easy",
        "total_correct": 0,
        "total_wrong": 0,
        "total_answered": 0,
        "current_streak": 0,
        "best_streak": 0,
        "fast_correct_count": 0,
        "unique_topics": [],
        "achievements": [],
        "history": [],
        "created_at": datetime.now().isoformat(),
        "last_played": None,
    }

    profiles[student_id] = profile
    _save_json(PROFILES_FILE, profiles)
    return profile, student_id


def get_profile(student_id):
    """Ambil profil siswa berdasarkan ID."""
    profiles = _load_json(PROFILES_FILE)
    return profiles.get(student_id)


def update_profile(student_id, updates):
    """Update profil siswa."""
    profiles = _load_json(PROFILES_FILE)

    if student_id not in profiles:
        return None

    profiles[student_id].update(updates)
    profiles[student_id]["last_played"] = datetime.now().isoformat()
    _save_json(PROFILES_FILE, profiles)
    return profiles[student_id]


def get_all_profiles():
    """Ambil semua profil siswa."""
    return _load_json(PROFILES_FILE)


def add_history_entry(student_id, entry):
    """Tambahkan entry ke history siswa."""
    profiles = _load_json(PROFILES_FILE)

    if student_id not in profiles:
        return None

    entry["timestamp"] = datetime.now().isoformat()
    profiles[student_id]["history"].append(entry)

    # Simpan hanya 100 history terakhir
    if len(profiles[student_id]["history"]) > 100:
        profiles[student_id]["history"] = profiles[student_id]["history"][-100:]

    _save_json(PROFILES_FILE, profiles)
    return profiles[student_id]


# ========================
# Leaderboard
# ========================

def update_leaderboard(student_id, nama, jenjang, points, jurusan=None, kelas=None):
    """Update leaderboard entry. Deduplicate by nama+kelas."""
    leaderboard = _load_json(LEADERBOARD_FILE, default=[])

    found = False
    for entry in leaderboard:
        # Match by student_id OR by same nama+kelas
        if (entry["student_id"] == student_id or
            (entry["nama"].lower() == nama.lower() and entry.get("kelas") == kelas)):
            entry["points"] = max(entry["points"], points)  # Keep highest score
            entry["student_id"] = student_id
            entry["nama"] = nama
            entry["kelas"] = kelas
            entry["updated_at"] = datetime.now().isoformat()
            found = True
            break

    if not found:
        leaderboard.append({
            "student_id": student_id,
            "nama": nama,
            "jenjang": jenjang,
            "jurusan": jurusan,
            "kelas": kelas,
            "points": points,
            "updated_at": datetime.now().isoformat(),
        })

    leaderboard.sort(key=lambda x: x["points"], reverse=True)
    _save_json(LEADERBOARD_FILE, leaderboard)
    return leaderboard


def get_leaderboard(kelas=None, limit=20):
    """Ambil leaderboard, opsional filter by kelas."""
    leaderboard = _load_json(LEADERBOARD_FILE, default=[])

    if kelas is not None:
        leaderboard = [e for e in leaderboard if e.get("kelas") == kelas]

    leaderboard.sort(key=lambda x: x["points"], reverse=True)

    for i, entry in enumerate(leaderboard[:limit]):
        entry["rank"] = i + 1

    return leaderboard[:limit]


# ========================
# Score Export API (for MVP Team)
# ========================

def export_all_scores():
    """Export semua score data untuk Tim MVP."""
    profiles = _load_json(PROFILES_FILE)
    leaderboard = _load_json(LEADERBOARD_FILE, default=[])

    export_data = {
        "exported_at": datetime.now().isoformat(),
        "total_students": len(profiles),
        "students": [],
    }

    for sid, profile in profiles.items():
        accuracy = 0
        if profile["total_answered"] > 0:
            accuracy = round(profile["total_correct"] / profile["total_answered"] * 100, 1)

        export_data["students"].append({
            "student_id": sid,
            "nama": profile["nama"],
            "jenjang": profile.get("jenjang", "SMA"),
            "jurusan": profile.get("jurusan"),
            "points": profile["points"],
            "difficulty": profile["difficulty"],
            "total_correct": profile["total_correct"],
            "total_wrong": profile["total_wrong"],
            "total_answered": profile["total_answered"],
            "accuracy": accuracy,
            "best_streak": profile.get("best_streak", 0),
            "achievements_count": len(profile.get("achievements", [])),
            "unique_topics_count": len(profile.get("unique_topics", [])),
            "created_at": profile.get("created_at"),
            "last_played": profile.get("last_played"),
        })

    export_data["leaderboard"] = leaderboard[:50]
    return export_data


def get_analytics_summary():
    """Summary analytics untuk Tim MVP dashboard."""
    profiles = _load_json(PROFILES_FILE)

    if not profiles:
        return {"total_students": 0, "message": "Belum ada data"}

    total_students = len(profiles)
    total_questions = sum(p["total_answered"] for p in profiles.values())
    total_correct = sum(p["total_correct"] for p in profiles.values())
    avg_points = sum(p["points"] for p in profiles.values()) / max(1, total_students)
    avg_accuracy = (total_correct / max(1, total_questions)) * 100

    # Difficulty distribution
    diff_dist = {"Easy": 0, "Medium": 0, "Hard": 0, "Expert": 0}
    for p in profiles.values():
        d = p.get("difficulty", "Easy")
        diff_dist[d] = diff_dist.get(d, 0) + 1

    # Topic popularity from history
    topic_counts = {}
    for p in profiles.values():
        for entry in p.get("history", []):
            topic = entry.get("subject", "Unknown")
            topic_counts[topic] = topic_counts.get(topic, 0) + 1

    top_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        "total_students": total_students,
        "total_questions_answered": total_questions,
        "total_correct_answers": total_correct,
        "overall_accuracy": round(avg_accuracy, 1),
        "average_points": round(avg_points, 1),
        "difficulty_distribution": diff_dist,
        "top_topics": [{"topic": t, "count": c} for t, c in top_topics],
        "generated_at": datetime.now().isoformat(),
    }


def reset_storage():
    """Reset semua data (untuk testing)."""
    _save_json(PROFILES_FILE, {})
    _save_json(LEADERBOARD_FILE, [])
