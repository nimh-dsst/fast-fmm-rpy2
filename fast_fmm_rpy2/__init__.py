# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    import os

    # Only load if R_HOME isn't already set
    if not os.getenv("R_HOME"):
        load_dotenv()
except ImportError:
    # python-dotenv not installed, skip loading .env
    pass

from .fmm_run import fui, get_fastfmm_version, check_fastfmm_version

__all__ = ["fui", "get_fastfmm_version", "check_fastfmm_version"]
