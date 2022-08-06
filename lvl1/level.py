import pygame
from support import *
from settings import *
from tile import Tile
from player import Player
from debug import debug
from random import choice, randint
from weapon import Weapon
from enemy import Enemy
from ui import UI
from magic import Magic
from upgrade import Upgrade
from particles import *

class SortYCameraGroup(pygame.sprite.Group):
	def __init__(self):
	 super().__init__()
	 self.display_surface = pygame.display.get_surface()
	 self.half_width = self.display_surface.get_size()[0]//2
	 self.half_height = self.display_surface.get_size()[1]//2
	 self.offset = pygame.math.Vector2()

	 self.floor_surf = pygame.image.load('../graphics/tilemap/ground.png').convert()
	 self.floor_rect = self.floor_surf.get_rect(topleft = (0,0))

	def custom_draw(self, player):
		self.offset.x = player.rect.centerx - self.half_width
		self.offset.y = player.rect.centery - self.half_height

		floor_offset_pos = self.floor_rect.topleft - self.offset
		self.display_surface.blit(self.floor_surf, floor_offset_pos)

		for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):
		#for sprite in self.sprites():
			offset_pos = sprite.rect.topleft - self.offset
			self.display_surface.blit(sprite.image, offset_pos)

	def enemy_update(self, player):
		enemy_sprites = [sprite for sprite in self.sprites() if hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'enemy']
		for enemy in enemy_sprites:
			enemy.enemy_update(player)


class Level:
	def __init__(self):
		#self.player = None
		self.display_surface = pygame.display.get_surface()

		self.visible_sprites = SortYCameraGroup()
		self.obstacle_sprites = pygame.sprite.Group()
		self.attack_sprites = pygame.sprite.Group()
		self.attackable_sprites = pygame.sprite.Group()
		self.game_paused = False

		self.current_attack = None
		self.ui = UI()
		#self.upgrade = Upgrade(self.player)
		self.create_map()

		self.animation_player = AnimationPlayer()
		self.magic = Magic(self.animation_player)

	def create_map(self):
		layouts = {
			'boundary': import_csv_layout('../map/map_FloorBlocks.csv'),
			'grass': import_csv_layout('../map/map_Grass.csv'),
			'object': import_csv_layout('../map/map_Objects.csv'),
			'entities': import_csv_layout('../map/map_Entities.csv')
		}
		graphics = {
			'grass': import_folder('../graphics/grass'),
			'object': import_folder('../graphics/objects')
		}

		for style, layout in layouts.items():
			for row_indx, row in enumerate(layout):
				for col_indx, col in enumerate(row):
					if col != '-1':
						x = col_indx * TILESIZE
						y = row_indx * TILESIZE
						if style == 'boundary':
							Tile((x,y), [self.obstacle_sprites], 'invisible')
						if style == 'grass':
							random_grass = choice(graphics['grass'])
							Tile((x,y), [self.visible_sprites, self.obstacle_sprites, self.attackable_sprites], 'grass', random_grass)
						if style == 'object':
							surf = graphics['object'][int(col)]
							Tile((x,y), [self.visible_sprites, self.obstacle_sprites], 'object', surf)
						if style == 'entities':
							if col == '394':
								self.player = Player((x,y), [self.visible_sprites], self.obstacle_sprites, self.create_attack, self.destroy_attack, self.create_magic)
								self.upgrade = Upgrade(self.player)
							else:
								if col == '390': monster_name = 'bamboo'
								elif col == '391': monster_name = 'spirit'
								elif col == '392': monster_name = 'raccoon'
								else: monster_name = 'squid'
								Enemy(monster_name, (x,y), [self.visible_sprites, self.attackable_sprites], self.obstacle_sprites, self.damage_player, self.death_particles, self.add_exp)
		# for row_indx, row in enumerate(WORLD_MAP):
		# 	for col_indx, col in enumerate(row):
		# 		x = col_indx * TILESIZE
		# 		y = row_indx * TILESIZE
		# 		if col == 'x':
		# 			Tile((x,y), [self.visible_sprites, self.obstacle_sprites])
		# 		elif col == 'p':
		# 			self.player = Player((x,y), [self.visible_sprites], self.obstacle_sprites)

	def create_attack(self):
		self.current_attack = Weapon(self.player,[self.visible_sprites, self.attack_sprites])

	def toggle_menu(self):
		self.game_paused = not self.game_paused

	def create_magic(self, style, strength, cost):
		#self.current_attack = Weapon(self.player,[self.visible_sprites, self.attack_sprites])
		# print(style)
		# print(strength)
		# print(cost)

		if style == 'heal':
			self.magic.heal(self.player, strength, cost, [self.visible_sprites])
		if style == 'flame':
			self.magic.fire(self.player, strength, cost, [self.visible_sprites, self.attack_sprites])

	def damage_player(self, amount, atk_type):
		if self.player.vulnerable:
			self.player.health -= amount
			self.player.vulnerable = False
			self.player.hurt_time = pygame.time.get_ticks()
			self.animation_player.generate_particle(self.player.rect.center, [self.visible_sprites], atk_type)

	def destroy_attack(self):
		if self.current_attack:
			self.current_attack.kill()
			self.current_attack = None

	def add_exp(self, amount):
		self.player.exp += amount

	def death_particles(self, pos, p_type):
		self.animation_player.generate_particle(pos, [self.visible_sprites], p_type)

	def attack_logic(self):
		if self.attack_sprites:
			for sprite in self.attack_sprites:
				struck = pygame.sprite.spritecollide(sprite, self.attackable_sprites, False)
				if struck:
					for coll_sprite in struck:
						if coll_sprite.sprite_type == 'grass':
							pos = coll_sprite.rect.center
							offset = pygame.math.Vector2(0,50)
							for leaf in range(randint(3,6)):
								self.animation_player.create_grass_particle(pos - offset, [self.visible_sprites])
							coll_sprite.kill()
						elif coll_sprite.sprite_type == 'enemy':
							coll_sprite.get_damage(self.player, sprite.sprite_type)

	def run(self):
		self.visible_sprites.custom_draw(self.player)
		self.ui.display(self.player)
		if self.game_paused:
			self.upgrade.display()
		else:
			self.visible_sprites.update()
			self.visible_sprites.enemy_update(self.player)
			self.attack_logic()
		