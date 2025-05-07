import pygame
import constants
import math

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
    self.image = self.animation_list[self.action][self.frame_index]
    self.rect = pygame.Rect(0, 0, constants.TILE_SIZE * size, constants.TILE_SIZE * size)
    self.rect.center = (x, y)

  def move(self, dx, dy):
    screen_scroll = [0, 0]
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
    self.rect.y += dy

    if self.char_type == 0:

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
    return screen_scroll

  def ai(self, screen_scroll):

    self.rect.x += screen_scroll[0]
    self.rect.y += screen_scroll[1]

  def update(self):

    if self.health <= 0:
      self.health = 0
      self.alive = False

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
    pygame.draw.rect(surface, constants.RED, self.rect, 1)