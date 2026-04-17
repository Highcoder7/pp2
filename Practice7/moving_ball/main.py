import pygame
import sys
from ball import Ball

def main():
    pygame.init()
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Moving Ball Game")
    clock = pygame.time.Clock()

    # Red ball with radius 25
    ball = Ball(width // 2, height // 2, 25, (255, 0, 0), width, height)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    ball.move(0, -1)
                elif event.key == pygame.K_DOWN:
                    ball.move(0, 1)
                elif event.key == pygame.K_LEFT:
                    ball.move(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    ball.move(1, 0)

        screen.fill((255, 255, 255))
        ball.draw(screen)
        pygame.display.flip()
        
        # Smooth frame rate
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
