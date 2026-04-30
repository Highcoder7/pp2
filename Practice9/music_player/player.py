import pygame
import os

class MusicPlayer:
    def __init__(self, music_dir):
        self.music_dir = music_dir
        self.playlist = []
        self.current_track_index = 0
        self.is_playing = False
        self._load_playlist()

    def _load_playlist(self):
        if not os.path.exists(self.music_dir):
            os.makedirs(self.music_dir)
            print(f"Created directory {self.music_dir}. Please add .wav or .mp3 files.")
            return

        # recursively find valid audio files (including in sample_tracks directory)
        for root, dirs, files in os.walk(self.music_dir):
            for f in files:
                if f.endswith('.wav') or f.endswith('.mp3'):
                    self.playlist.append(os.path.join(root, f))
        
        self.playlist.sort()

    def play(self):
        if not self.playlist:
            return
        if not self.is_playing and not pygame.mixer.music.get_busy():
            pygame.mixer.music.load(self.playlist[self.current_track_index])
            pygame.mixer.music.play()
            self.is_playing = True
        elif not self.is_playing:
            pygame.mixer.music.unpause()
            self.is_playing = True

    def stop(self):
        pygame.mixer.music.pause()
        self.is_playing = False
        
    def full_stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False

    def next_track(self):
        if not self.playlist:
            return
        self.current_track_index = (self.current_track_index + 1) % len(self.playlist)
        self.is_playing = False
        self.play()

    def prev_track(self):
        if not self.playlist:
            return
        self.current_track_index = (self.current_track_index - 1) % len(self.playlist)
        self.is_playing = False
        self.play()

    def get_current_track_name(self):
        if not self.playlist:
            return "No tracks found"
        return os.path.basename(self.playlist[self.current_track_index])
