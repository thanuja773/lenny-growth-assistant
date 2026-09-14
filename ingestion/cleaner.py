import re

def clean_text(text: str) -> str:
    # Remove excessive blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Strip leading/trailing whitespaces per line
    lines = [line.strip() for line in text.split('\n')]
    return '\n'.join(lines).strip()
