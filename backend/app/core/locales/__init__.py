"""응답 문구 로더. 사용자에게 보이는 문장은 모두 여기를 거친다."""
import json
from functools import lru_cache
from pathlib import Path

DEFAULT_LOCALE = "ko"


@lru_cache
def _messages(locale: str = DEFAULT_LOCALE) -> dict[str, str]:
    path = Path(__file__).parent / f"{locale}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def translate(code: str, locale: str = DEFAULT_LOCALE, **params: object) -> str:
    """코드에 해당하는 문구를 돌려준다. 없으면 코드를 그대로 쓴다."""
    template = _messages(locale).get(code, code)
    try:
        return template.format(**params)
    except (KeyError, IndexError):
        return template
