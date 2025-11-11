import os
import pygame

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "assets")

class Background:
    def __init__(self, screen):
        self.screen = screen
        path = os.path.join(ASSET_DIR, "bg.png")
        img = pygame.image.load(path).convert()
        w, h = screen.get_size()
        self.image = pygame.transform.smoothscale(img, (w, h))
        self.w, self.h = self.image.get_size()
        self.y = 0

    def update(self, dt):
        self.y += 50 * dt
        if self.y >= self.h:
            self.y = 0

    def draw(self):
        self.screen.blit(self.image, (0, -self.y))
        self.screen.blit(self.image, (0, self.h - self.y))
