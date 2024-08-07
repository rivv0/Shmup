import pygame
from pygame.locals import *
import random

# Initialize Pygame
pygame.init()

clock = pygame.time.Clock()
fps = 60
alien_cooldown = 1000
last_alien_shot = pygame.time.get_ticks()

screen_width = 600
screen_height = 800

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Space Invaders')


pygame.mixer.init()
pygame.font.init()

shoot_sound = pygame.mixer.Sound("audio/shoot.wav")
invader_killed_sound = pygame.mixer.Sound("audio/invaderkilled.wav")
spaceship_dead_sound = pygame.mixer.Sound("audio/explosion.wav")
bg = pygame.image.load("img/bg.png")

red = (255, 0, 0)
green = (0, 255, 0)

font = pygame.font.SysFont('Arial', 40)

score = 0

def draw_bg():
    screen.blit(bg, (0, 0))

def show_game_over():
    game_over_text = font.render("GAME OVER", True, (255, 255, 255))
    restart_text = font.render("Press R to Restart", True, (255, 255, 255))
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(game_over_text, (screen_width / 2 - game_over_text.get_width() / 2, screen_height / 2 - game_over_text.get_height() / 2))
    screen.blit(restart_text, (screen_width / 2 - restart_text.get_width() / 2, screen_height / 2 + 50))
    screen.blit(score_text, (screen_width / 2 - score_text.get_width() / 2, screen_height / 2 + 100))

def show_you_win():
    win_text = font.render("YOU WIN!", True, (255, 255, 255))
    restart_text = font.render("Press R to Play Again", True, (255, 255, 255))
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(win_text, (screen_width / 2 - win_text.get_width() / 2, screen_height / 2 - win_text.get_height() / 2))
    screen.blit(restart_text, (screen_width / 2 - restart_text.get_width() / 2, screen_height / 2 + 50))
    screen.blit(score_text, (screen_width / 2 - score_text.get_width() / 2, screen_height / 2 + 100))

def draw_score():
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

class Spaceship(pygame.sprite.Sprite):
    def __init__(self, x, y, health):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/spaceship.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.health_start = health
        self.health_remaining = health
        self.last_shot = pygame.time.get_ticks()
        
    
        self.double_shot = False
        self.double_shot_time = 0
        self.shield = False
        self.shield_time = 0

    def update(self):
        speed = 8
        cooldown = 500

        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= speed
        if key[pygame.K_RIGHT] and self.rect.right < screen_width:
            self.rect.x += speed

        time_now = pygame.time.get_ticks()

        if key[pygame.K_SPACE] and time_now - self.last_shot > cooldown:
            if self.double_shot:
                bullet1 = Bullets(self.rect.centerx - 10, self.rect.top)
                bullet2 = Bullets(self.rect.centerx + 10, self.rect.top)
                bullet_group.add(bullet1)
                bullet_group.add(bullet2)
            else:
                bullet = Bullets(self.rect.centerx, self.rect.top)
                bullet_group.add(bullet)
            self.last_shot = time_now
            shoot_sound.play()

        self.mask = pygame.mask.from_surface(self.image)

        
        pygame.draw.rect(screen, red, (self.rect.x, (self.rect.bottom + 10), self.rect.width, 15))
        if self.health_remaining > 0:
            pygame.draw.rect(screen, green, (self.rect.x, (self.rect.bottom + 10), (self.rect.width * (self.health_remaining / self.health_start)), 15))
        elif self.health_remaining <= 0:
            explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_group.add(explosion)
            spaceship_dead_sound.play()
            self.kill()

        if self.double_shot and time_now - self.double_shot_time > 5000:  # 5 seconds duration
            self.double_shot = False
        if self.shield and time_now - self.shield_time > 5000:  # 5 seconds duration
            self.shield = False

    def draw_powerup_timers(self):
        time_now = pygame.time.get_ticks()
        if self.double_shot:
            time_left = 5 - (time_now - self.double_shot_time) // 1000
            double_shot_text = font.render(f"Double Shot: {time_left}", True, (255, 255, 255))
            screen.blit(double_shot_text, (10, 50))
        if self.shield:
            time_left = 5 - (time_now - self.shield_time) // 1000
            shield_text = font.render(f"Shield: {time_left}", True, (255, 255, 255))
            screen.blit(shield_text, (10, 100))

class Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/bullet.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.y -= 5
        if self.rect.bottom < 0:
            self.kill()
        if pygame.sprite.spritecollide(self, alien_group, True):
            self.kill()
            global score
            score += 1
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)
            invader_killed_sound.play()

class Aliens(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/alien.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.horizontal_move_counter = 0
        self.move_direction = 1
        self.vertical_move = 10 
        self.vertical_move_counter = 0
        self.max_vertical_moves = 8
        self.speed = 2

    def update(self):
        global score 
        if score >= 10 :
            self.speed = 3
        self.rect.x += self.move_direction * self.speed
        self.horizontal_move_counter += self.speed
        if abs(self.horizontal_move_counter) > 75:
            self.move_direction *= -1
            self.horizontal_move_counter *= self.move_direction
            self.rect.y += self.vertical_move 
            self.vertical_move_counter += 1
        if self.vertical_move_counter >= self.max_vertical_moves:
            self.vertical_move *= -1
            self.vertical_move_counter = 0
        

class Alien_Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = image  # Use the image parameter for the bullet image
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.y += 2
        if self.rect.top > screen_height:
            self.kill()
        if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):
            if not spaceship.shield:
                self.kill()
                spaceship.health_remaining -= 1
                explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
                explosion_group.add(explosion)


