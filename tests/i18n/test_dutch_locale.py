"""Dutch UI locale integration tests.

Mirrors ``test_polish_locale.py``: each assertion pins one seam that decides
whether Dutch is selectable and actually served, so dropping it from any of
them fails here instead of silently serving English.
"""

from __future__ import annotations

import json
import pathlib
import re

import pytest

from deeptutor.api.routers.quiz_judge import (
    _JUDGE_SYSTEM_PROMPTS,
    SUPPORTED_JUDGE_LANGUAGES,
)
from deeptutor.core.response_languages import SUPPORTED_RESPONSE_LANGUAGES
from deeptutor.runtime.banner import LABELS, labels_for
from deeptutor.services.config.launch_settings import (
    _normalize_language as _launch_language,
)
from deeptutor.services.config.settings_spec import (
    _LANGUAGE_CHOICES,
    _RESPONSE_LANGUAGE_CHOICES,
)
from deeptutor.services.prompt.language import language_directive, language_label
from deeptutor.services.settings.interface_settings import (
    _normalize_language,
    _normalize_response_language,
)

WEB = pathlib.Path(__file__).resolve().parents[2] / "web"


def _catalog(locale: str) -> dict[str, str]:
    return json.loads((WEB / f"locales/{locale}/app.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    "raw",
    ["nl", "NL", " nl ", "dutch", "Nederlands", "nl-NL", "nl_BE"],
)
def test_normalizer_accepts_dutch_spellings(raw: str) -> None:
    assert _normalize_language(raw) == "nl"


def test_launch_settings_accept_dutch() -> None:
    assert _launch_language("nl-NL") == "nl"
    assert _launch_language("dutch") == "nl"
    assert _launch_language("nederlands") == "nl"


def test_settings_offers_dutch() -> None:
    assert "nl" in {code for code, _label, _desc in _LANGUAGE_CHOICES}


def test_cli_banner_is_fully_translated() -> None:
    assert set(LABELS["nl"]) == set(LABELS["en"])
    assert labels_for("nl-NL") is LABELS["nl"]


def test_judge_speaks_dutch() -> None:
    assert SUPPORTED_JUDGE_LANGUAGES == frozenset(_JUDGE_SYSTEM_PROMPTS)
    assert "nl" in SUPPORTED_JUDGE_LANGUAGES
    assert "Nederlands" in _JUDGE_SYSTEM_PROMPTS["nl"]


def test_web_locale_covers_every_english_key() -> None:
    en = _catalog("en")
    nl = _catalog("nl")

    assert set(en) <= set(nl)


def test_web_locale_keeps_interpolation_placeholders() -> None:
    en = _catalog("en")
    nl = _catalog("nl")

    pattern = re.compile(r"\{\{[^}]+\}\}")

    mismatches = [
        key
        for key in set(en) & set(nl)
        if set(pattern.findall(en[key])) != set(pattern.findall(nl[key]))
    ]

    assert mismatches == []


def test_every_locale_can_name_dutch() -> None:
    for locale in ("en", "zh", "fr", "de", "uk", "pl", "nl"):
        assert "language.dutch" in _catalog(locale)


def test_frontend_registers_dutch() -> None:
    languages = (WEB / "i18n/languages.ts").read_text(encoding="utf-8")
    assert '{ code: "nl", labelKey: "language.dutch" }' in languages

    init = (WEB / "i18n/init.ts").read_text(encoding="utf-8")
    assert "@/locales/nl/app.json" in init


@pytest.mark.parametrize("raw", ["nl", "NL", "nl-NL", "dutch", "Nederlands"])
def test_reply_language_accepts_dutch(raw: str) -> None:
    assert _normalize_response_language(raw) == "nl"


def test_reply_language_list_offers_dutch() -> None:
    assert "nl" in SUPPORTED_RESPONSE_LANGUAGES
    assert "nl" in {code for code, _label, _desc in _RESPONSE_LANGUAGE_CHOICES}


def test_reply_directive_names_dutch() -> None:
    assert language_label("nl") == "Nederlands"
    assert "Nederlands" in language_directive("nl")
