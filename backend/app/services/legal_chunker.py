import re
from dataclasses import dataclass


@dataclass(frozen=True)
class LegalChunkCandidate:
    article_or_point: str | None
    section_title: str | None
    chunk_index: int
    chunk_text: str
    metadata_json: dict


STRUCTURE_PATTERN = re.compile(
    r"(?im)^\s*((?:Статья|Модда)\s+\d+[.\d-]*|(?:Пункт|пункт)\s+\d+[.\d-]*|(?:Подпункт|подпункт)\s+[а-яa-z]\)|(?:Приложение|илова)\s+\d+)",
)


class LegalChunker:
    def chunk(self, text: str, max_chars: int = 1600) -> list[LegalChunkCandidate]:
        normalized = text.replace("\r\n", "\n").replace("\r", "\n").strip()
        if not normalized:
            return []
        structured = self._structured_chunks(normalized, max_chars)
        if structured:
            return structured
        return self._fallback_chunks(normalized, max_chars)

    def _structured_chunks(self, text: str, max_chars: int) -> list[LegalChunkCandidate]:
        matches = list(STRUCTURE_PATTERN.finditer(text))
        if not matches:
            return []
        chunks: list[LegalChunkCandidate] = []
        for index, match in enumerate(matches):
            start = match.start()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            label = _clean(match.group(1))
            chunk_text = text[start:end].strip()
            for part in _split_long_text(chunk_text, max_chars):
                chunks.append(
                    LegalChunkCandidate(
                        article_or_point=label,
                        section_title=_first_line(part),
                        chunk_index=len(chunks),
                        chunk_text=part,
                        metadata_json={"chunking": "structured"},
                    )
                )
        return chunks

    def _fallback_chunks(self, text: str, max_chars: int) -> list[LegalChunkCandidate]:
        chunks: list[LegalChunkCandidate] = []
        paragraphs = [paragraph.strip() for paragraph in re.split(r"\n\s*\n", text) if paragraph.strip()]
        buffer = ""
        for paragraph in paragraphs:
            if buffer and len(buffer) + len(paragraph) + 2 > max_chars:
                chunks.append(_fallback_candidate(len(chunks), buffer))
                buffer = paragraph
            else:
                buffer = f"{buffer}\n\n{paragraph}".strip()
        if buffer:
            chunks.append(_fallback_candidate(len(chunks), buffer))
        if not chunks:
            for part in _split_long_text(text, max_chars):
                chunks.append(_fallback_candidate(len(chunks), part))
        return chunks


def _fallback_candidate(index: int, text: str) -> LegalChunkCandidate:
    return LegalChunkCandidate(
        article_or_point="unknown",
        section_title=_first_line(text),
        chunk_index=index,
        chunk_text=text,
        metadata_json={"chunking": "fallback"},
    )


def _split_long_text(text: str, max_chars: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    parts: list[str] = []
    current = ""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    for sentence in sentences:
        if current and len(current) + len(sentence) + 1 > max_chars:
            parts.append(current.strip())
            current = sentence
        else:
            current = f"{current} {sentence}".strip()
    if current:
        parts.append(current.strip())
    return parts


def _first_line(text: str) -> str | None:
    first = text.strip().splitlines()[0].strip()
    return first[:500] if first else None


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).rstrip(".")


legal_chunker = LegalChunker()
