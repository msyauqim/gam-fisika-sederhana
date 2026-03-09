"""
Game Engine - Core Game Logic with Enhanced Gamification
Game Edukasi Sekolah Rakyat (Tim 4) — Game2

Fitur:
- Scoring with streak bonuses & time bonuses
- Achievement system
- Adaptive difficulty based on points
- LLM pipeline integration (mock/local/api)
"""

import time
from data.curriculum_data import (
    get_difficulty, SCORING, DIFFICULTY_TIERS, ACHIEVEMENTS
)
from backend.storage import (
    create_profile, get_profile, update_profile,
    add_history_entry, update_leaderboard
)
from pipeline.llm_pipeline import get_pipeline


class ScoringEngine:
    """Engine untuk menghitung skor dengan streak & time bonuses."""

    @staticmethod
    def calculate_score(current_points, is_correct, streak=0, answer_time=None):
        """
        Hitung skor baru dengan bonuses.
        - Base: +3 benar, -1 salah
        - Streak bonus: 3→+2, 5→+5, 10→+10
        - Time bonus: <5s→+3, <10s→+2, <15s→+1
        """
        bonus = 0

        if is_correct:
            base = SCORING["correct"]

            # Streak bonus
            streak_bonuses = SCORING.get("streak_bonus", {})
            for threshold, bonus_points in sorted(streak_bonuses.items(), reverse=True):
                if streak >= threshold:
                    bonus += bonus_points
                    break

            # Time bonus
            if answer_time is not None:
                time_bonuses = SCORING.get("time_bonus", {})
                for max_time, time_bonus in sorted(time_bonuses.items()):
                    if answer_time <= max_time:
                        bonus += time_bonus
                        break

            new_points = current_points + base + bonus
        else:
            new_points = current_points + SCORING["incorrect"]
            if new_points < SCORING["min_points"]:
                new_points = SCORING["min_points"]

        return new_points, bonus

    @staticmethod
    def get_difficulty_info(points):
        """Return difficulty level dan info lengkap."""
        level = get_difficulty(points)
        tier_info = DIFFICULTY_TIERS.get(level, DIFFICULTY_TIERS["Easy"])
        return {
            "level": level,
            "label": tier_info["label"],
            "color": tier_info["color"],
            "emoji": tier_info.get("emoji", ""),
            "points": points,
        }

    @staticmethod
    def check_achievements(profile):
        """Check dan return achievements baru yang di-unlock."""
        unlocked = profile.get("achievements", [])
        new_achievements = []

        for ach_id, ach in ACHIEVEMENTS.items():
            if ach_id in unlocked:
                continue

            condition = ach["condition"]
            earned = True

            if "total_correct" in condition:
                if profile.get("total_correct", 0) < condition["total_correct"]:
                    earned = False

            if "streak" in condition:
                if profile.get("current_streak", 0) < condition["streak"]:
                    earned = False

            if "min_points" in condition:
                if profile.get("points", 0) < condition["min_points"]:
                    earned = False

            if "accuracy_min" in condition and "min_answered" in condition:
                total = profile.get("total_answered", 0)
                if total < condition["min_answered"]:
                    earned = False
                else:
                    accuracy = profile.get("total_correct", 0) / total * 100
                    if accuracy < condition["accuracy_min"]:
                        earned = False

            if "fast_correct" in condition:
                if profile.get("fast_correct_count", 0) < condition["fast_correct"]:
                    earned = False

            if "unique_physics_topics" in condition:
                topics = profile.get("unique_topics", [])
                if len(topics) < condition["unique_physics_topics"]:
                    earned = False

            if earned:
                new_achievements.append({
                    "id": ach_id,
                    "name": ach["name"],
                    "description": ach["description"],
                    "points_reward": ach["points_reward"],
                })

        return new_achievements


