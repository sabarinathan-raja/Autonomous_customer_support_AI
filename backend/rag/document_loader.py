
import json
from pathlib import Path
from pypdf import PdfReader


class DocumentLoader:

    def __init__(self, data_path="data/policies"):
        self.data_path = Path(data_path)

    def load_documents(self):

        documents = []

        if not self.data_path.exists():
            return documents

        for file_path in self.data_path.rglob("*"):

            if not file_path.is_file():
                continue

            suffix = file_path.suffix.lower()

            if suffix == ".txt":
                text = file_path.read_text(encoding="utf-8")

            elif suffix == ".pdf":
                reader = PdfReader(str(file_path))
                text = "\n".join(
                    page.extract_text() or ""
                    for page in reader.pages
                )

            elif suffix == ".json":
                data = json.loads(
                    file_path.read_text(encoding="utf-8")
                )
                text = json.dumps(data, ensure_ascii=False, indent=2)

            else:
                continue

            if text.strip():
                documents.append({
                    "source": str(file_path),
                    "text": text
                })

        return documents
