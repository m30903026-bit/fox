"""Тесты разбивки сценария и группировки сцен."""
from __future__ import annotations

from fox2.core.script import chunk_sentences, parse_group_spec, split_sentences


def test_split_sentences_basic_ru() -> None:
    text = "Существует загадка. Почему одни люди спокойны? Другие — нет."
    out = split_sentences(text)
    assert out == [
        "Существует загадка.",
        "Почему одни люди спокойны?",
        "Другие — нет.",
    ]


def test_split_sentences_empty() -> None:
    assert split_sentences("") == []
    assert split_sentences("   ") == []


def test_chunk_sentences() -> None:
    sentences = ["Один.", "Два.", "Три.", "Четыре.", "Пять."]
    assert chunk_sentences(sentences, 2) == ["Один. Два.", "Три. Четыре.", "Пять."]
    assert chunk_sentences(sentences, 1) == sentences
    assert chunk_sentences(sentences, 0) == sentences  # за <1 берём 1


def test_parse_group_spec() -> None:
    assert parse_group_spec("", 3) == [[0], [1], [2]]
    assert parse_group_spec("1,3,3", 7) == [[0], [1, 2, 3], [4, 5, 6]]
    # Если суммарно меньше — добиваем последнюю группу
    assert parse_group_spec("2,2", 6) == [[0, 1], [2, 3, 4, 5]]
    # Невалид -> по умолчанию
    assert parse_group_spec("abc", 2) == [[0], [1]]
