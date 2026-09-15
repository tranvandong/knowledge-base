import logging
from pathlib import Path


def setup_logging() -> None:
    log_directory = Path("logs")
    log_directory.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | %(levelname)s | "
            "%(name)s | %(message)s"
        ),
        handlers=[
            logging.FileHandler(
                log_directory / "tools.log",
                encoding="utf-8",
            ),
            logging.StreamHandler(),
        ],
        force=True,
    )