import pygame
import constants
import math
import weapon

class Character():
  def __init__(self, x, y, health, mob_animations, char_type, boss, size):
    self.char_type = char_type
    self.boss = boss
    self.score = 0
    self.flip = False
    self.animation_list = mob_animations[char_type]
    self.frame_index = 0
    self.action = 0
    self.update_time = pygame.time.get_ticks()
    self.running = False
    self.health = health
    self.alive = True
    self.hit = False
    self.last_hit = pygame.time.get_ticks()
    self.last_attack = pygame.time.get_ticks()
    self.stunned = False
    self.image = self.animation_list[self.action][self.frame_index]
    self.rect = pygame.Rect(0, 0, constants.TILE_SIZE * size, constants.TILE_SIZE * size)
    self.rect.center = (x, y)

  def move(self, dx, dy,obstacle_tiles,exit_tile = None):
    screen_scroll = [0, 0]
    level_complete = False
    self.running = False

    if dx != 0 or dy != 0:
      self.running = True
    if dx < 0:
      self.flip = True
    if dx > 0:
      self.flip = False
    if dx != 0 and dy != 0:
      dx = dx * (math.sqrt(2) / 2)
      dy = dy * (math.sqrt(2) / 2)

    self.rect.x += dx
    for obstacle in obstacle_tiles:

      if obstacle[1].colliderect(self.rect):

        if dx > 0:
          self.rect.right = obstacle[1].left
        if dx < 0:
          self.rect.left = obstacle[1].right


    self.rect.y += dy
    for obstacle in obstacle_tiles:

      if obstacle[1].colliderect(self.rect):

        if dy > 0:
          self.rect.bottom = obstacle[1].top
        if dy < 0:
          self.rect.top = obstacle[1].bottom

    if self.char_type == 0:
      if exit_tile[1].colliderect(self.rect):

        exit_dist = math.sqrt(((self.rect.centerx - exit_tile[1].centerx) ** 2) + ((self.rect.centery - exit_tile[1].centery) ** 2))
        if exit_dist < 20:
          level_complete = True

      if self.rect.right > (constants.SCREEN_WIDTH - constants.SCROLL_THRESH):
        screen_scroll[0] = (constants.SCREEN_WIDTH - constants.SCROLL_THRESH) - self.rect.right
        self.rect.right = constants.SCREEN_WIDTH - constants.SCROLL_THRESH
      if self.rect.left < constants.SCROLL_THRESH:
        screen_scroll[0] = constants.SCROLL_THRESH - self.rect.left
        self.rect.left = constants.SCROLL_THRESH


      if self.rect.bottom > (constants.SCREEN_HEIGHT - constants.SCROLL_THRESH):
        screen_scroll[1] = (constants.SCREEN_HEIGHT - constants.SCROLL_THRESH) - self.rect.bottom
        self.rect.bottom = constants.SCREEN_HEIGHT - constants.SCROLL_THRESH
      if self.rect.top < constants.SCROLL_THRESH:
        screen_scroll[1] = constants.SCROLL_THRESH - self.rect.top
        self.rect.top = constants.SCROLL_THRESH
    return screen_scroll, level_complete

  def ai(self, player, obstacle_tiles,screen_scroll, fireball_image):
    clipped_line = ""
    stun_cooldown = 100
    ai_dx = 0
    ai_dy = 0
    fireball = None

    self.rect.x += screen_scroll[0]
    self.rect.y += screen_scroll[1]

    line_of_sight = ((self.rect.centerx, self.rect.centery), (player.rect.centerx, player.rect.centery))

    for obstacle in obstacle_tiles:
      if obstacle[1].clipline(line_of_sight):
        clipped_line = obstacle[1].clipline(line_of_sight)
    dist = math.sqrt(((self.rect.centerx - player.rect.centerx) ** 2) + ((self.rect.centery - player.rect.centery) ** 2))
    if not clipped_line and dist > constants.RANGE:
      if self.rect.centerx > player.rect.centerx:
        ai_dx = -constants.ENEMY_SPEED
      if self.rect.centerx < player.rect.centerx:
        ai_dx = constants.ENEMY_SPEED
      if self.rect.centery > player.rect.centery:
        ai_dy = -constants.ENEMY_SPEED
      if self.rect.centery < player.rect.centery:
        ai_dy = constants.ENEMY_SPEED

    if self.alive:
      if not self.stunned:

        self.move(ai_dx, ai_dy, obstacle_tiles)

        if dist < constants.ATTACK_RANGE and player.hit == False:
          player.health -= 10
          player.hit = True
          player.last_hit = pygame.time.get_ticks()

        fireball_cooldown = 700
        if self.boss:
          if dist < 500:
            if pygame.time.get_ticks() - self.last_attack >= fireball_cooldown:
              fireball = weapon.Fireball(fireball_image, self.rect.centerx, self.rect.centery, player.rect.centerx, player.rect.centery)
              self.last_attack = pygame.time.get_ticks()

      if self.hit == True:
        self.hit = False
        self.last_hit = pygame.time.get_ticks()
        self.stunned = True
        self.running = False
        self.update_action(0)

      if (pygame.time.get_ticks() - self.last_hit > stun_cooldown):
        self.stunned = False

    return fireball

  def update(self):

    if self.health <= 0:
      self.health = 0
      self.alive = False

    hit_cooldown = 1000
    if self.char_type == 0:
      if self.hit == True and (pygame.time.get_ticks() - self.last_hit) > hit_cooldown:
        self.hit = False

    if self.running == True:
      self.update_action(1)
    else:
      self.update_action(0)


    animation_cooldown = 70
    self.image = self.animation_list[self.action][self.frame_index]
    if pygame.time.get_ticks() - self.update_time > animation_cooldown:
     self.frame_index += 1
     self.update_time = pygame.time.get_ticks()
    if self.frame_index >= len(self.animation_list[self.action]):
      self.frame_index = 0


  def update_action(self, new_action):
    if new_action != self.action:
      self.action = new_action
      self.frame_index = 0
      self.update_time = pygame.time.get_ticks()

  def draw(self, surface):
    flipped_image = pygame.transform.flip(self.image, self.flip, False)
    if self.char_type == 0:
      surface.blit(flipped_image, (self.rect.x, self.rect.y - constants.SCALE * constants.OFFSET))
    else:
      surface.blit(flipped_image, self.rect)
