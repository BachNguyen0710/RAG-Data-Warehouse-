from pathlib import Path

ALLOWED_EXTENSIONS = {".txt", ".pdf", ".docx", ".html", ".json", ".xml", ".csv"}

def parse_file (file_path = Path) -> str:
    ext = file_path.suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}")
    
    if ext == ".pdf":
        return parse_pdf(file_path)
    
    if ext == ".docx":
        return parse_docx(file_path)
    
    if ext == ".html":
        return parse_html(file_path)
    
    if ext == ".json":
        return parse_json(file_path)
    
    else:
        return file_path.read_text(encoding="utf-8")  # .xml .csv .txt
    
def parse_pdf(path = Path) -> str:
    import fitz
    doc = fitz.open(str(path))
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text.strip()

def parse_docx(path = Path) -> str:
    from docx import Document  # pip install python-docx
    doc = Document(str(path))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)

def parse_html(path: Path) -> str:
    from bs4 import BeautifulSoup  
    html = path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    # Xóa script, style, nav — chỉ giữ nội dung chính
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    return soup.get_text(separator="\n", strip=True)


def parse_json(path: Path) -> str:
    import json
    data = json.loads(path.read_text(encoding="utf-8"))
    # Chuyển JSON thành text dạng key: value để AI dễ đọc
    return _flatten_json(data)

def _flatten_json(data, prefix="") -> str:
    """Đệ quy flatten JSON lồng nhau thành dạng text."""
    lines = []
    if isinstance(data, dict):
        for k, v in data.items():
            key = f"{prefix}.{k}" if prefix else k
            lines.append(_flatten_json(v, key))
    elif isinstance(data, list):
        for i, item in enumerate(data):
            lines.append(_flatten_json(item, f"{prefix}[{i}]"))
    else:
        lines.append(f"{prefix}: {data}")
    return "\n".join(lines)