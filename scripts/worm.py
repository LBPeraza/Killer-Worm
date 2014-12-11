import pygame, math, random
from vec2d import vec2d

class WormPiece(pygame.sprite.Sprite):
    @classmethod
    def init(cls):
        cls.player_image = pygame.image.load('images/worm/worm_piece.png').convert_alpha()
        cls.ai_image = pygame.image.load('images/ai_piece.png').convert_alpha()

    def __init__(self, screen, pos, camera, is_AI=False):
        pygame.sprite.Sprite.__init__(self)
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()
        if is_AI: self.base_image = self.__class__.ai_image
        else: self.base_image = self.__class__.player_image
        self.image = self.base_image
        self.pos = pos
        self.old_pos = pos
        self.get_rect()
        self.direction = vec2d(1, 0)
        self.radius = 25
        self.camera = camera

    def get_rect(self):
        self.image_w, self.image_h = self.image.get_size()
        self.rect = self.image.get_rect().move(self.pos.x - self.image_w/2,
                                               self.pos.y - self.image_h/2)

    def update(self):
        self.image = pygame.transform.rotate(self.base_image,
                                             -self.direction.angle)
        self.get_rect()

    def blit_me(self):
        if self.camera.rect_on_screen(self.rect):
            draw_rect = self.camera.rect_world_to_screen(self.rect)
            self.screen.blit(self.image, draw_rect)

class AIWormHead(WormPiece):
    def __init__(self, screen, pos, top_y, bottom_y, camera):
        super(AIWormHead, self).__init__(screen, pos, camera, True)
        self.speed = random.random()*0.5 + 0.25
        self.velocity = vec2d(self.speed, 0)
        self.turn_speed = 5.0
        self.top_y, self.bottom_y = top_y, bottom_y
        self.elapsed = 0.0
        self.change_time = random.random()*2 + 0.5
        self.turn_direction = random.choice([-1, 1, 0])

    def update(self, time_passed):
        self.elapsed += time_passed
        if self.elapsed >= self.change_time:
            self.change_time = random.random()*2 + 0.5
            new_dir = random.choice([-1, 1, 0])
            while new_dir == self.turn_direction:
                new_dir = random.choice([-1, 1, 0])
            self.turn_direction = new_dir
        self.velocity.rotate(self.turn_direction * self.turn_speed)
        self.pos += self.velocity
        if self.pos.y < self.top_y: self.velocity.y = abs(self.velocity.y)
        if self.pos.y > self.bottom_y: self.velocity.y = -abs(self.velocity.y)
        self.direction = self.velocity.normalized()
        super(AIWormHead, self).update()

class WormHead(WormPiece):
    def __init__(self, screen, pos, key_dict, ground_y, camera):
        super(WormHead, self).__init__(screen, pos, camera)
        self.avg_speed = 2
        self.fast_speed = 14
        self.velocity = vec2d(self.avg_speed, 0)
        self.turn_speed = 10
        self.fly_turn_ratio = 0.5
        self.key_dict = key_dict
        self.ground_y = ground_y

    def in_ground(self):
        return self.pos.y > self.ground_y

    def update(self, time_passed):
        self.old_pos = vec2d(self.pos)
        turn_direction = (self.key_dict.get(pygame.K_RIGHT, False) -
                          self.key_dict.get(pygame.K_LEFT, False))
        speed_amt = self.key_dict.get(pygame.K_UP, False)
        if speed_amt == 1: velocity = self.fast_speed
        elif speed_amt == 0: velocity = self.avg_speed
        else: assert(False)
        turn_speed = (self.turn_speed *
                      (1 if self.in_ground() else self.fly_turn_ratio))
        self.velocity.rotate(turn_speed * turn_direction)
        if self.in_ground():
            self.velocity.length += (velocity-self.velocity.length)/10.0
        else:
            self.velocity.y += .5
            self.velocity.x *= 0.99
        self.direction = self.velocity.normalized()
        self.pos += self.velocity
        self.camera.pos.x += ((self.pos.x - self.camera.width/2 -
                                    self.camera.pos.x) / 20.0)
        if (self.pos.y > self.screen_height - self.radius):
            self.pos.y = self.screen_height - self.radius
            self.velocity.y *= 0
        super(WormHead, self).update()

