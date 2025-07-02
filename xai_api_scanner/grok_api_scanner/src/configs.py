import re

KEYWORDS = [
    "grok",
    "xai",
    "grok api",
    "xai-grok",
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
    (re.compile(r"grok-[A-Za-z0-9]{32,}"), True, True),
    (re.compile(r"xai-grok-[A-Za-z0-9]{40,}"), True, True),
] 