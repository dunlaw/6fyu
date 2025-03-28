# Property Tycoon Sound_Manager.py
# It contains the classes for the sound manager, such as the sound volume, the music volume.

import pygame
import os
import json


class SoundManager:
    def __init__(self):
        pygame.mixer.init()

        self.sound_volume = 0.7
        self.music_volume = 0.5

        self.sounds = {}

        self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.sound_path = os.path.join(self.base_path, "assets", "sound")
        self.music_path = os.path.join(self.base_path, "assets", "music")

        os.makedirs(self.sound_path, exist_ok=True)
        os.makedirs(self.music_path, exist_ok=True)

        self.settings_path = os.path.join(self.base_path, "settings.json")

        self.load_settings()

        self.missing_files = []

    def load_settings(self):
        try:
            if os.path.exists(self.settings_path):
                with open(self.settings_path, "r") as f:
                    settings = json.load(f)
                    if "sound_volume" in settings:
                        self.sound_volume = settings["sound_volume"]
                    if "music_volume" in settings:
                        self.music_volume = settings["music_volume"]
        except Exception as e:
            print(f"Error loading sound settings: {e}")

    def save_settings(self):
        try:
            existing_settings = {}
            if os.path.exists(self.settings_path):
                with open(self.settings_path, "r") as f:
                    existing_settings = json.load(f)

            existing_settings["sound_volume"] = self.sound_volume
            existing_settings["music_volume"] = self.music_volume

            with open(self.settings_path, "w") as f:
                json.dump(existing_settings, f)
        except Exception as e:
            print(f"Error saving sound settings: {e}")

    def load_sounds(self):
        self.missing_files = []

        required_sounds = {
            "dice_roll": "dice_roll.mp3",
            "buy_property": "buy_property.mp3",
            "collect_money": "collect_money.mp3",
            "pay_money": "pay_money.mp3",
            "jail": "jail.mp3",
            "build_house": "build_house.mp3",
            "menu_click": "menu_click.mp3",
            "game_start": "game_start.mp3",
            "game_over": "game_over.mp3",
            "card_draw": "card_draw.mp3",
            "happy_click": "happy_click.mp3",
            "angry_click": "angry_click.mp3",
            "countdown": "countdown.mp3",
            "credits": "credits.mp3",
            "watson_games": "watson_games.mp3",
            "group_present": "group_present.mp3",
        }

        for sound_name, file_name in required_sounds.items():
            file_path = os.path.join(self.sound_path, file_name)
            if os.path.exists(file_path):
                try:
                    self.sounds[sound_name] = pygame.mixer.Sound(file_path)
                    self.sounds[sound_name].set_volume(self.sound_volume)
                except Exception as e:
                    print(f"Error loading sound {file_name}: {e}")
                    self.missing_files.append(file_name)
            else:
                self.missing_files.append(file_name)
                print(f"Missing sound file: {file_name}")

        return len(self.missing_files) == 0

    def load_music(self, music_file="background_music.mp3"):
        music_path = os.path.join(self.music_path, music_file)

        if os.path.exists(music_path):
            try:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(self.music_volume)
                return True
            except Exception as e:
                print(f"Error loading music {music_file}: {e}")
                self.missing_files.append(music_file)
        else:
            print(f"Missing music file: {music_file}")
            self.missing_files.append(music_file)

        return False

    def play_sound(self, sound_name):
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
        else:
            print(f"Sound '{sound_name}' not loaded")

    def play_music(self, loop=-1):
        try:
            pygame.mixer.music.play(loop)
        except Exception as e:
            print(f"Error playing music: {e}")

    def stop_music(self):
        pygame.mixer.music.stop()

    def pause_music(self):
        pygame.mixer.music.pause()

    def unpause_music(self):
        pygame.mixer.music.unpause()

    def set_sound_volume(self, volume):
        self.sound_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sound_volume)
        self.save_settings()

    def set_music_volume(self, volume):
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
        self.save_settings()

    def get_missing_files(self):
        return self.missing_files


sound_manager = SoundManager()
