"""
Pipeline Package - LLM Content Generation
Game Edukasi Sekolah Rakyat (Tim 4) — Game2

Modules:
- prompt_templates: Template prompt untuk generate konten Fisika
- llm_pipeline: GameContentPipeline (mock / local / api)
"""

from pipeline.llm_pipeline import get_pipeline, GameContentPipeline
from pipeline.prompt_templates import build_generation_prompt

__all__ = ['get_pipeline', 'GameContentPipeline', 'build_generation_prompt']
