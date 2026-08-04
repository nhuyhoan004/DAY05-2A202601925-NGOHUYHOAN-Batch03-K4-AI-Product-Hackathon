import os
from dotenv import load_dotenv

load_dotenv()

# Cấu hình Discord
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_GUILD_ID = os.getenv("DISCORD_GUILD_ID")

# Cấu hình OpenAI / LLM
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

# Embedding được gọi qua API OpenRouter để worker không tải model vào RAM.
# OPENROUTER_API_KEY được ưu tiên; OPENAI_API_KEY vẫn tương thích cấu hình cũ.
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY") or OPENAI_API_KEY
EMBEDDING_BASE_URL = os.getenv(
    "EMBEDDING_BASE_URL", "https://openrouter.ai/api/v1"
)
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL", "openai/text-embedding-3-small"
)
try:
    EMBEDDING_DIMENSIONS = int(os.getenv("EMBEDDING_DIMENSIONS", "1024"))
except ValueError:
    EMBEDDING_DIMENSIONS = 1024

try:
    EMBEDDING_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "32"))
except ValueError:
    EMBEDDING_BATCH_SIZE = 32

# Cấu hình RAG
try:
    TOP_K = int(os.getenv("TOP_K", "5"))
except ValueError:
    TOP_K = 5