class Fangs(pygame.sprite.Sprite):
    def __init__(self, screen, head, filename, camera):
        pygame.sprite.Sprite.__init__(self)
        self.screen = screen
        self.screen_width, sh = self.screen.get_size()
        self.base_image_top = pygame.image.load(filename).convert_alpha()
        self.base_image_bottom = pygame.transform.flip(self.base_image_top,
                                                       False, True)
        self.pos_angle = 60
        self.fang_angle = 0
        self.open_angle = 70
        self.head = head
        self.pos = head.pos
        self.get_fang_pos()
        self.update_images()
        self.opened = False
        self.camera = camera

    def get_fang_pos(self):
        base_angle = self.head.direction.angle
        radius = self.head.radius * 0.5
        top = vec2d(radius, 0)
        top.angle = base_angle - self.pos_angle
        bottom = vec2d(radius, 0)
        bottom.angle = base_angle + self.pos_angle
        self.top_pos = self.pos + top
        self.bot_pos = self.pos + bottom

    def update(self):
        angle = self.opened * self.open_angle
        self.fang_angle += (angle - self.fang_angle) / 2.0
        self.pos = self.head.pos
        self.get_fang_pos()
        self.update_images()

    def update_images(self):
        base_angle = self.head.direction.angle
        self.image_top = pygame.transform.rotate(self.base_image_top,
                                                -(base_angle-self.fang_angle))
        self.image_bot = pygame.transform.rotate(self.base_image_bottom,
                                                -(base_angle+self.fang_angle))
        self.get_rect()

    def get_rect(self):
        self.top_rect = self.image_top.get_rect()
        self.bot_rect = self.image_bot.get_rect()
        self.top_width, self.top_height = self.image_top.get_size()
        self.bot_width, self.bot_height = self.image_bot.get_size()
        union = self.top_rect.union(self.bot_rect)
        union_width, union_height = union.width, union.height
        self.rect = union.move(self.pos.x - union_width/2,
                               self.pos.y - union_height/2)

    def blit_me(self):
        top_pos = self.top_rect.move(
            self.top_pos.x - self.top_width/2,
            self.top_pos.y - self.top_height/2)
        bot_pos = self.bot_rect.move(
            self.bot_pos.x - self.bot_width/2,
            self.bot_pos.y - self.bot_height/2)
        top_rect = self.camera.rect_world_to_screen(top_pos)
        bot_rect = self.camera.rect_world_to_screen(bot_pos)
        self.screen.blit(self.image_top, top_rect)
        self.screen.blit(self.image_bot, bot_rect)

class WormLink(WormPiece):
    def __init__(self, screen, prev_piece, distance_from_prev, camera, is_AI=False):
        pos = prev_piece.pos - (distance_from_prev, 0)
        super(WormLink, self).__init__(screen, pos, camera, is_AI)
        self.prev_piece = prev_piece
        self.distance_from_prev = distance_from_prev

    def update(self, time_passed):
        self.old_pos = vec2d(self.pos)
        self.update_pos()
        self.direction = (self.prev_piece.pos - self.pos).normalized()
        super(WormLink, self).update()

    def update_pos(self):
        v1 = self.prev_piece.old_pos - self.pos
        v2 = self.prev_piece.pos - self.pos
        v1weight = 500
        v2weight = 1
        v1a = v1.angle
        v2a = v2.angle
        if v1a < -90 and v2a > 90: v1a += 360
        angle = ((v1weight*v1a*v1.length + v2weight*v2a*v2.length)/
                 (v1weight*v1.length+v2weight*v2.length))
        length = (self.prev_piece.pos-self.prev_piece.old_pos).length
        velocity = vec2d(length, 0)
        velocity.angle = angle
        self.pos += velocity
        self.correct_distance()

    def correct_distance(self):
        v1 = self.pos - self.prev_piece.pos
        v1.length = self.distance_from_prev
        self.pos = self.prev_piece.pos + v1

