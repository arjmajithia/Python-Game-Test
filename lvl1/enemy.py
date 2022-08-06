import pygame
from settings import *
from entity import Entity
from support import *

class Enemy(Entity):
	def __init__(self, name, pos, groups, obstacle_sprites, damage_player, death_particles, add_exp):
		super().__init__(groups)
		self.sprite_type = 'enemy'
		self.status = 'idle'

		self.name = name
		self.stats = monster_data[self.name]
		
		self.health = self.stats['health']
		self.exp = self.stats['exp']
		self.speed = self.stats['speed']
		self.atk_dmg = self.stats['damage']
		self.resis = self.stats['resistance']
		self.atk_rad = self.stats['attack_radius']
		self.not_rad = self.stats['notice_radius']
		self.atk_type = self.stats['attack_type']
		self.invuln_time = self.stats['invuln_time']
		self.damage_player = damage_player

		self.import_graphics(name)

		self.image = self.animations[self.status][self.frame_indx]
		self.rect = self.image.get_rect(topleft = pos)
		self.hbox = self.rect.inflate(0,-10)
		self.obstacle_sprites = obstacle_sprites

		self.vulnerable = True
		self.invuln_time = self.stats['invuln_time']
		self.attacked_time = None
		self.hit_knockback = None

		self.attack_switch = True
		self.attack_cd = 600
		self.attack_time = None
		self.add_exp = add_exp
		self.death_particles = death_particles

	def import_graphics(self, name):
		self.animations = {'idle': [], 'move': [], 'attack': []}
		main_path = f'../graphics/monsters/{name}/'
		for anim in self.animations.keys():
			self.animations[anim] = import_folder(main_path + anim)

	def player_dist_direc(self, player):
		enem_vec = pygame.math.Vector2(self.rect.center)
		play_vec = pygame.math.Vector2(player.rect.center)
		distance = (play_vec - enem_vec).magnitude()
		if distance > 0: direction = (play_vec - enem_vec).normalize()
		else: direction = pygame.math.Vector2()
		#distance = math.sqrt(math.pow(math.abs(enem_vec[1] - play_vec[1]), 2) + math.pow(math.abs(enem_vec[0] - play_vec[0])), 2)
		return (distance, direction)

	def get_status(self, player):
		dist_direc = self.player_dist_direc(player)

		if dist_direc[0] <= self.stats['attack_radius'] and self.attack_switch:
			if self.status != 'attack':
				self.frame_indx = 0
			self.status = 'attack'
		elif dist_direc[0] <= self.stats['notice_radius']:
			self.status = 'move'
		else:
			self.status = 'idle'

	def actions(self, player):
		if self.status == 'attack':
			self.attack_time = pygame.time.get_ticks()
			self.damage_player(self.atk_dmg, self.atk_type)
		elif self.status == 'move':
			pass
			self.direction = self.player_dist_direc(player)[1]
		else:
			direction = pygame.math.Vector2()

	def animate(self):
		animation = self.animations[self.status] 
		self.frame_indx += self.anim_speed
		if self.frame_indx >= len(self.animations[self.status]):
			if self.status == 'attack':
				self.attack_switch = False
			self.frame_indx = 0

		if not self.vulnerable:
			alpha = self.wave_value()
			self.image.set_alpha(alpha)
		else:
			self.image.set_alpha(255)
		#if self.frame_indx >= len(self.animations[self.status]):
	

		self.image = animation[int(self.frame_indx)]
		self.rect = self.image.get_rect(center = self.hbox.center)

	def get_damage(self, player, atk_sprite_type):
		if self.vulnerable:
			self.direction = self.player_dist_direc(player)[1]
			dmg = player.get_damage(atk_sprite_type)[0]
			hknock = player.get_damage(atk_sprite_type)[1]
			if atk_sprite_type == 'weapon':
				self.health -= player.get_damage(atk_sprite_type)[0]
				self.hit_knockback = player.get_damage(atk_sprite_type)[1]
				self.struck(player)
			elif atk_sprite_type == 'particle':
				self.health -= dmg
				self.hit_knockback = hknock
			self.attacked_time = pygame.time.get_ticks()
			self.vulnerable = False

	def check_death(self):
		if self.health <= 0:
			self.kill()
			self.add_exp(amount = self.exp)
			self.death_particles(self.rect.center, self.name)

	def struck(self, hit_knockback):
		if not self.vulnerable:
			knockback = self.resis - (hit_knockback)
			if knockback <= 0:
				self.direction *= knockback
			else:
				self.direction *= 1/knockback

	def cds(self):
		current_time = pygame.time.get_ticks()
		if not self.vulnerable:
			if current_time - self.attacked_time >= self.invuln_time:
				self.vulnerable = True
		if not self.attack_switch:
			if current_time - self.attack_time >= self.attack_cd:
				self.attack_switch = True

	def update(self):
		self.struck(self.hit_knockback)
		self.move(self.speed)
		self.animate()
		self.cds()
		self.check_death()

	def enemy_update(self,player):
		self.get_status(player)
		self.actions(player)
