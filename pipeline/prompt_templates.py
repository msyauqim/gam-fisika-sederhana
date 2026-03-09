"""
Prompt Templates - Template Prompt Fisika untuk Game Edukasi Sekolah Rakyat
Tim 4: LLM Game — Game2

Berisi system prompt, difficulty prompts, dan narrative themes
yang digunakan LLM pipeline untuk generate konten kuis fisika.
"""

import random

SYSTEM_PROMPT = """Kamu adalah AI Game Master untuk platform edukasi "Sekolah Rakyat". 
Tugasmu adalah mengubah materi Fisika SMA menjadi narasi cerita yang MENARIK dan INTERAKTIF, 
lalu membuat kuis pilihan ganda berdasarkan materi tersebut.

Aturan penting:
1. Narasi harus dikaitkan dengan konteks yang dekat dengan siswa (sepak bola, petualangan, game, kehidupan sehari-hari)
2. Narasi minimal 3-4 kalimat, menarik dan imajinatif
3. Kuis harus memiliki tepat 5 pilihan jawaban
4. Hanya 1 jawaban yang benar
5. Sertakan penjelasan jawaban yang jelas dan edukatif, termasuk rumus jika relevan
6. Sesuaikan tingkat kesulitan soal sesuai parameter
7. Output HARUS dalam format JSON yang valid

Format output JSON:
{
    "narasi": "...",
    "materi_inti": "...",
    "kuis": {
        "pertanyaan": "...",
        "pilihan": ["A", "B", "C", "D", "E"],
        "jawaban_benar": "...",
        "penjelasan": "..."
    }
}"""

# Prompt khusus untuk Qwen memverifikasi jawaban soal fisika
ANSWER_VERIFICATION_PROMPT = """Kamu adalah ahli Fisika SMA. Tugasmu adalah MEMVERIFIKASI jawaban soal fisika.

Diberikan sebuah soal pilihan ganda beserta 5 pilihan jawaban.
Tugasmu:
1. Analisis soal dengan teliti, identifikasi rumus yang relevan
2. Kerjakan perhitungan langkah demi langkah
3. Tentukan jawaban yang BENAR dari 5 pilihan
4. Berikan penjelasan singkat kenapa jawaban tersebut benar

Output dalam format JSON:
{
    "jawaban_benar": "...",
    "penjelasan": "...",
    "rumus_digunakan": "...",
    "langkah_perhitungan": "..."
}"""

# Template per difficulty level
DIFFICULTY_PROMPTS = {
    "Easy": """Tingkat kesulitan: MUDAH (Easy)
- Soal bersifat dasar dan menguji pemahaman konsep sederhana
- Pilihan jawaban jelas berbeda satu sama lain  
- Narasi menggunakan bahasa sederhana dan situasi familiar
- Cocok untuk siswa yang baru belajar topik ini
- Tidak melibatkan perhitungan rumit""",

    "Medium": """Tingkat kesulitan: MENENGAH (Medium)
- Soal membutuhkan pemahaman konsep yang lebih dalam
- Beberapa pilihan jawaban mirip sehingga perlu berpikir kritis
- Narasi lebih kompleks dengan detail ilmiah
- Soal mungkin melibatkan perhitungan 1-2 langkah""",

    "Hard": """Tingkat kesulitan: SULIT (Hard)
- Soal membutuhkan analisis dan aplikasi konsep
- Pilihan jawaban dirancang untuk menguji pemahaman mendalam
- Narasi mengandung skenario kompleks
- Soal melibatkan perhitungan atau logika multi-langkah""",

    "Expert": """Tingkat kesulitan: EXPERT
- Soal membutuhkan sintesis dari beberapa konsep sekaligus
- Pilihan jawaban sangat mirip, memerlukan pemahaman sangat detail
- Narasi menghubungkan topik dengan aplikasi dunia nyata yang kompleks
- Soal melibatkan pemecahan masalah tingkat tinggi dengan multiple rumus"""
}

# Tema narasi khusus fisika
NARRATIVE_THEMES = {
    "Fisika": [
        "sepak bola", "balapan mobil", "astronot", "superhero",
        "olahraga ekstrem", "pilot pesawat", "mekanik F1",
        "insinyur roket", "penemu", "petualangan luar angkasa",
    ],
    "Matematika": ["detektif", "arsitek", "game designer", "treasure hunter", "astronot"],
    "Kimia": ["laboratorium rahasia", "ilmuwan gila", "memasak", "forensik"],
    "Biologi": ["petualangan alam", "penjelajah hutan", "dokter muda"],
}

