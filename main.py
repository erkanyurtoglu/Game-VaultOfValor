import pygame
import constants
from character import Character
from weapon import Weapon

pygame.init()

screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
pygame.display.set_caption("Vault Of Valor")

clock = pygame.time.Clock()

moving_left = False
moving_right = False
moving_up = False
moving_down = False

font = pygame.font.Font("assets/fonts/AtariClassic.ttf", 20)

def scale_img(image, scale):
  w = image.get_width()
  h = image.get_height()
  return pygame.transform.scale(image, (w * scale, h * scale))

bow_image = scale_img(pygame.image.load("assets/images/weapons/bow.png").convert_alpha(), constants.WEAPON_SCALE)
arrow_image = scale_img(pygame.image.load("assets/images/weapons/arrow.png").convert_alpha(), constants.WEAPON_SCALE)


mob_animations = []
mob_types = ["elf", "imp", "skeleton", "goblin", "muddy", "tiny_zombie", "big_demon"]

animation_types = ["idle", "run"]
animation_list = []
for mob in mob_types:
  animation_list = []
  for animation in animation_types:

   temp_list = []
   for i in range(4):
     img = pygame.image.load(f"assets/images/characters/{mob}/{animation}/{i}.png").convert_alpha()
     img = scale_img(img, constants.SCALE)
     temp_list.append(img)
   animation_list.append(temp_list)
  mob_animations.append(animation_list)


class DamageText(pygame.sprite.Sprite):
  def __init__(self, x, y, damage, color):
    pygame.sprite.Sprite.__init__(self)
    self.image = font.render(damage, True, color)
    self.rect = self.image.get_rect()
    self.rect.center = (x, y)
    self.counter = 0

  def update(self):
    #move damage text up
    self.rect.y -= 1
    self.counter += 1
    if self.counter > 30:
      self.kill()


player = Character(100, 100, 100, mob_animations, 0)

enemy = Character(200, 300, 100, mob_animations, 1)

bow = Weapon(bow_image,arrow_image)

enemy_list = []
enemy_list.append(enemy)

damage_text_group = pygame.sprite.Group()
arrow_group = pygame.sprite.Group()

run = True
while run:

  clock.tick(constants.FPS)

  screen.fill(constants.BG)

  dx = 0
  dy = 0
  if moving_right == True:
    dx = constants.SPEED
  if moving_left == True:
    dx = -constants.SPEED
  if moving_up == True:
    dy = -constants.SPEED
  if moving_down == True:
    dy = constants.SPEED


  player.move(dx, dy)

  for enemy in enemy_list:
    enemy.update()
  player.update()
  arrow = bow.update(player)
  if arrow:
    arrow_group.add(arrow)
  for arrow in arrow_group:
    damage, damage_pos = arrow.update(enemy_list)
    if damage:
      damage_text = DamageText(damage_pos.centerx, damage_pos.y, str(damage), constants.RED)
      damage_text_group.add(damage_text)
  damage_text_group.update()

  for enemy in enemy_list:
    enemy.draw(screen)
  player.draw(screen)
  bow.draw(screen)
  for arrow in arrow_group:
    arrow.draw(screen)
  damage_text_group.draw(screen)

  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      run = False

    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_a:
        moving_left = True
      if event.key == pygame.K_d:
        moving_right = True
      if event.key == pygame.K_w:
        moving_up = True
      if event.key == pygame.K_s:
        moving_down = True

    if event.type == pygame.KEYUP:
      if event.key == pygame.K_a:
        moving_left = False
      if event.key == pygame.K_d:
        moving_right = False
      if event.key == pygame.K_w:
        moving_up = False
      if event.key == pygame.K_s:
        moving_down = False

  pygame.display.update()

pygame.quit()