"""Small Qt window helpers shared by generated-adjacent windows."""

from __future__ import annotations

from PySide6.QtWidgets import QApplication


def move_to_saved_or_default(
    window,
    settings,
    settings_key: str,
    *,
    default_offset: tuple[int, int],
) -> None:
    """Move a window to a saved position or to a visible default position."""
    location = settings.get_new_window_location(settings_key)
    use_default = not _is_valid_location(location)
    if not use_default:
        x, y = int(location[0]), int(location[1])
        use_default = _is_top_left_startup_position(x, y)
    if use_default:
        x, y = default_offset
        relative_to_screen = True
    else:
        relative_to_screen = False

    x, y = _visible_position(window, x, y, relative_to_screen=relative_to_screen)
    window.move(x, y)


def _is_valid_location(location: object) -> bool:
    if isinstance(location, (str, bytes)) or location is None:
        return False
    return (
        hasattr(location, "__len__")
        and hasattr(location, "__getitem__")
        and len(location) >= 2
        and location[0] is not None
        and location[1] is not None
    )


def _is_top_left_startup_position(x: int, y: int) -> bool:
    return x <= 8 and y <= 8


def _visible_position(
    window,
    x: int,
    y: int,
    *,
    relative_to_screen: bool,
) -> tuple[int, int]:
    screen = window.screen() or QApplication.primaryScreen()
    if screen is None:
        return max(40, x), max(40, y)

    area = screen.availableGeometry()
    margin = 32
    width = max(window.width(), window.minimumWidth(), 1)
    height = max(window.height(), window.minimumHeight(), 1)

    min_x = area.left() + margin
    min_y = area.top() + margin
    max_x = max(min_x, area.right() - width - margin)
    max_y = max(min_y, area.bottom() - height - margin)

    if relative_to_screen:
        x = area.left() + x
        y = area.top() + y

    x = min(max(x, min_x), max_x)
    y = min(max(y, min_y), max_y)
    return x, y


__all__ = ["move_to_saved_or_default"]
