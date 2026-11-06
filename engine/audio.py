"""
engine/audio.py

Gestor de audio: música de fondo y efectos de sonido.
Si el sistema no tiene audio, el gestor queda desactivado pero el juego
sigue funcionando.
"""

import pygame
from engine.shared_assets import MUSIC_VOLUME


class AudioManager:
    """Carga y reproduce música y efectos de sonido."""

    def __init__(self, num_channels=16):
        self.sounds = {}
        self.active_channels = {}  # Nombre del sonido -> canal activo
        self.music_path = None
        self.music_volume = MUSIC_VOLUME
        self.enabled = True
        try:
            pygame.mixer.pre_init(44100, -16, 2, 512)
            pygame.mixer.init()
            pygame.mixer.set_num_channels(num_channels)
        except pygame.error as e:
            self.enabled = False
            self.sounds = None

    # ------------------------------- Efectos ------------------------------ #
    def load_sound(self, name, path):
        """Carga un efecto de sonido y lo asocia a un nombre clave."""
        if not self.enabled:
            return
        try:
            self.sounds[name] = pygame.mixer.Sound(path)
        except pygame.error as e:
            pass

    def play_sound(self, name, loops=0):
        """Reproduce un efecto de sonido en el primer canal libre."""
        if not self.enabled or name not in self.sounds:
            return None
        channel = pygame.mixer.find_channel()
        if channel:
            channel.play(self.sounds[name], loops)
            self.active_channels[name] = channel
            return channel
        return None

    def stop_sound(self, name):
        """Detiene un efecto de sonido específico."""
        if not self.enabled or name not in self.active_channels:
            return
        channel = self.active_channels[name]
        if channel:
            channel.stop()
            del self.active_channels[name]

    # -------------------------------- Música ------------------------------ #
    def load_music(self, path):
        """Deja preparada la ruta de la música de fondo."""
        if not self.enabled:
            return
        self.music_path = path

    def play_music(self, loops=-1, volume=None):
        """Reproduce la música de fondo en bucle."""
        if not self.enabled or not self.music_path:
            return
        try:
            pygame.mixer.music.load(self.music_path)
            if volume is not None:
                self.set_music_volume(volume)
            else:
                pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(loops)
        except pygame.error as e:
            pass

    def set_music_volume(self, volume):
        """Actualiza el volumen persistente de la música, entre 0 y 1."""
        self.music_volume = max(0.0, min(1.0, volume))
        if self.enabled:
            pygame.mixer.music.set_volume(self.music_volume)

    def stop_music(self):
        if not self.enabled:
            return
        pygame.mixer.music.stop()

    def pause_music(self):
        """Pausa la música de fondo actual."""
        if not self.enabled:
            return
        pygame.mixer.music.pause()

    def unpause_music(self):
        """Reanuda la música de fondo pausada."""
        if not self.enabled:
            return
        pygame.mixer.music.unpause()
