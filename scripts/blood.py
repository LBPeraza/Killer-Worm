import pygame, random
from vec2d import vec2d

class BloodParticle(object):
    def __init__(self, power, pos, ground_y):
        self.velocity = vec2d(random.random()*power, 0)
        self.velocity.angle = random.randint(0, 359)
        self.pos = pos + self.velocity / 2
        self.ground_y = ground_y
        self.radius = random.randint(2, 5)
        self.color = (random.randint(128, 200), 0, 0)

    def update(self):
        self.velocity.y += 2
        self.pos += self.velocity
        if self.pos.y > self.ground_y:
            self.pos.y = self.ground_y
            self.velocity *= 0.8
        self.world_rect = pygame.Rect(
            self.pos.x - self.radius, self.pos.y - self.radius,
            2*self.radius, 2*self.radius)

    def blit_me(self, screen, camera):
        if camera.rect_on_screen(self.world_rect):
            draw_pos = camera.world_to_screen(self.pos)
            draw_pos.x, draw_pos.y = int(draw_pos.x), int(draw_pos.y)
            rad = int(self.radius)
            pygame.draw.circle(screen, self.color, draw_pos, rad)

class BloodExplosion(object):
    def __init__(self, screen, amount, power, pos, ground_y):
        self.screen = screen
        self.s_w, self.s_h = screen.get_size()
        self.blood_pieces = [BloodParticle(power, pos, ground_y)
                                    for _ in xrange(amount)]
        self.time_left = 5

    def update(self, camera):
        i = 0
        count = len(self.blood_pieces)
        while i < count:
            part = self.blood_pieces[i]
            part.update()
            if abs(part.velocity.x) <= 1:
                part.radius *= 0.96
                if part.radius <= 0.5:
                    self.blood_pieces.pop(i)
                    count -= 1
                else: i += 1
            else: i += 1

    def blit_me(self, camera):
        for part in self.blood_pieces:
            part.blit_me(self.screen, camera)