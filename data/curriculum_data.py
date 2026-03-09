"""
Curriculum Data - Struktur Kurikulum Fisika SMA Lengkap
Game Edukasi Sekolah Rakyat (Tim 4) — Game2

Fokus: Fisika SMA Kelas 10, 11, 12 sesuai kurikulum Sekolah Rakyat.
Mendukung multi-jenjang (SD/SMP/SMA) tapi dengan penekanan pada Fisika.
"""

CURRICULUM = {
    "SD": {
        "jurusan": None,
        "mata_pelajaran": {
            "IPA": {
                "icon": "🔬",
                "topik": [
                    "Gaya dan Gerak",
                    "Energi dan Perubahannya",
                    "Cahaya dan Bunyi",
                    "Magnet",
                    "Listrik Sederhana",
                ]
            },
            "Matematika": {
                "icon": "🔢",
                "topik": [
                    "Penjumlahan dan Pengurangan",
                    "Perkalian dan Pembagian",
                    "Pecahan",
                    "Bangun Datar",
                    "Bangun Ruang",
                ]
            },
        }
    },
    "SMP": {
        "jurusan": None,
        "mata_pelajaran": {
            "IPA": {
                "icon": "🔬",
                "topik": [
                    "Gerak dan Gaya",
                    "Pesawat Sederhana",
                    "Tekanan",
                    "Suhu dan Kalor",
                    "Getaran dan Gelombang",
                    "Cahaya dan Alat Optik",
                    "Listrik Statis dan Dinamis",
                    "Kemagnetan",
                ]
            },
            "Matematika": {
                "icon": "🔢",
                "topik": [
                    "Aljabar",
                    "Pythagoras",
                    "Lingkaran",
                    "Statistika Dasar",
                ]
            },
        }
    },
    "SMA": {
        "jurusan": ["IPA", "IPS"],
        "mata_pelajaran": {
            "IPA": {
                "Fisika": {
                    "icon": "⚡",
                    "kelas": {
                        "Kelas 10": [
                            "Besaran dan Satuan",
                            "Vektor",
                            "Gerak Lurus (GLB & GLBB)",
                            "Gerak Parabola",
                            "Hukum Newton",
                            "Usaha dan Energi",
                            "Momentum dan Impuls",
                            "Gerak Melingkar",
                            "Gravitasi",
                            "Getaran dan Gelombang",
                        ],
                        "Kelas 11": [
                            "Kinematika Gerak Lurus Lanjutan",
                            "Dinamika Rotasi",
                            "Kesetimbangan Benda Tegar",
                            "Fluida Statis",
                            "Fluida Dinamis",
                            "Termodinamika",
                            "Teori Kinetik Gas",
                            "Gelombang Mekanik",
                            "Gelombang Bunyi",
                            "Optik Geometri",
                            "Alat-alat Optik",
                        ],
                        "Kelas 12": [
                            "Listrik Statis",
                            "Listrik Dinamis",
                            "Medan Magnet",
                            "Induksi Elektromagnetik",
                            "Rangkaian Arus Bolak-Balik",
                            "Radiasi Elektromagnetik",
                            "Fisika Kuantum",
                            "Fisika Inti dan Radioaktivitas",
                            "Relativitas Khusus",
                        ],
                    },
                    "topik": [
                        # Kelas 10
                        "Besaran dan Satuan",
                        "Vektor",
                        "Gerak Lurus (GLB & GLBB)",
                        "Gerak Parabola",
                        "Hukum Newton",
                        "Usaha dan Energi",
                        "Momentum dan Impuls",
                        "Gerak Melingkar",
                        "Gravitasi",
                        "Getaran dan Gelombang",
                        # Kelas 11
                        "Kinematika Gerak Lurus Lanjutan",
                        "Dinamika Rotasi",
                        "Kesetimbangan Benda Tegar",
                        "Fluida Statis",
                        "Fluida Dinamis",
                        "Termodinamika",
                        "Teori Kinetik Gas",
                        "Gelombang Mekanik",
                        "Gelombang Bunyi",
                        "Optik Geometri",
                        "Alat-alat Optik",
                        # Kelas 12
                        "Listrik Statis",
                        "Listrik Dinamis",
                        "Medan Magnet",
                        "Induksi Elektromagnetik",
                        "Rangkaian Arus Bolak-Balik",
                        "Radiasi Elektromagnetik",
                        "Fisika Kuantum",
                        "Fisika Inti dan Radioaktivitas",
                        "Relativitas Khusus",
                    ]
                },
                "Matematika": {
                    "icon": "🔢",
                    "topik": [
                        "Eksponen dan Logaritma",
                        "Trigonometri",
                        "Limit",
                        "Turunan",
                        "Integral",
                        "Vektor",
                    ]
                },
                "Kimia": {
                    "icon": "🧪",
                    "topik": [
                        "Struktur Atom",
                        "Ikatan Kimia",
                        "Stoikiometri",
                        "Termokimia",
                        "Kesetimbangan Kimia",
                    ]
                },
                "Biologi": {
                    "icon": "🧬",
                    "topik": [
                        "Sel dan Organel",
                        "Ekosistem",
                        "Genetika dan Pewarisan Sifat",
                    ]
                },
            },
            "IPS": {
                "Ekonomi": {
                    "icon": "💰",
                    "topik": [
                        "Konsep Dasar Ekonomi",
                        "Permintaan dan Penawaran",
                    ]
                },
                "Sejarah": {
                    "icon": "📜",
                    "topik": [
                        "Proklamasi Kemerdekaan",
                        "Kerajaan Hindu-Buddha",
                    ]
                },
            }
        }
    }
}

