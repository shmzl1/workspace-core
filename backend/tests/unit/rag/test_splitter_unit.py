import pytest

from app.rag.ingestion.contracts import LoadedKnowledgeDocument
from app.rag.ingestion.splitter import StructuredKnowledgeSplitter
from app.rag.schemas import PolicyDocumentMetadata


def document(content: str) -> LoadedKnowledgeDocument:
    return LoadedKnowledgeDocument(
        metadata=PolicyDocumentMetadata(
            source_id="policy-001",
            title="招聘制度",
            document_type="POLICY",
            version="v1",
        ),
        content=content,
        attributes={"language": "zh-CN"},
    )


@pytest.mark.exception_path
@pytest.mark.parametrize(
    ("chunk_size", "chunk_overlap"),
    [(0, 0), (-1, 0), (10, -1), (10, 10), (10, 11)],
)
def test_invalid_splitter_configuration_is_rejected(chunk_size: int, chunk_overlap: int) -> None:
    with pytest.raises(ValueError, match="无效的知识分块配置"):
        StructuredKnowledgeSplitter(chunk_size, chunk_overlap)


@pytest.mark.exception_path
def test_empty_document_produces_no_chunks() -> None:
    assert StructuredKnowledgeSplitter(20, 5).split(document(" \r\n\t ")) == []


def test_line_endings_produce_stable_chunk_ids_and_text() -> None:
    splitter = StructuredKnowledgeSplitter(100, 10)
    crlf = splitter.split(document("# 标题\r\n\r\n第一段\r\n第二行"))
    lf = splitter.split(document("# 标题\n\n第一段\n第二行"))
    assert [chunk.chunk_id for chunk in crlf] == [chunk.chunk_id for chunk in lf]
    assert [chunk.text for chunk in crlf] == [chunk.text for chunk in lf]


def test_paragraphs_are_packed_and_overlap_is_preserved() -> None:
    splitter = StructuredKnowledgeSplitter(12, 4)
    chunks = splitter.split(document("第一段内容\n\n第二段内容\n\n第三段"))
    assert chunks
    assert all(0 < len(chunk.text) <= 12 for chunk in chunks)
    assert [chunk.ordinal for chunk in chunks] == list(range(len(chunks)))
    assert all(chunk.attributes == {"language": "zh-CN"} for chunk in chunks)
    assert chunks[1].text.startswith(chunks[0].text[-4:])


def test_oversized_piece_uses_deterministic_windows() -> None:
    splitter = StructuredKnowledgeSplitter(10, 3)
    chunks = splitter.split(document("abcdefghijklmnopqrstuvwxyz"))
    assert [chunk.text for chunk in chunks] == ["abcdefghij", "hijklmnopq", "opqrstuvwx", "vwxyz"]
    assert all(chunk.chunk_id.endswith(f":{index}") for index, chunk in enumerate(chunks))


def test_short_piece_is_flushed_before_oversized_piece() -> None:
    splitter = StructuredKnowledgeSplitter(10, 2)
    chunks = splitter.split(document("short\n\nabcdefghijklmnopqrstuvwxyz"))
    assert chunks[0].text == "short"
    assert chunks[1].text == "abcdefghij"



def test_heading_without_blank_line_starts_a_new_piece() -> None:
    pieces = StructuredKnowledgeSplitter._paragraph_pieces("正文\n# 新标题\n内容")
    assert pieces == ["正文", "# 新标题\n内容"]


def test_consecutive_headings_preserve_unicode_source_and_attributes() -> None:
    splitter = StructuredKnowledgeSplitter(20, 2)
    chunks = splitter.split(document("# 招聘\n## 面试\n### 录用\n候选人必须人工复核。"))
    repeated = splitter.split(document("# 招聘\n## 面试\n### 录用\n候选人必须人工复核。"))

    assert [chunk.chunk_id for chunk in chunks] == [chunk.chunk_id for chunk in repeated]
    assert all("招聘" in chunk.text or "候选人" in chunk.text for chunk in chunks)
    assert all(chunk.source.source_id == "policy-001" for chunk in chunks)
    assert all(chunk.attributes == {"language": "zh-CN"} for chunk in chunks)
