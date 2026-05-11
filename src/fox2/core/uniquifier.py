"""Уникализатор текста: переписывает сценарий, сохраняя смысл."""
from __future__ import annotations

import logging
import random
import re

from ..providers.base import LLMProvider, ProviderError

log = logging.getLogger("fox2.uniquifier")

# Минимальный словарь синонимов для оффлайн-уникализатора. Не предмет гордости —
# но это работающий минимум, когда LLM не подключён.
_SYNONYMS: dict[str, list[str]] = {
    "очень": ["крайне", "весьма", "невероятно"],
    "большой": ["крупный", "огромный", "масштабный"],
    "маленький": ["небольшой", "крошечный", "миниатюрный"],
    "быстро": ["стремительно", "оперативно", "молниеносно"],
    "медленно": ["неторопливо", "плавно", "размеренно"],
    "хороший": ["удачный", "достойный", "качественный"],
    "плохой": ["неудачный", "слабый", "посредственный"],
    "красивый": ["живописный", "привлекательный", "эффектный"],
    "сильный": ["мощный", "крепкий", "энергичный"],
    "слабый": ["уязвимый", "хрупкий", "вялый"],
    "идти": ["шагать", "двигаться", "следовать"],
    "видеть": ["наблюдать", "замечать", "обнаруживать"],
    "говорить": ["произносить", "сообщать", "проговаривать"],
    "думать": ["размышлять", "обдумывать", "полагать"],
    "человек": ["личность", "индивид", "персона"],
}


def uniquify_local(text: str, *, seed: int | None = None) -> str:
    """Грубый словарный шафл синонимов. Сохраняет регистр первого символа слова."""
    rng = random.Random(seed)
    text = text or ""

    def replace(match: re.Match[str]) -> str:
        word = match.group(0)
        lower = word.lower()
        if lower in _SYNONYMS and rng.random() < 0.6:
            choice = rng.choice(_SYNONYMS[lower])
            if word[0].isupper():
                choice = choice[0].upper() + choice[1:]
            return choice
        return word

    return re.sub(r"[А-Яа-яЁё]+", replace, text)


SYSTEM_PROMPT_RU = (
    "Ты — редактор-копирайтер. Получаешь текст на русском и переписываешь "
    "его другими словами, сохраняя смысл, длину и структуру предложений. "
    "Возвращай только переписанный текст, без вступлений и комментариев."
)


def uniquify_with_llm(llm: LLMProvider, text: str) -> str:
    if not text.strip():
        return text
    try:
        out = llm.complete(text, system=SYSTEM_PROMPT_RU, max_tokens=4096)
    except ProviderError as exc:
        log.warning("LLM не справился, fallback на локальный уникализатор: %s", exc)
        return uniquify_local(text)
    out = out.strip()
    return out or uniquify_local(text)
