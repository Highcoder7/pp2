import os
import wave
import struct
import math

# Create core asset directories
os.makedirs('Practice7/mickeys_clock/images', exist_ok=True)
os.makedirs('Practice7/music_player/music/sample_tracks', exist_ok=True)

try:
    import pygame
    pygame.init()
    # Create simple dummy Mickey Hand indicator
    surf = pygame.Surface((40, 200), pygame.SRCALPHA)
    pygame.draw.rect(surf, (0, 0, 0), (15, 0, 10, 100)) # Simple line pointing UP
    pygame.draw.circle(surf, (0, 0, 0), (20, 10), 15)   # Rounded tip
    pygame.image.save(surf, 'Practice7/mickeys_clock/images/mickey_hand.png')
except ImportError:
    print("Pygame not installed yet; skipping Mickey image generation.")

def generate_tone(filename, freq, duration=2.0):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    with wave.open(filename, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        for i in range(n_samples):
            value = int(32767.0 * 0.5 * math.sin(2.0 * math.pi * freq * i / sample_rate))
            data = struct.pack('<h', value)
            f.writeframesraw(data)

# Create some basic WAV sample tracks
generate_tone('Practice7/music_player/music/track1.wav', 440.0)    # A4 note
generate_tone('Practice7/music_player/music/track2.wav', 523.25)   # C5 note
print("Successfully generated placeholder dummy assets!")
