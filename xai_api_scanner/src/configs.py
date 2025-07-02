"""
Author: Kislay
GitHub: https://github.com/iKislay
LinkedIn: https://www.linkedin.com/in/kislayy/

Configuration settings for XAI API Scanner.
"""

import re

KEYWORDS = [
    "xai",
    "xai api",
    "xai-px",
    "api key",
    "apikey",
]

LANGUAGES = [
    "Dotenv",
    "Text",
    "JavaScript",
    "Python",
    "TypeScript",
    "Dockerfile",
    "Markdown",
    '"Jupyter Notebook"',
    "Shell",
    "Java",
    "Go",
    "C%2B%2B",
    "PHP",
]

PATHS = [
    "path:.xml OR path:.json OR path:.properties OR path:.sql OR path:.txt OR path:.log OR path:.tmp OR path:.backup OR path:.bak OR path:.enc",
    "path:.yml OR path:.yaml OR path:.toml OR path:.ini OR path:.config OR path:.conf OR path:.cfg OR path:.env OR path:.envrc OR path:.prod",
    "path:.secret OR path:.private OR path:*.key",
]

REGEX_LIST = [
    # XAI API Key: starts with xai- and followed by 80+ alphanumeric chars
    # Example: xai-pxtCxJayc5KrhpteLehVCTP7KN2l60cJ18QjYCK6qMKoxFqzcHMXIICKK8fcYuxfMPoudP4X1tMONcG9
    (re.compile(r"xai-[A-Za-z0-9]{80,}"), True, True),
] 