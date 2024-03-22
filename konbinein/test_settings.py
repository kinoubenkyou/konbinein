from konbinein import settings
from konbinein.settings import *  # noqa: F401, F403

MONGO = {**settings.MONGO, "db": "test"}
