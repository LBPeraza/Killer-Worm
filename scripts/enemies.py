import pygame, random, math
from animatedSprite import AnimatedSprite, ImageHolder
from blood import BloodExplosion
from vec2d import vec2d
from camera import Camera
from fire import Fire

def init():
    pygame.init()
    Megaman.init()
    Samus.init()
    Warthog.init()
    Bullet.init()

class Enemy(AnimatedSprite):
    @classmethod
    def init(cls, folder, *anims):
        cls.anims = []
        for anim in anims:
            cls.anims.append(
                ImageHolder.load_anim(folder, anim))

    @classmethod
    def on_screen(cls, screen, camera, screen_width, ground_pos):
        margin = 50
        x = random.randint(int(camera.left+margin), int(camera.right-margin))
        y = ground_pos - cls.y_sep
        return cls(screen, camera, (x, y), random.choice(["l", "r"]))

    def __init__(self, screen, camera, pos, name, anims):
        super(Enemy, self).__init__(screen, camera, pos, name, anims)
        self.speed = 10
        self.moving = False
        self.state = "idle"
        self.direction = "r"
        self.dead = False
        self.gone = False
        self.move_by_speed = False
        self.death_radius = 0

    def update(self, time_passed, worm, special=False):
        if not self.dead:
            if not special:
                if random.random() < 0.001:
                    self.change_direction()
                if random.random() < 0.005:
                    self.toggle_movement()
            self.update_anim()
            if self.move_by_speed:
                self.pos.x += self.speed
            elif self.moving:
                self.pos.x += self.speed * (
                    (self.direction == "r") - (self.direction == "l"))
            if self.pos.x < worm.pos.x - 2*self.camera.width:
                self.pos.x += 4*self.camera.width
            elif self.pos.x > worm.pos.x + 2*self.camera.width:
                self.pos.x -= 4*self.camera.width
        super(Enemy, self).update(time_passed)

    def change_direction(self):
        self.direction = "r" if self.direction == "l" else "l"

    def toggle_movement(self):
        self.moving = not self.moving

    def update_anim(self):
        self.current_anim = "%s_%s" % (self.state, self.direction)

    def die(self, worm_vel):
        self.dead = True

    def death_sound(self, sound_man):
        sound_man.play_sound_by_type("scream")

class OrganicEnemy(Enemy):
    def __init__(self, screen, camera, pos, name, blood_amt, blood_pwr,
                        anims):
        super(OrganicEnemy, self).__init__(
                    screen, camera, pos,name, anims)
        self.blood_amt = blood_amt
        self.blood_pwr = blood_pwr

    def new_blood(self, gp):
        return BloodExplosion(self.screen, self.blood_amt,
                              self.blood_pwr, self.pos, gp)

    def die(self, worm_vel): self.gone = True

class Megaman(OrganicEnemy):

    @classmethod
    def init(cls):
        super(Megaman, cls).init("megaman",
            "idle_l", "idle_r", "run_l", "run_r")

    y_sep = 17

    def __init__(self, screen, camera, pos, direction):
        super(Megaman, self).__init__(screen, camera, pos, "megaman", 40, 30,
                        Megaman.anims)
        self.speed = 4 + (random.random()*2 - 0.5)
        self.direction = direction
        self.current_anim = "idle_%s" % self.direction
        self.blood_amt = 40
        self.blood_pwr = 30
        self.play()

    def update(self, time_passed, worm):
        pos_sep = worm.pos - self.pos
        dist = pos_sep.length
        special = False
        min_dist = 70 if worm.in_ground() else 130
        if dist < min_dist:
            special = True
            if pos_sep.x < 0: self.direction = "r"
            else: self.direction = "l"
            if not self.moving: self.toggle_movement()
        super(Megaman, self).update(time_passed, worm, special)
        return dist

    def toggle_movement(self):
        super(Megaman, self).toggle_movement()

    def update_anim(self):
        self.state = "run" if self.moving else "idle"
        super(Megaman, self).update_anim()