class AIWorm(object):
    def __init__(self, screen, pos, ground_y, camera):
        self.screen = screen
        sw, sh = screen.get_size()
        self.head = AIWormHead(screen, pos, ground_y+50, sh-100, camera)
        self.pos = vec2d(pos)
        dist = 5
        self.dist = dist
        self.links = [WormLink(self.screen, self.head, dist, camera, True)]
        for i in xrange(1, 5):
            self.links.append(WormLink(self.screen, self.links[i-1], dist,
                                       camera, True))
        self.camera = camera

    def update(self, time_passed, main_worm):
        self.head.update(time_passed)
        self.pos = self.head.pos
        add_w = 0
        if self.pos.x < main_worm.pos.x - 2*self.camera.width:
            self.pos.x += 4*self.camera.width
            add_w = 4*self.camera.width
        elif self.pos.x > main_worm.pos.x + 2*self.camera.width:
            self.pos.x -= 4*self.camera.width
            add_w = -4*self.camera.width
        for link in self.links:
            link.pos.x += add_w
            link.update(time_passed)
        return (main_worm.pos - self.pos).length

    def blit_me(self):
        for link in reversed(self.links):
            link.blit_me()
        self.head.blit_me()

class Worm(object):
    @classmethod
    def init(cls):
        WormPiece.init()

    def __init__(self, screen, head_pos, length, key_dict, ground_y, camera):
        self.screen = screen
        self.key_dict = key_dict
        self.head = WormHead(screen, head_pos, self.key_dict, ground_y, camera)
        self.pos = vec2d(head_pos)
        dist = 20
        self.dist = dist
        self.links = [WormLink(self.screen, self.head, dist, camera)]
        for i in xrange(1,length):
            self.links.append(WormLink(self.screen, self.links[i-1], dist,
                                       camera))
        self.ground_y = ground_y
        self.fangs = Fangs(self.screen, self.head,
                           'images/worm/worm_small_fang.png', camera)
        self.dirt_list = []
        self.dirt_duration = 50
        self.dirt_colors = [(38, 18, 6), (30, 15, 7), (40, 20, 10),
                            (12, 6, 3), (16, 8, 4)]
        self.camera = camera
        self.health = 500
        self.max_health = 500

    def in_ground(self):
        return self.head.pos.y > self.ground_y

    def new_dirt(self, pos):
        self.dirt_list.append([pos, random.choice(self.dirt_colors), 
                                    self.dirt_duration])

    def new_link(self):
        self.links.append(WormLink(self.screen, self.links[-1], self.dist,
                                       self.camera))
    def update(self, time_passed):
        self.head.update(time_passed)
        self.pos = vec2d(self.head.pos)
        self.fangs.update()
        dirt_count = len(self.dirt_list)
        i = 0
        self.health -= 0.1
        while i < dirt_count:
            self.dirt_list[i][2] *= 0.95
            if self.dirt_list[i][2] <= 2:
                self.dirt_list.pop(i)
                dirt_count -= 1
            else: i += 1
        for link in self.links:
            link.update(time_passed)
        if (self.links[-1].pos.y > self.ground_y + self.head.radius and
            self.head.velocity.length > self.head.avg_speed + 1):
            self.new_dirt(self.links[-1].pos)

    def draw_dirt(self, pos, color, size):
        pos = vec2d(pos)
        scale = 1.0 * size / self.dirt_duration
        size = int(self.head.radius*scale)
        pos = self.camera.world_to_screen(pos)
        pos.x, pos.y = int(pos.x), int(pos.y)
        pygame.draw.circle(self.screen, color, pos, size)

    def draw_dirts(self):
        for pos, color, duration in self.dirt_list:
            self.draw_dirt(pos, color, duration)

    def draw(self):
        for link in reversed(self.links):
            link.blit_me()
        self.head.blit_me()
        self.fangs.blit_me()