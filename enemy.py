import os
import pygame
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "assets")

class Enemy:
    def __init__(self, screen_width, spawn_x=None, size=48):
        path = os.path.join(ASSET_DIR, "enemy.png")
        img = pygame.image.load(path).convert_alpha()
        self.image = pygame.transform.smoothscale(img, (size, size))

        if spawn_x is None:
            spawn_x = random.randint(50, max(50, screen_width - 50))

        self.rect = self.image.get_rect(center=(spawn_x, -160))
        self.speed = random.randint(120, 240)

    def update(self, dt):
        self.rect.y += self.speed * dt

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def collision_rect(self):
        return self.rect.inflate(-8, -8)
