from pathlib import Path

from docx import Document


class DocxLoader:
    async def load(self, path: Path) -> tuple[str, dict]:
        document = Document(str(path))
        paragraphs = [paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()]
        text = "\n\n".join(paragraphs)
        return text, {
            "source_type": "docx",
            "paragraph_count": len(paragraphs),
            "filename": path.name,
        }