# Konteks fisika per kelas untuk prompt yang lebih tajam
PHYSICS_CONTEXT = {
    "Kelas 10": """Konteks Kelas 10 Fisika:
- Fokus pada mekanika dasar: kinematika, dinamika, energi
- Siswa baru mengenal fisika SMA, perlu fondasi kuat
- Rumus dasar: s=vt, v=v₀+at, F=ma, W=Fs, p=mv
- Topik: Besaran, Vektor, GLB/GLBB, Parabola, Newton, Usaha & Energi, Momentum, Melingkar, Gravitasi""",

    "Kelas 11": """Konteks Kelas 11 Fisika:
- Memperdalam mekanika + mulai gelombang, optik, termodinamika
- Siswa sudah familiar dengan konsep dasar, bisa soal lebih analitis
- Rumus: τ=Fr, P=ρgh, FA=ρVg, v=fλ, Q=mcΔT, PV=nRT
- Topik: Rotasi, Kesetimbangan, Fluida, Termodinamika, Gas, Gelombang, Bunyi, Optik""",

    "Kelas 12": """Konteks Kelas 12 Fisika:
- Listrik, magnet, fisika modern, kuantum, relativitas
- Siswa siap untuk soal tingkat tinggi dan konsep abstrak
- Rumus: V=IR, F=BIL, ε=NΔΦ/Δt, E=hf, E=mc², λ=h/p
- Topik: Listrik Statis/Dinamis, Magnet, Induksi, AC, EM, Kuantum, Inti, Relativitas""",
}


def get_kelas_for_topic(topic):
    """Tentukan kelas berdasarkan topik fisika."""
    kelas_10_topics = [
        "Besaran", "Satuan", "Vektor", "Gerak Lurus", "GLB", "GLBB",
        "Parabola", "Newton", "Usaha", "Energi", "Momentum", "Impuls",
        "Melingkar", "Gravitasi", "Getaran", "Gelombang",
    ]
    kelas_11_topics = [
        "Kinematika", "Rotasi", "Kesetimbangan", "Benda Tegar", "Fluida",
        "Termodinamika", "Kinetik Gas", "Mekanik", "Bunyi", "Doppler",
        "Optik", "Snellius", "Lensa", "Cermin", "Alat-alat",
    ]
    kelas_12_topics = [
        "Listrik", "Ohm", "Coulomb", "Magnet", "Lorentz", "Induksi",
        "Faraday", "Bolak-Balik", "AC", "Trafo", "Elektromagnetik",
        "Kuantum", "Fotolistrik", "Broglie", "Inti", "Radioaktivitas",
        "Peluruhan", "Fisi", "Fusi", "Relativitas", "Einstein",
    ]

    for keyword in kelas_10_topics:
        if keyword.lower() in topic.lower():
            return "Kelas 10"
    for keyword in kelas_11_topics:
        if keyword.lower() in topic.lower():
            return "Kelas 11"
    for keyword in kelas_12_topics:
        if keyword.lower() in topic.lower():
            return "Kelas 12"
    return "Kelas 10"


def build_generation_prompt(subject, topic, difficulty, jenjang="SMA", jurusan=None):
    """
    Bangun prompt lengkap untuk generate konten game fisika.

    Args:
        subject: Mata pelajaran (e.g., "Fisika")
        topic: Topik spesifik (e.g., "Hukum Newton")
        difficulty: Tingkat kesulitan ("Easy", "Medium", "Hard", "Expert")
        jenjang: Jenjang pendidikan ("SD", "SMP", "SMA")
        jurusan: Jurusan untuk SMA ("IPA" / "IPS")

    Returns:
        list: Messages list untuk LLM chat format
    """
    # Pilih tema narasi
    themes = NARRATIVE_THEMES.get(subject, ["kehidupan sehari-hari"])
    theme = random.choice(themes)

    # Build context
    context = f"Jenjang: {jenjang}"
    if jurusan:
        context += f" - Jurusan: {jurusan}"

    # Tentukan kelas dan tambahkan konteks fisika
    kelas = get_kelas_for_topic(topic)
    physics_ctx = PHYSICS_CONTEXT.get(kelas, "")

    difficulty_prompt = DIFFICULTY_PROMPTS.get(difficulty, DIFFICULTY_PROMPTS["Easy"])

    user_prompt = f"""Buat konten game edukasi Fisika dengan detail berikut:

{context}
Mata Pelajaran: {subject}
Topik: {topic}
Tema Narasi: {theme}

{physics_ctx}

{difficulty_prompt}

Buatkan:
1. Narasi cerita yang menarik dengan tema "{theme}" yang mengajarkan tentang "{topic}"
2. Satu soal kuis pilihan ganda dengan 5 opsi jawaban
3. Penjelasan jawaban yang edukatif, sertakan rumus jika relevan

Output dalam format JSON yang valid sesuai template."""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

    return messages
