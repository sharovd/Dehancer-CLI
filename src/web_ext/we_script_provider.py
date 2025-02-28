from pathlib import Path

from rjsmin import jsmin

from src.api.constants import ENCODING_UTF_8
from src.utils import is_file_exist


class WebExtensionScriptProvider:
    """Provides the content of the web extension script."""

    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    SCRIPTS_DIR = PROJECT_ROOT / "scripts" / "web-ext"
    ORIGINAL_SCRIPT = SCRIPTS_DIR / "get-settings-via-browser-console.js"
    OBFUSCATED_SCRIPT = SCRIPTS_DIR / "get-settings-via-browser-console-obfuscated.js"

    @classmethod
    def _is_original_script_exist(cls) -> bool:
        return is_file_exist(str(cls.ORIGINAL_SCRIPT))

    @classmethod
    def _is_obfuscated_script_exist(cls) -> bool:
        return is_file_exist(str(cls.OBFUSCATED_SCRIPT))

    @classmethod
    def _get_original_script_minified_data(cls) -> str:
        return jsmin(cls.ORIGINAL_SCRIPT.read_text(encoding=ENCODING_UTF_8))

    @classmethod
    def _get_obfuscated_script_data(cls) -> str:
        return cls.OBFUSCATED_SCRIPT.read_text(encoding=ENCODING_UTF_8)

    @classmethod
    def get_script_content(cls) -> str:
        """
        Return the content of the web extension script.

        If the obfuscated version exists, returns it without modifications.
        Otherwise, it returns the minified version of the original script.

        Raises:
            FileNotFoundError: If file with web extension script is found.

        Returns:
            str: The script content.

        """
        if cls._is_obfuscated_script_exist():
            return cls._get_obfuscated_script_data()

        if cls._is_original_script_exist():
            return cls._get_original_script_minified_data()

        err_msg = f"Script not found: {cls.ORIGINAL_SCRIPT}"
        raise FileNotFoundError(err_msg)
