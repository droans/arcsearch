"""Arcsearch."""

import logging

handler = logging.FileHandler("parse.log", "w")
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[handler],
)