class GameSession:
    """Mengelola satu sesi game untuk seorang siswa."""

    # Mapping topik → gambar ilustrasi
    TOPIC_IMAGES = {
        "Besaran dan Satuan": "besaran.png",
        "Vektor": "vektor.png",
        "Gerak Lurus (GLB & GLBB)": "gerak_lurus.png",
        "Gerak Parabola": "gerak_parabola.png",
        "Hukum Newton": "hukum_newton.png",
        "Usaha dan Energi": "usaha_energi.png",
        "Momentum dan Impuls": "momentum.png",
        "Gerak Melingkar": "rotasi.png",
        "Gravitasi": "gravitasi.png",
        "Getaran dan Gelombang": "gelombang.png",
        "Kinematika Gerak Lurus Lanjutan": "gerak_lurus.png",
        "Dinamika Rotasi": "rotasi.png",
        "Kesetimbangan Benda Tegar": "rotasi.png",
        "Fluida Statis": "fluida.png",
        "Fluida Dinamis": "fluida.png",
        "Termodinamika": "termodinamika.png",
        "Teori Kinetik Gas": "termodinamika.png",
        "Gelombang Mekanik": "gelombang.png",
        "Gelombang Bunyi": "gelombang.png",
        "Optik Geometri": "optik.png",
        "Alat-alat Optik": "optik.png",
        "Listrik Statis": "listrik.png",
        "Listrik Dinamis": "listrik.png",
        "Medan Magnet": "magnet.png",
        "Induksi Elektromagnetik": "magnet.png",
        "Rangkaian Arus Bolak-Balik": "listrik.png",
        "Radiasi Elektromagnetik": "kuantum.png",
        "Fisika Kuantum": "kuantum.png",
        "Fisika Inti dan Radioaktivitas": "kuantum.png",
        "Relativitas Khusus": "relativitas.png",
    }

    def __init__(self, student_id):
        self.student_id = student_id
        self.current_content = None
        self.question_start_time = None
        self.scoring = ScoringEngine()

    def _get_image_url(self, topic):
        """Return URL gambar ilustrasi untuk topik."""
        filename = self.TOPIC_IMAGES.get(topic)
        if filename:
            return f"/static/images/{filename}"
        # Fallback: cari berdasarkan keyword
        for key, img in self.TOPIC_IMAGES.items():
            if key.lower() in topic.lower() or topic.lower() in key.lower():
                return f"/static/images/{img}"
        return None

    def generate_content(self, subject, topic, jenjang="SMA", jurusan=None):
        """Generate konten game (narasi + kuis) melalui pipeline."""
        profile = get_profile(self.student_id)
        if not profile:
            return None

        difficulty = get_difficulty(profile["points"])

        # Generate content via pipeline (mock / local / api)
        pipeline = get_pipeline()
        content = pipeline.generate(subject, topic, difficulty, jenjang, jurusan)

        if not content:
            # Generic fallback
            content = {
                "narasi": f"Mari kita pelajari tentang {topic} dalam {subject}!",
                "materi_inti": topic,
                "kuis": {
                    "pertanyaan": f"Pertanyaan tentang {topic}:",
                    "pilihan": [f"Jawaban A", f"Jawaban B", f"Jawaban C (benar)", f"Jawaban D", f"Jawaban E"],
                    "jawaban_benar": f"Jawaban C (benar)",
                    "penjelasan": f"Ini adalah konten placeholder untuk {topic}."
                }
            }

        self.current_content = content
        self.question_start_time = time.time()

        return {
            "content": content,
            "image_url": self._get_image_url(topic),
            "student_info": self.scoring.get_difficulty_info(profile["points"]),
        }

    def submit_answer(self, selected_answer):
        """Submit jawaban kuis dengan streak & time tracking."""
        if not self.current_content:
            return {"error": "Tidak ada kuis aktif"}

        profile = get_profile(self.student_id)
        if not profile:
            return {"error": "Profil tidak ditemukan"}

        # Calculate answer time
        answer_time = None
        if self.question_start_time:
            answer_time = time.time() - self.question_start_time

        correct_answer = self.current_content["kuis"]["jawaban_benar"]
        is_correct = selected_answer == correct_answer

        # Update streak
        old_streak = profile.get("current_streak", 0)
        new_streak = old_streak + 1 if is_correct else 0
        best_streak = max(profile.get("best_streak", 0), new_streak)

        # Calculate score with bonuses
        old_points = profile["points"]
        new_points, bonus = self.scoring.calculate_score(
            old_points, is_correct, new_streak, answer_time
        )
        point_change = new_points - old_points

        # Track fast correct
        fast_correct = profile.get("fast_correct_count", 0)
        if is_correct and answer_time is not None and answer_time < 5:
            fast_correct += 1

        # Track unique topics
        unique_topics = profile.get("unique_topics", [])
        topic = self.current_content.get("materi_inti", "")
        if topic and topic not in unique_topics:
            unique_topics.append(topic)

        # Update profile
        update_data = {
            "points": new_points,
            "difficulty": get_difficulty(new_points),
            "total_correct": profile["total_correct"] + (1 if is_correct else 0),
            "total_wrong": profile["total_wrong"] + (0 if is_correct else 1),
            "total_answered": profile["total_answered"] + 1,
            "current_streak": new_streak,
            "best_streak": best_streak,
            "fast_correct_count": fast_correct,
            "unique_topics": unique_topics,
        }
        updated_profile = update_profile(self.student_id, update_data)

        # Check achievements
        new_achievements = self.scoring.check_achievements(updated_profile)
        achievement_points = 0
        if new_achievements:
            ach_ids = updated_profile.get("achievements", [])
            for ach in new_achievements:
                ach_ids.append(ach["id"])
                achievement_points += ach["points_reward"]

            # Add achievement bonus points
            if achievement_points > 0:
                updated_profile["points"] += achievement_points
                new_points += achievement_points
                point_change += achievement_points

            update_profile(self.student_id, {
                "achievements": ach_ids,
                "points": updated_profile["points"],
            })

        # Add history
        add_history_entry(self.student_id, {
            "subject": self.current_content.get("materi_inti", "Unknown"),
            "question": self.current_content["kuis"]["pertanyaan"],
            "selected": selected_answer,
            "correct": correct_answer,
            "is_correct": is_correct,
            "point_change": point_change,
            "answer_time": round(answer_time, 1) if answer_time else None,
            "streak": new_streak,
        })

        # Update leaderboard
        update_leaderboard(
            self.student_id,
            profile["nama"],
            profile.get("jenjang", "SMA"),
            new_points,
            profile.get("jurusan"),
            profile.get("kelas")
        )

        # Build result
        accuracy = round(
            updated_profile["total_correct"] / max(1, updated_profile["total_answered"]) * 100, 1
        )

        result = {
            "is_correct": is_correct,
            "correct_answer": correct_answer,
            "selected_answer": selected_answer,
            "penjelasan": self.current_content["kuis"]["penjelasan"],
            "point_change": point_change,
            "bonus": bonus,
            "old_points": old_points,
            "new_points": new_points,
            "answer_time": round(answer_time, 1) if answer_time else None,
            "streak": new_streak,
            "best_streak": best_streak,
            "difficulty": self.scoring.get_difficulty_info(new_points),
            "new_achievements": new_achievements,
            "stats": {
                "total_correct": updated_profile["total_correct"],
                "total_wrong": updated_profile["total_wrong"],
                "total_answered": updated_profile["total_answered"],
                "accuracy": accuracy,
                "current_streak": new_streak,
                "best_streak": best_streak,
            }
        }

        self.current_content = None
        self.question_start_time = None

        return result


# Active sessions in memory
_active_sessions = {}


def get_or_create_session(student_id):
    """Get atau buat session untuk student."""
    if student_id not in _active_sessions:
        _active_sessions[student_id] = GameSession(student_id)
    return _active_sessions[student_id]


def clear_session(student_id):
    """Hapus session dari memory."""
    if student_id in _active_sessions:
        del _active_sessions[student_id]
