import re
from dataclasses import dataclass


TARGET_CHUNK_CHARS = 3500
HARD_MAX_CHUNK_CHARS = 9000


@dataclass(frozen=True)
class LegalChunkCandidate:
    article_or_point: str | None
    section_title: str | None
    chunk_index: int
    chunk_text: str
    metadata_json: dict


STRUCTURE_PATTERN = re.compile(
    "("
    r"(?P<article>(?:\u0421\u0442\u0430\u0442\u044c\u044f|\u041c\u043e\u0434\u0434\u0430)\s+\d+[.\d-]*)"
    "|"
    r"(?P<named_point>(?:\u041f\u0443\u043d\u043a\u0442|\u043f\u0443\u043d\u043a\u0442)\s+\d+[.\d-]*)"
    "|"
    r"(?P<named_subpoint>(?:\u041f\u043e\u0434\u043f\u0443\u043d\u043a\u0442|\u043f\u043e\u0434\u043f\u0443\u043d\u043a\u0442)\s+[\u0430-\u044fa-z]\))"
    "|"
    r"(?P<annex>(?:\u041f\u0420\u0418\u041b\u041e\u0416\u0415\u041d\u0418\u0415|\u041f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435|\u0418\u041b\u041e\u0412\u0410|\u0418\u043b\u043e\u0432\u0430|\u0438\u043b\u043e\u0432\u0430)(?:\s*(?:\u2116|N|No\.?)?\s*\d+)?)"
    "|"
    r"(?P<uzbek_annex>\d+-\s*(?:\u0438\u043b\u043e\u0432\u0430|\u0418\u041b\u041e\u0412\u0410|ilova))"
    "|"
    r"(?P<table_heading>\u041f\u0430\u0441\u043f\u043e\u0440\u0442|\u041f\u0435\u0440\u0435\u0447\u0435\u043d\u044c|\u0421\u0445\u0435\u043c\u0430|\u041f\u043e\u043b\u043e\u0436\u0435\u043d\u0438\u0435)"
    "|"
    r"(?P<nested_number>\d+\.\d+(?:\.\d+)*\.)"
    "|"
    r"(?P<numbered_point>\d+\.)"
    "|"
    r"(?P<letter_subpoint>[\u0430-\u044fa-z]\))"
    "|"
    r"(?P<uzbek_band>\d+-\s*(?:\u0431\u0430\u043d\u0434|\u0411\u0410\u041d\u0414|band)|(?:\u043a\u0438\u0447\u0438\u043a\s+)?\u0431\u0430\u043d\u0434|(?:kichik\s+)?band)"
    ")",
    re.IGNORECASE,
)


class LegalChunker:
    def chunk(
        self,
        text: str,
        max_chars: int = TARGET_CHUNK_CHARS,
        hard_max_chars: int = HARD_MAX_CHUNK_CHARS,
    ) -> list[LegalChunkCandidate]:
        normalized = text.replace("\r\n", "\n").replace("\r", "\n").strip()
        if not normalized:
            return []
        structured = self._structured_chunks(normalized, max_chars, hard_max_chars)
        if structured:
            return structured
        return self._fallback_chunks(normalized, max_chars, hard_max_chars)

    def _structured_chunks(self, text: str, max_chars: int, hard_max_chars: int) -> list[LegalChunkCandidate]:
        matches = list(_iter_structure_matches(text))
        if not matches:
            return []
        chunks: list[LegalChunkCandidate] = []
        for index, match in enumerate(matches):
            start = match.start()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            label = _label_for_match(match)
            chunk_text = text[start:end].strip()
            for part in _split_long_text(chunk_text, max_chars, hard_max_chars):
                chunks.append(
                    LegalChunkCandidate(
                        article_or_point=label,
                        section_title=_first_line(part),
                        chunk_index=len(chunks),
                        chunk_text=part,
                        metadata_json={"chunking": "structured", "pattern": _match_kind(match)},
                    )
                )
        return chunks

    def _fallback_chunks(self, text: str, max_chars: int, hard_max_chars: int) -> list[LegalChunkCandidate]:
        chunks: list[LegalChunkCandidate] = []
        paragraphs = [paragraph.strip() for paragraph in re.split(r"\n\s*\n", text) if paragraph.strip()]
        buffer = ""
        for paragraph in paragraphs:
            if len(paragraph) > hard_max_chars:
                if buffer:
                    chunks.extend(_fallback_parts(len(chunks), buffer, max_chars, hard_max_chars))
                    buffer = ""
                chunks.extend(_fallback_parts(len(chunks), paragraph, max_chars, hard_max_chars))
                continue
            if buffer and len(buffer) + len(paragraph) + 2 > max_chars:
                chunks.extend(_fallback_parts(len(chunks), buffer, max_chars, hard_max_chars))
                buffer = paragraph
            else:
                buffer = f"{buffer}\n\n{paragraph}".strip()
        if buffer:
            chunks.extend(_fallback_parts(len(chunks), buffer, max_chars, hard_max_chars))
        if not chunks:
            chunks.extend(_fallback_parts(len(chunks), text, max_chars, hard_max_chars))
        return chunks


