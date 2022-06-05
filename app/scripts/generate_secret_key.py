import os
import secrets

import dotenv

new_secret = secrets.token_urlsafe(32)

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

os.environ["SECRET_KEY"] = secrets.token_urlsafe()
# Write changes to .env file.
dotenv.set_key(dotenv_file, "SECRET_KEY", os.environ["SECRET_KEY"], quote_mode="never")

print("Secrets generated successfully!")