# Difficulty tiers berdasarkan poin
DIFFICULTY_TIERS = {
    "Easy": {"min": 0, "max": 200, "label": "Pemula ⭐", "color": "#4CAF50", "emoji": "🌱"},
    "Medium": {"min": 201, "max": 500, "label": "Menengah ⭐⭐", "color": "#FF9800", "emoji": "🔥"},
    "Hard": {"min": 501, "max": 900, "label": "Sulit ⭐⭐⭐", "color": "#F44336", "emoji": "💪"},
    "Expert": {"min": 901, "max": float('inf'), "label": "Expert ⭐⭐⭐⭐", "color": "#9C27B0", "emoji": "🏆"},
}

# Scoring rules — enhanced with streak bonuses
SCORING = {
    "correct": 3,
    "incorrect": -1,
    "min_points": 0,
    "streak_bonus": {
        3: 2,    # 3 benar berturut-turut → +2 bonus
        5: 5,    # 5 benar berturut-turut → +5 bonus
        10: 10,  # 10 benar berturut-turut → +10 bonus
    },
    "time_bonus": {
        5: 3,    # jawab < 5 detik → +3 bonus
        10: 2,   # jawab < 10 detik → +2 bonus
        15: 1,   # jawab < 15 detik → +1 bonus
    }
}

# Achievement definitions
ACHIEVEMENTS = {
    "first_correct": {
        "name": "Langkah Pertama! 🎉",
        "description": "Jawab 1 soal dengan benar",
        "condition": {"total_correct": 1},
        "points_reward": 5,
    },
    "streak_3": {
        "name": "Tiga Berturut! 🔥",
        "description": "Jawab 3 soal benar berturut-turut",
        "condition": {"streak": 3},
        "points_reward": 10,
    },
    "streak_5": {
        "name": "Streak Master! 💫",
        "description": "Jawab 5 soal benar berturut-turut",
        "condition": {"streak": 5},
        "points_reward": 20,
    },
    "streak_10": {
        "name": "Unstoppable! ⚡",
        "description": "Jawab 10 soal benar berturut-turut",
        "condition": {"streak": 10},
        "points_reward": 50,
    },
    "total_10": {
        "name": "10 Jawaban Benar 📚",
        "description": "Total 10 jawaban benar",
        "condition": {"total_correct": 10},
        "points_reward": 15,
    },
    "total_50": {
        "name": "50 Jawaban Benar 🎓",
        "description": "Total 50 jawaban benar",
        "condition": {"total_correct": 50},
        "points_reward": 50,
    },
    "total_100": {
        "name": "Centurion! 💯",
        "description": "Total 100 jawaban benar",
        "condition": {"total_correct": 100},
        "points_reward": 100,
    },
    "accuracy_80": {
        "name": "Akurasi Tinggi 🎯",
        "description": "Akurasi di atas 80% (min 20 soal)",
        "condition": {"accuracy_min": 80, "min_answered": 20},
        "points_reward": 30,
    },
    "speed_demon": {
        "name": "Speed Demon ⚡",
        "description": "Jawab 5 soal benar dalam < 5 detik",
        "condition": {"fast_correct": 5},
        "points_reward": 25,
    },
    "physics_explorer": {
        "name": "Fisikawan Muda 🔬",
        "description": "Jawab soal dari 5 topik fisika berbeda",
        "condition": {"unique_physics_topics": 5},
        "points_reward": 20,
    },
    "level_medium": {
        "name": "Naik Level! 📈",
        "description": "Mencapai tingkat Menengah",
        "condition": {"min_points": 201},
        "points_reward": 15,
    },
    "level_hard": {
        "name": "Level Sulit! 🏔️",
        "description": "Mencapai tingkat Sulit",
        "condition": {"min_points": 501},
        "points_reward": 30,
    },
    "level_expert": {
        "name": "Expert Mode! 👑",
        "description": "Mencapai tingkat Expert",
        "condition": {"min_points": 901},
        "points_reward": 50,
    },
}


def get_jenjang_list():
    """Return daftar jenjang yang tersedia."""
    return list(CURRICULUM.keys())


def get_jurusan_list(jenjang):
    """Return daftar jurusan untuk jenjang tertentu."""
    if jenjang not in CURRICULUM:
        return None
    return CURRICULUM[jenjang].get("jurusan")


def get_subjects(jenjang, jurusan=None):
    """Return daftar mata pelajaran berdasarkan jenjang dan jurusan."""
    if jenjang not in CURRICULUM:
        return {}

    mapel_data = CURRICULUM[jenjang]["mata_pelajaran"]

    if jenjang == "SMA" and jurusan:
        if jurusan in mapel_data:
            return mapel_data[jurusan]
        return {}

    return mapel_data


def get_topics(jenjang, subject, jurusan=None):
    """Return daftar topik untuk mata pelajaran tertentu."""
    subjects = get_subjects(jenjang, jurusan)
    if subject in subjects:
        return subjects[subject].get("topik", [])
    return []


def get_physics_topics_by_kelas(kelas=None):
    """Return topik fisika berdasarkan kelas (10/11/12). None = semua."""
    fisika = CURRICULUM["SMA"]["mata_pelajaran"]["IPA"]["Fisika"]
    kelas_data = fisika.get("kelas", {})

    if kelas:
        return kelas_data.get(f"Kelas {kelas}", [])

    # Return semua topik
    all_topics = []
    for topics in kelas_data.values():
        all_topics.extend(topics)
    return all_topics


def get_difficulty(points):
    """Return difficulty level berdasarkan poin."""
    for level, tier in DIFFICULTY_TIERS.items():
        if tier["min"] <= points <= tier["max"]:
            return level
    return "Easy"
