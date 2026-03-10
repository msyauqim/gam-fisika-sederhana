# Deskripsi Proyek — Game Edukasi "Sekolah Rakyat"
## Tim 4: LLM Game — Game2

---

## 1. Persiapan Data

### 1.1 Sumber Data Soal
Data soal fisika dikumpulkan dari dokumen standar ujian nasional resmi:

| Sumber | Jenis | Jumlah Soal |
|--------|-------|-------------|
| Pembahasan Fisika UN 2019 & 2018 (Kak Ajaz) | PDF soal + pembahasan | ~20 soal |
| Prediksi Soal Fisika TKA & US 2025 Paket 2 | PDF prediksi | ~14 soal |
| Paket Akhir UNBK Fisika | PDF resmi | ~10 soal |

**Total: 44 soal fisika** yang sudah di-curate dan divalidasi jawabannya.

### 1.2 Struktur Data Soal
Setiap soal disimpan dalam format terstruktur di `data/physics_content.py` dengan skema:

```json
{
    "narasi": "Konteks cerita yang menjelaskan situasi fisika...",
    "materi_inti": "Nama sub-topik (misal: Percepatan Sistem Benda)",
    "kuis": {
        "pertanyaan": "Teks pertanyaan pilihan ganda...",
        "pilihan": ["A", "B", "C", "D", "E"],
        "jawaban_benar": "Jawaban yang benar (harus ada di pilihan)",
        "penjelasan": "Pembahasan lengkap termasuk rumus dan langkah perhitungan"
    }
}
```

### 1.3 Cakupan Kurikulum
Soal mencakup **30 topik fisika SMA** yang dipetakan ke 3 jenjang kelas:

| Kelas | Topik | Contoh |
|-------|-------|--------|
| **Kelas 10** | 10 topik (Mekanika Dasar) | Besaran & Satuan, Vektor, GLB/GLBB, Gerak Parabola, Hukum Newton, Usaha & Energi, Momentum, Gerak Melingkar, Gravitasi, Getaran & Gelombang |
| **Kelas 11** | 10 topik (Mekanika Lanjut + Gelombang) | Kinematika Lanjutan, Dinamika Rotasi, Kesetimbangan Benda Tegar, Fluida Statis & Dinamis, Termodinamika, Teori Kinetik Gas, Gelombang Mekanik & Bunyi, Optik Geometri, Alat-alat Optik |
| **Kelas 12** | 10 topik (Listrik, Magnet, Fisika Modern) | Listrik Statis & Dinamis, Medan Magnet, Induksi Elektromagnetik, Rangkaian AC, Radiasi EM, Fisika Kuantum, Fisika Inti & Radioaktivitas, Relativitas Khusus |

### 1.4 Ilustrasi Visual
Setiap kategori topik dilengkapi **17 gambar ilustrasi** yang di-generate menggunakan AI image generation, disimpan di `static/images/`. Mapping 30 topik → 17 gambar memastikan setiap topik memiliki representasi visual yang relevan.

---

## 2. Pemilihan Base Model

### 2.1 Kriteria Pemilihan Model
Pemilihan base model LLM untuk game edukasi ini mempertimbangkan beberapa faktor:

| Kriteria | Bobot | Pertimbangan |
|----------|-------|-------------|
| **Kemampuan Bahasa Indonesia** | Tinggi | Model harus mampu generate soal dan narasi dalam Bahasa Indonesia yang natural dan benar secara tata bahasa |
| **Pemahaman Fisika** | Tinggi | Model harus mampu membuat soal fisika yang akurat secara saintifik, termasuk perhitungan numerik |
| **Kecepatan Inferensi** | Menengah | Response time harus reasonable untuk pengalaman game yang responsif (< 15 detik) |
| **Biaya Aksesibilitas** | Menengah | Harus bisa diakses secara gratis atau murah untuk proyek edukasi |
| **Format Output JSON** | Tinggi | Model harus reliable menghasilkan JSON terstruktur sesuai skema yang sudah ditentukan |

### 2.2 Model yang Dipilih: Qwen 2.5 (by Alibaba Cloud)

**Model utama: `Qwen/Qwen2.5-7B-Instruct`**

Alasan pemilihan Qwen dibandingkan model lain:

| Aspek | Qwen 2.5 | LLaMA 3 | Mistral | GPT-4 |
|-------|----------|---------|---------|-------|
| Bahasa Indonesia | ✅ Sangat baik (dilatih multilingual termasuk ID) | ⚠️ Cukup baik | ⚠️ Sedang | ✅ Sangat baik |
| Akses Gratis | ✅ Free via HuggingFace API | ❌ Butuh auth | ❌ Butuh auth | ❌ Berbayar |
| JSON Output | ✅ Reliable | ✅ Baik | ⚠️ Kadang error | ✅ Sangat baik |
| Kecepatan (7B) | ✅ ~10-15 detik | - | - | - |
| Open Source | ✅ Ya | ✅ Ya | ✅ Ya | ❌ Tidak |

