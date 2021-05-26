import os

VALIDATE_EMAIL_DOMAINS = True if os.environ.get("VALIDATE_EMAIL_DOMAINS",
                                                0) == "1" else False
SECRET = os.environ.get("SECRET")
PREFIX_LIST = ["080", "090", "070", "081", "071", "091"]