class Bullet(AnimatedSprite):
    @classmethod
    def init(cls):
        cls.bullet_types = dict()
        for enemy in ['samus', 'warthog']:
            try:
                cls.bullet_types[enemy] = ImageHolder.load_anim('bullets', enemy)
            except: pass

    def __init__(self, screen, camera, pos, speed, direction, size,
                        color=(255,255,255), outline=(0,0,0),
                        max_time=10, bullet_type=None, flippable=False):
        super(Bullet, self).__init__(screen, camera, pos, 'bullet',
                                     Bullet.bullet_types.values())
        self.size = size
        self.color = color
        self.outline = outline
        self.velocity = speed * vec2d(direction).normalized()
        self.time_passed = 0.0
        self.max_time = max_time
        self.flip = random.choice([flippable, False])
        if bullet_type != None:
            self.rotation = vec2d(direction).angle
            self.current_anim = bullet_type
            self.play()

    def update(self, time_passed, ground_pos):
        if self.current_anim != None:
            super(Bullet, self).update(time_passed)
        self.pos += self.velocity
        self.time_passed += time_passed
        if self.pos.y >= ground_pos or self.time_passed > self.max_time:
            return False
        return True

    def blit_me(self):
        if self.camera.pt_on_screen(self.pos):
            if self.current_anim == None:
                draw_pos = camera.world_to_screen(self.pos)
                draw_pos.x, draw_pos.y = int(draw_pos.x), int(draw_pos.y)
                rad = self.size / 2
                pygame.draw.circle(screen, self.color, draw_pos, rad)
                pygame.draw.circle(screen, self.outline, draw_pos, rad, 1)
            else:
                super(Bullet, self).blit_me(self.flip)

class Samus(OrganicEnemy):
    @classmethod
    def init(cls):
        idles = ["idle_l_shoot_n", "idle_l_shoot_ul", "idle_l_shoot_u",
                 "idle_r_shoot_n", "idle_r_shoot_ur", "idle_r_shoot_u",
                 "idle_l_shoot_l", "idle_r_shoot_r"]
        runs = ["run_l_shoot_n", "run_l_shoot_l", "run_l_shoot_ul",
                "run_r_shoot_n", "run_r_shoot_r", "run_r_shoot_ur"]
        super(Samus, cls).init("samus", *(idles + runs))

    @classmethod
    def on_screen(cls, screen, camera, screen_width, ground_pos, bullets):
        margin = 50
        x = random.randint(int(camera.left+margin), int(camera.right-margin))
        y = ground_pos - cls.y_sep
        return cls(screen, camera, (x, y), random.choice(["l", "r"]), bullets)

    y_sep = 20

    def __init__(self, screen, camera, pos, direction, bullet_list):
        super(Samus, self).__init__(screen, camera, pos, "samus", 40, 30,
                        Samus.anims)
        self.speed = 3 + (random.random()*1.5 - 0.25)
        self.direction = direction
        self.current_anim = "idle_%s_shoot_n" % self.direction
        self.blood_amt = 45
        self.blood_pwr = 25
        self.shoot_angle = self.direction
        self.shoot_time = 0
        self.shoot_sep = random.random()*0.2 + 0.6
        self.shooting = False
        self.min_dist = 90 + random.randint(-15, 15)
        self.max_dist = 500 + random.randint(-40, 40)
        self.bullets = bullet_list
        self.play()

    def update(self, time_passed, worm):
        pos_sep = worm.pos - self.pos
        dist = pos_sep.length
        self.shooting = False
        special = False
        if 50 < dist < 600 and not worm.in_ground():
            special = True
            self.direction = "r" if pos_sep.x >= 0 else "l"
            if dist < self.min_dist:
                self.direction = "l" if pos_sep.x >= 0 else "r"
                self.moving = True
                self.shoot_time = 0
            else:
                self.moving = False if dist < self.max_dist else True
                angle = -pos_sep.angle
                if angle >= 0:
                    self.shooting = True
                    if 0 <= angle < 22.5: self.shoot_angle = "r"
                    elif 22.5 <= angle < 157.5:
                        if self.moving:
                            if 22.5 <= angle < 90: self.shoot_angle = "ur"
                            else: self.shoot_angle = "ul"
                        else:
                            if 22.5 <= angle < 67.5: self.shoot_angle = "ur"
                            elif 67.5 <= angle < 112.5: self.shoot_angle = "u"
                            else: self.shoot_angle = "ul"
                    else: self.shoot_angle = "l"
                self.shoot_time += time_passed
                if self.shoot_time > self.shoot_sep:
                    self.shoot_time = 0
                    self.shoot(worm)
        else: self.shoot_time = 0
        super(Samus, self).update(time_passed, worm, special)
        return dist

    def shoot(self, worm):
        s_ang = self.shoot_angle
        if s_ang == "u":
            bullet_dif = (-3, -25) if self.direction == "l" else (3, -25)
        elif s_ang == "ur": bullet_dif = (16, -22)
        elif s_ang == "ul": bullet_dif = (-16, -22)
        elif s_ang == "r": bullet_dif = (18, -10)
        elif s_ang == "l": bullet_dif = (-18, -10)
        elif s_ang == "n": assert(False)
        bullet_pos = self.pos + bullet_dif
        bullet_dir = worm.pos - bullet_pos
        self.bullets.append(Bullet(self.screen, self.camera, bullet_pos, 8, bullet_dir, 7,
            color=(255,128,0), bullet_type='samus', flippable=True))
