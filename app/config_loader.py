import os
import importlib

def _try_import(module_name: str):
    """
    Try to import a module by name. Return the module if found, otherwise None.
    We catch ModuleNotFoundError (not ImportError) to avoid hiding other import errors.
    """
    try:
        return importlib.import_module(module_name)
    except ModuleNotFoundError:
        return None

# FIX: Only try to import from top-level config.* since config files are in ./config/
_dev_module = _try_import("config.development")
_prod_module = _try_import("config.production")

# Extract class references if present; otherwise None.
DevelopmentConfig = getattr(_dev_module, "DevelopmentConfig", None) if _dev_module else None
ProductionConfig = getattr(_prod_module, "ProductionConfig", None) if _prod_module else None


class ConfigLoader:
    """
    Unified configuration entry point for the application.

    Behavior:
      - Uses DevelopmentConfig (YAML) when APP_ENV=development (default)
      - Uses ProductionConfig (AWS Secrets Manager) when APP_ENV=production
      - Exposes a .get(key, default, cast) API for retrieving config attributes
      - Exposes .validate(required_keys) to ensure required attributes exist

    This loader will raise an ImportError at initialization if neither
    development nor production config classes can be found for the selected env.
    """

    def __init__(self):
        self.env = os.getenv("APP_ENV", "development").lower()

        # Select and instantiate the appropriate config class
        if self.env == "production":
            print("Using Production configuration (AWS Secrets Manager)")
            if ProductionConfig:
                self.config = ProductionConfig()
                self._source = getattr(_prod_module, "__name__", "config.production")
            else:
                attempted = ["config.production"]
                raise ImportError(
                    f"ProductionConfig not found. Attempted imports: {attempted}. "
                    "Ensure production config module exists or set APP_ENV=development for local testing."
                )
        else:
            print("Using Development configuration (YAML file)")
            if DevelopmentConfig:
                self.config = DevelopmentConfig()
                self._source = getattr(_dev_module, "__name__", "config.development")
            else:
                attempted = ["config.development"]
                raise ImportError(
                    f"DevelopmentConfig not found. Attempted imports: {attempted}. "
                    "Ensure development config module exists at config/development.py."
                )

    def get(self, key, default=None, cast=None):
        """
        Retrieve a config attribute from the active config object.

        :param key: attribute name on the chosen config object
        :param default: fallback value if attribute doesn't exist
        :param cast: optional callable to cast/convert the retrieved value
        """
        value = getattr(self.config, key, default)
        if cast and value is not None:
            try:
                value = cast(value)
            except Exception:
                # If cast fails, leave the original value unchanged
                pass
        return value

    def validate(self, required_keys=None):
        """
        Ensure required configuration keys are present and not falsy.
        Raises ValueError listing missing keys if any are absent.
        """
        required_keys = required_keys or ["SECRET_KEY", "DATABASE_PATH"]
        missing = [k for k in required_keys if not getattr(self.config, k, None)]
        if missing:
            raise ValueError(f"Missing required config keys: {', '.join(missing)}")
        print("All required configuration keys are present")
        return True

    def source_info(self):
        """
        Optional helper to return which module provided the configuration.
        Useful for debugging.
        """
        return getattr(self, "_source", None)