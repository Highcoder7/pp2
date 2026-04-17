import pygame
import math
import os
import datetime

class MickeyClock:
    def __init__(self, center_x, center_y):
        self.center_x = center_x
        self.center_y = center_y
        
        self.hand_img = None
        # Load the Mickey hand image if it exists
        img_path = os.path.join(os.path.dirname(__file__), "images", "mickey_hand.png")
        if os.path.exists(img_path):
            try:
                self.hand_img = pygame.image.load(img_path).convert_alpha()
            except Exception as e:
                print(f"Could not load image: {e}")

    def draw(self, screen):
        now = datetime.datetime.now()
        minutes = now.minute
        seconds = now.second

        # Clock logic: 60 units -> 360 degrees, so 1 unit = 6 degrees.
        # Minute hand rotation (smooth)
        minute_angle = minutes * 6 + (seconds * 0.1)
        self._draw_hand(screen, minute_angle, 150, (0, 0, 0), scale_factor=1.0)

        # Second hand rotation
        second_angle = seconds * 6
        self._draw_hand(screen, second_angle, 180, (255, 0, 0), scale_factor=0.8)

        # Draw the center point
        pygame.draw.circle(screen, (0, 0, 0), (self.center_x, self.center_y), 10)

    def _draw_hand(self, screen, angle_degrees, length, color, scale_factor):
        if self.hand_img:
            w, h = self.hand_img.get_size()
            scaled_img = pygame.transform.scale(self.hand_img, (int(w * scale_factor), int(h * scale_factor)))
            # Pygame's rotation is counter-clockwise. Negative angle makes it clockwise.
            rotated_img = pygame.transform.rotate(scaled_img, -angle_degrees)
            # Center the image as the pivot point
            rect = rotated_img.get_rect(center=(self.center_x, self.center_y))
            screen.blit(rotated_img, rect.topleft)
        else:
            # Fallback drawing lines if image not found
            # -90 degrees offset makes 0 degrees point straight UP (12 o'clock)
            rad_angle = math.radians(angle_degrees - 90)
            end_x = self.center_x + length * math.cos(rad_angle)
            end_y = self.center_y + length * math.sin(rad_angle)
            pygame.draw.line(screen, color, (self.center_x, self.center_y), (end_x, end_y), 5)
