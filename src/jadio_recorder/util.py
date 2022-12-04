import re


def fix_to_path(x: str) -> str:
    return re.sub(r'[\\|/|:|?|.|"|<|>|\|]', "_", x)