class _OffsetMatch:
    def __init__(self, match: re.Match[str], start_offset: int) -> None:
        self.match = match
        self.start_offset = start_offset

    def start(self) -> int:
        return self.start_offset

    def group(self, *args):
        return self.match.group(*args)

    def groupdict(self) -> dict[str, str | None]:
        return self.match.groupdict()


def _iter_structure_matches(text: str):
    line_start = 0
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        if stripped:
            match = STRUCTURE_PATTERN.match(stripped)
            if match and not _is_false_heading(match, stripped):
                yield _OffsetMatch(match, line_start + line.index(stripped))
        line_start += len(line)


def _fallback_candidate(index: int, text: str, chunking: str = "fallback") -> LegalChunkCandidate:
    return LegalChunkCandidate(
        article_or_point="unknown",
        section_title=_first_line(text),
        chunk_index=index,
        chunk_text=text,
        metadata_json={"chunking": chunking},
    )


def _fallback_parts(start_index: int, text: str, max_chars: int, hard_max_chars: int) -> list[LegalChunkCandidate]:
    chunking = "fallback_size_split" if len(text) > hard_max_chars else "fallback"
    return [
        _fallback_candidate(start_index + offset, part, chunking)
        for offset, part in enumerate(_split_long_text(text, max_chars, hard_max_chars))
    ]


def _split_long_text(text: str, max_chars: int, hard_max_chars: int) -> list[str]:
    if len(text) <= hard_max_chars:
        return [text]
    parts: list[str] = []
    current = ""
    for sentence in _split_boundaries(text):
        if len(sentence) > hard_max_chars:
            if current:
                parts.append(current.strip())
                current = ""
            parts.extend(_split_by_size(sentence, max_chars, hard_max_chars))
            continue
        if current and len(current) + len(sentence) + 1 > max_chars:
            parts.append(current.strip())
            current = sentence
        else:
            current = f"{current} {sentence}".strip()
    if current:
        parts.append(current.strip())
    return [part for part in parts if part]


def _split_boundaries(text: str) -> list[str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) > 1:
        return lines
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", text) if part.strip()]


def _split_by_size(text: str, max_chars: int, hard_max_chars: int) -> list[str]:
    limit = min(max_chars, hard_max_chars)
    parts: list[str] = []
    cursor = 0
    while cursor < len(text):
        end = min(cursor + limit, len(text))
        if end < len(text):
            split_at = text.rfind(" ", cursor, end)
            if split_at <= cursor:
                split_at = end
            end = split_at
        part = text[cursor:end].strip()
        if part:
            parts.append(part)
        cursor = end
        while cursor < len(text) and text[cursor].isspace():
            cursor += 1
    return parts


def _match_kind(match: _OffsetMatch) -> str:
    for name, value in match.groupdict().items():
        if value:
            return name
    return "unknown"


def _is_false_heading(match: re.Match[str], line: str) -> bool:
    kind = _raw_match_kind(match)
    value = match.group(0)
    if kind == "nested_number" and _looks_like_date_prefix(value, line[match.end() :]):
        return True
    if kind == "numbered_point" and value.rstrip(".").isdigit() and int(value.rstrip(".")) > 100:
        return True
    return False


def _raw_match_kind(match: re.Match[str]) -> str:
    for name, value in match.groupdict().items():
        if value:
            return name
    return "unknown"


def _looks_like_date_prefix(value: str, remainder: str) -> bool:
    parts = [part for part in value.strip(".").split(".") if part]
    if len(parts) < 2 or not all(part.isdigit() for part in parts[:2]):
        return False
    day = int(parts[0])
    month = int(parts[1])
    return 1 <= day <= 31 and 1 <= month <= 12 and bool(re.match(r"\s*\d{2,4}\b", remainder))


def _label_for_match(match: _OffsetMatch) -> str:
    kind = _match_kind(match)
    value = _clean(match.group(0))
    if kind == "numbered_point":
        return f"Point {value.rstrip('.')}"
    if kind == "nested_number":
        return f"Subpoint {value.rstrip('.')}"
    if kind == "letter_subpoint":
        return f"Subpoint {value}"
    return value


def _first_line(text: str) -> str | None:
    first = text.strip().splitlines()[0].strip()
    return first[:500] if first else None


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).rstrip(".")


legal_chunker = LegalChunker()
