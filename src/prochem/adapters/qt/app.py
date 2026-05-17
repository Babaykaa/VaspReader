"""Qt application entry point."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from PySide6.QtGui import QColor, QPalette
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
    app.setStyle("Fusion")
    app.setPalette(_light_palette())
    settings_object = Settings(str(project_dir)).load_settings()
    PrintWindow(settings_object, str(project_dir))
    return app.exec()


def _light_palette() -> QPalette:
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(245, 245, 245))
    palette.setColor(QPalette.WindowText, QColor(20, 20, 20))
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
    palette.setColor(QPalette.Text, QColor(20, 20, 20))
    palette.setColor(QPalette.Button, QColor(245, 245, 245))
    palette.setColor(QPalette.ButtonText, QColor(20, 20, 20))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 240))
    palette.setColor(QPalette.ToolTipText, QColor(20, 20, 20))
    palette.setColor(QPalette.Highlight, QColor(0, 160, 180))
    palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
    return palette