Qwen 2.5 dipilih karena kombinasi terbaik antara kemampuan Bahasa Indonesia, aksesibilitas gratis via HuggingFace Inference API, dan kemampuan menghasilkan output JSON yang terstruktur.

### 2.3 Konfigurasi Model
```python
# Parameter inferensi yang digunakan
model = "Qwen/Qwen2.5-7B-Instruct"
temperature = 0.85          # Cukup kreatif untuk variasi soal
top_p = 0.9                 # Nucleus sampling untuk output berkualitas
max_tokens = 1024           # Cukup untuk narasi + soal + penjelasan
```

### 2.4 Opsi Model Alternatif
Pipeline dirancang fleksibel dengan **3 mode** yang mendukung berbagai deployment:

| Mode | Model | Kebutuhan | Use Case |
|------|-------|-----------|----------|
| `api` (default) | Qwen 2.5 via HuggingFace | Internet + HF Token | Development & Production ringan |
| `local` | Qwen model via `transformers` | GPU lokal (≥8GB VRAM) | Production offline / tanpa internet |
| `mock` | Bank soal statis dari PDF | Tidak ada | Fallback & testing cepat |

---

## 3. Pengembangan Pipeline yang Stabil untuk Parameter Game Edukasi

### 3.1 Arsitektur Pipeline (`pipeline/`)

Pipeline konten game terdiri dari 3 komponen utama:

```
┌─────────────────────────────────────────────────────────────┐
│                   GameContentPipeline                       │
│                                                             │
│  ┌─────────────┐    ┌──────────────┐    ┌───────────────┐  │
│  │ Prompt       │    │ LLM Engine   │    │ Output        │  │
│  │ Templates    │───▶│ (Qwen 2.5)   │───▶│ Parser &      │  │
│  │              │    │              │    │ Validator     │  │
│  └─────────────┘    └──────────────┘    └───────────────┘  │
│        ▲                                       │           │
│        │              ┌──────────────┐         │           │
│        └──────────────│ Mock Bank    │◀────────┘           │
│          (fallback)   │ (44 soal)    │  (jika gagal)       │
│                       └──────────────┘                     │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Komponen Pipeline

#### 3.2.1 Prompt Engineering (`pipeline/prompt_templates.py`)

**System Prompt** mendefinisikan peran AI sebagai "Game Master" dengan aturan ketat:
- Narasi harus dikaitkan dengan konteks dekat siswa (sepak bola, petualangan, game)
- Kuis harus memiliki tepat 5 pilihan jawaban
- Output HARUS dalam format JSON yang valid
- Tingkat kesulitan harus sesuai parameter

**Difficulty Tiers** — 4 level kesulitan adaptif:

| Level | Trigger | Karakteristik Soal |
|-------|---------|-------------------|
| Easy (Pemula ⭐) | 0-9 poin | Konsep dasar, tidak ada perhitungan rumit |
| Medium (Pelajar 📚) | 10-29 poin | Perhitungan 1-2 langkah, pilihan mirip |
| Hard (Ahli 🔬) | 30-49 poin | Analisis multi-langkah, skenario kompleks |
| Expert (Master 🏆) | 50+ poin | Sintesis beberapa konsep, multiple rumus |

**Konteks per Kelas** — Prompt diperkaya dengan konteks fisika spesifik per kelas termasuk daftar rumus relevan (misalnya Kelas 10: `s=vt, v=v₀+at, F=ma, W=Fs, p=mv`).

**Tema Narasi** — 10 tema acak untuk variasi cerita: sepak bola, astronot, superhero, pilot pesawat, petualangan luar angkasa, dll.

#### 3.2.2 LLM Engine (`pipeline/llm_pipeline.py`)

Kelas `GameContentPipeline` mengelola seluruh siklus inferensi:

1. **Inisialisasi** — Singleton pattern memastikan hanya 1 instance pipeline aktif
2. **Randomisasi** — Setiap request di-inject "seed" random agar soal selalu berbeda:
   ```python
   randomizer = random.choice([
       "Buatkan soal yang UNIK dan BERBEDA...",
       "Ciptakan pertanyaan BARU yang belum pernah ditanyakan...",
       ...
   ])
   # + angka random untuk variasi konteks
   ```
3. **Parsing JSON** — Robust parser yang menangani berbagai format output LLM:
   - Parse JSON langsung
   - Ekstrak dari code block ` ```json ... ``` `
   - Regex pencarian `{ ... }` terluar
4. **Validasi Output** — Memastikan struktur JSON sesuai skema:
   - Harus ada key: `narasi`, `materi_inti`, `kuis`
   - Kuis harus punya: `pertanyaan`, `pilihan` (tepat 5), `jawaban_benar`, `penjelasan`
   - `jawaban_benar` harus ada di dalam array `pilihan`
5. **Pengacakan Jawaban** — Posisi jawaban benar diacak agar tidak selalu di posisi yang sama
6. **Graceful Fallback** — Jika API gagal (timeout, error, parsing gagal), otomatis gunakan bank soal statis. Game tidak pernah crash karena masalah LLM

#### 3.2.3 Answer Verification (`prompt_templates.py`)

Prompt khusus `ANSWER_VERIFICATION_PROMPT` memungkinkan Qwen memverifikasi jawaban soal fisika secara mandiri:
- Identifikasi rumus yang relevan
- Kerjakan perhitungan langkah demi langkah
- Tentukan jawaban yang BENAR
- Berikan penjelasan

### 3.3 Parameter Stabilitas Pipeline

| Parameter | Nilai | Fungsi |
|-----------|-------|--------|
| `timeout` | 60 detik | Batas waktu API call sebelum fallback |
| `temperature` | 0.85 | Keseimbangan kreativitas vs akurasi |
| `max_tokens` | 1024 | Cukup untuk narasi + soal lengkap |
| `top_p` | 0.9 | Nucleus sampling untuk kualitas |
| Fallback mode | `mock` | Jaminan konten selalu tersedia |
| Answer shuffle | Random | Mencegah pattern jawaban yang predictable |
| Seed injection | Random int | Memaksa variasi output setiap request |

---

## 4. Pengembangan Arsitektur Game Awal

### 4.1 Diagram Arsitektur Keseluruhan

```
┌──────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Browser)                           │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │
│  │ Login &    │  │ Topic        │  │ Quiz Engine  │  │ Leader-  │ │
│  │ Profile    │  │ Selection    │  │ + Timer      │  │ board    │ │
│  └────────────┘  └──────────────┘  └──────────────┘  └──────────┘ │
│  HTML/CSS/JS (game.js + style.css + index.html)                    │
└──────────────────────────┬───────────────────────────────────────────┘
                           │ REST API (JSON)
