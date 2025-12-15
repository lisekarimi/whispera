"""Environment file management utilities."""

import os
from .config import get_application_path


def read_env_file():
    """Read .env file and return as dictionary."""
    env_path = os.path.join(get_application_path(), '.env')
    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    return env_vars


def write_env_file(env_vars):
    """Write dictionary to .env file."""
    env_path = os.path.join(get_application_path(), '.env')
    with open(env_path, 'w') as f:
        if 'OPENAI_API_KEY' in env_vars:
            f.write(f"OPENAI_API_KEY={env_vars['OPENAI_API_KEY']}\n")
        # FFMPEG_PATH is no longer used - app always uses default ffmpeg/ folder location
