"""Qt application entry point."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from prochem.adapters.qt.logs.print import PrintWindow
from prochem.adapters.qt.settings.settings import Settings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ProChem",
        description="ProChem is a program for reading and analyzing quantum chemistry calculations.",
        epilog="Developed by A.A.Solovykh",
    )
    parser.add_argument("-v", "--version", action="version", version="ProChem 1.0.0")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args(argv)

    project_dir = Path.cwd()
    logging.basicConfig(
        filename=project_dir / "ProChem.log",
        level=logging.DEBUG if args.debug else logging.INFO,
        filemode="w",
    )
    app = QApplication(sys.argv if argv is None else argv)
    settings_object = Settings(str(project_dir)).load_settings()
    PrintWindow(settings_object, str(project_dir))
    return app.exec()

