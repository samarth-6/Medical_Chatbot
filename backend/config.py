from dotenv import load_dotenv
import os

load_dotenv()

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)
SERPER_API_KEY = os.getenv("SERPER_API_KEY") 


TRUSTED_DOMAINS = [
    "mayoclinic.org",
    "webmd.com",
    "healthline.com",
    "medlineplus.gov",
    "nih.gov",
    "who.int",
    "cdc.gov",
    "clevelandclinic.org",
    "hopkinsmedicine.org",
    "pubmed.ncbi.nlm.nih.gov"
]


UPLOAD_DIR = "./backend/uploads"

MAX_SEARCH_RESULTS = 5

MAX_CONTEXT_CHARS = 5000

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

DEFAULT_TOP_K = 5

CHUNK_SIZE = 800

CHUNK_OVERLAP = 150

GEMINI_MODEL = "models/gemini-2.5-flash"