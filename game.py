import pygame
from pygame.locals import QUIT, MOUSEBUTTONDOWN
from player import Player
from enemy import Enemy
from item import Item
from background import Background
import random
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "assets")
HIGHSCORE_FILE = os.path.join(BASE_DIR, "highscore.json")

class Game:
    def __init__(self, width=800, height=600):
        # Pygame 초기화
        pygame.init()
        try:
            pygame.mixer.init()
        except Exception:
            pass

        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Star Drift")
        self.clock = pygame.time.Clock()

        # 하트(생명) 시스템
        self.max_life = 3
        self.life = self.max_life
        try:
            self.heart_img = pygame.image.load(os.path.join(ASSET_DIR, "heart.png")).convert_alpha()
            self.heart_img = pygame.transform.smoothscale(self.heart_img, (32, 32))
        except Exception as e:
            print("하트 이미지 로드 실패:", e)
            self.heart_img = None

        # 객체 초기화
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

        # 사운드 로드 (예외 처리)
        try:
            self.sfx_hit = pygame.mixer.Sound(os.path.join(ASSET_DIR, "sfx_hit.wav"))
            self.sfx_pick = pygame.mixer.Sound(os.path.join(ASSET_DIR, "sfx_pick.wav"))
            self.sfx_gameover = pygame.mixer.Sound(os.path.join(ASSET_DIR, "sfx_gameover.wav"))
            self.bgm = os.path.join(ASSET_DIR, "bgm.wav")
            pygame.mixer.music.load(self.bgm)
            pygame.mixer.music.set_volume(0.6)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print("사운드 로드 실패:", e)
            self.sfx_hit = None
            self.sfx_pick = None
            self.sfx_gameover = None

        # 최고점 로드
        self.highscore = self.load_highscore()

        print("Game.__init__ 완료 running =", self.running, "inv_time =", self.invincible_time)

    # ----------------- 스코어 파일 -----------------
    def load_highscore(self):
        if os.path.exists(HIGHSCORE_FILE):
            try:
                with open(HIGHSCORE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("highscore", 0)
            except Exception:
                return 0
        return 0

    def save_highscore(self):
        try:
            best = max(self.highscore, self.score)
            with open(HIGHSCORE_FILE, "w", encoding="utf-8") as f:
                json.dump({"highscore": best}, f)
        except Exception as e:
            print("하이스코어 저장 실패:", e)

    # ----------------- 스폰 -----------------
    def spawn_enemy(self):
        avoid_rect = self.player.rect.inflate(160, 0)
        for _ in range(12):
            x = random.randint(50, self.width - 50)
            temp = self.player.rect.copy()
            temp.center = (x, -160)
            if not temp.colliderect(avoid_rect):
                self.enemies.append(Enemy(self.width, spawn_x=x))
                return
        x = random.randint(50, self.width - 50)
        self.enemies.append(Enemy(self.width, spawn_x=x))

    def spawn_item(self):
        self.items.append(Item(self.width))

    # ----------------- 이벤트 -----------------
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                # 게임 루프 종료 신호
                self.running = False

    # ----------------- 업데이트 -----------------
    def update(self, dt):
        # 무적시간 감소 처리
        if self.invincible_time > 0:
            self.invincible_time -= dt
            if self.invincible_time < 0:
                self.invincible_time = 0

        # 입력 및 플레이어 이동
        keys = pygame.key.get_pressed()
        self.player.move(keys, dt, self.width, self.height)

        # 적 생성 타이머
        self.spawn_timer += dt
        if self.spawn_timer > 0.8 and len(self.enemies) < 6:
            self.spawn_enemy()
            self.spawn_timer = 0.0

        # 아이템 생성 타이머
        self.item_timer += dt
        if self.item_timer > 4.0:
            self.spawn_item()
            self.item_timer = 0.0

        # 적 업데이트 및 충돌 처리
        for e in self.enemies[:]:
            e.update(dt)

            # 화면 아래로 벗어나면 제거 및 점수 증가
            if e.rect.top > self.height + 50:
                try:
                    self.enemies.remove(e)
                except ValueError:
                    pass
                self.score += 1
                continue

            # 충돌 판정: 적이 충분히 화면에 들어온 상태에서만, 무적시간이 0일 때만 판정
            enemy_cr = e.collision_rect()
            player_cr = self.player.collision_rect()
            if e.rect.top >= 50 and self.invincible_time <= 0:
                if enemy_cr.colliderect(player_cr):
                    # 충돌 이펙트
                    if self.sfx_hit:
                        try:
                            self.sfx_hit.play()
                        except:
                            pass

                    # 생명 감소 및 무적시간 부여
                    self.life -= 1
                    self.invincible_time = 1.5

                    # 충돌한 적 제거
                    try:
                        self.enemies.remove(e)
                    except ValueError:
                        pass

                    # 생명이 0 이하이면 running 표시만 변경
                    if self.life <= 0:
                        self.running = False
                        # game_over는 run() 에서 처리
                        return

        # 아이템 업데이트 및 충돌 처리
        for it in self.items[:]:
            it.update(dt)
            if it.rect.top > self.height + 50:
                try:
                    self.items.remove(it)
                except ValueError:
                    pass
            else:
                if it.collision_rect().colliderect(self.player.collision_rect()):
                    # 아이템 획득 사운드
                    if self.sfx_pick:
                        try:
                            self.sfx_pick.play()
                        except:
                            pass

                    # 제거 시도
                    try:
                        self.items.remove(it)
                    except ValueError:
                        pass

                    # 회복 아이템이면 생명 회복(최대 제한)
                    if getattr(it, "is_heal", False):
                        if self.life < self.max_life:
                            self.life += 1
                    else:
                        # 일반 아이템은 점수 추가
                        self.score += getattr(it, "value", 0)

        # 배경 업데이트
        self.bg.update(dt)

    # ----------------- 드로우 -----------------
    def draw(self):
        self.screen.fill((0, 0, 0))
        self.bg.draw()
        for e in self.enemies:
            e.draw(self.screen)
        for it in self.items:
            it.draw(self.screen)
        self.player.draw(self.screen)

        # 하트 표시 (좌상단)
        if self.heart_img:
            for i in range(self.life):
                x = 10 + i * 36
                y = 10
                self.screen.blit(self.heart_img, (x, y))

        score_surf = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_surf, (10, 48))
        hs_surf = self.font.render(f"High: {self.highscore}", True, (255, 255, 0))
        self.screen.blit(hs_surf, (10, 72))

    # ----------------- 게임오버 UI -----------------
    def game_over(self):
        # 음악 일시정지
        try:
            pygame.mixer.music.stop()
        except:
            pass

        # 최고점 갱신
        if self.score > self.highscore:
            self.highscore = self.score
            self.save_highscore()

        # 게임오버 사운드
        if self.sfx_gameover:
            try:
                self.sfx_gameover.play()
            except:
                pass

        # 간단한 게임오버 루프 (버튼: Restart / Quit)
        button_font = pygame.font.SysFont(None, 36)
        restart_rect = pygame.Rect(self.width//2 - 120, self.height//2 + 60, 100, 44)
        quit_rect = pygame.Rect(self.width//2 + 20, self.height//2 + 60, 100, 44)

        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    raise SystemExit
                if event.type == MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    if restart_rect.collidepoint(mx, my):
                        # 재시작: 게임 리셋 후 run 재진입
                        self.reset_game()
                        try:
                            pygame.mixer.music.play(-1)
                        except:
                            pass
                        return
                    if quit_rect.collidepoint(mx, my):
                        pygame.quit()
                        raise SystemExit

            # 그리기
            self.screen.fill((0, 0, 0))
            self.bg.draw()
            title = self.title_font.render("THE FORCE WAS NOT WITH YOU", True, (255, 50, 50))
            title_rect = title.get_rect(center=(self.width//2, self.height//2 - 20))
            self.screen.blit(title, title_rect)

            score_text = self.font.render(f"SCORE: {self.score}", True, (255,255,255))
            self.screen.blit(score_text, (self.width//2 - 60, self.height//2 + 10))
            high_text = self.font.render(f"HIGH: {self.highscore}", True, (255,215,0))
            self.screen.blit(high_text, (self.width//2 - 60, self.height//2 + 34))

            # 버튼 그리기
            pygame.draw.rect(self.screen, (70,70,200), restart_rect)
            pygame.draw.rect(self.screen, (200,70,70), quit_rect)
            self.screen.blit(button_font.render("Restart", True, (255,255,255)), (restart_rect.x+8, restart_rect.y+8))
            self.screen.blit(button_font.render("Quit", True, (255,255,255)), (quit_rect.x+24, quit_rect.y+8))

            pygame.display.flip()
            self.clock.tick(30)

    # ----------------- 게임 리셋 -----------------
    def reset_game(self):
        self.enemies.clear()
        self.items.clear()
        self.score = 0
        self.spawn_timer = -0.5
        self.item_timer = 0.0
        self.invincible_time = 2.0
        self.life = self.max_life
        self.running = True

    # ----------------- 메인 루프 -----------------
    def run(self):
        print("Game.run 시작 running =", self.running)
        frame = 0

        while True:
            # 게임 진행 루프
            while self.running:
                dt = self.clock.tick(60) / 1000.0
                frame += 1
                if frame % 60 == 0:
                    print(f"프레임 {frame} - enemies={len(self.enemies)} items={len(self.items)} score={self.score} inv_time={self.invincible_time:.2f} life={self.life}")

                self.handle_events()
                self.update(dt)
                self.draw()
                pygame.display.flip()

            # self.running 이 False면 여기로 도달합니다
            # 게임오버 화면 호출
            try:
                self.game_over()
            except SystemExit:
                break

            # 재시작을 위해 running이 True이면 다시 루프 진입
            if not self.running:
                break

        pygame.quit()
