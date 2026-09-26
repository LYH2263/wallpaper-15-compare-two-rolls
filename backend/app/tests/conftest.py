import os
import tempfile

os.environ["DATA_DIR"] = tempfile.mkdtemp(prefix="wallpaper-test-")

from app import seed  # noqa: E402

seed.init_db()
