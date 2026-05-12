"""Parser registry and parser auto-detection."""

# This file is part of ProChem.
# ProChem Copyright (C) 2021-2026 A.A.Solovykh - https://github.com/asolovykh
# See LICENSE.txt for details.

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Type

from prochem.core.models import Calculation
from prochem.io.base import AbstractParser

__all__ = [
    "ParserRegistry",
    "ParserSpec",
    "default_registry",
    "detect_parser",
    "parse",
]


@dataclass(frozen=True, slots=True)
class ParserSpec:
    """One parser registered in ProChem."""

    name: str
    parser_cls: Type[AbstractParser]


class ParserRegistry:
    """Registry of available calculation parsers."""

    def __init__(self) -> None:
        self._parsers: list[ParserSpec] = []

    def register(self, name: str, parser_cls: Type[AbstractParser]) -> None:
        """Register a parser class."""
        self._parsers.append(ParserSpec(name=name, parser_cls=parser_cls))

    def detect(self, path: str | Path) -> Type[AbstractParser]:
        """Return parser class for path or raise ValueError."""
        for parser in self._parsers:
            if parser.parser_cls.can_parse(path):
                return parser.parser_cls
        raise ValueError(f"No parser registered for {path}.")

    def parse(self, path: str | Path) -> Calculation:
        """Detect parser and parse path."""
        parser_cls = self.detect(path)
        return parser_cls(path).parse()

    @property
    def parsers(self) -> tuple[ParserSpec, ...]:
        """Registered parser specs."""
        return tuple(self._parsers)


_DEFAULT_REGISTRY: ParserRegistry | None = None


def default_registry() -> ParserRegistry:
    """Return registry with built-in parser classes."""
    global _DEFAULT_REGISTRY
    if _DEFAULT_REGISTRY is None:
        from prochem.io.qe.trajectory import Parser as QEParser
        from prochem.io.vasp import Parser as VASPParser

        registry = ParserRegistry()
        registry.register("vasp", VASPParser)
        registry.register("quantum_espresso", QEParser)
        _DEFAULT_REGISTRY = registry
    return _DEFAULT_REGISTRY


def detect_parser(path: str | Path) -> Type[AbstractParser]:
    """Detect parser class for path using the default registry."""
    return default_registry().detect(path)


def parse(path: str | Path) -> Calculation:
    """Parse path using the default registry."""
    return default_registry().parse(path)