┌──────────────────────────▼───────────────────────────────────────────┐
│                      BACKEND (Flask - app.py)                       │
│                                                                     │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │ Profile  │  │ Game Engine  │  │ Leaderboard  │  │ Score      │ │
│  │ API      │  │ (Scoring,    │  │ API          │  │ Export API │ │
│  │          │  │  Achievements│  │              │  │ (Tim MVP)  │ │
│  └──────────┘  └──────┬───────┘  └──────────────┘  └────────────┘ │
│                        │                                            │
│  ┌─────────────────────▼──────────────────────────────────────────┐ │
│  │              LLM Pipeline (GameContentPipeline)                │ │
│  │  ┌───────┐  ┌─────────┐  ┌────────────────────────┐          │ │
│  │  │ Mock  │  │  Local  │  │  API (HuggingFace +    │          │ │
│  │  │ Bank  │  │  (GPU)  │  │  Qwen 2.5-7B-Instruct)│          │ │
│  │  └───────┘  └─────────┘  └────────────────────────┘          │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │              Storage Layer (JSON-based)                        │ │
│  │  profiles.json          leaderboard.json                      │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.2 Komponen Backend

#### 4.2.1 Flask Web Server (`app.py`)
Server utama dengan **22 API endpoint** yang mengelola seluruh fungsionalitas game:

| Kategori | Endpoint | Method | Fungsi |
|----------|----------|--------|--------|
| Frontend | `/` | GET | Halaman utama game |
| Profile | `/api/profile` | POST | Buat/ambil profil siswa |
| Profile | `/api/profile/<id>` | GET | Detail profil siswa |
| Kurikulum | `/api/subjects` | GET | Daftar mata pelajaran |
| Kurikulum | `/api/physics/topics` | GET | Topik fisika per kelas |
| Game | `/api/generate` | POST | Generate soal (LLM/mock) |
| Game | `/api/answer` | POST | Submit jawaban kuis |
| Leaderboard | `/api/leaderboard` | GET | Ranking per kelas |
| Achievement | `/api/achievements/<id>` | GET | Badge & pencapaian siswa |
| Export | `/api/scores/export` | GET | Export data skor (Tim MVP) |
| Export | `/api/scores/student/<id>` | GET | Detail skor per siswa |
| Analytics | `/api/analytics/summary` | GET | Ringkasan analitik |
| Stats | `/api/stats` | GET | Statistik umum game |

#### 4.2.2 Game Engine (`backend/game_engine.py`)

**ScoringEngine** — Sistem penilaian gamifikasi:
- Base score: +3 benar, -1 salah
- Streak bonus: 3 berturut → +2, 5 berturut → +5, 10 berturut → +10
- Time bonus: < 5 detik → +3, < 10 detik → +2, < 15 detik → +1
- 4 tier kesulitan adaptif berdasarkan akumulasi poin

**Achievement System** — 13 badge pencapaian:
- Milestone-based: Langkah Pertama, Penjelajah, Veteran, dll.
- Streak-based: Streak Master (5 berturut), Hot Streak (10 berturut)
- Mastery-based: Perfeksionis, Speed Runner, dll.

**GameSession** — Mengelola sesi quiz per siswa:
- Generate konten melalui pipeline
- Track waktu jawab per soal
- Hitung skor dengan semua bonuses
- Update leaderboard otomatis

#### 4.2.3 Storage Layer (`backend/storage.py`)
Penyimpanan data berbasis JSON file:
- `profiles.json` — Data profil siswa (nama, kelas, poin, history, achievements)
- `leaderboard.json` — Ranking global dengan deduplikasi per nama+kelas
- Score Export API — Endpoint khusus untuk Tim MVP menarik data skor

### 4.3 Komponen Frontend

#### 4.3.1 UI Design (`templates/index.html` + `static/style.css`)
- **Dark theme premium** dengan gradien dan glassmorphism
- Responsive design untuk desktop dan mobile
- Animasi micro-interaction pada tombol, card, dan transisi
- Loading spinner kustom saat LLM generate soal ("Robot AI sedang berpikir... 🤖")

#### 4.3.2 Game Logic (`static/game.js`)
- State management untuk sesi permainan
- Timer 60 detik per soal dengan visual countdown
- Tab navigasi: Topik, Leaderboard, Achievement
- Filter leaderboard per kelas (10, 11, 12, Semua)
- Feedback visual saat jawab benar/salah dengan penjelasan

### 4.4 Alur Permainan (Game Flow)

```
Login (Nama + Kelas)
       │
       ▼
Pilih Topik Fisika (30 topik dengan ilustrasi)
       │
       ▼
Loading ("Robot AI sedang berpikir... 🤖")
       │
       ▼
Qwen 2.5 Generate Soal Baru ──(gagal)──▶ Fallback Bank Soal
       │
       ▼
Tampilkan Narasi + Gambar Ilustrasi + Soal
       │
       ▼
Siswa Jawab (Timer 60 detik)
       │
       ▼
Hitung Skor (Base + Streak + Time Bonus)
       │
       ▼
Tampilkan Hasil + Penjelasan + Achievement
       │
       ▼
Update Leaderboard ──▶ Soal Berikutnya / Kembali ke Topik
```

### 4.5 Integrasi dengan Tim Lain

| Tim | Integrasi | Endpoint |
|-----|-----------|----------|
| **Tim MVP** | Export data skor untuk dashboard | `GET /api/scores/export`, `GET /api/analytics/summary` |
| **Tim RAG** | Potensi integrasi knowledge base | Pipeline API mode dapat diarahkan ke RAG endpoint |
| **Tim Agentic** | Potensi multi-agent game master | `ANSWER_VERIFICATION_PROMPT` untuk agent verifier |

---

## 5. Tech Stack

| Layer | Teknologi | Versi |
|-------|-----------|-------|
| Frontend | HTML5, CSS3, Vanilla JS | - |
| Backend | Python Flask | 3.x |
| LLM | Qwen 2.5-7B-Instruct | via HuggingFace Inference API |
| Storage | JSON file-based | - |
| API Protocol | REST (JSON) | - |
| Deployment | localhost:5051 | Development server |

---

## 6. Cara Menjalankan

```bash
# 1. Masuk ke direktori game
cd "project game edukasi kelompok 4/game2"

# 2. Aktifkan virtual environment
source venv/bin/activate

# 3. Jalankan server (mode API — Qwen aktif)
PIPELINE_MODE=api python3 app.py

# 4. Buka browser
# → http://localhost:5051
```

**Environment Variables:**

| Variable | Default | Keterangan |
|----------|---------|------------|
| `PIPELINE_MODE` | `api` | Mode pipeline: `mock`, `local`, atau `api` |
| `HF_TOKEN` | (sudah di-hardcode) | Token HuggingFace untuk akses API |
| `LLM_API_MODEL` | `Qwen/Qwen2.5-7B-Instruct` | Model LLM yang digunakan |
