# Property Tycoon ui.py
# It contains the classes for the UI, such as the buttons, input fields, and other UI elements.

import pygame
import sys
import time
import math
import random
from src.Font_Manager import font_manager
from src.Sound_Manager import sound_manager
import os
import webbrowser

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (59, 59, 59)
UI_BG = (18, 18, 18)

DARK_RED = (139, 0, 0)
DARK_GREEN = (0, 100, 0)
DARK_BLUE = (0, 0, 139)
GOLD = (218, 165, 32)
CREAM = (255, 253, 208)
BURGUNDY = (128, 0, 32)

ACCENT_COLOR = BURGUNDY
BUTTON_HOVER = (160, 20, 40)
ERROR_COLOR = (220, 53, 69)
SUCCESS_COLOR = DARK_GREEN
MODE_COLOR = DARK_BLUE
TIME_COLOR = (255, 180, 100)
HUMAN_COLOR = DARK_GREEN
AI_COLOR = DARK_RED

DEFAULT_RES = (854, 480)

base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATH = os.path.join(base_path, "assets", "font", "Ticketing.ttf")


def get_window_size():
    surface = pygame.display.get_surface()
    if surface:
        return surface.get_size()
    return DEFAULT_RES


class UIButton:
    def __init__(self, rect, text, font, color=ACCENT_COLOR):
        self.rect = rect
        self.text = text
        self.font = font
        self.color = color
        self.hover = False
        self.active = True
        self.is_selected = False
        self.image = None
        self.shadow_height = 4
        self.border_width = 2

    def _draw_basic_button(self, screen, base_color):
        shadow_rect = self.rect.copy()
        shadow_rect.y += self.shadow_height
        shadow = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        pygame.draw.rect(shadow, (*BLACK, 128), shadow.get_rect(), border_radius=8)
        screen.blit(shadow, shadow_rect)

        button_surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)

        gradient = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        for i in range(self.rect.height):
            alpha = 255 - int(i * 0.5)
            pygame.draw.line(
                gradient, (*base_color, alpha), (0, i), (self.rect.width, i)
            )

        pygame.draw.rect(
            button_surface, base_color, button_surface.get_rect(), border_radius=8
        )
        button_surface.blit(gradient, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        border_color = GOLD if self.hover else CREAM
        pygame.draw.rect(
            button_surface,
            border_color,
            button_surface.get_rect(),
            width=self.border_width,
            border_radius=8,
        )

        if self.hover:
            highlight = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            for i in range(4):
                alpha = 100 - i * 25
                pygame.draw.rect(
                    highlight,
                    (255, 255, 255, alpha),
                    highlight.get_rect().inflate(-i * 2, -i * 2),
                    border_radius=8,
                )
            button_surface.blit(highlight, (0, 0))

        screen.blit(button_surface, self.rect)

        text_shadow = self.font.render(self.text, True, BLACK)
        text_surface = self.font.render(self.text, True, CREAM)

        text_rect = text_surface.get_rect(center=self.rect.center)
        shadow_rect = text_rect.copy()
        shadow_rect.x += 1
        shadow_rect.y += 1

        screen.blit(text_shadow, shadow_rect)
        screen.blit(text_surface, text_rect)

    def draw(self, screen):
        if not self.active:
            base_color = GRAY
            self._draw_basic_button(screen, base_color)
            return

        if self.image:
            if self.hover or self.is_selected:
                hover_img = self.image.copy()
                hover_img.fill((255, 255, 255, 50), special_flags=pygame.BLEND_RGBA_ADD)
                screen.blit(hover_img, self.rect)
            else:
                screen.blit(self.image, self.rect)
        else:
            base_color = BUTTON_HOVER if self.hover else self.color
            self._draw_basic_button(screen, base_color)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered


class UIInput:
    def __init__(
        self, rect, text, font, active_color=ACCENT_COLOR, inactive_color=GRAY
    ):
        self.rect = rect
        self.text = text
        self.font = font
        self.active_color = active_color
        self.inactive_color = inactive_color
        self.active = False
        self.placeholder = "Enter name..."
        self.is_selected = False
        self.error = False
        self.background_alpha = 200

    def draw(self, screen):
        s = pygame.Surface(self.rect.size)
        s.set_alpha(self.background_alpha)
        if self.error:
            s.fill(ERROR_COLOR[:3])
        else:
            color = (
                self.active_color
                if self.active or self.is_selected
                else self.inactive_color
            )
            s.fill(color[:3])
        screen.blit(s, self.rect)
        if self.text:
            color = WHITE
            text = self.text
        else:
            color = LIGHT_GRAY
            text = self.placeholder
        text_surface = self.font.render(text, True, color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        border_color = WHITE if self.active or self.is_selected else LIGHT_GRAY
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=5)
        if self.is_selected:
            pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=5)


