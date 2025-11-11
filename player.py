import pygame
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "assets")

class Player:
    def __init__(self, x, y, size=70):
        path = os.path.join(ASSET_DIR, "kirby.png")
        img = pygame.image.load(path).convert_alpha()
        self.image = pygame.transform.smoothscale(img, (size, size))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 300

    def move(self, keys, dt, screen_w, screen_h):
        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1

        self.rect.x += dx * self.speed * dt
        self.rect.y += dy * self.speed * dt
        self.rect.clamp_ip(pygame.Rect(0, 0, screen_w, screen_h))

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def collision_rect(self):
        return self.rect.inflate(-20, -20)
