# Property Tycoon FontManager.py
# It contains the classes for the fonts, such as the font path, the font size, and the font cache.

import pygame
import os


class FontManager:
    _instance = None
    _fonts = {}
    _current_font_path = None

    _base_width = 1280
    _base_height = 720
    _scale_factor = 1.0

    @classmethod
    def get_font(cls, size):
        """Get a font at the specified base size (will be automatically scaled)"""
        if cls._current_font_path is None:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            cls._current_font_path = os.path.join(
                base_path, "assets", "font", "Ticketing.ttf"
            )

        scaled_size = cls.get_scaled_size(size)
        cache_key = (cls._current_font_path, scaled_size)

        if cache_key not in cls._fonts:
            try:
                cls._fonts[cache_key] = pygame.font.Font(
                    cls._current_font_path, scaled_size
                )
            except (pygame.error, FileNotFoundError) as e:
                print(f"Error loading font {cls._current_font_path}: {e}")
                cls._fonts[cache_key] = pygame.font.Font(None, scaled_size)

        return cls._fonts[cache_key]

    @classmethod
    def update_font_path(cls, new_font_path):
        """Update the current font and clear the cache"""
        if cls._current_font_path != new_font_path:
            cls._current_font_path = new_font_path
            cls._fonts.clear()

    @classmethod
    def update_scale_factor(cls, width, height):
        """Update the text scaling factor based on screen dimensions"""
        width_scale = width / cls._base_width
        height_scale = height / cls._base_height
        cls._scale_factor = min(width_scale, height_scale)
        cls._fonts.clear()
        return cls._scale_factor

    @classmethod
    def get_scaled_size(cls, base_size):
        """Get a scaled font size based on the current scale factor"""
        return int(base_size * cls._scale_factor)

    @classmethod
    def clear_cache(cls):
        """Clear the font cache"""
        cls._fonts.clear()


font_manager = FontManager()
