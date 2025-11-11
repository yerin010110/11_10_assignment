import pygame
from pygame.locals import QUIT, MOUSEBUTTONDOWN
from player import Player
from enemy import Enemy
from item import Item
from background import Background
import random
import os
import json
import traceback

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "assets")
HIGHSCORE_FILE = os.path.join(BASE_DIR, "highscore.json")

class Game:
    def __init__(self, width=800, height=600, debug=False):
        self.debug = debug

        pygame.init()
        try:
            pygame.mixer.init()
        except:
            pass

        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Star Drift")
        self.clock = pygame.time.Clock()

        # 생명(하트)
        self.max_life = 3
        self.life = 3
        try:
            self.heart_img = pygame.image.load(os.path.join(ASSET_DIR, "heart.png")).convert_alpha()
            self.heart_img = pygame.transform.smoothscale(self.heart_img, (32, 32))
        except:
            self.heart_img = None

        # 게임 오브젝트
        self.bg = Background(self.screen)
        self.player = Player(self.width // 2, self.height - 80)
        self.enemies = []
        self.items = []

        # 타이머 및 점수
        self.spawn_timer = -0.5
        self.item_timer = 0.0
        self.score = 0
        self.invincible_time = 2.0
        self.running = True

        # 폰트
        self.font = pygame.font.SysFont(None, 28)
        self.title_font = pygame.font.SysFont(None, 48, bold=True)

        # 효과음 (BGM 제거)
        try:
            self.sfx_hit = pygame.mixer.Sound(os.path.join(ASSET_DIR, "sfx_hit.wav"))
        except:
            self.sfx_hit = None
        try:
            self.sfx_pick = pygame.mixer.Sound(os.path.join(ASSET_DIR, "sfx_pick.wav"))
        except:
            self.sfx_pick = None
        try:
            self.sfx_gameover = pygame.mixer.Sound(os.path.join(ASSET_DIR, "sfx_gameover.wav"))
        except:
            self.sfx_gameover = None

        self.highscore = self.load_highscore()

    # ✅ 하이스코어 로드
    def load_highscore(self):
        if os.path.exists(HIGHSCORE_FILE):
            try:
                with open(HIGHSCORE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f).get("highscore", 0)
            except:
                return 0
        return 0

    # ✅ 하이스코어 저장
    def save_highscore(self):
        try:
            with open(HIGHSCORE_FILE, "w", encoding="utf-8") as f:
                json.dump({"highscore": max(self.highscore, self.score)}, f)
        except:
            pass

    # 적 스폰
    def spawn_enemy(self):
        x = random.randint(50, self.width - 50)
        self.enemies.append(Enemy(self.width, spawn_x=x))

    # 아이템 스폰
    def spawn_item(self):
        self.items.append(Item(self.width))

    # 이벤트 처리
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False

    # ✅ 게임 업데이트
    def update(self, dt):
        if self.invincible_time > 0:
            self.invincible_time -= dt

        keys = pygame.key.get_pressed()
        self.player.move(keys, dt, self.width, self.height)

        self.spawn_timer += dt
        if self.spawn_timer > 0.8:
            self.spawn_enemy()
            self.spawn_timer = 0

        self.item_timer += dt
        if self.item_timer > 4.0:
            self.spawn_item()
            self.item_timer = 0

        # 충돌 처리
        for e in self.enemies[:]:
            e.update(dt)
            if e.rect.colliderect(self.player.rect) and self.invincible_time <= 0:
                if self.sfx_hit:
                    self.sfx_hit.play()
                self.life -= 1
                self.invincible_time = 1.5
                self.enemies.remove(e)
                if self.life <= 0:
                    self.running = False
                    return

        for it in self.items[:]:
            it.update(dt)
            if it.rect.colliderect(self.player.rect):
                if self.sfx_pick:
                    self.sfx_pick.play()
                self.items.remove(it)
                if getattr(it, "is_heal", False):
                    if self.life < self.max_life:
                        self.life += 1
                else:
                    self.score += it.value

        self.bg.update(dt)

    # ✅ 그리기
    def draw(self):
        self.screen.fill((0, 0, 0))
        self.bg.draw()
        for e in self.enemies:
            e.draw(self.screen)
        for it in self.items:
            it.draw(self.screen)
        self.player.draw(self.screen)

        # 하트 UI
        if self.heart_img:
            for i in range(self.life):
                self.screen.blit(self.heart_img, (10 + i * 36, 10))

        self.screen.blit(self.font.render(f"Score: {self.score}", True, (255,255,255)), (10, 50))
        self.screen.blit(self.font.render(f"High: {self.highscore}", True, (255,215,0)), (10, 75))

    # ✅ 게임 오버
    def game_over(self):
        if self.sfx_gameover:
            self.sfx_gameover.play()
        self.save_highscore()

        restart = pygame.Rect(300, 350, 100, 40)
        quit_btn = pygame.Rect(420, 350, 100, 40)

        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    exit()
                if event.type == MOUSEBUTTONDOWN:
                    if restart.collidepoint(event.pos):
                        self.reset_game()
                        return
                    if quit_btn.collidepoint(event.pos):
                        pygame.quit()
                        exit()

            self.screen.fill((0,0,0))
            txt = self.title_font.render("THE FORCE WAS NOT WITH YOU", True, (255,0,0))
            self.screen.blit(txt, (self.width//2 - txt.get_width()//2, 200))

            pygame.draw.rect(self.screen, (70,70,200), restart)
            pygame.draw.rect(self.screen, (200,70,70), quit_btn)
            self.screen.blit(self.font.render("Restart", True, (255,255,255)), (restart.x+10, restart.y+10))
            self.screen.blit(self.font.render("Quit", True, (255,255,255)), (quit_btn.x+25, quit_btn.y+10))

            pygame.display.flip()

    # ✅ 게임 리셋
    def reset_game(self):
        self.enemies.clear()
        self.items.clear()
        self.score = 0
        self.life = self.max_life
        self.running = True

    # ✅ ⭐⭐⭐ run() 이 Game 클래스 안에 제대로 들어가 있음 ⭐⭐⭐
    def run(self):
        while True:
            while self.running:
                dt = self.clock.tick(60) / 1000
                self.handle_events()
                self.update(dt)
                self.draw()
                pygame.display.flip()

            self.game_over()
