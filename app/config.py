import os
from dotenv import load_dotenv

load_dotenv()


def get_env_variable(name: str, required: bool = True, default=None):
    """Get the environment variable or return default value"""
    value = os.getenv(name, default)
    if required and (value is None or value == ""):
        raise ValueError(f"Environment variable {name} is required but not set.")
    return value


def get_list_env_var(name: str, required=True, default=None, separator=","):
    raw = get_env_variable(name, required=required, default=default)
    return [item.strip() for item in raw.split(separator) if item.strip()]


TEMP_BASE_DIR = get_env_variable("TEMP_BASE_DIR")
ALLOWED_MEDIA_ORIGINS_LIST = get_list_env_var("ALLOWED_MEDIA_ORIGINS_LIST", default="instagram,tiktok")
FFMPEG_PATH = get_env_variable("FFMPEG_PATH", default="/usr/bin/ffmpeg")
VOSK_MODEL_DIR = get_env_variable("VOSK_MODEL_DIR")
AI_PROMPT_DIR = get_env_variable("AI_PROMPT_DIR")
OPENAI_API_KEY = get_env_variable("OPENAI_API_KEY")
AI_MODEL = get_env_variable("AI_MODEL", default="gpt-4o-mini")
AI_TEMPERATURE = get_env_variable("AI_TEMPERATURE", default=0.2)
AI_MAX_TOKENS = get_env_variable("AI_MAX_TOKENS", default=4096)
MEALIER_URL = get_env_variable("MEALIER_URL")
MEALIER_API_KEY = get_env_variable("MEALIER_API_KEY")
INPUT_TOKENS_PRICE_PER_MILLION = get_env_variable("INPUT_TOKENS_PRICE_PER_MILLION", default=0)
OUTPUT_TOKENS_PRICE_PER_MILLION = get_env_variable("OUTPUT_TOKENS_PRICE_PER_MILLION", default=0)
MEALIER_DEFAULT_CATEGORIES_ID = get_list_env_var("MEALIER_DEFAULT_CATEGORIES_ID", default="")
AI_INPUT_IMAGES = get_env_variable("AI_INPUT_IMAGES", default=4)
PYKTOK_BROWSER = get_env_variable("PYKTOK_BROWSER", default="firefox")
AI_CONFIDENCE_THRESHOLD = get_env_variable("AI_CONFIDENCE_THRESHOLD", default=8)

TELEGRAM_BOT_TOKEN = get_env_variable("TELEGRAM_BOT_TOKEN")
TELEGRAM_MASTER_ID = get_env_variable("TELEGRAM_MASTER_ID", default=0)
TELEGRAM_WHITE_LIST = get_list_env_var("TELEGRAM_WHITE_LIST", required=False, default="")
TELEGRAM_BLACK_LIST = get_list_env_var("TELEGRAM_BLACK_LIST", required=False, default="")
