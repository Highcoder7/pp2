import pygame

class Ball:
    def __init__(self, x, y, radius, color, screen_width, screen_height):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.speed = 20

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

    def move(self, dx, dy):
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed

        # Check boundary conditions before completing the move
        if new_x - self.radius >= 0 and new_x + self.radius <= self.screen_width:
            self.x = new_x
        if new_y - self.radius >= 0 and new_y + self.radius <= self.screen_height:
            self.y = new_y
