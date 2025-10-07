import os
import boto3
import json


class ProductionConfig:
    '''
    Production configuration:
    - Loads all secrets from AWS Secrets Manager
    - Applies safe defaults for rate limiting and quiet hours
    - Enforces webhook validation
    '''

    def __init__(self):
        # ---------------------------
        # Load AWS secrets
        # ---------------------------
        self.cfg = self._load_from_aws()

        # ---------------------------
        # Required configs
        # ---------------------------
        self.SECRET_KEY = self.cfg.get("SECRET_KEY")
        self.DATABASE_PATH = self.cfg.get(
            "DATABASE_PATH", "/db/sqlitedb/whatsapp_platform.db"
        )

        # Twilio credentials
        self.TWILIO_ACCOUNT_SID = self.cfg.get("TWILIO.ACCOUNT_SID")
        self.TWILIO_AUTH_TOKEN = self.cfg.get("TWILIO.AUTH_TOKEN")
        self.TWILIO_WHATSAPP_FROM = self.cfg.get("TWILIO.WHATSAPP_FROM")

        # ---------------------------
        # Webhook & security
        # ---------------------------
        self.TWILIO_VALIDATE_WEBHOOKS = True  # always True in production

        # ---------------------------
        # Rate limiting & quiet hours
        # ---------------------------
        self.DEFAULT_RATE_LIMIT = int(self.cfg.get("DEFAULT_RATE_LIMIT", 5))
        self.DEFAULT_QUIET_START = int(self.cfg.get("DEFAULT_QUIET_START", 21))
        self.DEFAULT_QUIET_END = int(self.cfg.get("DEFAULT_QUIET_END", 9))

        # ---------------------------
        # Verified numbers & default user
        # ---------------------------
        verified = self.cfg.get("VERIFIED_NUMBERS", [])
        if isinstance(verified, str):
            verified = [num.strip() for num in verified.split(",") if num.strip()]
        self.VERIFIED_NUMBERS = verified

        self.DEFAULT_CREATED_BY = self.cfg.get("DEFAULT_CREATED_BY", "system")

    # ----------------------------
    # AWS Secrets Manager loader
    # ----------------------------
    def _load_from_aws(self):
        secret_name = os.getenv("AWS_SECRET_NAME", "prod/whatsapp-config")
        region_name = os.getenv("AWS_REGION", "us-east-1")
        session = boto3.session.Session()
        client = session.client(service_name="secretsmanager", region_name=region_name)

        try:
            resp = client.get_secret_value(SecretId=secret_name)
            secret_string = resp.get("SecretString")
            if not secret_string:
                raise ValueError("AWS secret returned empty string")
            config = json.loads(secret_string)
            print(f"Loaded config from AWS Secrets Manager: {secret_name}")
            return config
        except Exception as e:
            raise RuntimeError(f"Failed to load AWS secret '{secret_name}': {e}")

'''
SECRET KEY LIKE

{
  "SECRET_KEY": "super-secure-secret-key",
  "DATABASE_URI": "mysql+pymysql://user:password@prod-db:3306/whatsapp_platform",
  "TWILIO_ACCOUNT_SID": "ACxxxxxxxxxxxxxxxxxxxxx",
  "TWILIO_AUTH_TOKEN": "xxxxxxxxxxxxxxxxxxxxx",
  "TWILIO_WHATSAPP_FROM": "whatsapp:+14155238886",
  "DEFAULT_RATE_LIMIT": 10,
  "DEFAULT_QUIET_START": 22,
  "DEFAULT_QUIET_END": 8,
  "VERIFIED_NUMBERS": "+94771234567,+94775555555",
  "DEFAULT_CREATED_BY": "system"
}

'''