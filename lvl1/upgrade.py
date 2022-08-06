import pygame
from settings import *

class Upgrade:
	def __init__(self, player):
		self.display_surface = pygame.display.get_surface()
		self.player = player
		self.max_values = list(player.max_stats.values())

		self.nbr_attribute = len(player.stats)
		self.attribute_names = list(player.stats.keys())
		self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)
		self.offset = 0.8

		self.select_index = 0
		self.selection_time = None
		self.can_move = True

		self.height = self.display_surface.get_size()[1] * self.offset
		self.width = self.display_surface.get_size()[0] // (self.nbr_attribute + 1)
		self.create_boxes()

	def create_boxes(self):
		self.attributes = []

		for attr, index in enumerate(range(self.nbr_attribute)):
			fwidth = self.display_surface.get_size()[0]
			incr = fwidth // self.nbr_attribute
			left = (attr * incr) + (incr - self.width) // 2

			top = self.display_surface.get_size()[1] * ((round(1 - self.offset, 2))/3.5)

			attr = Choice_Box(left, top, self.width, self.height, index, self.font)
			self.attributes.append(attr)

	def input(self):
		keys = pygame.key.get_pressed()
		if self.can_move:
			if keys[pygame.K_RIGHT]:
				self.select_index = (self.select_index + 1) % (self.nbr_attribute)
				self.can_move = False
				self.selection_time = pygame.time.get_ticks()
			elif keys[pygame.K_LEFT]:
				self.select_index -= 1
				if self.select_index < 0: self.select_index = (self.nbr_attribute - 1)
				self.can_move = False
				self.selection_time = pygame.time.get_ticks()

			if keys[pygame.K_SPACE]:
				self.can_move = False
				self.selection_time = pygame.time.get_ticks()
				self.attributes[self.select_index].ameliorate(self.player)

	def cds(self):
		if not self.can_move:
			current_time = pygame.time.get_ticks()
			if current_time - self.selection_time >= 300:
				self.can_move = True

	def display(self):
		self.input()
		self.cds()

		for index, attr in enumerate(self.attributes):
			name = self.attribute_names[index]
			value = self.player.value_by_index(index, 'value')
			cost = self.player.value_by_index(index, 'cost')
			max_val = self.max_values[index]
			attr.display(surface = self.display_surface, 
						select_num = self.select_index, 
						name = name, 
						value = value, 
						cost = cost, 
						max_val = max_val) # test values


class Choice_Box:
	def __init__(self, left, top, width, height, index, font):
		self.rect = pygame.Rect(left, top, width, height)
		self.index = index
		self.font = font


	def display_names(self, surface, name, cost, value, selected):
		color = TEXT_COLOR_SELECTED if selected else TEXT_COLOR

		title_surface = self.font.render(name, False, color)
		title_rect = title_surface.get_rect(midtop = self.rect.midtop + pygame.math.Vector2(0,20))

		cos = round(cost)
		cost_surface = self.font.render(f'{cos}', False, color)
		cost_rect = cost_surface.get_rect(midbottom = self.rect.midbottom - pygame.math.Vector2(0,20))

		#value_surface = self.font.render(f'{value}', False, color)
		#value_rect = value_surface.get_rect(midtop = self.rect.center - pygame.math.Vector2(-40,20))

		surface.blit(title_surface, title_rect)
		surface.blit(cost_surface, cost_rect)
		#surface.blit(value_surface, value_rect)

	def display_bar(self, surface, value, max_val, selected):

		top = self.rect.midtop + pygame.math.Vector2(0,60)
		bottom = self.rect.midbottom - pygame.math.Vector2(0,60)
		color = BAR_COLOR_SELECTED if selected else BAR_COLOR

		full_height = bottom[1] - top[1]
		relative = (value/max_val) * full_height
		value_rect = pygame.Rect(top[0] - 15, bottom[1] - relative, 30, 10)

		val = round(value, 2)
		val_text_surface = self.font.render(f'{val}', False, color)
		val_text_rect = val_text_surface.get_rect(center = value_rect.center - pygame.math.Vector2(-47,0))

		pygame.draw.line(surface, color, top, bottom, 5)
		pygame.draw.rect(surface, color, value_rect)
		surface.blit(val_text_surface, val_text_rect)

	def ameliorate(self,player):
		upgrade_attribute = list(player.stats.keys())[self.index]
		if player.exp >= player.upgrade_cost[upgrade_attribute] and (player.stats[upgrade_attribute] < player.max_stats[upgrade_attribute]):
			player.exp -= player.upgrade_cost[upgrade_attribute]
			player.stats[upgrade_attribute] += player.upgrade_amount[upgrade_attribute]
			player.upgrade_cost[upgrade_attribute] *= 1.2

		if player.stats[upgrade_attribute] >= player.max_stats[upgrade_attribute]:
			player.stats[upgrade_attribute] = player.max_stats[upgrade_attribute]

	def display(self, surface, select_num, name, value, max_val, cost):
		if self.index == select_num:
			pygame.draw.rect(surface, UPGRADE_BG_COLOR_SELECTED, self.rect)
			pygame.draw.rect(surface, UI_BORDER_COLOR, self.rect, 3)
		else:
			pygame.draw.rect(surface, UI_BG_COLOR, self.rect)
			pygame.draw.rect(surface, UI_BORDER_COLOR, self.rect, 3)

		self.display_names(surface, name, cost, value, self.index == select_num)
		self.display_bar(surface, value, max_val, self.index == select_num)