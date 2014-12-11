from scripts.pygamegame import PygameGame
from scripts.camera import Camera
import pygame, random
import scripts.enemies as enemies
from scripts.vec2d import vec2d
from scripts.worm import Worm, AIWorm
from scripts.blood import BloodExplosion
from scripts.text import FontManager
from scripts.sound import SoundManager

WHITE = (255, 255, 255)

class Background(pygame.sprite.Sprite):
    def __init__(self, screen, filename, screen_width, screen_height, camera):
        super(Background, self).__init__()
        self.screen = screen
        self.base_image = pygame.image.load(filename).convert_alpha()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.camera = camera

    def blit_me(self):
        left = self.camera.left % self.screen_width
        left_dest = pygame.Rect(self.screen_width-left+1, 0,
                        self.screen_width, self.screen_height)
        left_area = pygame.Rect(0, 0, left, self.screen_height)
        right_dest = pygame.Rect(0, 0, left, self.screen_height)
        right_area = pygame.Rect(left, 0, self.screen_width, self.screen_height)
        im = self.base_image
        self.screen.blit(im, left_dest, left_area)
        self.screen.blit(im, right_dest, right_area)

class KillerWorms2(PygameGame):
    def key_pressed(self, key):
        if key == pygame.K_w:
            self.enemies.append(enemies.Warthog.on_screen(
                    self.screen, self.cam, self.screen_width,
                    self.ground_y, self.bullets))
        elif key == pygame.K_s:
            self.enemies.append(enemies.Samus.on_screen(
                    self.screen, self.cam, self.screen_width,
                    self.ground_y, self.bullets))
        elif key == pygame.K_m:
            self.enemies.append(enemies.Megaman.on_screen(
                    self.screen, self.cam, self.screen_width,
                    self.ground_y))

    def init(self):
        Worm.init()
        pygame.display.set_icon(
                    pygame.image.load('images/icon.png').convert_alpha())
        enemies.init()
        self.arial30 = FontManager("arial", 30)
        self.cam = Camera(0, 0, self.screen_width, self.screen_height)
        self.ground = Background(self.screen, 'images/bg/close.png',
            self.screen_width, self.screen_height, self.cam)
        self.slow_cam = Camera(0, 0, self.screen_width, self.screen_height)
        self.sky = Background(self.screen, 'images/bg/far.jpg',
            self.screen_width, self.screen_height, self.slow_cam)
        self.mid_cam = Camera(0, 0, self.screen_width, self.screen_height)
        self.mid_ground = Background(self.screen, 'images/bg/mid.png',
            self.screen_width, self.screen_height, self.mid_cam)
        self.ground_y = 440
        self.worm = Worm(self.screen, vec2d(600, 665), 10, self.key_dict,
                        self.ground_y, self.cam)
        self.enemies = []
        self.bullets = []
        for _ in xrange(10):
            self.enemies.append(enemies.Megaman.on_screen(
                    self.screen, self.cam, self.screen_width,
                    self.ground_y))
        for _ in xrange(5):
            self.enemies.append(enemies.Samus.on_screen(
                    self.screen, self.cam, self.screen_width,
                    self.ground_y, self.bullets))
        for _ in xrange(3):
            self.enemies.append(enemies.Warthog.on_screen(
                    self.screen, self.cam, self.screen_width,
                    self.ground_y, self.bullets))
        self.worms = []
        for _ in xrange(10):
            self.new_worm()
        self.bloods = []
        self.sound_man = SoundManager()
        self.scream_time = 0.0
        self.next_scream = random.random()*0.5 + 0.25

    def new_worm(self, off_screen=False):
        x = random.randint(-self.cam.width, 2*self.cam.width)
        x += self.cam.center.x
        while off_screen and abs(self.cam.center.x - x < self.cam.width/2):
            x = random.randint(-self.cam.width, 2*self.cam.width)
            x += self.cam.center.x
        y = random.randint(self.ground_y+50, self.screen_height-100)
        self.worms.append(AIWorm(
                self.screen, vec2d(x, y), self.ground_y,
                self.cam))

    def update_enemies(self, time_passed):
        self.scream_time += time_passed
        enemy_count = len(self.enemies)
        enemies_alive = 0
        i = 0
        close = False
        while i < enemy_count:
            enemy = self.enemies[i]
            dist = enemy.update(time_passed, self.worm)
            if dist < 70: close = True
            if not enemy.dead: enemies_alive += 1
            if (dist < self.worm.head.radius+enemy.death_radius and
                not self.worm.head.in_ground() and
                not enemy.dead):
                if self.scream_time > self.next_scream:
                    enemy.death_sound(self.sound_man)
                    self.scream_time = 0
                    self.next_scream = random.random()*0.5 + 0.25
                enemy.die(self.worm.head.velocity)
                if isinstance(enemy, enemies.OrganicEnemy):
                    self.bloods.append(enemy.new_blood(self.ground_y))
            if enemy.gone:
                self.enemies.pop(i)
                enemy_count -= 1
            else:
                i += 1
        self.enemies_alive = enemies_alive
        return close

    def update_worms(self, time_passed):
        close = False
        worm_count = len(self.worms)
        i = 0
        while i < worm_count:
            worm = self.worms[i]
            dist = worm.update(time_passed, self.worm)
            if dist < 70: close = True
            if dist < self.worm.head.radius:
                self.worms.pop(i)
                worm_count -= 1
                self.worm.health = min(self.worm.max_health,
                                        self.worm.health+10)
                self.new_worm(True)
            else: i += 1
        return close

    def timer_fired(self, time_passed):
        if self.is_key_down(pygame.K_h): self.worm.health -= 10
        self.worm.update(time_passed)
        close = (self.update_enemies(time_passed) or
                 self.update_worms(time_passed))
        self.worm.fangs.opened = close
        b = 0
        blood_count = len(self.bloods)
        while blood_count > 7:
            self.bloods.pop(0)
            blood_count -= 1
        while b < blood_count:
            blood = self.bloods[b]
            blood.update(self.cam)
            if blood.blood_pieces == []:
                self.bloods.pop(b)
                blood_count -= 1
            else: b += 1
        b = 0
        bullet_count = len(self.bullets)
        while b < bullet_count:
            bullet = self.bullets[b]
            if not bullet.update(time_passed, self.ground_y):
                self.bullets.pop(b)
                bullet_count -= 1
            else: b += 1
        self.mid_cam.pos = self.cam.pos / 2
        self.slow_cam.pos = self.cam.pos / 4

    def draw_bg(self):
        self.sky.blit_me()
        self.mid_ground.blit_me()

    def draw_enemy_count(self):
        margin = 60
        text_y = self.screen_height - 50 - self.arial30.height
        text = "ENEMIES LEFT: %d" % self.enemies_alive
        width, height = self.arial30.size(text)
        text_x = self.screen_width-margin-width
        self.arial30.write(self.screen, text_x, text_y, text, (255, 255, 255))

    def draw_health(self):
        margin = 60
        width = self.screen_width - 2 * margin
        health_top = self.screen_height - 50
        text_y = health_top - self.arial30.height
        self.arial30.write(self.screen, margin, text_y, "HEALTH", WHITE)
        health_height = 20
        outline_rect = pygame.Rect(margin, health_top, width, health_height)
        health_width = 1.0*width*self.worm.health/self.worm.max_health
        health_rect = pygame.Rect(margin, health_top,
                                  health_width, health_height)
        health_red = min(230, 230*self.worm.health/(self.worm.max_health/3))
        health_color = (230, max(health_red, 0), max(health_red, 0))
        pygame.draw.rect(self.screen, health_color, health_rect)
        pygame.draw.rect(self.screen, WHITE, outline_rect, 3)

    def redraw_all(self):
        self.draw_bg()
        for enemy in self.enemies:
            enemy.blit_me()
        self.ground.blit_me()
        self.worm.draw_dirts()
        for blood in self.bloods:
            blood.blit_me(self.cam)
        for bullet in self.bullets:
            bullet.blit_me()
        for worm in self.worms:
            worm.blit_me()
        self.worm.draw()
        self.draw_health()
        self.draw_enemy_count()

    def run(self):
        self.fps = 30
        super(KillerWorms2, self).run(1200, 890, self.fps, "KILLER WORM")

KillerWorms2().run()