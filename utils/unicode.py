import unicodedata
import re

def normalize_text(text: str) -> str:
    """
    Normalizes unicode text to NFC form to avoid macOS/Linux discrepancies 
    where characters like 'é' could be composed of multiple codepoints.
    """
    return unicodedata.normalize('NFC', text)

def sanitize_filename(filename: str) -> str:
    """
    Removes illegal characters from filenames across OSes.
    """
    # Windows reserved characters: < > : " / \ | ? *
    illegal_chars = r'[<>:"/\\|?*]'
    clean = re.sub(illegal_chars, '_', filename)
    
    # Trim leading/trailing spaces and dots
    clean = clean.strip(' .')
    if not clean:
        return "unnamed_file"
    
    return clean

def check_mac_restrictions(filename: str) -> str:
    # macOS mostly just forbids ':'
    return filename.replace(':', '_')
