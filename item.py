import os
import pygame
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "assets")

class Item:
    def __init__(self, screen_width, size=32):
        path = os.path.join(ASSET_DIR, "item.png")
        img = pygame.image.load(path).convert_alpha()
        self.image = pygame.transform.smoothscale(img, (size, size))
        self.rect = self.image.get_rect(center=(random.randint(40, max(40, screen_width - 40)), -30))
        self.speed = 150
        self.value = 5
        self.is_heal = False

    def update(self, dt):
        self.rect.y += self.speed * dt

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def collision_rect(self):
        return self.rect.inflate(-8, -8)