class UFO(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/ufo.jpg")
        self.image = pygame.transform.scale(self.image, (50, 25))
        self.rect = self.image.get_rect()
        self.rect.x = 0  # Start from the left
        self.rect.y = 50  # Position above the aliens
        self.speed = 3
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        self.rect.x += self.speed

        if self.rect.left > screen_width or self.rect.right < 0:
            self.kill()
        time_now = pygame.time.get_ticks()
        if time_now - self.last_shot > 2000:
            bullet_image = pygame.image.load("img/ufo_bullet.png")  # Load UFO bullet image
            bullet_image = pygame.transform.scale(bullet_image, (100, 40))  # Scale as needed
            bullet = Alien_Bullets(self.rect.centerx, self.rect.bottom, bullet_image)
            alien_bullet_group.add(bullet)
            self.last_shot = time_now

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f"img/exp{num}.png")
            if size == 1:
                img = pygame.transform.scale(img, (20, 20))
            if size == 2:
                img = pygame.transform.scale(img, (40, 40))
            if size == 3:
                img = pygame.transform.scale(img, (160, 160))
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.counter = 0

    def update(self):
        explosion_speed = 3
        self.counter += 1

        if self.counter >= explosion_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]

        if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
            self.kill()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, kind):
        pygame.sprite.Sprite.__init__(self)
        self.kind = kind
        if self.kind == 'double_shot':
            self.image = pygame.image.load("img/double_shot.png")
            self.image = pygame.transform.scale(self.image, (50, 25))
        elif self.kind == 'shield':
            self.image = pygame.image.load("img/shield.jpg")
            self.image = pygame.transform.scale(self.image, (20, 30))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
    
    def update(self):
        self.rect.y += 2
        if self.rect.top > screen_height:
            self.kill()
        if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):
            self.kill()
            if self.kind == 'double_shot':
                spaceship.double_shot = True
                spaceship.double_shot_time = pygame.time.get_ticks()
            elif self.kind == 'shield':
                spaceship.shield = True
                spaceship.shield_time = pygame.time.get_ticks()

def create_aliens():
    global alien_group
    alien_group = pygame.sprite.Group()
    for row in range(5):
        for col in range(5):
            alien = Aliens(100 + col * 100, 100 + row * 70)
            alien_group.add(alien)

def reset_game():
    global spaceship, score
    score = 0
    spaceship_group.empty()
    bullet_group.empty()
    alien_group.empty()
    explosion_group.empty()
    power_up_group.empty()
    create_aliens()
    spaceship = Spaceship(int(screen_width / 2), screen_height - 100, 3)
    spaceship_group.add(spaceship)

spaceship_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
alien_bullet_group = pygame.sprite.Group()
ufo_group = pygame.sprite.Group()
power_up_group = pygame.sprite.Group()

create_aliens()
spaceship = Spaceship(int(screen_width / 2), screen_height - 100, 3)
spaceship_group.add(spaceship)

run = True
game_over = False
you_win = False

while run:
    clock.tick(fps)
    draw_bg()
    draw_score()
    time_now = pygame.time.get_ticks()

    if time_now - last_alien_shot > alien_cooldown and len(alien_bullet_group) < 5 and len(alien_group) > 0:
        attacking_alien = random.choice(alien_group.sprites())
        alien_bullet_image = pygame.image.load("img/bullet.png")  # Load alien bullet image
        alien_bullet_image = pygame.transform.scale(alien_bullet_image, (10, 20))  # Scale as needed
        alien_bullet = Alien_Bullets(attacking_alien.rect.centerx, attacking_alien.rect.bottom, alien_bullet_image)
        alien_bullet_group.add(alien_bullet)
        last_alien_shot = time_now

    if random.randint(0, 500) == 0 and not any(isinstance(sprite, UFO) for sprite in ufo_group.sprites()):
        ufo = UFO()
        ufo_group.add(ufo)

    if random.randint(0, 1000) == 0 and len(power_up_group) < 3:  # Limit number of power-ups on screen
        kind = random.choice(['double_shot', 'shield'])
        power_up = PowerUp(random.randint(0, screen_width), 0, kind)
        power_up_group.add(power_up)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN and (game_over or you_win):
            if event.key == pygame.K_r:
                game_over = False
                you_win = False
                reset_game()

    if not game_over and not you_win:
        spaceship.update()
        spaceship.draw_powerup_timers()
        bullet_group.update()
        alien_group.update()
        alien_bullet_group.update()
        explosion_group.update()
        ufo_group.update()
        power_up_group.update()
    elif game_over:
        show_game_over()
    elif you_win:
        show_you_win()

    spaceship_group.draw(screen)
    bullet_group.draw(screen)
    alien_group.draw(screen)
    alien_bullet_group.draw(screen)
    explosion_group.draw(screen)
    ufo_group.draw(screen)
    power_up_group.draw(screen)

    if not spaceship.alive():
        game_over = True

    if len(alien_group) == 0 and not game_over:
        you_win = True

    pygame.display.update()

pygame.quit()

