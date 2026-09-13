from sqlalchemy import create_engine
from app.db.base import Base
from app.db.models import *

def test_models_importable():
    # If this runs, models are successfully imported and configured
    assert len(Base.metadata.tables) > 0
