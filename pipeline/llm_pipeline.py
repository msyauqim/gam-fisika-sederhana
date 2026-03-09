"""
LLM Pipeline - Inference Pipeline untuk Game Edukasi Sekolah Rakyat
Tim 4: LLM Game — Game2

Pipeline untuk generate konten game (narasi + kuis) menggunakan LLM Qwen.
Mode default: 'api' menggunakan HuggingFace Inference API (gratis, tanpa GPU lokal).
Fallback: 'mock' menggunakan bank soal statis dari PDF UN/UNBK.
"""

import json
import os
import random
import re
from pipeline.prompt_templates import build_generation_prompt, NARRATIVE_THEMES


class GameContentPipeline:
    """
    Pipeline utama untuk generate konten game edukasi.

    Modes:
    - 'mock': Bank soal statis dari physics_content.py (fallback)
    - 'local': Model Qwen lokal via transformers (butuh GPU)
    - 'api': HuggingFace Inference API + Qwen (default, gratis, tanpa GPU)
    """

    def __init__(self, mode="api", model_name="Qwen/Qwen2.5-72B-Instruct"):
        self.mode = mode
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self._hf_client = None

        if mode == "local":
            self._load_model()
        elif mode == "api":
            self._init_api_client()

    def _load_model(self):
        """Load model Qwen untuk mode lokal."""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            print(f"🔄 Loading model: {self.model_name}...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype="auto",
                device_map="auto"
            )
            print("✅ Model loaded successfully!")
        except ImportError:
            print("⚠️ transformers not installed. Install with: pip install transformers torch")
            print("📌 Falling back to mock mode...")
            self.mode = "mock"
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            print("📌 Falling back to mock mode...")
            self.mode = "mock"

    def _init_api_client(self):
        """Init HuggingFace Inference API client."""
        try:
            from huggingface_hub import InferenceClient

            # HF Token (opsional untuk rate limit yang lebih tinggi)
            hf_token = os.environ.get("HF_TOKEN", None)
            self.api_model = os.environ.get("LLM_API_MODEL", "Qwen/Qwen2.5-72B-Instruct")

            self._hf_client = InferenceClient(
                model=self.api_model,
                token=hf_token,
                timeout=60,
            )
            print(f"🔌 HuggingFace API mode: {self.api_model}")
            if hf_token:
                print("🔑 HF Token detected — higher rate limits")
            else:
                print("💡 Tip: Set HF_TOKEN env var untuk rate limit lebih tinggi")

        except ImportError:
            print("⚠️ huggingface_hub not installed. pip install huggingface_hub")
            print("📌 Falling back to mock mode...")
            self.mode = "mock"
        except Exception as e:
            print(f"❌ API init error: {e}")
            print("📌 Falling back to mock mode...")
            self.mode = "mock"

    def generate(self, subject, topic, difficulty="Easy", jenjang="SMA", jurusan=None):
        """
        Generate konten game (narasi + kuis) menggunakan Qwen.

        Returns:
            dict: {narasi, materi_inti, kuis: {pertanyaan, pilihan, jawaban_benar, penjelasan}}
        """
        if self.mode == "mock":
            return self._generate_mock(subject, topic, difficulty, jenjang, jurusan)
        elif self.mode == "local":
            return self._generate_local(subject, topic, difficulty, jenjang, jurusan)
        elif self.mode == "api":
            return self._generate_api(subject, topic, difficulty, jenjang, jurusan)
        else:
            return self._generate_mock(subject, topic, difficulty, jenjang, jurusan)

    # ============================================================
    # Mode: API — HuggingFace Inference (Qwen)
    # ============================================================

    def _generate_api(self, subject, topic, difficulty, jenjang, jurusan):
        """Generate menggunakan HuggingFace Inference API + Qwen."""
        try:
            messages = build_generation_prompt(subject, topic, difficulty, jenjang, jurusan)

            # Tambahkan instruksi randomisasi agar soal selalu baru
            randomizer = random.choice([
                "Buatkan soal yang UNIK dan BERBEDA dari soal-soal sebelumnya.",
                "Ciptakan pertanyaan BARU yang belum pernah ditanyakan sebelumnya.",
                "Buat variasi soal yang KREATIF dan SEGAR tentang topik ini.",
                "Generate soal ORIGINAL yang menantang dengan konteks yang menarik.",
                "Buat soal BARU dengan angka-angka dan skenario yang berbeda dari biasanya.",
            ])

            # Inject randomizer ke user message
            if messages and messages[-1]["role"] == "user":
                messages[-1]["content"] += f"\n\n⚠️ PENTING: {randomizer} " \
                    f"Gunakan angka random: {random.randint(1,100)}, {random.randint(1,50)}, {random.randint(100,999)}. " \
                    f"Seed: {random.randint(10000,99999)}"

            response = self._hf_client.chat_completion(
                messages=messages,
                max_tokens=1024,
                temperature=0.85,
                top_p=0.9,
            )

            content = response.choices[0].message.content
            print(f"✅ Qwen generated content for {topic} ({difficulty})")

            result = self._parse_json_response(content, subject, topic, difficulty, jenjang, jurusan)

            if result:
                # Randomize jawaban position
                self._shuffle_answers(result)
                return result

            # Fallback ke mock jika parsing gagal
            print("⚠️ Qwen response parsing failed, using bank soal")
            return self._generate_mock(subject, topic, difficulty, jenjang, jurusan)

        except Exception as e:
            print(f"⚠️ API call failed: {e}")
            print("📌 Falling back to bank soal...")
            return self._generate_mock(subject, topic, difficulty, jenjang, jurusan)

    # ============================================================
    # Mode: LOCAL (Qwen via transformers)
    # ============================================================

    def _generate_local(self, subject, topic, difficulty, jenjang, jurusan):
        """Generate menggunakan model Qwen lokal."""
        messages = build_generation_prompt(subject, topic, difficulty, jenjang, jurusan)

        text = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

        generated_ids = self.model.generate(
            model_inputs.input_ids,
            max_new_tokens=1024,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
        )

        # Decode response
        generated_ids = [
            output_ids[len(input_ids):]
            for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]
        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

        return self._parse_json_response(response, subject, topic, difficulty, jenjang, jurusan)

    # ============================================================
    # JSON Response Parsing
    # ============================================================

    def _parse_json_response(self, response, subject, topic, difficulty, jenjang=None, jurusan=None):
        """Parse dan validasi JSON response dari LLM."""
        try:
            # Coba parse langsung
            result = json.loads(response)
        except json.JSONDecodeError:
            # Coba ekstrak JSON dari response (LLM kadang menambahkan teks di luar JSON)
            try:
                # Cari pattern ```json ... ``` dulu
                code_block = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
                if code_block:
                    result = json.loads(code_block.group(1))
                else:
                    # Cari { ... } terluar
                    json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
                    if json_match:
                        result = json.loads(json_match.group())
                    else:
                        print("⚠️ No JSON found in LLM response")
                        return None
            except json.JSONDecodeError:
                print("⚠️ JSON extraction failed from LLM response")
                return None

        # Validasi struktur output
        if not self._validate_output(result):
            print("⚠️ Invalid output structure from LLM")
            return None

        return result

    def _validate_output(self, result):
        """Validasi bahwa output memiliki struktur yang benar."""
        required_keys = ["narasi", "materi_inti", "kuis"]
        kuis_keys = ["pertanyaan", "pilihan", "jawaban_benar", "penjelasan"]

        for key in required_keys:
            if key not in result:
                return False

        for key in kuis_keys:
            if key not in result["kuis"]:
                return False

        # Check pilihan has exactly 5 options
        if len(result["kuis"]["pilihan"]) != 5:
            return False

        # Check jawaban_benar is in pilihan
        if result["kuis"]["jawaban_benar"] not in result["kuis"]["pilihan"]:
            return False

        return True

    def _shuffle_answers(self, result):
        """Acak posisi jawaban benar agar tidak selalu di posisi yang sama."""
        if "kuis" in result and "pilihan" in result["kuis"]:
            correct = result["kuis"]["jawaban_benar"]
            pilihan = result["kuis"]["pilihan"]
            random.shuffle(pilihan)
            # Pastikan jawaban benar masih ada
            if correct not in pilihan:
                pilihan[0] = correct
            result["kuis"]["pilihan"] = pilihan

    # ============================================================
    # Mode: MOCK (bank soal dari physics_content.py)
    # ============================================================

    def _generate_mock(self, subject, topic, difficulty="Easy", jenjang="SMA", jurusan=None):
        """Generate konten mock dari bank soal."""
        from data.physics_content import get_mock_content

        content = get_mock_content(subject, topic, difficulty)

        if content:
            return content

        # Fallback ke generic mock
        return self._generate_generic_mock(subject, topic, difficulty, jenjang)

    def _generate_generic_mock(self, subject, topic, difficulty, jenjang):
        """Generate konten mock generik ketika topik tidak ada di database."""
        themes = NARRATIVE_THEMES.get(subject, ["kehidupan sehari-hari"])
        theme = random.choice(themes)

        difficulty_labels = {
            "Easy": "dasar",
            "Medium": "menengah",
            "Hard": "lanjutan",
            "Expert": "tingkat tinggi"
        }
        diff_label = difficulty_labels.get(difficulty, "dasar")

        return {
            "narasi": f"Kamu sedang menjalani petualangan sebagai {theme}! "
                      f"Dalam perjalananmu, kamu menemukan konsep menarik tentang {topic} "
                      f"dalam mata pelajaran {subject}. "
                      f"Mari kita pelajari bersama melalui tantangan {diff_label} ini! "
                      f"Perhatikan baik-baik penjelasan berikut untuk menjawab kuis di akhir.",
            "materi_inti": topic,
            "kuis": {
                "pertanyaan": f"Pertanyaan tentang {topic} ({subject}, tingkat {diff_label}):",
                "pilihan": [
                    f"Jawaban A tentang {topic}",
                    f"Jawaban B tentang {topic}",
                    f"Jawaban C tentang {topic} (benar)",
                    f"Jawaban D tentang {topic}",
                    f"Jawaban E tentang {topic}"
                ],
                "jawaban_benar": f"Jawaban C tentang {topic} (benar)",
                "penjelasan": f"Penjelasan detail tentang konsep {topic} dalam {subject}. "
                             f"Ini adalah konten placeholder — akan di-generate oleh LLM saat mode local/api aktif."
            }
        }


# ============================================================
# Singleton Pipeline Instance
# ============================================================

_pipeline_instance = None


def get_pipeline(mode=None):
    """
    Get atau create pipeline singleton.

    Mode diambil dari environment variable PIPELINE_MODE.
    Default: 'api' (menggunakan Qwen via HuggingFace Inference API)
    """
    global _pipeline_instance

    if mode is None:
        mode = os.environ.get("PIPELINE_MODE", "api")

    if _pipeline_instance is None or _pipeline_instance.mode != mode:
        _pipeline_instance = GameContentPipeline(mode=mode)

    return _pipeline_instance