#def __init__(self, screen, camera, pos, speed, direction, size,
 #                       color=(255,255,255), outline=(0,0,0),
  #                      max_time=10, bullet_type=None):
    def update_anim(self):
        movement = "run" if self.moving else "idle"
        shoot = self.shoot_angle if self.shooting else "n"
        direction = self.direction
        self.current_anim = "%s_%s_shoot_%s" % (movement, direction, shoot)

class Wheels(object):
    @classmethod
    def init(cls):
        cls.front_wheel = [ImageHolder.load_anim(cls.folder, "wheels/front")]
        cls.back_wheel = [ImageHolder.load_anim(cls.folder, "wheels/back")]

    def __init__(self, screen, camera, vehicle, pos_front, pos_back):
        self.vehicle = vehicle
        self.front_sep = vec2d(pos_front)
        self.back_sep = vec2d(pos_back)
        self.front = AnimatedSprite(screen, camera, vehicle.pos+pos_front, "f_wheel",
            self.__class__.front_wheel)
        self.back = AnimatedSprite(screen, camera, vehicle.pos-pos_back, "b_wheel",
            self.__class__.back_wheel)
        self.front.play()
        self.back.play()
        self.front_times = [1*time for time in self.front.current_anim.frame_times]
        self.back_times = [1*time for time in self.back.current_anim.frame_times]
        self.time_mult = 1.0

    def update(self, time_passed):
        if self.vehicle.direction == "r":
            front_sep, back_sep = self.front_sep, self.back_sep
        else:
            front_sep, back_sep = self.front_sep*(-1, 1), self.back_sep*(-1, 1)
        self.front.pos = self.vehicle.pos + front_sep
        self.back.pos = self.vehicle.pos + back_sep
        self.front.current_anim.frame_times = [self.time_mult*t for t in self.front_times]
        self.back.current_anim.frame_times = [self.time_mult*t for t in self.back_times]
        self.front.update(time_passed)
        self.back.update(time_passed)

    def blit_me(self):
        flip = self.vehicle.direction == "l"
        self.front.blit_me(flip)
        self.back.blit_me(flip)

    def pause(self):
        self.front.pause()
        self.back.pause()

    def unpause(self):
        self.front.unpause()
        self.back.unpause()

class WarthogWheels(Wheels):
    folder = "warthog"

    def __init__(self, screen, camera, warthog):
        super(WarthogWheels, self).__init__(screen, camera, warthog,
            (43, 31), (-38, 30))

