import os

class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATABASE_URI = f"{os.path.join(BASE_DIR, 'data', 'urls.db')}"
