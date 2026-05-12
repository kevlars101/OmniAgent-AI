from pathlib import Path

from pypdf import PdfReader


class PdfLoader:
    async def load(self, path: Path) -> tuple[str, dict]:
        reader = PdfReader(str(path))
        pages: list[str] = []
        for page in reader.pages:
            pages.append(page.extract_text() or "")

        text = "\n\n".join(page.strip() for page in pages if page.strip())
        return text, {
            "source_type": "pdf",
            "page_count": len(reader.pages),
            "filename": path.name,
        }

