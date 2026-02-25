import re

# Define common legal keywords
LEGAL_TERMS = [
    "agreement", "liability", "party", "contract", "confidentiality",
    "clause", "terms", "conditions", "warranty", "obligation",
    "jurisdiction", "rights", "intellectual property", "indemnity",
    "termination", "disclosure", "privacy", "policy", "security",
    "law", "dispute", "governing", "breach", "notice", "compliance"
]

def highlight_terms(text):
    """
    Finds all legal terms and wraps them with <mark> tags for frontend highlighting.
    """
    highlighted = text
    for term in LEGAL_TERMS:
        pattern = re.compile(rf"\b({term})\b", re.IGNORECASE)
        highlighted = pattern.sub(r"<mark>\1</mark>", highlighted)
    return highlighted