class Warthog(Enemy):
    y_sep = 44
    want_directions = ["r", "l", "i"]

    @classmethod
    def on_screen(cls, screen, camera, screen_width, ground_pos, bullets):
        margin = 50
        x = random.randint(int(camera.left+margin), int(camera.right-margin))
        y = ground_pos - cls.y_sep
        return cls(screen, camera, (x, y), random.choice(["l", "r"]), bullets)

    @classmethod
    def init(cls):
        angles = ["straight", "u1", "u2", "u3", "d1", "d2"]
        anims = ([("front_%s"% angle) for angle in angles] + 
                 [("back_%s" % angle) for angle in angles] +
                 ["broken"])
        super(Warthog, cls).init("warthog", *anims)
        WarthogWheels.init()

    def __init__(self, screen, camera, pos, direction, bullets):
        super(Warthog, self).__init__(screen, camera, pos, "warthog", Warthog.anims)
        self.pos = vec2d(pos)
        self.ground_pos = self.pos.y + Warthog.y_sep
        self.screen = screen
        self.bullets = bullets
        self.wheels = WarthogWheels(screen, camera, self)
        self.max_speed = random.randint(9, 13)
        self.move_by_speed = True
        self.speed = 0
        self.want_direction = random.choice(Warthog.want_directions)
        self.turret_sep = vec2d(-32, -25)
        self.shoot_dir = "front"
        self.angle = "straight"
        self.death_radius = 10
        self.shot_timer = 0.0
        self.shoot_time = random.random()*0.5+0.25

    def alive_update(self, time_passed, worm):
        super(Warthog, self).update(time_passed, worm, True)
        chance = 0.05 if self.want_direction == "i" else 0.02
        if random.random() < chance:
            self.want_direction = random.choice(Warthog.want_directions)
        if self.want_direction == "r":
            self.speed += 0.25 if self.speed >= 0 else 0.5
        elif self.want_direction == "l":
            self.speed -= 0.25 if self.speed <= 0 else 0.5
        else:
            if self.speed > 0: self.speed -= 0.25
            elif self.speed < 0: self.speed += 0.25
        if self.speed > self.max_speed: self.speed = self.max_speed
        if self.speed < -self.max_speed: self.speed = -self.max_speed
        self.moving = self.speed != 0
        if self.moving:
            self.wheels.time_mult = self.max_speed / abs(2*self.speed)
            self.wheels.unpause()
        else: self.wheels.pause()
        self.wheels.update(time_passed)
        if self.update_angle(worm):
            self.shot_timer += time_passed
            if self.shot_timer >= self.shoot_time: self.shoot(worm)
        else: self.shot_timer = 0
        return (worm.pos - self.pos).length

    def dead_update(self, time_passed):
        self.velocity += 0, 0.5
        self.pos += self.velocity
        self.rot_speed *= 0.95
        self.rotation += self.rot_speed
        super(Warthog, self).update(time_passed, None)
        self.fire.update(time_passed, self.pos.y < self.ground_pos)
        if (self.pos.y > self.ground_pos + 100 and
            len(self.fire.fire_parts) == 0):
            self.gone = True
        return 100

    def update(self, time_passed, worm):
        if self.dead: return self.dead_update(time_passed)
        else: return self.alive_update(time_passed, worm)

    def update_angle(self, worm):
        t_sep = self.turret_sep if self.direction == "r" else self.turret_sep*(-1, 1)
        turret_pos = self.pos + t_sep
        pos_sep = worm.pos - turret_pos
        dist = pos_sep.length
        if dist > 800 or worm.in_ground(): self.angle = "straight"; return False
        angle = -pos_sep.angle
        if angle < -90: angle += 360
        dir_angle = -abs(angle - 90) + 90
        if dir_angle < -15: self.angle = "d2"
        elif -15 <= dir_angle < -5: self.angle = "d1"
        elif -5 <= dir_angle < 7.5: self.angle = "straight"
        elif 7.5 <= dir_angle < 20.5: self.angle = "u1"
        elif 20.5 <= dir_angle < 28: self.angle = "u2"
        else: self.angle = "u3"
        if pos_sep.x > 0:
            self.shoot_dir = "front" if self.direction == "r" else "back"
        else:
            self.shoot_dir = "back" if self.direction == "r" else "front"
        return True

    def shoot(self, worm):
        self.shot_timer = 0
        t_sep = self.turret_sep if self.direction == "r" else self.turret_sep*(-1, 1)
        turret_pos = self.pos + t_sep
        turret_len = 36
        if self.direction == "r":
            direction = 1 if self.shoot_dir == "front" else -1
        else:
            direction = -1 if self.shoot_dir == "front" else 1
        angles = {"straight": 0, "d1": -13.0, "d2": -20.7,
                  "u1": 15.5, "u2": 28.0, "u3": 38.2}
        d_x = direction * turret_len * math.cos(math.radians(angles[self.angle]))
        d_y = -turret_len * math.sin(math.radians(angles[self.angle]))
        bullet_pos = turret_pos + (d_x, d_y)
        self.bullets.append(Bullet(self.screen, self.camera, bullet_pos, 14, 
            worm.pos - turret_pos, 5, bullet_type="warthog"))

    def blit_me(self):
        super(Warthog, self).blit_me(self.direction == "l")
        if self.dead: self.fire.blit_me()
        else: self.wheels.blit_me()

    def update_anim(self):
        if self.speed > 0: self.direction = "r"
        elif self.speed < 0: self.direction = "l"
        self.current_anim = "%s_%s" % (self.shoot_dir, self.angle)

    def die(self, worm_vel):
        super(Warthog, self).die(worm_vel)
        self.current_anim = "broken"
        self.current_anim.play()
        self.current_anim.update(0, self.pos)
        self.velocity = vec2d(worm_vel.x, 0) + (0, random.randint(-10, -5))
        self.rot_speed = 30
        self.fire = Fire(self.screen, self.camera, self)
        self.fire.update(0)

    def death_sound(self, sound_man):
        super(Warthog, self).death_sound(sound_man)
        sound_man.play_sound_by_type("crunch")

if __name__ == "__main__":
    Warthog.init()