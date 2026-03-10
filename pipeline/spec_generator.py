"""
Spec Generator — Stage 1: SFT-based Game Specification Generator
Game Edukasi Sekolah Rakyat (Tim 4) — Game2

Menggunakan Qwen + SFT few-shot prompting untuk menghasilkan
spesifikasi game terstruktur dari topik fisika.
"""

import json
import os
import random

from huggingface_hub import InferenceClient


# Load SFT dataset sebagai few-shot examples
_sft_dataset = None

def _load_sft_examples():
    global _sft_dataset
    if _sft_dataset is None:
        sft_path = os.path.join(os.path.dirname(__file__), "sft_dataset.json")
        with open(sft_path, "r", encoding="utf-8") as f:
            _sft_dataset = json.load(f)
    return _sft_dataset


# System prompt untuk spec generator
SPEC_SYSTEM_PROMPT = """Kamu adalah AI Game Designer spesialis game edukasi Fisika SMA.
Tugasmu adalah membuat SPESIFIKASI GAME INTERAKTIF yang detail dari topik fisika yang diberikan.

Spesifikasi harus dalam format JSON dengan struktur berikut:
{
    "game_type": "tipe game (drag_and_drop / simulation / clicker_game / racing_game / puzzle / quiz_interactive)",
    "title": "judul game yang menarik",
    "description": "deskripsi singkat game (2-3 kalimat)",
    "mechanics": {
        "interaction": "cara pemain berinteraksi",
        "objective": "tujuan game",
        "rules": ["aturan 1", "aturan 2", "aturan 3"],
        "win_condition": "kondisi menang"
    },
    "visual_style": {
        "theme": "tema visual",
        "colors": ["warna1", "warna2", "warna3", "warna4"],
        "elements": ["elemen visual 1", "elemen 2", "elemen 3"]
    },
    "quiz_questions": [
        {
            "question": "pertanyaan fisika terkait topik",
            "options": ["A", "B", "C", "D"],
            "answer": "jawaban benar",
            "explanation": "penjelasan + rumus"
        }
    ],
    "scoring_rules": {
        "correct_action": 10,
        "wrong_action": -2,
        "time_bonus": true,
        "max_time_seconds": 90
    }
}

ATURAN PENTING:
1. Game harus INTERAKTIF dan MENARIK untuk siswa SMA
2. Mekanik game harus relevan dengan konsep fisika yang diajarkan
3. Soal kuis harus akurat secara saintifik
4. Visual style harus modern dan appealing
5. Output HARUS valid JSON"""


class GameSpecGenerator:
    """
    Stage 1: Generate game specification dari topik fisika.
    Menggunakan SFT few-shot prompting dengan Qwen.
    """

    def __init__(self):
        hf_token = os.environ.get("HF_TOKEN", "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")
        model = os.environ.get("LLM_API_MODEL", "Qwen/Qwen2.5-7B-Instruct")

        self._client = InferenceClient(
            model=model,
            token=hf_token,
            timeout=90,
        )
        self._sft_examples = _load_sft_examples()
        print(f"🎮 Spec Generator ready: {model} ({len(self._sft_examples)} SFT examples)")

    def generate_spec(self, topic, kelas=10, difficulty="Easy"):
        """
        Generate game specification dari topik fisika.

        Args:
            topic: Topik fisika (e.g., "Hukum Newton")
            kelas: Kelas SMA (10, 11, 12)
            difficulty: Tingkat kesulitan ("Easy", "Medium", "Hard")

        Returns:
            dict: Game specification JSON, or None if failed
        """
        try:
            messages = self._build_prompt(topic, kelas, difficulty)

            response = self._client.chat_completion(
                messages=messages,
                max_tokens=1500,
                temperature=0.8,
                top_p=0.9,
            )

            content = response.choices[0].message.content
            spec = self._parse_spec(content)

            if spec:
                print(f"✅ [Stage 1] Spec generated: {spec.get('title', '?')} ({spec.get('game_type', '?')})")
                return spec
            else:
                print(f"⚠️ [Stage 1] Parsing failed, using fallback spec")
                return self._fallback_spec(topic, kelas, difficulty)

        except Exception as e:
            print(f"❌ [Stage 1] Error: {e}")
            return self._fallback_spec(topic, kelas, difficulty)

    def _build_prompt(self, topic, kelas, difficulty):
        """Build few-shot prompt menggunakan SFT dataset."""
        # Pilih 2-3 contoh SFT yang relevan sebagai few-shot
        examples = random.sample(self._sft_examples, min(3, len(self._sft_examples)))

        few_shot_text = ""
        for ex in examples:
            few_shot_text += f"\n--- Contoh ---\nInstruction: {ex['instruction']}\n"
            few_shot_text += f"Output:\n```json\n{json.dumps(ex['output'], ensure_ascii=False, indent=2)}\n```\n"

        user_prompt = f"""Berikut adalah beberapa contoh spesifikasi game yang sudah dibuat:
{few_shot_text}

--- Tugas Kamu ---
Sekarang buatkan spesifikasi mini-game interaktif untuk:
- Topik: {topic}
- Kelas: {kelas}
- Level: {difficulty}

Buatkan spesifikasi game yang UNIK, KREATIF, dan BERBEDA dari contoh di atas.
Game harus relevan dengan konsep fisika "{topic}" dan sesuai untuk siswa kelas {kelas} SMA.
Seed random: {random.randint(10000, 99999)}

Output HANYA valid JSON (tanpa teks tambahan di luar JSON)."""

        return [
            {"role": "system", "content": SPEC_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]

    def _parse_spec(self, content):
        """Parse JSON spec dari LLM response."""
        import re

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # Try extracting from code block
        code_block = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
        if code_block:
            try:
                return json.loads(code_block.group(1))
            except json.JSONDecodeError:
                pass

        # Try finding outermost { ... }
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        return None

    def _fallback_spec(self, topic, kelas, difficulty):
        """Fallback spec jika generation gagal."""
        return {
            "game_type": "quiz_interactive",
            "title": f"Kuis {topic}",
            "description": f"Kuis interaktif tentang {topic} untuk siswa kelas {kelas} SMA.",
            "mechanics": {
                "interaction": "Pilih jawaban yang benar dari 4 pilihan",
                "objective": f"Jawab pertanyaan tentang {topic} dengan benar",
                "rules": ["Pilih 1 jawaban dari 4 opsi", "Jawab dalam waktu yang ditentukan", "Skor bertambah jika benar"],
                "win_condition": "Jawab semua pertanyaan dengan benar"
            },
            "visual_style": {
                "theme": "modern_quiz",
                "colors": ["#1a1a2e", "#16213e", "#0f3460", "#e94560"],
                "elements": ["Kartu soal", "Tombol jawaban", "Timer", "Skor"]
            },
            "quiz_questions": [
                {
                    "question": f"Pertanyaan tentang {topic} (kelas {kelas})",
                    "options": ["Jawaban A", "Jawaban B", "Jawaban C", "Jawaban D"],
                    "answer": "Jawaban A",
                    "explanation": f"Penjelasan tentang konsep {topic}."
                }
            ],
            "scoring_rules": {
                "correct_answer": 10,
                "wrong_answer": -2,
                "time_bonus": True,
                "max_time_seconds": 60
            }
        }


# Singleton
_spec_generator = None

def get_spec_generator():
    global _spec_generator
    if _spec_generator is None:
        _spec_generator = GameSpecGenerator()
    return _spec_generator
