import os
import yaml


class DevelopmentConfig:
    """Development configuration (loads from config/config.yaml if available)."""

    def __init__(self):
        # Locate YAML file (relative to project root)
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config"))
        default_yaml_path = os.path.join(base_dir, "config.yaml")

        # Allow override from environment variable
        yaml_path = os.getenv("CONFIG_PATH", default_yaml_path)

        if not os.path.exists(yaml_path):
            print(f"Warning: YAML config file not found: {yaml_path}")
            print("Using default configuration...")
            self.config = {}
        else:
            try:
                with open(yaml_path, "r", encoding="utf-8") as file:
                    self.config = yaml.safe_load(file) or {}
                print(f"Loaded YAML config from: {yaml_path}")
            except Exception as e:
                print(f"Warning: Failed to load YAML config: {e}")
                self.config = {}
                print("Using default configuration...")

        # ---------- App Settings ----------
        self.DEBUG = True
        self.TESTING = False
        self.SECRET_KEY = self.config.get("SECRET_KEY", "dev-secret-key")

        # ---------- Database ----------
        db_path = self.config.get("DATABASE_PATH", os.path.join("db", "sqlitedb", "whatsapp_platform.db"))
        if not os.path.isabs(db_path):
            # make absolute relative to project root
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            db_path = os.path.join(project_root, db_path)
        self.DATABASE_PATH = db_path

        # ---------- Twilio ----------
        twilio = self.config.get("TWILIO", {}) or {}
        self.TWILIO_ACCOUNT_SID = twilio.get("ACCOUNT_SID", "")
        self.TWILIO_AUTH_TOKEN = twilio.get("AUTH_TOKEN", "")
        whatsapp_from = twilio.get("WHATSAPP_FROM", "")
        if whatsapp_from and not str(whatsapp_from).startswith("whatsapp:"):
            whatsapp_from = f"whatsapp:{whatsapp_from}"
        self.TWILIO_WHATSAPP_FROM = whatsapp_from
        self.TWILIO_VALIDATE_WEBHOOKS = bool(self.config.get("TWILIO_VALIDATE_WEBHOOKS", False))

        # ---------- Default values ----------
        self.DEFAULT_RATE_LIMIT = int(self.config.get("DEFAULT_RATE_LIMIT", 1))
        self.DEFAULT_CREATED_BY = self.config.get("DEFAULT_CREATED_BY", "system")
        self.DEFAULT_QUIET_START = self.config.get("DEFAULT_QUIET_START", "22:00")
        self.DEFAULT_QUIET_END = self.config.get("DEFAULT_QUIET_END", "08:00")
        self.VERIFIED_NUMBERS = self.config.get("VERIFIED_NUMBERS", [])

        # Optional: short masked summary for debug visibility
        def _mask(v):
            if not v:
                return None
            s = str(v)
            return s[:4] + "..." + s[-2:] if len(s) > 6 else "****"

        print("DevelopmentConfig loaded:")
        print(f"  TWILIO_ACCOUNT_SID: {_mask(self.TWILIO_ACCOUNT_SID)}")
        print(f"  TWILIO_WHATSAPP_FROM: {self.TWILIO_WHATSAPP_FROM}")
