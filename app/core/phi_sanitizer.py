import re

class PHISanitizer:
    def __init__(self):
        # Programmatic compiled regex rules matching critical PHI patterns
        self.patterns = {
            "SSN": re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
            "PHONE": re.compile(r'\b(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]?\d{3}[-. ]?\d{4}\b'),
            "EMAIL": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            "MRN": re.compile(r'\bMRN\s*[:#-]?\s*\d{6,10}\b', re.IGNORECASE),
            "DATE_OF_BIRTH": re.compile(r'\b(DOB|Date of Birth)\s*[:#-]?\s*\d{2}[-/]\d{2}[-/]\d{4}\b', re.IGNORECASE)
        }

    def redact(self, text: str) -> str:
        """Scan text and replace identified PHI targets with standardized secure tags."""
        sanitized_text = text
        for phi_type, regex in self.patterns.items():
            sanitized_text = regex.sub(f"[{phi_type}_REDACTED]", sanitized_text)
        return sanitized_text

phi_sanitizer = PHISanitizer()
