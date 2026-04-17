import pygame
import sys
import os
from player import MusicPlayer

def main():
    pygame.init()
    pygame.mixer.init()
    width, height = 600, 400
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Music Player")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    small_font = pygame.font.SysFont(None, 24)

    music_dir = os.path.join(os.path.dirname(__file__), "music")
    player = MusicPlayer(music_dir)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    player.play()
                elif event.key == pygame.K_s:
                    player.full_stop()
                elif event.key == pygame.K_n:
                    player.next_track()
                elif event.key == pygame.K_b:
                    player.prev_track()
                elif event.key == pygame.K_q:
                    running = False

        screen.fill((30, 30, 30))

        # UI Elements
        title_text = font.render(f"Track: {player.get_current_track_name()}", True, (255, 255, 255))
        status_text = font.render(
            "Status: Playing" if player.is_playing else "Status: Stopped", 
            True, 
            (0, 255, 0) if player.is_playing else (255, 0, 0)
        )
        
        instructions = [
            "P: Play",
            "S: Stop",
            "N: Next Track",
            "B: Previous Track",
            "Q: Quit"
        ]

        screen.blit(title_text, (50, 50))
        screen.blit(status_text, (50, 100))

        for i, text in enumerate(instructions):
            inst_surf = small_font.render(text, True, (200, 200, 200))
            screen.blit(inst_surf, (50, 200 + i * 30))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
