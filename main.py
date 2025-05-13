import pygame
from pygame import mixer
import csv
import constants
from character import Character
from weapon import Weapon
from items import Item
from world import World
from button import Button

mixer.init()
pygame.init()

screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
pygame.display.set_caption("Vault Of Valor")

clock = pygame.time.Clock()

level = 1
start_game = False
pause_game = False
start_intro = False
scren_scroll = [0, 0]

moving_left = False
moving_right = False
moving_up = False
moving_down = False

font = pygame.font.Font("assets/fonts/AtariClassic.ttf", 20)

def scale_img(image, scale):
  w = image.get_width()
  h = image.get_height()
  return pygame.transform.scale(image, (w * scale, h * scale))


pygame.mixer.music.load("assets/audio/music.wav")
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 5000)
shot_fx = pygame.mixer.Sound("assets/audio/arrow_shot.mp3")
shot_fx.set_volume(0.5)
hit_fx = pygame.mixer.Sound("assets/audio/arrow_hit.wav")
hit_fx.set_volume(0.5)
coin_fx = pygame.mixer.Sound("assets/audio/coin.wav")
coin_fx.set_volume(0.5)
heal_fx = pygame.mixer.Sound("assets/audio/heal.wav")
heal_fx.set_volume(0.5)

start_img = scale_img(pygame.image.load("assets/images/buttons/button_start_new.png").convert_alpha(), constants.BUTTON_SCALE)
exit_img = scale_img(pygame.image.load("assets/images/buttons/button_exit_new.png").convert_alpha(), constants.BUTTON_SCALE)
restart_img = scale_img(pygame.image.load("assets/images/buttons/restart_button_new.png").convert_alpha(), constants.BUTTON_SCALE)
resume_img = scale_img(pygame.image.load("assets/images/buttons/button_resume.png").convert_alpha(), constants.BUTTON_SCALE)

heart_empty = scale_img(pygame.image.load("assets/images/items/heart_empty.png").convert_alpha(), constants.ITEM_SCALE)
heart_half = scale_img(pygame.image.load("assets/images/items/heart_half.png").convert_alpha(), constants.ITEM_SCALE)
heart_full = scale_img(pygame.image.load("assets/images/items/heart_full.png").convert_alpha(), constants.ITEM_SCALE)


coin_images = []
for x in range(4):
  img = scale_img(pygame.image.load(f"assets/images/items/coin_f{x}.png").convert_alpha(), constants.ITEM_SCALE)
  coin_images.append(img)


red_potion = scale_img(pygame.image.load("assets/images/items/potion_red.png").convert_alpha(), constants.POTION_SCALE)

item_images = []
item_images.append(coin_images)
item_images.append(red_potion)