class BasePage:
    def __init__(self, instructions=None):
        window_size = get_window_size()
        self.screen = pygame.display.set_mode(window_size)
        try:
            asset_path = os.path.join(base_path, "assets/image/Logo.png")
            self.logo_image = pygame.image.load(asset_path)
            logo_width = int(window_size[0] * 0.3)
            logo_height = int(
                logo_width
                * (self.logo_image.get_height() / self.logo_image.get_width())
            )
            self.logo_image = pygame.transform.scale(
                self.logo_image, (logo_width, logo_height)
            )
        except (pygame.error, FileNotFoundError):
            print("Could not load game logo")
            self.logo_image = None

        try:
            asset_path = os.path.join(base_path, "assets/image/starterbackground.png")
            self.background_image = pygame.image.load(asset_path)
            self.original_background = self.background_image.copy()
        except (pygame.error, FileNotFoundError):
            print("Could not load background image")
            self.background_image = None
            self.original_background = None

        self.title_font = font_manager.get_font(82)
        self.button_font = font_manager.get_font(42)
        self.version_font = font_manager.get_font(28)
        self.small_font = font_manager.get_font(24)
        self.instructions = instructions

    def draw_background(self):
        window_size = get_window_size()
        if self.original_background:
            img_width, img_height = self.original_background.get_size()
            window_width, window_height = window_size

            img_aspect = img_width / img_height
            window_aspect = window_width / window_height

            if window_aspect > img_aspect:
                scaled_width = window_width
                scaled_height = int(scaled_width / img_aspect)
            else:
                scaled_height = window_height
                scaled_width = int(scaled_height * img_aspect)

            pos_x = (window_width - scaled_width) // 2
            pos_y = (window_height - scaled_height) // 2

            scaled_bg = pygame.transform.scale(
                self.original_background, (scaled_width, scaled_height)
            )
            self.screen.blit(scaled_bg, (pos_x, pos_y))
        else:
            self.screen.fill(UI_BG)
            gradient = pygame.Surface(window_size, pygame.SRCALPHA)
            for i in range(window_size[1]):
                alpha = int(255 * (1 - i / window_size[1]))
                pygame.draw.line(
                    gradient, (*ACCENT_COLOR[:3], alpha), (0, i), (window_size[0], i)
                )
            self.screen.blit(gradient, (0, 0))

    def draw_title(self):
        window_size = get_window_size()

        if (
            hasattr(self, "logo_image")
            and self.logo_image is not None
            and (isinstance(self, MainMenuPage) or isinstance(self, HowToPlayPage))
        ):
            logo_rect = self.logo_image.get_rect(centerx=window_size[0] // 2, y=80)
            self.screen.blit(self.logo_image, logo_rect)
        elif isinstance(self, MainMenuPage) or isinstance(self, HowToPlayPage):
            title_shadow = self.title_font.render(
                "Property Tycoon Alpha 25.03.2025", True, BLACK
            )
            title_glow = self.title_font.render(
                "Property Tycoon Alpha 25.03.2025", True, ACCENT_COLOR
            )
            title_text = self.title_font.render(
                "Property Tycoon Alpha 25.03.2025", True, WHITE
            )
            title_rect = title_text.get_rect(centerx=window_size[0] // 2, y=80)
            shadow_rect = title_rect.copy()
            shadow_rect.x += 2
            shadow_rect.y += 2
            self.screen.blit(title_shadow, shadow_rect)
            self.screen.blit(title_glow, title_rect)
            self.screen.blit(title_text, title_rect)

    def draw_instructions(self):
        if self.instructions:
            window_size = get_window_size()
            font_size = 20
            font = font_manager.get_font(font_size)
            padding = 10
            line_height = font_size + 2

            total_height = len(self.instructions) * line_height

            for i, instruction in enumerate(self.instructions):
                text_surface = font.render(instruction, True, WHITE)
                y_position = (
                    window_size[1] - (total_height - (i * line_height)) - padding
                )
                self.screen.blit(text_surface, (padding, y_position))

    def draw(self):
        self.draw_background()
        self.draw_title()
        self.draw_instructions()
        pygame.display.flip()


class MainMenuPage(BasePage):
    def __init__(self, instructions=None):
        super().__init__(instructions=instructions)
        self.small_font = font_manager.get_font(24)
        button_width = 300
        button_height = 60

        self.start_button = UIButton(
            pygame.Rect(
                (get_window_size()[0] - button_width) // 2,
                get_window_size()[1] // 2,
                button_width,
                button_height,
            ),
            "Start Game",
            self.button_font,
        )

        self.how_to_play_button = UIButton(
            pygame.Rect(
                (get_window_size()[0] - button_width) // 2,
                get_window_size()[1] // 2 + 80,
                button_width,
                button_height,
            ),
            "How to Play",
            self.button_font,
            color=MODE_COLOR,
        )

        self.settings_button = UIButton(
            pygame.Rect(
                20,
                get_window_size()[1] - button_height - 20,
                button_width,
                button_height,
            ),
            "Settings",
            self.button_font,
        )

        try:
            youtube_path = os.path.join(base_path, "assets/image/Youtube Logo.png")
            self.youtube_logo = pygame.image.load(youtube_path)
            self.youtube_logo = pygame.transform.scale(self.youtube_logo, (40, 40))
            self.youtube_rect = self.youtube_logo.get_rect(topleft=(20, 20))

            github_path = os.path.join(base_path, "assets/image/GitHub-Symbol.png")
            self.github_logo = pygame.image.load(github_path)
            self.github_logo = pygame.transform.scale(self.github_logo, (40, 40))
            self.github_rect = self.github_logo.get_rect(topleft=(80, 20))

            self.github_hover = False
            self.youtube_hover = False

            self.github_url = "https://github.com/Minosaji/Software-Engineering-Project"
            self.youtube_url = "https://www.youtube.com/@UOS-G6046-Group5"
        except (pygame.error, FileNotFoundError) as e:
            print(f"Could not load social media logos: {e}")
            self.github_logo = None
            self.youtube_logo = None

    def draw(self):
        self.draw_background()
        self.draw_title()

        self.start_button.draw(self.screen)
        self.how_to_play_button.draw(self.screen)
        self.settings_button.draw(self.screen)

        if hasattr(self, "youtube_logo") and self.youtube_logo:
            if self.youtube_hover:
                glow_surface = pygame.Surface(
                    (self.youtube_rect.width + 10, self.youtube_rect.height + 10),
                    pygame.SRCALPHA,
                )
                pygame.draw.rect(
                    glow_surface,
                    (*ACCENT_COLOR, 150),
                    pygame.Rect(
                        0, 0, glow_surface.get_width(), glow_surface.get_height()
                    ),
                    border_radius=5,
                )
                self.screen.blit(
                    glow_surface, (self.youtube_rect.x - 5, self.youtube_rect.y - 5)
                )
            self.screen.blit(self.youtube_logo, self.youtube_rect)

        if hasattr(self, "github_logo") and self.github_logo:
            if self.github_hover:
                glow_surface = pygame.Surface(
                    (self.github_rect.width + 10, self.github_rect.height + 10),
                    pygame.SRCALPHA,
                )
                pygame.draw.rect(
                    glow_surface,
                    (*ACCENT_COLOR, 150),
                    pygame.Rect(
                        0, 0, glow_surface.get_width(), glow_surface.get_height()
                    ),
                    border_radius=5,
                )
                self.screen.blit(
                    glow_surface, (self.github_rect.x - 5, self.github_rect.y - 5)
                )
            self.screen.blit(self.github_logo, self.github_rect)

        version_text = self.version_font.render(
            "Build Version: Alpha 25.03.2025", True, ERROR_COLOR
        )
        version_rect = version_text.get_rect(
            right=get_window_size()[0] - 20, bottom=get_window_size()[1] - 20
        )
        self.screen.blit(version_text, version_rect)

        controls_text1 = self.small_font.render(
            "Press ENTER to start", True, LIGHT_GRAY
        )
        controls_text2 = self.small_font.render(
            "H for how to play, S for settings", True, LIGHT_GRAY
        )

        controls_rect1 = controls_text1.get_rect(
            right=get_window_size()[0] - 20, bottom=get_window_size()[1] - 70
        )
        controls_rect2 = controls_text2.get_rect(
            right=get_window_size()[0] - 20, bottom=get_window_size()[1] - 45
        )

        self.screen.blit(controls_text1, controls_rect1)
        self.screen.blit(controls_text2, controls_rect2)

        pygame.display.flip()

    def handle_click(self, pos):
        if self.start_button.check_hover(pos):
            return "start"
        elif self.how_to_play_button.check_hover(pos):
            return "how_to_play"
        elif self.settings_button.check_hover(pos):
            return "settings"
        elif hasattr(self, "github_rect") and self.github_rect.collidepoint(pos):
            try:
                webbrowser.open(self.github_url)
                print(f"Opening GitHub URL: {self.github_url}")
            except Exception as e:
                print(f"Error opening GitHub URL: {e}")
        elif hasattr(self, "youtube_rect") and self.youtube_rect.collidepoint(pos):
            try:
                webbrowser.open(self.youtube_url)
                print(f"Opening YouTube URL: {self.youtube_url}")
            except Exception as e:
                print(f"Error opening YouTube URL: {e}")
        return None

    def handle_motion(self, pos):
        self.start_button.check_hover(pos)
        self.how_to_play_button.check_hover(pos)
        self.settings_button.check_hover(pos)

        if hasattr(self, "github_rect"):
            self.github_hover = self.github_rect.collidepoint(pos)
        if hasattr(self, "youtube_rect"):
            self.youtube_hover = self.youtube_rect.collidepoint(pos)

    def handle_key(self, event):
        if event.key == pygame.K_RETURN:
            return "start"
        elif event.key == pygame.K_h:
            return "how_to_play"
        elif event.key == pygame.K_s:
            return "settings"
        return None


class SettingsPage(BasePage):
    CONFIRMATION_DURATION = 5000

    def __init__(self, instructions=None):
        super().__init__(instructions=instructions)
        self.small_font = font_manager.get_font(24)
        self.resolution_options = [
            (1280, 720),
            (854, 480),
            (1600, 900),
            (1920, 1080),
            (2560, 1440),
        ]
        self.font_options = [
            ("Ticketing", "Ticketing.ttf"),
            ("Play Regular", "Play-Regular.ttf"),
            ("British Railway=", "britrdn_.ttf"),
            ("Uni of Sussex", "LibreBaskerville-Bold.ttf"),
        ]
        self.current_resolution = 0
        self.current_font = 0
        self.show_confirmation = False
        self.confirmation_time = 0

        self.sound_manager = sound_manager

        self.sound_volume = int(self.sound_manager.sound_volume * 100)
        self.music_volume = int(self.sound_manager.music_volume * 100)

        button_width = 500
        button_height = 60
        self.resolution_button = UIButton(
            pygame.Rect(
                (get_window_size()[0] - button_width) // 2,
                get_window_size()[1] // 2 - 220,
                button_width,
                button_height,
            ),
            f"Screen Size: {self.resolution_options[self.current_resolution][0]}x{self.resolution_options[self.current_resolution][1]}",
            self.button_font,
        )

        self.font_button = UIButton(
            pygame.Rect(
                (get_window_size()[0] - button_width) // 2,
                get_window_size()[1] // 2 - 150,
                button_width,
                button_height,
            ),
            f"Font: {self.font_options[self.current_font][0]}",
            self.button_font,
            color=MODE_COLOR,
        )

        self.sound_volume_button = UIButton(
            pygame.Rect(
                (get_window_size()[0] - button_width) // 2,
                get_window_size()[1] // 2 - 80,
                button_width,
                button_height,
            ),
            f"Sound Volume: {self.sound_volume}%",
            self.button_font,
            color=MODE_COLOR,
        )

        self.music_volume_button = UIButton(
            pygame.Rect(
                (get_window_size()[0] - button_width) // 2,
                get_window_size()[1] // 2 - 10,
                button_width,
                button_height,
            ),
            f"Music Volume: {self.music_volume}%",
            self.button_font,
            color=MODE_COLOR,
        )

        confirm_button_width = 350
        self.confirm_button = UIButton(
            pygame.Rect(
                (get_window_size()[0] - confirm_button_width) // 2,
                get_window_size()[1] // 2 + 60,
                confirm_button_width,
                button_height,
            ),
            "Confirm",
            self.button_font,
        )

        self.back_button = UIButton(
            pygame.Rect(20, get_window_size()[1] - 80, 200, button_height),
            "Back",
            self.button_font,
        )

        self.test_sound_button = UIButton(
            pygame.Rect(
                (get_window_size()[0] + button_width) // 2 + 20,
                get_window_size()[1] // 2 - 80,
                100,
                button_height,
            ),
            "Test",
            self.button_font,
            color=(0, 150, 200),
        )

        self.test_music_button = UIButton(
            pygame.Rect(
                (get_window_size()[0] + button_width) // 2 + 20,
                get_window_size()[1] // 2 - 10,
                100,
                button_height,
            ),
            "Test",
            self.button_font,
            color=(0, 150, 200),
        )

    def draw(self):
        self.draw_background()
        self.draw_title()

        settings_text = self.button_font.render("Game Settings", True, WHITE)
        settings_rect = settings_text.get_rect(centerx=get_window_size()[0] // 2, y=100)
        self.screen.blit(settings_text, settings_rect)

        self.resolution_button.text = f"Screen Size: {self.resolution_options[self.current_resolution][0]}x{self.resolution_options[self.current_resolution][1]}"
        self.resolution_button.draw(self.screen)

        info_text = self.small_font.render(
            "All resolutions maintain 16:9 aspect ratio", True, LIGHT_GRAY
        )
        info_rect = info_text.get_rect(
            centerx=get_window_size()[0] // 2,
            top=self.resolution_button.rect.bottom + 10,
        )
        self.screen.blit(info_text, info_rect)

        self.font_button.text = f"Font: {self.font_options[self.current_font][0]}"
        self.font_button.draw(self.screen)

        self.sound_volume_button.text = f"Sound Volume: {self.sound_volume}%"
        self.sound_volume_button.draw(self.screen)
        self.test_sound_button.draw(self.screen)

        self.music_volume_button.text = f"Music Volume: {self.music_volume}%"
        self.music_volume_button.draw(self.screen)
        self.test_music_button.draw(self.screen)

        if self.show_confirmation:
            current_time = pygame.time.get_ticks()
            if current_time - self.confirmation_time < self.CONFIRMATION_DURATION:
                confirm_text = self.small_font.render(
                    "Press ENTER or click Confirm to apply changes", True, SUCCESS_COLOR
                )
                confirm_rect = confirm_text.get_rect(
                    centerx=get_window_size()[0] // 2,
                    top=self.confirm_button.rect.bottom + 10,
                )
                self.screen.blit(confirm_text, confirm_rect)
            else:
                self.show_confirmation = False

        controls = [
            "Controls:",
            "R - Change screen resolution",
            "F - Change font",
            "S - Adjust sound volume",
            "M - Adjust music volume",
            "Enter/Space - Apply and return",
        ]

        y_offset = get_window_size()[1] - 180
        for hint in controls:
            hint_text = self.small_font.render(hint, True, LIGHT_GRAY)
            hint_rect = hint_text.get_rect(right=get_window_size()[0] - 20, y=y_offset)
            self.screen.blit(hint_text, hint_rect)
            y_offset += 25

        self.confirm_button.draw(self.screen)
        self.back_button.draw(self.screen)

        pygame.display.flip()

    def handle_click(self, pos):
        if self.resolution_button.check_hover(pos):
            self.current_resolution = (self.current_resolution + 1) % len(
                self.resolution_options
            )
            self.show_confirmation = True
            self.confirmation_time = pygame.time.get_ticks()
            return False
        elif self.font_button.check_hover(pos):
            self.current_font = (self.current_font + 1) % len(self.font_options)
            self.show_confirmation = True
            self.confirmation_time = pygame.time.get_ticks()
            return False
        elif self.sound_volume_button.check_hover(pos):
            self.sound_volume = (self.sound_volume + 10) % 110
            self.sound_manager.set_sound_volume(self.sound_volume / 100.0)
            self.show_confirmation = True
            self.confirmation_time = pygame.time.get_ticks()
            return False
        elif self.music_volume_button.check_hover(pos):
            self.music_volume = (self.music_volume + 10) % 110
            self.sound_manager.set_music_volume(self.music_volume / 100.0)
            self.show_confirmation = True
            self.confirmation_time = pygame.time.get_ticks()
            return False
        elif self.test_sound_button.check_hover(pos):
            self.sound_manager.play_sound("menu_click")
            return False
        elif self.test_music_button.check_hover(pos):
            if not pygame.mixer.music.get_busy():
                self.sound_manager.load_music()
                self.sound_manager.play_music(loop=0)
            else:
                self.sound_manager.stop_music()
            return False
        elif self.confirm_button.check_hover(pos):
            current_resolution = get_window_size()
            new_resolution = self.resolution_options[self.current_resolution]
            global FONT_PATH
            new_font_path = os.path.join(
                base_path, "assets", "font", self.font_options[self.current_font][1]
            )
            if current_resolution != new_resolution or FONT_PATH != new_font_path:
                FONT_PATH = new_font_path
                font_manager.update_font_path(new_font_path)
                return True
        elif self.back_button.check_hover(pos):
            return "back"
        return False

    def handle_motion(self, pos):
        self.resolution_button.check_hover(pos)
        self.font_button.check_hover(pos)
        self.sound_volume_button.check_hover(pos)
        self.music_volume_button.check_hover(pos)
        self.test_sound_button.check_hover(pos)
        self.test_music_button.check_hover(pos)
        self.confirm_button.check_hover(pos)
        self.back_button.check_hover(pos)

    def handle_key(self, event):
        if event.key == pygame.K_r:
            self.current_resolution = (self.current_resolution + 1) % len(
                self.resolution_options
            )
            self.show_confirmation = True
            self.confirmation_time = pygame.time.get_ticks()
            return False
        elif event.key == pygame.K_f:
            self.current_font = (self.current_font + 1) % len(self.font_options)
            self.show_confirmation = True
            self.confirmation_time = pygame.time.get_ticks()
            return False
        elif event.key == pygame.K_s:
            self.sound_volume = (self.sound_volume + 10) % 110
            self.sound_manager.set_sound_volume(self.sound_volume / 100.0)
            self.show_confirmation = True
            self.confirmation_time = pygame.time.get_ticks()
            return False
        elif event.key == pygame.K_m:
            self.music_volume = (self.music_volume + 10) % 110
            self.sound_manager.set_music_volume(self.music_volume / 100.0)
            self.show_confirmation = True
            self.confirmation_time = pygame.time.get_ticks()
            return False
        elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
            current_resolution = get_window_size()
            new_resolution = self.resolution_options[self.current_resolution]
            global FONT_PATH
            new_font_path = os.path.join(
                base_path, "assets", "font", self.font_options[self.current_font][1]
            )
            if current_resolution != new_resolution or FONT_PATH != new_font_path:
                FONT_PATH = new_font_path
                font_manager.update_font_path(new_font_path)
                return True
        elif event.key == pygame.K_ESCAPE:
            return "back"
        return False

    def get_settings(self):
        return {
            "resolution": self.resolution_options[self.current_resolution],
            "font": os.path.join(
                base_path, "assets", "font", self.font_options[self.current_font][1]
            ),
            "sound_volume": self.sound_volume / 100.0,
            "music_volume": self.music_volume / 100.0,
        }


class StartPage(BasePage):
    def __init__(self, instructions=None):
        super().__init__(instructions=instructions)
        self.screen = pygame.display.set_mode(get_window_size())
        pygame.display.set_caption("Property Tycoon Alpha 25.03.2025")
        self.title_font = font_manager.get_font(82)
        self.button_font = font_manager.get_font(42)
        self.version_font = font_manager.get_font(28)
        self.input_font = font_manager.get_font(36)
        self.small_font = font_manager.get_font(24)
        self.selected_element = 0
        self.active_input = -1

        self.human_count = 1
        self.ai_count = 1
        self.total_players = self.human_count + self.ai_count
        self.player_names = ["Human Player 1"]
        self.ai_names = ["Bot 1"]
        self.ai_name_counter = 1

        self.token_images = []
        for i in range(1, 7):
            try:
                image_path = os.path.join(
                    base_path, "assets", "image", f"Playertoken ({i}).png"
                )
                if os.path.exists(image_path):
                    token_image = pygame.image.load(image_path)
                    token_image = pygame.transform.scale(token_image, (40, 40))
                    self.token_images.append(token_image)
                else:
                    print(f"Token image {i} not found at {image_path}")
                    fallback = pygame.Surface((40, 40), pygame.SRCALPHA)
                    pygame.draw.circle(fallback, (50 * i, 100, 150), (20, 20), 20)
                    self.token_images.append(fallback)
            except Exception as e:
                print(f"Error loading token image {i}: {e}")
                fallback = pygame.Surface((40, 40), pygame.SRCALPHA)
                pygame.draw.circle(fallback, (50 * i, 100, 150), (20, 20), 20)
                self.token_images.append(fallback)

        self.player_token_indices = [0]
        self.ai_token_indices = [1]

        button_width = 300
        button_height = 60
        input_y_start = get_window_size()[1] // 2 - 50
        input_width = 300
        input_height = 50
        count_x_offset = 250

        player_controls_y = input_y_start - 180

        self.human_minus_button = UIButton(
            pygame.Rect(
                get_window_size()[0] // 2 - count_x_offset - 100,
                player_controls_y,
                50,
                50,
            ),
            "-",
            self.button_font,
            color=HUMAN_COLOR,
        )

        self.human_plus_button = UIButton(
            pygame.Rect(
                get_window_size()[0] // 2 - count_x_offset + 50,
                player_controls_y,
                50,
                50,
            ),
            "+",
            self.button_font,
            color=HUMAN_COLOR,
        )

        self.ai_minus_button = UIButton(
            pygame.Rect(
                get_window_size()[0] // 2 + count_x_offset - 100,
                player_controls_y,
                50,
                50,
            ),
            "-",
            self.button_font,
            color=AI_COLOR,
        )

        self.ai_plus_button = UIButton(
            pygame.Rect(
                get_window_size()[0] // 2 + count_x_offset + 50,
                player_controls_y,
                50,
                50,
            ),
            "+",
            self.button_font,
            color=AI_COLOR,
        )

        self.name_inputs = []
        input_spacing = 50
        for i in range(5):
            self.name_inputs.append(
                UIInput(
                    pygame.Rect(
                        (get_window_size()[0] - input_width) // 2,
                        input_y_start + i * input_spacing,
                        input_width,
                        input_height,
                    ),
                    "",
                    self.input_font,
                )
            )

        self.start_button = UIButton(
            pygame.Rect(
                (get_window_size()[0] - button_width) // 2,
                get_window_size()[1] - 100,
                button_width,
                button_height,
            ),
            "Start Game",
            self.button_font,
        )

        self.back_button = UIButton(
            pygame.Rect(20, get_window_size()[1] - 80, 200, button_height),
            "Back",
            self.button_font,
        )

        self.token_button_rects = []
        self.token_selection_active = False
        self.token_selection_for_player = -1
        self.token_selection_is_ai = False

    def generate_unique_ai_name(self):
        self.ai_name_counter += 1
        return f"Bot {self.ai_name_counter}"

    def update_player_lists(self):
        while len(self.ai_names) < self.ai_count:
            self.ai_names.append(self.generate_unique_ai_name())
        while len(self.ai_names) > self.ai_count:
            self.ai_names.pop()

        while len(self.player_token_indices) < self.human_count:
            used_indices = self.player_token_indices + self.ai_token_indices
            for i in range(6):
                if i not in used_indices:
                    self.player_token_indices.append(i)
                    break
            else:
                self.player_token_indices.append(0)

        while len(self.player_token_indices) > self.human_count:
            self.player_token_indices.pop()

        while len(self.ai_token_indices) < self.ai_count:
            used_indices = self.player_token_indices + self.ai_token_indices
            for i in range(6):
                if i not in used_indices:
                    self.ai_token_indices.append(i)
                    break
            else:
                self.ai_token_indices.append(0)

        while len(self.ai_token_indices) > self.ai_count:
            self.ai_token_indices.pop()

    def draw(self):
        self.draw_background()
        self.draw_title()

        player_setup_title = self.button_font.render("Player Setup", True, WHITE)
        title_rect = player_setup_title.get_rect(
            centerx=get_window_size()[0] // 2, y=100
        )
        self.screen.blit(player_setup_title, title_rect)

        input_y_start = get_window_size()[1] // 2 - 50

        player_controls_y = input_y_start - 120

        human_text = self.button_font.render(
            f"Human Players: {self.human_count}", True, HUMAN_COLOR
        )
        human_rect = human_text.get_rect(
            centerx=get_window_size()[0] // 2 - 150, y=player_controls_y - 40
        )
        self.screen.blit(human_text, human_rect)

        ai_text = self.button_font.render(
            f"AI Players: {self.ai_count}", True, AI_COLOR
        )
        ai_rect = ai_text.get_rect(
            centerx=get_window_size()[0] // 2 + 150, y=player_controls_y - 40
        )
        self.screen.blit(ai_text, ai_rect)

        total_text = self.small_font.render(
            f"Total Players: {self.total_players}/5", True, LIGHT_GRAY
        )
        total_rect = total_text.get_rect(
            centerx=get_window_size()[0] // 2, y=player_controls_y + 20
        )
        self.screen.blit(total_text, total_rect)

        button_y = player_controls_y + 60

        self.human_minus_button.rect.y = button_y
        self.human_plus_button.rect.y = button_y
        self.ai_minus_button.rect.y = button_y
        self.ai_plus_button.rect.y = button_y

        self.human_minus_button.active = self.human_count > 1
        self.human_plus_button.active = self.human_count < 5 and self.total_players < 5
        self.ai_minus_button.active = self.ai_count > 0
        self.ai_plus_button.active = self.ai_count < 4 and self.total_players < 5

        self.human_minus_button.draw(self.screen)
        self.human_plus_button.draw(self.screen)
        self.ai_minus_button.draw(self.screen)
        self.ai_plus_button.draw(self.screen)

        input_spacing = 50

        if self.token_selection_active:
            self.draw_token_selection()
        else:
            for i in range(self.human_count):
                self.name_inputs[i].active = i == self.active_input
                self.name_inputs[i].text = (
                    self.player_names[i] if i < len(self.player_names) else ""
                )
                self.name_inputs[i].draw(self.screen)

                human_label = self.small_font.render("Human", True, HUMAN_COLOR)
                label_rect = human_label.get_rect(
                    right=self.name_inputs[i].rect.left - 10,
                    centery=self.name_inputs[i].rect.centery,
                )
                self.screen.blit(human_label, label_rect)

                token_rect = pygame.Rect(
                    self.name_inputs[i].rect.right + 10,
                    self.name_inputs[i].rect.centery - 20,
                    40,
                    40,
                )

                token_index = (
                    self.player_token_indices[i]
                    if i < len(self.player_token_indices)
                    else 0
                )
                token_image = self.token_images[token_index]
                self.screen.blit(token_image, token_rect)

                pygame.draw.rect(
                    self.screen, HUMAN_COLOR, token_rect, 2, border_radius=5
                )

                if i >= len(self.token_button_rects):
                    self.token_button_rects.append((token_rect, i, False))
                else:
                    self.token_button_rects[i] = (token_rect, i, False)

            for i in range(self.ai_count):
                ai_input_rect = pygame.Rect(
                    (get_window_size()[0] - 300) // 2,
                    input_y_start + (self.human_count + i) * input_spacing,
                    300,
                    50,
                )

                if self.active_input == self.human_count + i:
                    pygame.draw.rect(
                        self.screen, ACCENT_COLOR, ai_input_rect, 2, border_radius=5
                    )

                ai_text = self.input_font.render(self.ai_names[i], True, LIGHT_GRAY)
                ai_rect = ai_text.get_rect(center=ai_input_rect.center)

                pygame.draw.rect(
                    self.screen, (*AI_COLOR[:3], 50), ai_input_rect, border_radius=5
                )
                self.screen.blit(ai_text, ai_rect)

                ai_label = self.small_font.render("AI", True, AI_COLOR)
                label_rect = ai_label.get_rect(
                    right=ai_input_rect.left - 10, centery=ai_input_rect.centery
                )
                self.screen.blit(ai_label, label_rect)

                if self.human_count + i >= len(self.token_button_rects):
                    self.token_button_rects.append((ai_input_rect, i, True))
                else:
                    _, idx, is_ai = self.token_button_rects[self.human_count + i]
                    self.token_button_rects[self.human_count + i] = (
                        ai_input_rect,
                        i,
                        True,
                    )

                token_rect = pygame.Rect(
                    ai_input_rect.right + 10, ai_input_rect.centery - 20, 40, 40
                )

                token_index = (
                    self.ai_token_indices[i] if i < len(self.ai_token_indices) else 0
                )
                token_image = self.token_images[token_index]
                self.screen.blit(token_image, token_rect)

                pygame.draw.rect(self.screen, AI_COLOR, token_rect, 2, border_radius=5)

                button_index = self.human_count + i
                token_button_index = len(self.token_button_rects)
                self.token_button_rects.append((token_rect, i, True))

        can_start = (
            all(name.strip() for name in self.player_names[: self.human_count])
            and self.total_players >= 2
            and self.total_players <= 5
        )
        self.start_button.active = can_start
        self.start_button.draw(self.screen)

        self.back_button.draw(self.screen)

        controls = [
            "Controls:",
            "H/h - Adjust human players",
            "A/a - Adjust AI players",
            "Enter - Edit selected name",
            "Tab - Switch between name fields",
            "Space - Start game",
            "ESC/Back - Return to menu",
            "Click token icon - Change player token",
            "Click player name - Edit name",
        ]

        y_offset = get_window_size()[1] - 210
        for hint in controls:
            hint_text = self.small_font.render(hint, True, LIGHT_GRAY)
            hint_rect = hint_text.get_rect(right=get_window_size()[0] - 20, y=y_offset)
            self.screen.blit(hint_text, hint_rect)
            y_offset += 20

        pygame.display.flip()

    def draw_token_selection(self):
        overlay = pygame.Surface(get_window_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        panel_width = 500
        panel_height = 400
        panel_x = (get_window_size()[0] - panel_width) // 2
        panel_y = (get_window_size()[1] - panel_height) // 2

        pygame.draw.rect(
            self.screen,
            UI_BG,
            pygame.Rect(panel_x, panel_y, panel_width, panel_height),
            border_radius=15,
        )
        pygame.draw.rect(
            self.screen,
            ACCENT_COLOR,
            pygame.Rect(panel_x, panel_y, panel_width, panel_height),
            2,
            border_radius=15,
        )

        player_type = "AI" if self.token_selection_is_ai else "Human"
        player_index = self.token_selection_for_player + 1
        title_text = self.button_font.render(
            f"Select Token for {player_type} {player_index}", True, WHITE
        )
        title_rect = title_text.get_rect(
            centerx=panel_x + panel_width // 2, top=panel_y + 20
        )
        self.screen.blit(title_text, title_rect)

        hint_text = self.small_font.render(
            "Click any token to select", True, LIGHT_GRAY
        )
        hint_rect = hint_text.get_rect(
            centerx=panel_x + panel_width // 2, top=panel_y + 60
        )
        self.screen.blit(hint_text, hint_rect)

        token_size = 60
        token_spacing = 20
        tokens_per_row = 3
        total_width = (token_size * tokens_per_row) + (
            token_spacing * (tokens_per_row - 1)
        )
        start_x = panel_x + (panel_width - total_width) // 2
        start_y = panel_y + 100

        self.token_selection_rects = []

        for i, token_image in enumerate(self.token_images):
            row = i // tokens_per_row
            col = i % tokens_per_row

            x = start_x + col * (token_size + token_spacing)
            y = start_y + row * (token_size + token_spacing)

            scaled_token = pygame.transform.scale(token_image, (token_size, token_size))
            token_rect = pygame.Rect(x, y, token_size, token_size)

            token_in_use = False
            token_user = None
            token_is_ai = False

            for j, token_idx in enumerate(self.player_token_indices):
                if token_idx == i:
                    token_in_use = True
                    token_user = j + 1
                    token_is_ai = False
                    break

            if not token_in_use:
                for j, token_idx in enumerate(self.ai_token_indices):
                    if token_idx == i:
                        token_in_use = True
                        token_user = j + 1
                        token_is_ai = True
                        break

            self.screen.blit(scaled_token, token_rect)

            if self.token_selection_is_ai:
                is_selected = (
                    i == self.ai_token_indices[self.token_selection_for_player]
                )
                border_color = AI_COLOR if is_selected else WHITE
            else:
                is_selected = (
                    i == self.player_token_indices[self.token_selection_for_player]
                )
                border_color = HUMAN_COLOR if is_selected else WHITE

            pygame.draw.rect(self.screen, border_color, token_rect, 2, border_radius=5)

            if (
                token_in_use
                and not (
                    self.token_selection_is_ai
                    and token_is_ai
                    and token_user == self.token_selection_for_player + 1
                )
                and not (
                    not self.token_selection_is_ai
                    and not token_is_ai
                    and token_user == self.token_selection_for_player + 1
                )
            ):
                user_text = self.small_font.render(
                    f"{'AI' if token_is_ai else 'P'}{token_user}",
                    True,
                    AI_COLOR if token_is_ai else HUMAN_COLOR,
                )
                user_rect = user_text.get_rect(
                    center=(x + token_size // 2, y + token_size + 10)
                )
                self.screen.blit(user_text, user_rect)

            self.token_selection_rects.append((token_rect, i, True))

        close_button_width = 100
        close_button_height = 40
        close_button_rect = pygame.Rect(
            panel_x + (panel_width - close_button_width) // 2,
            panel_y + panel_height - 60,
            close_button_width,
            close_button_height,
        )

        pygame.draw.rect(self.screen, ACCENT_COLOR, close_button_rect, border_radius=5)
        close_text = self.small_font.render("Close", True, WHITE)
        close_rect = close_text.get_rect(center=close_button_rect.center)
        self.screen.blit(close_text, close_rect)

        self.close_button_rect = close_button_rect

    def handle_click(self, pos):
        if self.token_selection_active:
            return self.handle_token_selection_click(pos)

        if self.start_button.check_hover(pos):
            return True

        if self.back_button.check_hover(pos):
            return "back"

        if self.human_minus_button.check_hover(pos) and self.human_count > 1:
            self.human_count -= 1
            self.active_input = -1
            self.update_player_lists()
            self.total_players = self.human_count + self.ai_count
            return False

        if (
            self.human_plus_button.check_hover(pos)
            and self.human_count < 5
            and self.total_players < 5
        ):
            self.human_count += 1
            self.active_input = -1
            if len(self.player_names) < self.human_count:
                self.player_names.append(f"Human Player {self.human_count}")
            self.update_player_lists()
            self.total_players = self.human_count + self.ai_count
            return False

        if self.ai_minus_button.check_hover(pos) and self.ai_count > 0:
            self.ai_count -= 1
            self.active_input = -1
            self.update_player_lists()
            self.total_players = self.human_count + self.ai_count
            return False

        if (
            self.ai_plus_button.check_hover(pos)
            and self.ai_count < 4
            and self.total_players < 5
        ):
            self.ai_count += 1
            self.active_input = -1
            self.update_player_lists()
            self.total_players = self.human_count + self.ai_count
            return False

        for i in range(self.human_count):
            rect = pygame.Rect(
                (get_window_size()[0] - 300) // 2,
                (get_window_size()[1] // 2 - 50) + i * 50,
                300,
                50,
            )

            if rect.collidepoint(pos):
                self.active_input = i
                return False

        for i in range(self.ai_count):
            ai_input_rect = pygame.Rect(
                (get_window_size()[0] - 300) // 2,
                (get_window_size()[1] // 2 - 50) + (self.human_count + i) * 50,
                300,
                50,
            )

            if ai_input_rect.collidepoint(pos):
                self.active_input = self.human_count + i
                return False

        for rect, player_idx, is_ai in self.token_button_rects:
            if rect.collidepoint(pos):
                self.token_selection_active = True
                self.token_selection_for_player = player_idx
                self.token_selection_is_ai = is_ai
                return False

        self.active_input = -1
        return False

    def handle_token_selection_click(self, pos):
        if hasattr(self, "close_button_rect") and self.close_button_rect.collidepoint(
            pos
        ):
            self.token_selection_active = False
            return False

        for rect, token_idx, available in self.token_selection_rects:
            if rect.collidepoint(pos):
                if self.token_selection_is_ai:
                    for i, human_token in enumerate(self.player_token_indices):
                        if human_token == token_idx:
                            self.player_token_indices[i] = self.ai_token_indices[
                                self.token_selection_for_player
                            ]
                            self.ai_token_indices[self.token_selection_for_player] = (
                                token_idx
                            )
                            self.token_selection_active = False
                            return False

                    for i, ai_token in enumerate(self.ai_token_indices):
                        if (
                            ai_token == token_idx
                            and i != self.token_selection_for_player
                        ):
                            self.ai_token_indices[i] = self.ai_token_indices[
                                self.token_selection_for_player
                            ]
                            self.ai_token_indices[self.token_selection_for_player] = (
                                token_idx
                            )
                            self.token_selection_active = False
                            return False

                    self.ai_token_indices[self.token_selection_for_player] = token_idx
                else:
                    for i, ai_token in enumerate(self.ai_token_indices):
                        if ai_token == token_idx:
                            self.ai_token_indices[i] = self.player_token_indices[
                                self.token_selection_for_player
                            ]
                            self.player_token_indices[
                                self.token_selection_for_player
                            ] = token_idx
                            self.token_selection_active = False
                            return False

                    for i, human_token in enumerate(self.player_token_indices):
                        if (
                            human_token == token_idx
                            and i != self.token_selection_for_player
                        ):
                            self.player_token_indices[i] = self.player_token_indices[
                                self.token_selection_for_player
                            ]
                            self.player_token_indices[
                                self.token_selection_for_player
                            ] = token_idx
                            self.token_selection_active = False
                            return False

                    self.player_token_indices[self.token_selection_for_player] = (
                        token_idx
                    )

                self.token_selection_active = False
                return False

        return False

    def handle_motion(self, pos):
        self.human_minus_button.check_hover(pos)
        self.human_plus_button.check_hover(pos)
        self.ai_minus_button.check_hover(pos)
        self.ai_plus_button.check_hover(pos)
        self.start_button.check_hover(pos)
        self.back_button.check_hover(pos)

    def handle_key(self, event):
        if self.token_selection_active:
            if event.key == pygame.K_ESCAPE:
                self.token_selection_active = False
            elif event.key == pygame.K_LEFT:
                if self.token_selection_for_player >= 0:
                    current_indices = (
                        self.player_token_indices
                        if not self.token_selection_is_ai
                        else self.ai_token_indices
                    )
                    current_idx = current_indices[self.token_selection_for_player]
                    used_indices = self.player_token_indices + self.ai_token_indices
                    for i in range(current_idx - 1, -1, -1):
                        if i not in used_indices or i == current_idx:
                            if not self.token_selection_is_ai:
                                self.player_token_indices[
                                    self.token_selection_for_player
                                ] = i
                            else:
                                self.ai_token_indices[
                                    self.token_selection_for_player
                                ] = i
                            break
            elif event.key == pygame.K_RIGHT:
                if self.token_selection_for_player >= 0:
                    current_indices = (
                        self.player_token_indices
                        if not self.token_selection_is_ai
                        else self.ai_token_indices
                    )
                    current_idx = current_indices[self.token_selection_for_player]
                    used_indices = self.player_token_indices + self.ai_token_indices
                    for i in range(current_idx + 1, 6):
                        if i not in used_indices or i == current_idx:
                            if not self.token_selection_is_ai:
                                self.player_token_indices[
                                    self.token_selection_for_player
                                ] = i
                            else:
                                self.ai_token_indices[
                                    self.token_selection_for_player
                                ] = i
                            break
            elif event.key == pygame.K_RETURN:
                self.token_selection_active = False
            return False

        if self.active_input >= 0:
            if event.key == pygame.K_RETURN:
                self.active_input = -1
            elif event.key == pygame.K_BACKSPACE:
                if self.active_input < self.human_count:
                    name = self.player_names[self.active_input]
                    self.player_names[self.active_input] = (
                        name[:-1] if len(name) > 0 else ""
                    )
                else:
                    ai_idx = self.active_input - self.human_count
                    name = self.ai_names[ai_idx]
                    self.ai_names[ai_idx] = name[:-1] if len(name) > 0 else ""
            elif event.key == pygame.K_TAB:
                if event.mod & pygame.KMOD_SHIFT:
                    self.active_input = (self.active_input - 1) % (
                        self.human_count + self.ai_count
                    )
                else:
                    self.active_input = (self.active_input + 1) % (
                        self.human_count + self.ai_count
                    )
            elif event.key == pygame.K_UP:
                self.active_input = (self.active_input - 1) % (
                    self.human_count + self.ai_count
                )
            elif event.key == pygame.K_DOWN:
                self.active_input = (self.active_input + 1) % (
                    self.human_count + self.ai_count
                )
            elif event.key == pygame.K_ESCAPE:
                self.active_input = -1
            else:
                if self.active_input < self.human_count:
                    if len(self.player_names[self.active_input]) < 15:
                        self.player_names[self.active_input] += event.unicode
                else:
                    ai_idx = self.active_input - self.human_count
                    if len(self.ai_names[ai_idx]) < 15:
                        self.ai_names[ai_idx] += event.unicode
        else:
            if event.key == pygame.K_h:
                if (
                    event.mod & pygame.KMOD_SHIFT
                    and self.human_count < 5
                    and self.total_players < 5
                ):
                    self.human_count += 1
                    if len(self.player_names) < self.human_count:
                        self.player_names.append(f"Human Player {self.human_count}")
                    self.update_player_lists()
                elif self.human_count > 1:
                    self.human_count -= 1
                    self.update_player_lists()
                self.total_players = self.human_count + self.ai_count

            elif event.key == pygame.K_a:
                if (
                    event.mod & pygame.KMOD_SHIFT
                    and self.ai_count < 4
                    and self.total_players < 5
                ):
                    self.ai_count += 1
                    self.update_player_lists()
                elif self.ai_count > 0:
                    self.ai_count -= 1
                    self.update_player_lists()
                self.total_players = self.human_count + self.ai_count

            elif event.key == pygame.K_t:
                if self.human_count > 0:
                    self.token_selection_active = True
                    self.token_selection_for_player = 0
                    self.token_selection_is_ai = False

            elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                if self.start_button.active:
                    return True

            elif event.key == pygame.K_ESCAPE:
                return "back"
        return False

    def get_player_info(self):
        all_names = (
            self.player_names[: self.human_count] + self.ai_names[: self.ai_count]
        )
        return (
            self.total_players,
            all_names,
            self.ai_count,
            self.player_token_indices + self.ai_token_indices,
        )


class PlayerSelectPage(BasePage):
    def __init__(self):
        super().__init__()
        self.input_font = font_manager.get_font(36)
        self.small_font = font_manager.get_font(24)
        self.selected_element = 0
        self.active_input = -1

        self.player_count = 2
        self.player_names = ["" for _ in range(5)]

        input_width = 300
        input_height = 50
        input_y_start = get_window_size()[1] // 2 - 100

        self.name_inputs = []
        for i in range(5):
            input_rect = pygame.Rect(
                (get_window_size()[0] - input_width) // 2,
                input_y_start + i * 70,
                input_width,
                input_height,
            )
            input_field = UIInput(input_rect, "", self.input_font)
            input_field.placeholder = f"Enter Player {i+1} name..."
            self.name_inputs.append(input_field)

        count_x_offset = 250
        self.minus_button = UIButton(
            pygame.Rect(
                get_window_size()[0] // 2 - count_x_offset, input_y_start - 80, 50, 50
            ),
            "-",
            self.button_font,
        )

        self.plus_button = UIButton(
            pygame.Rect(
                get_window_size()[0] // 2 + count_x_offset - 50,
                input_y_start - 80,
                50,
                50,
            ),
            "+",
            self.button_font,
        )

        button_width = 300
        button_height = 60
        self.continue_button = UIButton(
            pygame.Rect(
                (get_window_size()[0] - button_width) // 2,
                get_window_size()[1] - 120,
                button_width,
                button_height,
            ),
            "Continue",
            self.button_font,
        )

    def draw(self):
        self.draw_background()
        self.draw_title()

        section_title = self.button_font.render("Select Number of Players", True, WHITE)
        title_rect = section_title.get_rect(
            centerx=get_window_size()[0] // 2, y=get_window_size()[1] // 2 - 170
        )
        self.screen.blit(section_title, title_rect)

        count_text = self.button_font.render(str(self.player_count), True, WHITE)
        count_rect = count_text.get_rect(
            centerx=get_window_size()[0] // 2, y=get_window_size()[1] // 2 - 130
        )
        self.screen.blit(count_text, count_rect)

        self.minus_button.active = self.player_count > 2
        self.plus_button.active = self.player_count < 5
        self.minus_button.is_selected = self.selected_element == 0
        self.plus_button.is_selected = self.selected_element == 1
        self.minus_button.draw(self.screen)
        self.plus_button.draw(self.screen)

        name_section_title = self.button_font.render("Enter Player Names", True, WHITE)
        name_title_rect = name_section_title.get_rect(
            centerx=get_window_size()[0] // 2, y=get_window_size()[1] // 2 - 90
        )
        self.screen.blit(name_section_title, name_title_rect)

        for i in range(self.player_count):
            self.name_inputs[i].active = i == self.active_input
            self.name_inputs[i].is_selected = self.selected_element == i + 2
            self.name_inputs[i].error = not self.player_names[i].strip()
            if self.player_names[i]:
                self.name_inputs[i].text = self.player_names[i]
            self.name_inputs[i].draw(self.screen)

            if i == self.active_input:
                help_text = self.small_font.render(
                    "Type name and press Enter", True, LIGHT_GRAY
                )
                help_rect = help_text.get_rect(
                    left=self.name_inputs[i].rect.right + 10,
                    centery=self.name_inputs[i].rect.centery,
                )
                self.screen.blit(help_text, help_rect)

        can_continue = all(
            name.strip() for name in self.player_names[: self.player_count]
        )
        self.continue_button.active = can_continue
        self.continue_button.is_selected = self.selected_element == 7
        self.continue_button.draw(self.screen)

        controls = [
            "↑/↓ - Navigate fields",
            "Enter - Edit name",
            "Tab - Next field",
            "Escape - Cancel editing",
        ]

        y_offset = get_window_size()[1] - 80
        for hint in controls:
            hint_text = self.small_font.render(hint, True, LIGHT_GRAY)
            hint_rect = hint_text.get_rect(
                centerx=get_window_size()[0] // 2, y=y_offset
            )
            self.screen.blit(hint_text, hint_rect)
            y_offset += 20

        pygame.display.flip()

    def handle_click(self, pos):
        if self.minus_button.check_hover(pos) and self.player_count > 2:
            self.player_count -= 1
            return False

        if self.plus_button.check_hover(pos) and self.player_count < 5:
            self.player_count += 1
            return False

        for i in range(self.player_count):
            if self.name_inputs[i].rect.collidepoint(pos):
                self.active_input = i
                return False

        if self.continue_button.check_hover(pos):
            if all(name.strip() for name in self.player_names[: self.player_count]):
                return True

        self.active_input = -1
        return False

    def handle_motion(self, pos):
        self.minus_button.check_hover(pos)
        self.plus_button.check_hover(pos)
        self.continue_button.check_hover(pos)

    def handle_key(self, event):
        if self.active_input >= 0:
            if event.key == pygame.K_RETURN:
                if self.name_inputs[self.active_input].text.strip():
                    self.player_names[self.active_input] = self.name_inputs[
                        self.active_input
                    ].text.strip()
                self.active_input = -1
            elif event.key == pygame.K_BACKSPACE:
                if self.name_inputs[self.active_input].text:
                    self.name_inputs[self.active_input].text = self.name_inputs[
                        self.active_input
                    ].text[:-1]
                    self.player_names[self.active_input] = self.name_inputs[
                        self.active_input
                    ].text
            elif event.key == pygame.K_TAB:
                if self.name_inputs[self.active_input].text.strip():
                    self.player_names[self.active_input] = self.name_inputs[
                        self.active_input
                    ].text.strip()
                self.active_input = (self.active_input + 1) % self.player_count
                self.selected_element = self.active_input + 2
            elif event.key == pygame.K_ESCAPE:
                self.active_input = -1
            else:
                if len(self.name_inputs[self.active_input].text) < 15:
                    self.name_inputs[self.active_input].text += event.unicode
                    self.player_names[self.active_input] = self.name_inputs[
                        self.active_input
                    ].text
        else:
            if event.key in (pygame.K_UP, pygame.K_LEFT):
                self.selected_element = (self.selected_element - 1) % 8
                while (
                    self.selected_element >= 2
                    and self.selected_element < 7
                    and self.selected_element - 2 >= self.player_count
                ):
                    self.selected_element = (self.selected_element - 1) % 8
            elif event.key in (pygame.K_DOWN, pygame.K_RIGHT):
                self.selected_element = (self.selected_element + 1) % 8
                while (
                    self.selected_element >= 2
                    and self.selected_element < 7
                    and self.selected_element - 2 >= self.player_count
                ):
                    self.selected_element = (self.selected_element + 1) % 8
            elif event.key == pygame.K_RETURN:
                if self.selected_element == 0 and self.player_count > 2:
                    self.player_count -= 1
                elif self.selected_element == 1 and self.player_count < 5:
                    self.player_count += 1
                elif 2 <= self.selected_element <= 6:
                    self.active_input = self.selected_element - 2
                elif self.selected_element == 7:
                    if all(
                        name.strip() for name in self.player_names[: self.player_count]
                    ):
                        return True
            elif event.key == pygame.K_ESCAPE:
                self.active_input = -1
        return False

    def get_player_info(self):
        return self.player_count, [
            name.strip() for name in self.player_names[: self.player_count]
        ]


class HowToPlayPage(BasePage):
    def __init__(self, instructions=None):
        super().__init__(instructions=instructions)
        self.small_font = font_manager.get_font(24)

        button_width = 300
        button_height = 60
        self.back_button = UIButton(
            pygame.Rect(20, get_window_size()[1] - 80, 200, button_height),
            "Back",
            self.button_font,
        )

        self.shortcuts_button = UIButton(
            pygame.Rect(
                get_window_size()[0] - 320,
                get_window_size()[1] - 80,
                300,
                button_height,
            ),
            "Keyboard Shortcuts",
            self.button_font,
        )

        self.instructions = [
            "How to Play",
            "",
            "Become the wealthiest player by buying, renting, and developing properties!",
            "",
            "• Roll dice to move around the board",
            "• Buy properties when you land on them",
            "• Collect rent from other players",
            "• Build houses to increase property value",
        ]

    def draw(self):
        self.draw_background()
        self.draw_title()

        panel_width = 1000
        panel_height = get_window_size()[1] - 350
        panel_x = (get_window_size()[0] - panel_width) // 2
        panel_y = 320

        shadow_offset = 5
        shadow = pygame.Surface(
            (panel_width + shadow_offset * 2, panel_height + shadow_offset * 2),
            pygame.SRCALPHA,
        )
        pygame.draw.rect(shadow, (*BLACK, 128), shadow.get_rect(), border_radius=15)
        self.screen.blit(shadow, (panel_x - shadow_offset, panel_y - shadow_offset))

        pygame.draw.rect(
            self.screen,
            WHITE,
            pygame.Rect(panel_x, panel_y, panel_width, panel_height),
            border_radius=15,
        )

        title = self.instructions[0]
        title_surface = self.button_font.render(title, True, ACCENT_COLOR)
        title_rect = title_surface.get_rect(
            centerx=get_window_size()[0] // 2, y=panel_y + 15
        )
        self.screen.blit(title_surface, title_rect)

        y_offset = panel_y + 100

        for i in range(1, len(self.instructions)):
            line = self.instructions[i]

            if line == "":
                y_offset += 12
                continue
            elif line.endswith(":"):
                text_surface = self.button_font.render(line, True, ACCENT_COLOR)
                y_offset += 10
            else:
                text_surface = self.small_font.render(line, True, BLACK)

            text_rect = text_surface.get_rect(
                centerx=get_window_size()[0] // 2, y=y_offset
            )
            self.screen.blit(text_surface, text_rect)
            y_offset += 22

        self.back_button.draw(self.screen)
        self.shortcuts_button.draw(self.screen)

        hint_text = self.small_font.render(
            "Press ESC or BACKSPACE to return", True, LIGHT_GRAY
        )
        hint_rect = hint_text.get_rect(
            right=get_window_size()[0] - 20, y=get_window_size()[1] - 180
        )
        self.screen.blit(hint_text, hint_rect)

        pygame.display.flip()

    def handle_click(self, pos):
        if self.back_button.check_hover(pos):
            return True
        if self.shortcuts_button.check_hover(pos):
            return "keyboard_shortcuts"
        return None

    def handle_motion(self, pos):
        self.back_button.check_hover(pos)
        self.shortcuts_button.check_hover(pos)

    def handle_key(self, event):
        if event.key in [pygame.K_ESCAPE, pygame.K_BACKSPACE]:
            return True
        return None


class KeyboardShortcutsPage(BasePage):
    def __init__(self, instructions=None):
        super().__init__(instructions=instructions)
        self.small_font = font_manager.get_font(24)

        button_width = 200
        button_height = 60
        self.back_button = UIButton(
            pygame.Rect(20, get_window_size()[1] - 80, button_width, button_height),
            "Back",
            self.button_font,
        )

        self.shortcuts = [
            ["General", ""],
            ["Space/Enter", "Roll dice"],
            ["Q", "Exit game voluntarily"],
            ["Arrow Keys", "Move camera view"],
            ["ESC", "Close popups"],
            ["", ""],
            ["Property Buying", ""],
            ["Y/Enter", "Buy property"],
            ["N/ESC", "Pass on buying property"],
            ["", ""],
            ["Auction", ""],
            ["Number Keys", "Enter bid amount"],
            ["Backspace", "Delete last digit of bid"],
            ["Enter", "Submit bid"],
            ["ESC", "Pass in auction"],
            ["", ""],
            ["Property Management", ""],
            ["1", "Build house/hotel"],
            ["2", "Mortgage/Unmortgage property"],
            ["3", "Sell house/hotel"],
            ["4", "Put property up for auction"],
            ["ESC", "Exit property development mode"],
            ["", ""],
            ["Jail Options", ""],
            ["1", "Use Get Out of Jail Free card"],
            ["2", "Pay £50 fine"],
            ["3", "Try rolling doubles"],
            ["4", "Stay in jail (skip turns)"],
            ["", ""],
            ["Abridged Mode", ""],
            ["P", "Pause/Resume game"],
            ["T", "Show time statistics"],
        ]

    def draw(self):
        self.draw_background()

        title = "Keyboard Shortcuts"
        title_surface = self.title_font.render(title, True, DARK_RED)
        title_rect = title_surface.get_rect(centerx=get_window_size()[0] // 2, y=50)
        self.screen.blit(title_surface, title_rect)

        panel_width = 1000
        panel_height = get_window_size()[1] - 150
        panel_x = (get_window_size()[0] - panel_width) // 2
        panel_y = 120

        shadow_offset = 5
        shadow = pygame.Surface(
            (panel_width + shadow_offset * 2, panel_height + shadow_offset * 2),
            pygame.SRCALPHA,
        )
        pygame.draw.rect(shadow, (*BLACK, 128), shadow.get_rect(), border_radius=15)
        self.screen.blit(shadow, (panel_x - shadow_offset, panel_y - shadow_offset))

        pygame.draw.rect(
            self.screen,
            WHITE,
            pygame.Rect(panel_x, panel_y, panel_width, panel_height),
            border_radius=15,
        )

        left_column = []
        right_column = []

        current_category = None
        for shortcut in self.shortcuts:
            key, description = shortcut

            if description == "" and key != "":
                current_category = key

            if current_category in ["General", "Property Buying", "Auction"]:
                left_column.append(shortcut)
            else:
                right_column.append(shortcut)

        y_offset = panel_y + 10
        section_header_font = self.button_font
        column_width = panel_width // 2 - 20

        for i, (key, description) in enumerate(left_column):
            if key == "" and description == "":
                y_offset += 15
                continue

            if description == "":
                text_surface = section_header_font.render(key, True, ACCENT_COLOR)
                text_rect = text_surface.get_rect(x=panel_x + 30, y=y_offset)
                self.screen.blit(text_surface, text_rect)
                y_offset += 35
            else:
                key_width = 200
                key_surface = self.small_font.render(key, True, BLACK)
                key_rect = key_surface.get_rect(x=panel_x + 50, y=y_offset)
                self.screen.blit(key_surface, key_rect)

                desc_surface = self.small_font.render(description, True, BLACK)
                desc_rect = desc_surface.get_rect(
                    x=panel_x + 50 + key_width, y=y_offset
                )
                self.screen.blit(desc_surface, desc_rect)

                y_offset += 30

        y_offset = panel_y + 10
        right_x = panel_x + panel_width // 2

        for i, (key, description) in enumerate(right_column):
            if key == "" and description == "":
                y_offset += 15
                continue

            if description == "":
                text_surface = section_header_font.render(key, True, ACCENT_COLOR)
                text_rect = text_surface.get_rect(x=right_x + 30, y=y_offset)
                self.screen.blit(text_surface, text_rect)
                y_offset += 35
            else:
                key_width = 200
                key_surface = self.small_font.render(key, True, BLACK)
                key_rect = key_surface.get_rect(x=right_x + 50, y=y_offset)
                self.screen.blit(key_surface, key_rect)

                desc_surface = self.small_font.render(description, True, BLACK)
                desc_rect = desc_surface.get_rect(
                    x=right_x + 50 + key_width, y=y_offset
                )
                self.screen.blit(desc_surface, desc_rect)

                y_offset += 30

        self.back_button.draw(self.screen)

        hint_text = self.small_font.render(
            "Press ESC or BACKSPACE to return", True, LIGHT_GRAY
        )
        hint_rect = hint_text.get_rect(
            right=get_window_size()[0] - 20, y=get_window_size()[1] - 180
        )
        self.screen.blit(hint_text, hint_rect)

        pygame.display.flip()

    def handle_click(self, pos):
        if self.back_button.check_hover(pos):
            return True
        return None

    def handle_motion(self, pos):
        self.back_button.check_hover(pos)

    def handle_key(self, event):
        if event.key in [pygame.K_ESCAPE, pygame.K_BACKSPACE]:
            return True
        return None


class GameModePage(BasePage):
    def __init__(self, instructions=None):
        super().__init__(instructions=instructions)
        self.small_font = font_manager.get_font(24)

        self.game_mode = "full"
        self.time_limit = None

        self.custom_time_input = UIInput(
            pygame.Rect(
                (get_window_size()[0] - 300) // 2,
                get_window_size()[1] // 2 + 50,
                300,
                60,
            ),
            "30",
            self.button_font,
            active_color=TIME_COLOR,
        )

        self.custom_time_input.placeholder = "Enter time..."

        self.last_time_input = "30"

        mode_button_width = 400
        button_height = 60
        self.mode_button = UIButton(
            pygame.Rect(
                (get_window_size()[0] - mode_button_width) // 2,
                get_window_size()[1] // 2 - 120,
                mode_button_width,
                button_height,
            ),
            "Game Mode: Full Game",
            self.button_font,
            color=MODE_COLOR,
        )

        self.time_label = "Time Limit (minutes, max 180):"

        button_width = 300
        self.start_button = UIButton(
            pygame.Rect(
                (get_window_size()[0] - button_width) // 2,
                get_window_size()[1] - 120,
                button_width,
                button_height,
            ),
            "Start Game",
            self.button_font,
        )

        self.back_button = UIButton(
            pygame.Rect(20, get_window_size()[1] - 80, 200, button_height),
            "Back",
            self.button_font,
        )

        self.full_game_text = "Full Game: Last player standing wins"
        self.abridged_text = "Abridged Game: Highest value after time limit wins"
        self.input_error = None

    def draw(self):
        self.draw_background()
        self.draw_title()

        mode_title = self.button_font.render("Select Game Mode", True, WHITE)
        mode_title_rect = mode_title.get_rect(centerx=get_window_size()[0] // 2, y=100)
        self.screen.blit(mode_title, mode_title_rect)

        self.mode_button.rect.y = get_window_size()[1] // 2 - 120
        self.mode_button.text = (
            f"Game Mode: {'Abridged' if self.game_mode == 'abridged' else 'Full Game'}"
        )
        self.mode_button.draw(self.screen)

        mode_info = (
            self.abridged_text if self.game_mode == "abridged" else self.full_game_text
        )
        info_text = self.small_font.render(mode_info, True, LIGHT_GRAY)
        info_rect = info_text.get_rect(
            centerx=get_window_size()[0] // 2, top=self.mode_button.rect.bottom + 10
        )
        self.screen.blit(info_text, info_rect)

        if self.game_mode == "abridged":
            label_text = self.small_font.render(self.time_label, True, LIGHT_GRAY)
            label_rect = label_text.get_rect(
                centerx=get_window_size()[0] // 2,
                bottom=self.custom_time_input.rect.top - 15,
            )
            self.screen.blit(label_text, label_rect)

            self.custom_time_input.draw(self.screen)

            if self.input_error:
                error_text = self.small_font.render(self.input_error, True, ERROR_COLOR)
                error_rect = error_text.get_rect(
                    centerx=get_window_size()[0] // 2,
                    top=self.custom_time_input.rect.bottom + 5,
                )
                self.screen.blit(error_text, error_rect)
            else:
                try:
                    minutes = int(self.custom_time_input.text)
                    time_info = f"Game will end after {minutes} minutes"
                    time_text = self.small_font.render(time_info, True, LIGHT_GRAY)
                    time_rect = time_text.get_rect(
                        centerx=get_window_size()[0] // 2,
                        top=self.custom_time_input.rect.bottom + 5,
                    )
                    self.screen.blit(time_text, time_rect)
                except ValueError:
                    pass

        self.start_button.draw(self.screen)
        self.back_button.draw(self.screen)

        controls = [
            "Controls: ↑/↓ to navigate",
            "M - Change game mode",
        ]
        if self.game_mode == "abridged":
            controls.append("Click on time input to enter custom time")

        y_offset = get_window_size()[1] - 180
        for hint in controls:
            hint_text = self.small_font.render(hint, True, LIGHT_GRAY)
            hint_rect = hint_text.get_rect(right=get_window_size()[0] - 20, y=y_offset)
            self.screen.blit(hint_text, hint_rect)
            y_offset += 25

        pygame.display.flip()

    def handle_click(self, pos):
        if self.mode_button.check_hover(pos):
            self.game_mode = "abridged" if self.game_mode == "full" else "full"
            if self.game_mode == "abridged":
                try:
                    minutes = int(self.custom_time_input.text)
                    if minutes > 180:
                        minutes = 180
                        self.custom_time_input.text = "180"
                    self.time_limit = minutes * 60
                    print(f"Custom time limit set: {minutes} minutes")
                except ValueError:
                    self.time_limit = 30 * 60
                    print("Default time limit set: 30 minutes")
            else:
                self.time_limit = None
                print("Game mode changed to Full Game (no time limit)")
            return False

        if self.game_mode == "abridged" and self.custom_time_input.rect.collidepoint(
            pos
        ):
            self.custom_time_input.active = True
            return False

        if self.start_button.check_hover(pos):
            if self.game_mode == "abridged":
                try:
                    minutes = int(self.custom_time_input.text)
                    if minutes <= 0:
                        self.input_error = "Time must be greater than 0"
                        return False
                    if minutes > 180:
                        self.input_error = "Time cannot exceed 180 minutes"
                        self.custom_time_input.text = "180"
                        minutes = 180
                    self.time_limit = minutes * 60
                    self.input_error = None
                    print(f"Starting abridged game with time limit: {minutes} minutes")
                except ValueError:
                    self.input_error = "Please enter a valid number"
                    return False
            else:
                print("Starting full game (no time limit)")
            return True

        if self.back_button.check_hover(pos):
            return "back"

        self.custom_time_input.active = False
        return False

    def handle_motion(self, pos):
        self.mode_button.check_hover(pos)
        self.start_button.check_hover(pos)
        self.back_button.check_hover(pos)

    def handle_key(self, event):
        if self.custom_time_input.active and self.game_mode == "abridged":
            if event.key == pygame.K_RETURN:
                try:
                    minutes = int(self.custom_time_input.text)
                    if minutes <= 0:
                        self.input_error = "Time must be greater than 0"
                        return False
                    if minutes > 180:
                        self.input_error = "Time cannot exceed 180 minutes"
                        self.custom_time_input.text = "180"
                        minutes = 180
                    self.time_limit = minutes * 60
                    self.input_error = None
                    self.custom_time_input.active = False
                    print(f"Custom time limit set: {minutes} minutes")
                except ValueError:
                    self.input_error = "Please enter a valid number"
                return False
            elif event.key == pygame.K_ESCAPE or event.key == pygame.K_TAB:
                self.custom_time_input.active = False
                return False
            elif event.key == pygame.K_BACKSPACE:
                self.custom_time_input.text = self.custom_time_input.text[:-1]
                self.input_error = None
                return False
            elif event.unicode.isdigit() and len(self.custom_time_input.text) < 4:
                self.custom_time_input.text += event.unicode
                self.input_error = None
                return False
            return False

        if event.key == pygame.K_m:
            self.game_mode = "abridged" if self.game_mode == "full" else "full"
            if self.game_mode == "abridged":
                try:
                    minutes = int(self.custom_time_input.text)
                    if minutes > 180:
                        minutes = 180
                        self.custom_time_input.text = "180"
                    self.time_limit = minutes * 60
                    print(f"Custom time limit set: {minutes} minutes")
                except ValueError:
                    self.time_limit = 30 * 60
                    print("Default time limit set: 30 minutes")
            else:
                self.time_limit = None
                print("Game mode changed to Full Game (no time limit)")
        elif event.key == pygame.K_t and self.game_mode == "abridged":
            self.custom_time_input.active = True
        elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
            if self.game_mode == "abridged":
                try:
                    minutes = int(self.custom_time_input.text)
                    if minutes <= 0:
                        self.input_error = "Time must be greater than 0"
                        return False
                    if minutes > 180:
                        self.input_error = "Time cannot exceed 180 minutes"
                        self.custom_time_input.text = "180"
                        minutes = 180
                    self.time_limit = minutes * 60
                    self.input_error = None
                    print(f"Starting abridged game with time limit: {minutes} minutes")
                except ValueError:
                    self.input_error = "Please enter a valid number"
                    return False
            else:
                print("Starting full game (no time limit)")
            return True
        elif event.key == pygame.K_ESCAPE:
            return "back"
        return False

    def get_game_settings(self):
        settings = {"mode": self.game_mode, "time_limit": None}

        if self.game_mode == "abridged":
            try:
                minutes = int(self.custom_time_input.text)
                if minutes > 0:
                    if minutes > 180:
                        minutes = 180
                    settings["time_limit"] = minutes * 60
                    print(
                        f"Game settings: Abridged mode with {minutes} minutes time limit"
                    )
                else:
                    settings["time_limit"] = 30 * 60
                    print(
                        "Game settings: Abridged mode with default 30 minutes time limit (invalid input)"
                    )
            except ValueError:
                settings["time_limit"] = 30 * 60
                print(
                    "Game settings: Abridged mode with default 30 minutes time limit (invalid input)"
                )
        else:
            print("Game settings: Full game mode (no time limit)")

        return settings


class EndGamePage(BasePage):
    def __init__(
        self,
        winner_name,
        final_assets=None,
        bankrupted_players=None,
        voluntary_exits=None,
        tied_winners=None,
        lap_count=None,
    ):
        super().__init__()
        self.small_font = font_manager.get_font(24)
        self.winner_name = winner_name
        self.final_assets = final_assets or {}
        self.bankrupted_players = bankrupted_players or []
        self.voluntary_exits = voluntary_exits or []
        self.tied_winners = tied_winners or []
        self.lap_count = lap_count or {}

        self.screen = pygame.display.get_surface()
        if not self.screen:
            self.screen = pygame.display.set_mode(get_window_size())
            print("Created new surface for EndGamePage")
        else:
            print("Using existing surface for EndGamePage")

        try:
            endgame_bg_path = os.path.join(base_path, "assets/image/EndgamePageBG.jpg")
            self.original_endgame_bg = pygame.image.load(endgame_bg_path)
            print("Loaded EndgamePageBG.jpg successfully")
        except (pygame.error, FileNotFoundError) as e:
            print(f"Could not load end game background: {e}")
            self.original_endgame_bg = None

        button_width = 300
        button_height = 60
        self.play_again_button = UIButton(
            pygame.Rect(
                (get_window_size()[0] - button_width) // 2,
                get_window_size()[1] - 100,
                button_width,
                button_height,
            ),
            "Play Again",
            self.button_font,
            color=SUCCESS_COLOR,
        )

        self.quit_button = UIButton(
            pygame.Rect(
                (get_window_size()[0] - button_width) // 2,
                get_window_size()[1] - 180,
                button_width,
                button_height,
            ),
            "Quit Game",
            self.button_font,
            color=ERROR_COLOR,
        )

        self.credits_button = UIButton(
            pygame.Rect(20, get_window_size()[1] - 100, 200, button_height),
            "Credits",
            self.button_font,
            color=MODE_COLOR,
        )

        self.confetti = []
        for _ in range(100):
            self.confetti.append(
                {
                    "x": random.randint(0, get_window_size()[0]),
                    "y": random.randint(-100, 0),
                    "speed": random.uniform(1, 3),
                    "size": random.randint(5, 15),
                    "color": random.choice(
                        [
                            (255, 223, 0),
                            (255, 0, 0),
                            (0, 255, 0),
                            (0, 0, 255),
                            (255, 0, 255),
                            (0, 255, 255),
                        ]
                    ),
                }
            )

    def draw(self):
        window_size = get_window_size()

        if hasattr(self, "original_endgame_bg") and self.original_endgame_bg:
            bg_width, bg_height = self.original_endgame_bg.get_size()
            window_width, window_height = window_size

            bg_aspect = bg_width / bg_height
            window_aspect = window_width / window_height

            if window_aspect > bg_aspect:
                scaled_width = window_width
                scaled_height = int(scaled_width / bg_aspect)
            else:
                scaled_height = window_height
                scaled_width = int(scaled_height * bg_aspect)

            pos_x = (window_width - scaled_width) // 2
            pos_y = (window_height - scaled_height) // 2

            scaled_bg = pygame.transform.scale(
                self.original_endgame_bg, (scaled_width, scaled_height)
            )
            self.screen.blit(scaled_bg, (pos_x, pos_y))

            overlay = pygame.Surface(window_size, pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            self.screen.blit(overlay, (0, 0))
        else:
            self.draw_background()

        for particle in self.confetti:
            particle["y"] += particle["speed"]
            if particle["y"] > get_window_size()[1]:
                particle["y"] = random.randint(-100, 0)
                particle["x"] = random.randint(0, get_window_size()[0])

            pygame.draw.rect(
                self.screen,
                particle["color"],
                (particle["x"], particle["y"], particle["size"], particle["size"]),
            )

        card_width = 900
        card_height = 600
        card_x = (get_window_size()[0] - card_width) // 2
        card_y = (get_window_size()[1] - card_height) // 2 - 30

        shadow = pygame.Surface((card_width + 8, card_height + 8), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (*BLACK, 128), shadow.get_rect(), border_radius=15)
        self.screen.blit(shadow, (card_x + 4, card_y + 4))

        pygame.draw.rect(
            self.screen,
            WHITE,
            pygame.Rect(card_x, card_y, card_width, card_height),
            border_radius=15,
        )

        winner_text = self.title_font.render("Game Over!", True, ACCENT_COLOR)
        self.screen.blit(
            winner_text,
            (card_x + (card_width - winner_text.get_width()) // 2, card_y + 40),
        )

        trophy_size = 60
        trophy_x = card_x + (card_width - trophy_size) // 2
        trophy_y = card_y + 100

        gold_color = (255, 215, 0)

        pygame.draw.rect(
            self.screen,
            gold_color,
            (trophy_x + 15, trophy_y + 45, 30, 15),
            border_radius=5,
        )

        pygame.draw.rect(
            self.screen, gold_color, (trophy_x + 25, trophy_y + 25, 10, 25)
        )

        pygame.draw.ellipse(self.screen, gold_color, (trophy_x + 10, trophy_y, 40, 30))

        pygame.draw.ellipse(self.screen, gold_color, (trophy_x, trophy_y + 10, 15, 20))
        pygame.draw.ellipse(
            self.screen, gold_color, (trophy_x + 45, trophy_y + 10, 15, 20)
        )

        if self.winner_name == "Tie" and self.tied_winners:
            winner_text = "It's a Tie!"
            winner_name = self.button_font.render(winner_text, True, SUCCESS_COLOR)
            self.screen.blit(
                winner_name,
                (card_x + (card_width - winner_name.get_width()) // 2, card_y + 180),
            )

            tied_text = self.small_font.render(
                f"Tied players: {', '.join(self.tied_winners)}", True, ACCENT_COLOR
            )
            self.screen.blit(
                tied_text,
                (card_x + (card_width - tied_text.get_width()) // 2, card_y + 220),
            )
        else:
            winner_name = self.button_font.render(
                f"Winner: {self.winner_name}", True, SUCCESS_COLOR
            )
            self.screen.blit(
                winner_name,
                (card_x + (card_width - winner_name.get_width()) // 2, card_y + 180),
            )

        pygame.draw.line(
            self.screen,
            LIGHT_GRAY,
            (card_x + 70, card_y + 230),
            (card_x + card_width - 70, card_y + 230),
            2,
        )

        y_offset = card_y + 260
        if self.final_assets:
            assets_title = self.button_font.render("Final Assets", True, BLACK)
            self.screen.blit(
                assets_title,
                (card_x + (card_width - assets_title.get_width()) // 2, y_offset),
            )
            y_offset += 40

            sorted_assets = sorted(
                self.final_assets.items(), key=lambda x: x[1], reverse=True
            )
            col_width = (card_width - 100) // 2

            for i, (name, amount) in enumerate(sorted_assets):
                col = i % 2
                row = i // 2

                x_pos = card_x + 50 + col * col_width
                y_pos = y_offset + row * 35

                if self.tied_winners and name in self.tied_winners:
                    text_color = SUCCESS_COLOR
                elif name == self.winner_name and not self.tied_winners:
                    text_color = SUCCESS_COLOR
                else:
                    text_color = LIGHT_GRAY

                player_text = self.small_font.render(
                    f"{name}: £{amount:,}", True, text_color
                )
                self.screen.blit(player_text, (x_pos, y_pos))

        if self.bankrupted_players:
            y_offset = (
                y_offset
                + (len(sorted_assets) // 2 + (1 if len(sorted_assets) % 2 else 0)) * 35
                + 20
            )

            bankrupt_title = self.small_font.render(
                "Bankrupted Players:", True, ERROR_COLOR
            )
            self.screen.blit(bankrupt_title, (card_x + 50, y_offset))
            y_offset += 30

            bankrupt_text = self.small_font.render(
                f"{', '.join(self.bankrupted_players)}", True, ERROR_COLOR
            )
            self.screen.blit(bankrupt_text, (card_x + 70, y_offset))
            y_offset += 40

        if self.voluntary_exits:
            y_offset += 20
            voluntary_title = self.small_font.render(
                "Voluntary Exits:", True, ACCENT_COLOR
            )
            self.screen.blit(voluntary_title, (card_x + 50, y_offset))
            y_offset += 30

            voluntary_text = self.small_font.render(
                f"{', '.join(self.voluntary_exits)}", True, ACCENT_COLOR
            )
            self.screen.blit(voluntary_text, (card_x + 70, y_offset))
            y_offset += 40

        if self.lap_count:
            y_offset += 50

            lap_title = self.small_font.render("Laps Completed:", True, ACCENT_COLOR)
            self.screen.blit(lap_title, (card_x + 50, y_offset))
            y_offset += 30

            sorted_laps = sorted(
                self.lap_count.items(), key=lambda x: x[1], reverse=True
            )

            lap_text_parts = []
            for name, laps in sorted_laps:
                if (self.tied_winners and name in self.tied_winners) or (
                    name == self.winner_name and not self.tied_winners
                ):
                    lap_text_parts.append(f"{name}: {laps}")
                else:
                    lap_text_parts.append(f"{name}: {laps}")

            lap_text_combined = ", ".join(lap_text_parts)
            max_width = card_width - 140

            test_text = self.small_font.render(lap_text_combined, True, ACCENT_COLOR)
            if test_text.get_width() > max_width:
                current_line = ""
                current_y = y_offset

                for i, part in enumerate(lap_text_parts):
                    test_line = current_line + (", " if current_line else "") + part
                    test_render = self.small_font.render(test_line, True, ACCENT_COLOR)

                    if test_render.get_width() > max_width and current_line:
                        line_text = self.small_font.render(
                            current_line, True, ACCENT_COLOR
                        )
                        self.screen.blit(line_text, (card_x + 70, current_y))
                        current_y += 25
                        current_line = part
                    else:
                        current_line = (
                            test_line
                            if not current_line
                            else current_line + ", " + part
                        )

                if current_line:
                    line_text = self.small_font.render(current_line, True, ACCENT_COLOR)
                    self.screen.blit(line_text, (card_x + 70, current_y))
            else:
                lap_text = self.small_font.render(lap_text_combined, True, ACCENT_COLOR)
                self.screen.blit(lap_text, (card_x + 70, y_offset))

        self.play_again_button.draw(self.screen)
        self.quit_button.draw(self.screen)
        self.credits_button.draw(self.screen)

    def handle_click(self, pos):
        if self.play_again_button.check_hover(pos):
            return "play_again"
        elif self.quit_button.check_hover(pos):
            return "quit"
        elif self.credits_button.check_hover(pos):
            return "credits"
        return None

    def handle_motion(self, pos):
        self.play_again_button.check_hover(pos)
        self.quit_button.check_hover(pos)
        self.credits_button.check_hover(pos)

    def handle_key(self, event):
        if event.key == pygame.K_SPACE:
            return "play_again"
        elif event.key == pygame.K_ESCAPE:
            return "quit"
        elif event.key == pygame.K_c:
            return "credits"
        return None


class CreditsPage(BasePage):
    def __init__(self, instructions=None):
        super().__init__(instructions=instructions)
        self.small_font = font_manager.get_font(24)

        button_width = 300
        button_height = 60
        self.back_button = UIButton(
            pygame.Rect(20, get_window_size()[1] - 80, 200, button_height),
            "Back",
            self.button_font,
        )

        self.developers = [
            "Eric Shi",
            "Stuart Baker",
            "Lin Moe Hein",
            "Duncan Law",
            "Owen Chen",
        ]

        sound_manager.play_sound("credits")

    def draw(self):
        self.draw_background()

        title_text = self.title_font.render("Property Tycoon", True, ERROR_COLOR)
        title_rect = title_text.get_rect(centerx=get_window_size()[0] // 2, y=80)
        self.screen.blit(title_text, title_rect)

        panel_width = 700
        panel_height = get_window_size()[1] - 250
        panel_x = (get_window_size()[0] - panel_width) // 2
        panel_y = 160

        shadow_offset = 5
        shadow = pygame.Surface(
            (panel_width + shadow_offset * 2, panel_height + shadow_offset * 2),
            pygame.SRCALPHA,
        )
        pygame.draw.rect(shadow, (*BLACK, 128), shadow.get_rect(), border_radius=15)
        self.screen.blit(shadow, (panel_x - shadow_offset, panel_y - shadow_offset))

        pygame.draw.rect(
            self.screen,
            WHITE,
            pygame.Rect(panel_x, panel_y, panel_width, panel_height),
            border_radius=15,
        )

        credits_text = self.button_font.render("Developers", True, ACCENT_COLOR)
        credits_rect = credits_text.get_rect(
            centerx=get_window_size()[0] // 2, y=panel_y + 30
        )
        self.screen.blit(credits_text, credits_rect)

        pygame.draw.line(
            self.screen,
            LIGHT_GRAY,
            (panel_x + 80, credits_rect.bottom + 10),
            (panel_x + panel_width - 80, credits_rect.bottom + 10),
            2,
        )

        y_offset = credits_rect.bottom + 30
        line_spacing = 35

        for dev in self.developers:
            dev_text = self.button_font.render(dev, True, BLACK)
            dev_rect = dev_text.get_rect(centerx=get_window_size()[0] // 2, y=y_offset)
            self.screen.blit(dev_text, dev_rect)
            y_offset += line_spacing

        y_offset = panel_y + panel_height - 170

        thanks_text = self.button_font.render("Special Thanks", True, ACCENT_COLOR)
        thanks_rect = thanks_text.get_rect(
            centerx=get_window_size()[0] // 2, y=y_offset
        )
        self.screen.blit(thanks_text, thanks_rect)

        pygame.draw.line(
            self.screen,
            LIGHT_GRAY,
            (panel_x + 80, thanks_rect.bottom + 10),
            (panel_x + panel_width - 80, thanks_rect.bottom + 10),
            2,
        )

        quentin_text = self.small_font.render(
            "Mr Quentin Raffles @ Watson Games", True, BLACK
        )
        quentin_rect = quentin_text.get_rect(
            centerx=get_window_size()[0] // 2, y=thanks_rect.bottom + 15
        )
        self.screen.blit(quentin_text, quentin_rect)

        thanks_msg_text = self.small_font.render(
            "Thank you for playing our game!", True, BLACK
        )
        thanks_msg_rect = thanks_msg_text.get_rect(
            centerx=get_window_size()[0] // 2, y=quentin_rect.bottom + 15
        )
        self.screen.blit(thanks_msg_text, thanks_msg_rect)

        watson_text = self.small_font.render("Watson Games © 2025", True, BLACK)
        watson_rect = watson_text.get_rect(
            centerx=get_window_size()[0] // 2, y=thanks_msg_rect.bottom + 10
        )
        self.screen.blit(watson_text, watson_rect)

        self.back_button.draw(self.screen)

        hint_text = self.small_font.render(
            "Press ESC or BACKSPACE to return", True, LIGHT_GRAY
        )
        hint_rect = hint_text.get_rect(
            right=get_window_size()[0] - 20, y=get_window_size()[1] - 180
        )
        self.screen.blit(hint_text, hint_rect)

        pygame.display.flip()

    def handle_click(self, pos):
        if self.back_button.check_hover(pos):
            return True
        return None

    def handle_motion(self, pos):
        self.back_button.check_hover(pos)

    def handle_key(self, event):
        if event.key in [pygame.K_ESCAPE, pygame.K_BACKSPACE]:
            return True
        return None


class AIDifficultyPage(BasePage):
    def __init__(self, instructions=None):
        super().__init__(instructions=instructions)
        self.small_font = font_manager.get_font(24)
        button_width = 300
        button_height = 60
        center_y = get_window_size()[1] // 2

        self.easy_button = UIButton(
            pygame.Rect(
                (get_window_size()[0] - button_width) // 2,
                center_y - 50,
                button_width,
                button_height,
            ),
            "Easy",
            self.button_font,
            color=SUCCESS_COLOR,
        )

        self.hard_button = UIButton(
            pygame.Rect(
                (get_window_size()[0] - button_width) // 2,
                center_y + 50,
                button_width,
                button_height,
            ),
            "Hard",
            self.button_font,
            color=ERROR_COLOR,
        )

        self.back_button = UIButton(
            pygame.Rect(20, get_window_size()[1] - 80, 200, button_height),
            "Back",
            self.button_font,
        )

    def draw(self):
        self.draw_background()
        self.draw_title()

        difficulty_text = self.button_font.render("Select AI Difficulty", True, WHITE)
        text_rect = difficulty_text.get_rect(centerx=get_window_size()[0] // 2, y=100)
        self.screen.blit(difficulty_text, text_rect)

        easy_desc = self.small_font.render(
            "AI will make basic decisions", True, LIGHT_GRAY
        )
        easy_rect = easy_desc.get_rect(
            centerx=get_window_size()[0] // 2, y=self.easy_button.rect.bottom + 10
        )

        hard_desc = self.small_font.render(
            "AI will make strategic decisions", True, LIGHT_GRAY
        )
        hard_rect = hard_desc.get_rect(
            centerx=get_window_size()[0] // 2, y=self.hard_button.rect.bottom + 10
        )

        self.easy_button.draw(self.screen)
        self.hard_button.draw(self.screen)

        self.screen.blit(easy_desc, easy_rect)
        self.screen.blit(hard_desc, hard_rect)

        controls = ["Press E for Easy mode", "Press H for Hard mode"]
        y_offset = get_window_size()[1] - 180
        for hint in controls:
            hint_text = self.small_font.render(hint, True, LIGHT_GRAY)
            hint_rect = hint_text.get_rect(right=get_window_size()[0] - 20, y=y_offset)
            self.screen.blit(hint_text, hint_rect)
            y_offset += 25

        self.back_button.draw(self.screen)

        pygame.display.flip()

    def handle_click(self, pos):
        if self.back_button.check_hover(pos):
            return "back"
        if self.easy_button.check_hover(pos):
            return "easy"
        elif self.hard_button.check_hover(pos):
            return "hard"
        return None

    def handle_motion(self, pos):
        self.back_button.check_hover(pos)
        self.easy_button.check_hover(pos)
        self.hard_button.check_hover(pos)

    def handle_key(self, event):
        if event.key == pygame.K_ESCAPE:
            return "back"
        elif event.key in [pygame.K_e, pygame.K_RETURN]:
            return "easy"
        elif event.key == pygame.K_h:
            return "hard"
        return None


class DevelopmentNotification:
    def __init__(self, screen, player_name, font=None):
        self.screen = screen
        self.player_name = player_name
        self.window_size = screen.get_size()

        if font:
            self.font = font
        else:
            self.font = font_manager.get_font(24)

        self.dev_font = font_manager.get_font(26)

        self.text = f"{self.player_name}, you may modify properties now"
        self.sub_text = "Click Continue or press SPACE/ENTER to end your turn"

        self.padding = 20
        self.notification_text = self.dev_font.render(self.text, True, WHITE)
        self.sub_notification_text = self.font.render(self.sub_text, True, WHITE)

        text_width = max(
            self.notification_text.get_width(), self.sub_notification_text.get_width()
        )
        self.bg_width = text_width + self.padding * 2
        self.bg_height = (
            self.notification_text.get_height()
            + self.sub_notification_text.get_height()
            + self.padding * 3
        )

        self.x = (self.window_size[0] - self.bg_width) // 2
        self.y = 80

        button_width = 120
        button_height = 45
        button_margin = 20
        button_y = self.window_size[1] - button_height - button_margin

        self.continue_button = pygame.Rect(
            self.window_size[0] - button_width - button_margin,
            button_y,
            button_width,
            button_height,
        )

        self.dev_color = (0, 180, 120)
        self.button_hover = False

    def draw(self, mouse_pos):
        bg_surface = pygame.Surface((self.bg_width, self.bg_height), pygame.SRCALPHA)

        pygame.draw.rect(
            bg_surface, (*self.dev_color, 230), bg_surface.get_rect(), border_radius=15
        )

        for i in range(4):
            alpha = 80 - i * 20
            pygame.draw.rect(
                bg_surface,
                (*self.dev_color, alpha),
                (-i, -i, self.bg_width + i * 2, self.bg_height + i * 2),
                border_radius=15,
            )

        self.screen.blit(bg_surface, (self.x, self.y))

        self.screen.blit(
            self.notification_text, (self.x + self.padding, self.y + self.padding)
        )

        self.screen.blit(
            self.sub_notification_text,
            (
                self.x + self.padding,
                self.y + self.padding * 2 + self.notification_text.get_height(),
            ),
        )

        self.button_hover = self.continue_button.collidepoint(mouse_pos)
        button_color = BUTTON_HOVER if self.button_hover else ACCENT_COLOR

        pygame.draw.rect(
            self.screen, button_color, self.continue_button, border_radius=10
        )
        pygame.draw.rect(
            self.screen, (255, 255, 255), self.continue_button, 2, border_radius=10
        )

        button_text = self.font.render("Continue", True, WHITE)
        text_x = (
            self.continue_button.x
            + (self.continue_button.width - button_text.get_width()) // 2
        )
        text_y = (
            self.continue_button.y
            + (self.continue_button.height - button_text.get_height()) // 2
        )
        self.screen.blit(button_text, (text_x, text_y))

    def check_click(self, pos):
        if self.continue_button.collidepoint(pos):
            return True
        return False

    def handle_key(self, event):
        if event.key in [pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE]:
            return True
        return False


class AIEmotionUI:

    def __init__(self, screen, ai_player, game_instance):

        self.screen = screen
        self.ai_player = ai_player
        self.game = game_instance
        self.visible = False
        self.window_size = get_window_size()

        button_size = (48, 48)
        panel_width = 200
        panel_height = 120

        self.panel_rect = pygame.Rect(10, 340, panel_width, panel_height)

        self.happy_button_rect = pygame.Rect(
            self.panel_rect.x + 30,
            self.panel_rect.y + (self.panel_rect.height - button_size[1]) // 2,
            button_size[0],
            button_size[1],
        )

        self.angry_button_rect = pygame.Rect(
            self.panel_rect.x + panel_width - button_size[0] - 30,
            self.panel_rect.y + (self.panel_rect.height - button_size[1]) // 2,
            button_size[0],
            button_size[1],
        )

        self.happy_image = None
        self.angry_image = None
        self.happy_hover = False
        self.angry_hover = False

        try:
            happy_path = os.path.join(base_path, "assets/image/Happy.png")
            self.happy_image = pygame.image.load(happy_path)
            self.happy_image = pygame.transform.scale(self.happy_image, button_size)

            angry_path = os.path.join(base_path, "assets/image/Angry.png")
            self.angry_image = pygame.image.load(angry_path)
            self.angry_image = pygame.transform.scale(self.angry_image, button_size)
        except (pygame.error, FileNotFoundError):
            print("Could not load emotion king images")
            self.happy_image = pygame.Surface(button_size)
            self.happy_image.fill((50, 200, 50))
            self.angry_image = pygame.Surface(button_size)
            self.angry_image.fill((200, 50, 50))

        self.font = font_manager.get_font(18)

        self.happy_clicks_after_limit = 0
        self.angry_clicks_after_limit = 0
        self.easter_egg_threshold = 5
        self.youtube_url = (
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ&pp=ygUJcmljayByb2xs"
        )
        self.easter_egg_triggered = False

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def draw(self):
        if not self.visible:
            return

        if (
            not self.ai_player
            or not self.ai_player.is_ai
            or not hasattr(self.ai_player, "ai_controller")
            or not hasattr(self.ai_player.ai_controller, "mood_modifier")
        ):
            return

        pygame.draw.rect(self.screen, (*UI_BG, 220), self.panel_rect, border_radius=10)
        pygame.draw.rect(
            self.screen, ACCENT_COLOR, self.panel_rect, 2, border_radius=10
        )

        title_text = self.font.render("Taunt AI", True, WHITE)
        title_rect = title_text.get_rect(
            centerx=self.panel_rect.centerx, y=self.panel_rect.y + 5
        )
        self.screen.blit(title_text, title_rect)

        if self.happy_hover:
            glow = pygame.Surface(
                (self.happy_button_rect.width + 4, self.happy_button_rect.height + 4),
                pygame.SRCALPHA,
            )
            pygame.draw.rect(
                glow, (255, 255, 255, 128), glow.get_rect(), border_radius=5
            )
            self.screen.blit(
                glow, (self.happy_button_rect.x - 2, self.happy_button_rect.y - 2)
            )

        if self.angry_hover:
            glow = pygame.Surface(
                (self.angry_button_rect.width + 4, self.angry_button_rect.height + 4),
                pygame.SRCALPHA,
            )
            pygame.draw.rect(
                glow, (255, 255, 255, 128), glow.get_rect(), border_radius=5
            )
            self.screen.blit(
                glow, (self.angry_button_rect.x - 2, self.angry_button_rect.y - 2)
            )

        self.screen.blit(self.happy_image, self.happy_button_rect)
        self.screen.blit(self.angry_image, self.angry_button_rect)

        mood_value = getattr(self.ai_player.ai_controller, "mood_modifier", 0)
        mood_text = f"Mood: {mood_value:.2f}"
        mood_color = (
            int(255 * min(1, max(0, (mood_value + 0.3) / 0.6))),
            int(255 * min(1, max(0, (0.3 - mood_value) / 0.6))),
            50,
        )
        mood_surface = self.font.render(mood_text, True, mood_color)
        mood_rect = mood_surface.get_rect(
            centerx=self.panel_rect.centerx, bottom=self.panel_rect.bottom - 5
        )
        self.screen.blit(mood_surface, mood_rect)

        total_clicks = self.happy_clicks_after_limit + self.angry_clicks_after_limit
        if total_clicks > 0 and total_clicks < self.easter_egg_threshold:
            egg_text = f"{self.easter_egg_threshold - total_clicks} more..."
            egg_surface = self.font.render(egg_text, True, (255, 215, 0))
            egg_rect = egg_surface.get_rect(
                centerx=self.panel_rect.centerx, bottom=self.panel_rect.bottom - 25
            )
            self.screen.blit(egg_surface, egg_rect)

    def check_hover(self, pos):

        if not self.visible:
            return False

        self.happy_hover = self.happy_button_rect.collidepoint(pos)
        self.angry_hover = self.angry_button_rect.collidepoint(pos)

        return self.happy_hover or self.angry_hover

    def handle_click(self, pos):

        if not self.visible:
            return False

        if self.happy_button_rect.collidepoint(pos):
            mood_value = getattr(self.ai_player.ai_controller, "mood_modifier", 0)
            if mood_value >= 0.3:
                self.happy_clicks_after_limit += 1
                self._check_easter_egg()

            print(f"Happy button clicked for {self.ai_player.name} - making AI happier")
            sound_manager.play_sound("happy_click")
            self.game.update_ai_mood(self.ai_player.name, False)
            return True

        if self.angry_button_rect.collidepoint(pos):
            mood_value = getattr(self.ai_player.ai_controller, "mood_modifier", 0)
            if mood_value <= -0.3:
                self.angry_clicks_after_limit += 1
                self._check_easter_egg()

            print(f"Angry button clicked for {self.ai_player.name} - making AI angrier")
            sound_manager.play_sound("angry_click")
            self.game.update_ai_mood(self.ai_player.name, True)
            return True

        return False

    def handle_key(self, event):
        if not self.visible:
            return False

        if event.key == pygame.K_h:
            mood_value = getattr(self.ai_player.ai_controller, "mood_modifier", 0)
            if mood_value >= 0.3:
                self.happy_clicks_after_limit += 1
                self._check_easter_egg()

            sound_manager.play_sound("happy_click")
            self.game.update_ai_mood(self.ai_player.name, False)
            return True

        elif event.key == pygame.K_a:
            mood_value = getattr(self.ai_player.ai_controller, "mood_modifier", 0)
            if mood_value <= -0.3:
                self.angry_clicks_after_limit += 1
                self._check_easter_egg()

            sound_manager.play_sound("angry_click")
            self.game.update_ai_mood(self.ai_player.name, True)
            return True

        return False

    def _check_easter_egg(self):
        total_clicks = self.happy_clicks_after_limit + self.angry_clicks_after_limit

        if total_clicks >= self.easter_egg_threshold and not self.easter_egg_triggered:
            try:
                webbrowser.open(self.youtube_url)
                self.easter_egg_triggered = True
                self.happy_clicks_after_limit = 0
                self.angry_clicks_after_limit = 0
            except Exception as e:
                print(f"Error opening YouTube URL: {e}")