background_img = pygame.image.load("assets/images/girisArkaPlan.png").convert()
background_img = pygame.transform.scale(background_img, (constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
game_over_img = scale_img(pygame.image.load("assets/images/game_over.png").convert_alpha(), 1.0)
game_background_img = pygame.image.load("assets/images/game_background.png").convert()
game_background_img = pygame.transform.scale(game_background_img, (constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))

bow_image = scale_img(pygame.image.load("assets/images/weapons/bow.png").convert_alpha(), constants.WEAPON_SCALE)
arrow_image = scale_img(pygame.image.load("assets/images/weapons/arrow.png").convert_alpha(), constants.WEAPON_SCALE)
fireball_image = scale_img(pygame.image.load("assets/images/weapons/fireball.png").convert_alpha(), constants.FIREBALL_SCALE)

tile_list = []
for x in range(constants.TILE_TYPES):
  tile_image = pygame.image.load(f"assets/images/tiles/{x}.png").convert_alpha()
  tile_image = pygame.transform.scale(tile_image, (constants.TILE_SIZE, constants.TILE_SIZE))
  tile_list.append(tile_image)

mob_animations = []
mob_types = ["elf", "imp", "skeleton", "goblin", "muddy", "tiny_zombie", "big_demon"]

animation_types = ["idle", "run"]
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



def draw_text(text, font, text_col, x, y):
  img = font.render(text, True, text_col)
  screen.blit(img, (x, y))


def draw_info():
  pygame.draw.rect(screen, constants.PANEL, (0, 0, constants.SCREEN_WIDTH, 50))
  pygame.draw.line(screen, constants.WHITE, (0, 50), (constants.SCREEN_WIDTH, 50))
  half_heart_drawn = False
  for i in range(5):
    if player.health >= ((i + 1) * 20):
      screen.blit(heart_full, (10 + i * 50, 0))
    elif (player.health % 20 > 0) and half_heart_drawn == False:
      screen.blit(heart_half, (10 + i * 50, 0))
      half_heart_drawn = True
    else:
      screen.blit(heart_empty, (10 + i * 50, 0))

  draw_text("LEVEL: " + str(level), font, constants.WHITE, constants.SCREEN_WIDTH / 2, 15)
  draw_text(f"X{player.score}", font, constants.WHITE, constants.SCREEN_WIDTH - 100, 15)


def reset_level():
  damage_text_group.empty()
  arrow_group.empty()
  item_group.empty()
  fireball_group.empty()
  data = []
  for row in range(constants.ROWS):
    r = [-1] * constants.COLS
    data.append(r)
  return data



class DamageText(pygame.sprite.Sprite):
  def __init__(self, x, y, damage, color):
    pygame.sprite.Sprite.__init__(self)
    self.image = font.render(damage, True, color)
    self.rect = self.image.get_rect()
    self.rect.center = (x, y)
    self.counter = 0

  def update(self):
    self.rect.x += screen_scroll[0]
    self.rect.y += screen_scroll[1]
    self.rect.y -= 1
    self.counter += 1
    if self.counter > 30:
      self.kill()


class ScreenFade():
  def __init__(self, direction, colour, speed):
    self.direction = direction
    self.colour = colour
    self.speed = speed
    self.fade_counter = 0
  def fade(self):
    fade_complete = False
    self.fade_counter += self.speed
    if self.direction == 1:
      pygame.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, constants.SCREEN_WIDTH // 2, constants.SCREEN_HEIGHT))
      pygame.draw.rect(screen, self.colour, (constants.SCREEN_WIDTH // 2 + self.fade_counter, 0, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
      pygame.draw.rect(screen, self.colour, (0, 0 - self.fade_counter, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT // 2))
      pygame.draw.rect(screen, self.colour, (0, constants.SCREEN_HEIGHT // 2 + self.fade_counter, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
    elif self.direction == 2:
      pygame.draw.rect(screen, self.colour, (0, 0, constants.SCREEN_WIDTH, 0 + self.fade_counter))
    if self.fade_counter >= constants.SCREEN_WIDTH:
      fade_complete = True
    return fade_complete


world_data = []
for row in range(constants.ROWS):
  r = [-1] * constants.COLS
  world_data.append(r)

with open(f"levels/level{level}_data.csv", newline="") as csvfile:
  reader = csv.reader(csvfile, delimiter = ",")
  for x, row in enumerate(reader):
    for y, tile in enumerate(row):
      world_data[x][y] = int(tile)

world = World()
world.process_data(world_data, tile_list, item_images, mob_animations)
player = world.player
bow = Weapon(bow_image, arrow_image)
enemy_list = world.character_list

damage_text_group = pygame.sprite.Group()
arrow_group = pygame.sprite.Group()
item_group = pygame.sprite.Group()
fireball_group = pygame.sprite.Group()

score_coin = Item(constants.SCREEN_WIDTH - 115, 23, 0, coin_images, True)
item_group.add(score_coin)
for item in world.item_list:
  item_group.add(item)

intro_fade = ScreenFade(1, constants.BLACK, 4)
death_fade = ScreenFade(2, constants.PINK, 4)

start_button = Button(constants.SCREEN_WIDTH // 2 - 65, constants.SCREEN_HEIGHT // 1.8 - 10, start_img)
exit_button = Button(constants.SCREEN_WIDTH // 2 - 65, constants.SCREEN_HEIGHT // 1.8 + 50, exit_img)
restart_button = Button(constants.SCREEN_WIDTH // 2 - 115, constants.SCREEN_HEIGHT // 2 + 170, restart_img)
resume_button = Button(constants.SCREEN_WIDTH // 2 - 175, constants.SCREEN_HEIGHT // 2 - 150, resume_img)


run = True
while run:
  clock.tick(constants.FPS)
  if start_game == False:
    screen.blit(background_img, (0, 0))
    if start_button.draw(screen):
      start_game = True
      start_intro = True
    if exit_button.draw(screen):
      run = False
  else:
    if pause_game == True:
      screen.blit(background_img, (0, 0))
      if resume_button.draw(screen):
        pause_game = False
      if exit_button.draw(screen):
        run = False
    else:
      screen.blit(game_background_img, (0, 0))

      if player.alive:
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

        screen_scroll, level_complete = player.move(dx, dy, world.obstacle_tiles, world.exit_tile)

        world.update(screen_scroll)
        for enemy in enemy_list:
          fireball = enemy.ai(player, world.obstacle_tiles, screen_scroll, fireball_image)
          if fireball:
            fireball_group.add(fireball)
          if enemy.alive:
            enemy.update()
        player.update()
        arrow = bow.update(player)
        if arrow:
          arrow_group.add(arrow)
          shot_fx.play()
        for arrow in arrow_group:
          damage, damage_pos = arrow.update(screen_scroll,world.obstacle_tiles, enemy_list)
          if damage:
            damage_text = DamageText(damage_pos.centerx, damage_pos.y, str(damage), constants.RED)
            damage_text_group.add(damage_text)
        damage_text_group.update()
        fireball_group.update(screen_scroll, player)
        item_group.update(screen_scroll, player, coin_fx, heal_fx)

      world.draw(screen)
      for enemy in enemy_list:
        enemy.draw(screen)
      player.draw(screen)
      bow.draw(screen)
      for arrow in arrow_group:
        arrow.draw(screen)
      for fireball in fireball_group:
        fireball.draw(screen)
      damage_text_group.draw(screen)
      item_group.draw(screen)
      draw_info()
      score_coin.draw(screen)


      if level_complete == True:
        start_intro = True
        level += 1
        world_data = reset_level()

        with open(f"levels/level{level}_data.csv", newline="") as csvfile:
          reader = csv.reader(csvfile, delimiter = ",")
          for x, row in enumerate(reader):
            for y, tile in enumerate(row):
              world_data[x][y] = int(tile)
        world = World()
        world.process_data(world_data, tile_list, item_images, mob_animations)
        temp_hp = player.health
        temp_score = player.score
        player = world.player
        player.health = temp_hp
        player.score = temp_score
        enemy_list = world.character_list
        score_coin = Item(constants.SCREEN_WIDTH - 115, 23, 0, coin_images, True)
        item_group.add(score_coin)

        for item in world.item_list:
          item_group.add(item)

      if start_intro == True:
        if intro_fade.fade():
          start_intro = False
          intro_fade.fade_counter = 0


      if player.alive == False:
        screen.fill((0, 0, 0))
        screen.blit(game_over_img, ((constants.SCREEN_WIDTH - game_over_img.get_width()) // 2,
                                    (constants.SCREEN_HEIGHT - game_over_img.get_height()) // 2))
        if restart_button.draw(screen):
          start_intro = True
          world_data = reset_level()
          with open(f"levels/level{level}_data.csv", newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            for x, row in enumerate(reader):
              for y, tile in enumerate(row):
                world_data[x][y] = int(tile)
          world = World()
          world.process_data(world_data, tile_list, item_images, mob_animations)
          temp_score = player.score
          player = world.player
          player.score = temp_score
          enemy_list = world.character_list
          score_coin = Item(constants.SCREEN_WIDTH - 115, 23, 0, coin_images, True)
          item_group.add(score_coin)
          for item in world.item_list:
            item_group.add(item)


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
      if event.key == pygame.K_ESCAPE:
        pause_game = True


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