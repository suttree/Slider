 #! /usr/bin/env python

import os
import sys
import random
import pygame
import marshal
import webbrowser

from pygame.locals import *
from menu.Hints import HintHeader, HintLine1, HintLine2
from menu.Items import Bonus, Collect, EndGame, GameOver, HiScore, NewGame, SubmitScore, Timer

RED = [255,0,0]
GREEN = [0,255,0]
BLUE = [0,0,255]
YELLOW = [255,255,0]
ORANGE = [255,128,0]
PURPLE = [128,0,128]

FONT = os.path.join('fonts', 'nrkis.ttf')

# BONUS SOUND
# ERROR SOUND

class Game:
	def __init__(self):
		self.game_over = 0

		self.prev_x = 0
		self.prev_y = 0
		self.last_click = 0

		self.load_scores()

	def create_grid(self):
		# This is the grid, remove a few squares and then create it
		positions = [
			'0,0',   '50,0',   '100,0',   '150,0',   '200,0',   '250,0',   '300,0',   '350,0',
			'0,50',  '50,50',  '100,50',  '150,50',  '200,50',  '250,50',  '300,50',  '350,50',
			'0,100', '50,100', '100,100', '150,100', '200,100', '250,100', '300,100', '350,100',
			'0,150', '50,150', '100,150', '150,150', '200,150', '250,150', '300,150', '350,150',
			'0,200', '50,200', '100,200', '150,200', '200,200', '250,200', '300,200', '350,200',
			'0,250', '50,250', '100,250', '150,250', '200,250', '250,250', '300,250', '350,250',
			'0,300', '50,300', '100,300', '150,300', '200,300', '250,300', '300,300', '350,300',
			'0,350', '50,350', '100,350', '150,350', '200,350', '250,350', '300,350', '350,350',
		]

		random.shuffle(positions)

		self.blank_tiles = []

		for i in range(8):
			self.blank_tiles.append(positions.pop())

		for pos in positions:
			x,y = pos.split(",")
			self.tiles.add(Tile( self.colours[ random.randrange(len(self.colours)) ], [int(x),int(y)] ))

	def demo_mode(self):

		pygame.init()

		sound_file = os.path.join('sounds', 'wah2.wav')
		self.soundtrack = pygame.mixer.Sound(sound_file)
		self.soundtrack.set_volume(0.6)
		self.soundtrack.play(-1)

		sound_file = os.path.join('sounds', 'bonus.wav')
		self.game_over_sound = pygame.mixer.Sound(sound_file)
		self.game_over_sound.set_volume(0.5)
		
		pygame.display.set_caption('Playaholics: Slider')
		self.screen = pygame.display.set_mode([600,400])
		self.background = pygame.image.load('images/how_to_play.png').convert()
		self.screen.blit(self.background, [0, 0])
		pygame.display.update()

		in_demo=1
		while in_demo:
			for event in pygame.event.get():
				if event.type == QUIT:
					sys.exit()

				elif event.type == MOUSEBUTTONDOWN:
					in_demo=0
					self.soundtrack.fadeout(10000)
				else:
					pass

		self.start()

	def double_clicked(self,x,y):
		time_now = pygame.time.get_ticks()
		pause = time_now - self.last_click
	
		if self.prev_x == x and self.prev_y == y:
			if pause <= 300:
				return 1
	
		self.prev_x     = x
		self.prev_y     = y
		self.last_click = time_now

		return 0

	def load_scores(self):
		self.top_scores = []
		try:
			scores = os.path.join('menu', 'scores.dat')
			infile = open(scores, "rb")
			self.top_scores = marshal.load(infile)
			infile.close()
		except:
			pass

	def reset(self):
		self.game_over = 0
		self.bonus.reset()
		self.hint_line1.reset()
		self.hint_line2.reset()
		self.gamesprites.remove(self.bonus)

	def restart(self):
		"""Restart the game"""

		self.tiles.empty()

		self.reset()
		self.timer.reset()
		self.score.reset()
		self.submit_score_menu.reset()

		self.gamesprites.remove(self.bonus)
		self.menusprites.remove(self.game_over_menu)
		self.menusprites.remove(self.submit_score_menu)

		for hi_score in self.hi_scores:
			self.menusprites.remove(hi_score)

		self.colours = [ [255,0,0],[0,255,0],[0,0,255], [255,255,0], [255,128,0], [128,0,128] ] # red, green, blue, yellow, orange, purple

		self.run()

	def run(self):
		"""Run the game"""

		self.timer.start()
		self.create_grid()

		# Restrict what events we have to deal with
		pygame.event.set_allowed(None)
		pygame.event.set_allowed([QUIT,MOUSEBUTTONDOWN,MOUSEMOTION,MOUSEBUTTONUP])
		
		# Animate the tiles, scores and timers
		start_tile = None
		end_tile = None
		moveable = 1
		while 1:
			for event in pygame.event.get():
				if event.type == QUIT:
					sys.exit()

				elif event.type == MOUSEBUTTONDOWN:
					moveable = 1
					x,y = pygame.mouse.get_pos()
					starting_clicked_area = pygame.Rect(x,y,1,1)
		
					# Have we clicked on a tile rather than a space?
					for tile in self.tiles.sprites():
						if starting_clicked_area.colliderect(tile.rect):
							start_tile = tile

					# If we've double clicked on a tile, then attempt
					# to move in in this order - up, down, left, right
					if self.double_clicked(x,y) and start_tile:
						for direction in ['up','down','left','right']:
							if not moveable:
								break
							if direction == 'up':
								neighbour_x = start_tile.rect[0]
								neighbour_y = start_tile.rect[1]-50
							elif direction == 'down':
								neighbour_x = start_tile.rect[0]
								neighbour_y = start_tile.rect[1]+50
							elif direction == 'left':
								neighbour_x = start_tile.rect[0]-50
								neighbour_y = start_tile.rect[1]
							elif direction == 'right':
								neighbour_x = start_tile.rect[0]+50
								neighbour_y = start_tile.rect[1]

							if neighbour_x < 0 or neighbour_y < 0:
								continue
							elif neighbour_x > 350 or neighbour_y > 350:
								continue

							neighbour = pygame.Rect(neighbour_x,neighbour_y,1,1)

							for tile in self.tiles.sprites():
								if neighbour.colliderect(tile.rect):
									end_tile = tile

							if not end_tile:
								moveable = 0
								start_tile.move([neighbour_x,neighbour_y])
		
							end_tile = None

 				elif event.type == MOUSEMOTION:
					try:
						if moveable:
							x,y = pygame.mouse.get_pos()
							if x < 0:
								x=0
							if x > 350:
								x=350
							if y < 0:
								y=0
							if y > 350:
								y=350
							finishing_dragged_area = pygame.Rect(x,y,10,10)
			
							# Are we over a tile? If so, we can't slide here
							for tile in self.tiles.sprites():
								if finishing_dragged_area.colliderect(tile.rect):
									end_tile = tile
									break

							if start_tile and not end_tile:
								start_tile.move([x,y])
			
							end_tile = None
					except:
						pass

				elif event.type == MOUSEBUTTONUP:
					self.collect.click_test()
					self.end_game.click_test()
					self.new_game.click_test()
					if moveable:
						x,y = pygame.mouse.get_pos()
						if x < 0:
							x=0
						if x > 350:
							x=350
						if y < 0:
							y=0
						if y > 350:
							y=350
						finishing_clicked_area = pygame.Rect(x,y,10,10)
			
						# Have we clicked on a tile? If so, we can't slide here
						for tile in self.tiles.sprites():
							if finishing_clicked_area.colliderect(tile.rect):
								end_tile = tile
								break
			
						if start_tile and not end_tile:
							start_tile.move([x,y])
			
						start_tile = None
						end_tile = None
						moveable = 0

			self.tiles.update()
			self.score.update()
			self.gamesprites.update()
			self.menusprites.update()

			if self.bonus.off_screen:
				self.bonus.reset()
				self.score.bonus = 0
				self.gamesprites.remove(self.bonus)
			elif self.score.bonus > 0:
				self.bonus.award(self.score.bonus)
				self.gamesprites.add(self.bonus)
				self.score.bonus = 0

			if self.collect.clicked and not self.game_over:
				self.score.calculate(self.tiles)
				self.timer.timer = self.timer.timer + self.score.time_bonus

				if self.timer.timer > 60:
					self.timer.timer = 60

				self.score.time_bonus = 0
				
				# Recreate the board then add any penaly tiles to it
				additions = 0
				for tile in self.score.replacements:
					if tile == 'plus_one':
						additions = additions + 1
					else:
						type = int(round(random.uniform(0,100))) % 20
						self.tiles.add(Tile( self.colours[ random.randrange(len(self.colours)) ], [int(tile[0]),int(tile[1])], type ))

				for i in range(additions):
					new_tile = Tile( self.colours[ random.randrange(len(self.colours)) ], [0,0], False )
					added = False
					for x in range(0,351,50):
						if added:
							break
						else:
							for y in range(0,351,50):
								new_tile.rect[0] = x
								new_tile.rect[1] = y
								if not pygame.sprite.spritecollideany(new_tile,self.tiles) and not added:
									added = True
									self.tiles.add(Tile( self.colours[ random.randrange(len(self.colours)) ], [x,y], False ))
									if len(self.tiles.sprites()) == 64:
										self.timer.timer = 1	# game over, board is full
	
				self.hint_line1.next()
				self.hint_line2.next()

				self.collect.clicked = 0
				self.score.replacements = []

			if self.timer.time_up():
				self.timer.stop()

				self.score.clear_board(self.tiles)

				self.submit_score_menu.score = self.score.score

				if not self.game_over:
					self.save_scores()

					i = 0
					colour = ""
					self.hi_scores = []
					self.hi_scores.append(HiScore(self,"Hi-Scores",RED,[150,90]))
					for score in self.top_scores:
						i = i + 1

						if score == self.score.score:
							colour = RED
						else:
							colour = [0,0,0]

						if i < 10:
							score = " %d.    %d" % (i, score)
						else:
							score = "%d.   %d" % (i, score)

						self.hi_scores.append(HiScore(self,score,colour,[150,100+20*i]))

					for hi_score in self.hi_scores:
						self.menusprites.add(hi_score)

					self.game_over_sound.play()

				self.menusprites.add(self.game_over_menu)
				self.menusprites.add(self.submit_score_menu)

				self.game_over = 1

			if not self.game_over:
				tile_list = self.tiles.draw(self.screen)
				pygame.display.update(tile_list)

			ui_list = self.gamesprites.draw(self.screen)
			pygame.display.update(ui_list)
			menu_list = self.menusprites.draw(self.screen)
			pygame.display.update(menu_list)

			pygame.time.delay(10)
			self.tiles.clear(self.screen, self.background)
			self.gamesprites.clear(self.screen, self.background)
			self.menusprites.clear(self.screen, self.background)

	def save_scores(self):
		if self.score.score not in self.top_scores:
			self.top_scores.append(self.score.score)
		self.top_scores.sort()
		self.top_scores.reverse()
		scores = os.path.join('menu', 'scores.dat')
		outfile = open(scores, "wb")
		marshal.dump(self.top_scores[0:9],outfile)
		outfile.close()

	def start(self):
		"""Initialise the game and start it running"""

		self.background = pygame.image.load('images/slider.png').convert()
		self.screen.blit(self.background, [0, 0])
		pygame.display.update()

		self.bonus = Bonus()
		self.score = Score()
		self.timer = Timer()
		self.collect = Collect(self)

		self.end_game = EndGame()
		self.new_game = NewGame(self)
		self.hint_header = HintHeader()
		self.hint_line1 = HintLine1()
		self.hint_line2 = HintLine2()
		self.game_over_menu = GameOver(self)
		self.submit_score_menu = SubmitScore()

		self.tiles = pygame.sprite.RenderUpdates()
		self.gamesprites = pygame.sprite.RenderUpdates()
		self.menusprites = pygame.sprite.RenderUpdates()
		self.colours = [ [255,0,0],[0,255,0],[0,0,255], [255,255,0], [255,128,0], [128,0,128] ] # red, green, blue, yellow, orange, purple

		self.gamesprites.add(self.score)
		self.gamesprites.add(self.timer)
		self.gamesprites.add(self.hint_header)
		self.gamesprites.add(self.hint_line1)
		self.gamesprites.add(self.hint_line2)

		self.menusprites.add(self.collect)
		self.menusprites.add(self.end_game)
		self.menusprites.add(self.new_game)

		self.run()

class Score(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)

		self.bonus = 0
		self.score = 0
		self.time_bonus = 0
		self.tile_groups = {}
		self.replacements = []

		sound_file = os.path.join('sounds', 'dink.wav')
		self.sound = pygame.mixer.Sound(sound_file)
		self.sound.set_volume(0.25)

		sound_file = os.path.join('sounds', 'bonus.wav')
		self.bonus_sound = pygame.mixer.Sound(sound_file)
		self.bonus_sound.set_volume(0.5)

		sound_file = os.path.join('sounds', 'buzzer3.wav')
		self.penalty_sound = pygame.mixer.Sound(sound_file)
		self.penalty_sound.set_volume(0.1)

		self.font = pygame.font.Font(FONT, 32)
		self.image = self.font.render("Score: %d" % self.score, 1, (255,255,255))
		self.rect = self.image.get_rect()
		self.rect = self.rect.move([410,5])

		self.marker = Tile([0,0,0],[0,0])

	def calculate(self,board):
		"""Group together the tiles into their colours and award points for each one"""
		self.board = board
		all_tiles = []
		matched_chains = []
		all_chains = { 'red': [], 'green': [], 'blue': [], 'yellow': [], 'orange': [], 'purple': [] }
		colours = { 'red': [], 'green': [], 'blue': [], 'yellow': [], 'orange': [], 'purple': [] }
		
		# Separate the board into each colour
		for tile in board.sprites():
			all_tiles.append([tile.rect[0],tile.rect[1]])
			if tile.colour == RED:
				colours['red'].append([tile.rect[0],tile.rect[1]])
			elif tile.colour == GREEN:
				colours['green'].append([tile.rect[0],tile.rect[1]])
			elif tile.colour == BLUE:
				colours['blue'].append([tile.rect[0],tile.rect[1]])
			elif tile.colour == YELLOW:
				colours['yellow'].append([tile.rect[0],tile.rect[1]])
			elif tile.colour == ORANGE:
				colours['orange'].append([tile.rect[0],tile.rect[1]])
			elif tile.colour == PURPLE:
				colours['purple'].append([tile.rect[0],tile.rect[1]])
			else:
				pass

		matched_chains = []
		
		for colour in colours:
			for tile in colours[colour]:
				x,y = tile

				neighbours = []
				neighbours.append([x, y-50]) # up
				neighbours.append([x, y+50]) # down
				neighbours.append([x-50, y]) # left
				neighbours.append([x+50, y]) # right

				found=0
				matched_chains = []
				for neighbour in neighbours:
					if neighbour in colours[colour]:
						i=0
						for chain in all_chains[colour]:
							try:
								if neighbour in chain:
									found=1
									if tile not in chain:
										chain.append(tile)
									else:
										matched_chains.append(i)
								elif tile in chain:
									found=1
									if neighbour not in chain:
										chain.append(neighbour)
									else:
										matched_chains.append(i)
							except:
								pass
		
							i=i+1
		
						if not found:
							found=1
							all_chains[colour].append([tile,neighbour])
		
				if not found:
					found=1
					all_chains[colour].append([tile])
		
				combined_chain = []
				if len(matched_chains) > 1:
					for idx in matched_chains:
						for tile in all_chains[colour][idx]:
							if tile not in combined_chain:
								combined_chain.append(tile)
		
				if len(matched_chains) > 1:
					for idx in matched_chains:
						all_chains[colour][idx] = []
		
				if combined_chain:
					combined_chain.sort()
					all_chains[colour].append(combined_chain)

		bonus = []
		replacements = []

		# Special tiles
		bonus_found = False
		penalty_found = False
		for colour in all_chains:
			for chain in all_chains[colour]:
				if len(chain) >= 3:
					for chain_tile in chain:
						for board_tile in board.sprites():
							if chain_tile == [board_tile.rect[0],board_tile.rect[1]]:
								if board_tile.special:
									if board_tile.special == 'all':
										# play good sound
										bonus_found = True
										all_chains[colour] = [colours[colour]]
										board_tile.special = False
									elif board_tile.special == 'horizontal':
										# play good sound
										bonus_found = True
										bonus_chain = []
										for i in range(0,351,50):
											if i == board_tile.rect[0]:
												continue
											elif [i,board_tile.rect[1]] in all_tiles:
												bonus_chain.append([i,board_tile.rect[1]])
										all_chains[colour].append( bonus_chain )
										board_tile.special = False
									elif board_tile.special == 'vertical':
										# play good sound
										bonus_found = True
										bonus_chain = []
										for i in range(0,351,50):
											if i == board_tile.rect[1]:
												continue
											elif [board_tile.rect[0],i] in all_tiles:
												bonus_chain.append([board_tile.rect[0],i])
										all_chains[colour].append( bonus_chain )
										board_tile.special = False
									elif board_tile.special == 'plus_one':
										# play bad sound
										penalty_found = True
										replacements.append('plus_one')
									elif board_tile.special == 'time_penalty':
										# play bad sound
										penalty_found = True
										self.time_bonus = self.time_bonus - 14

		for colour in all_chains:
			for chain in all_chains[colour]:
				# Bonus for all grouping together all tiles of a colour
				if len(chain) == len(colours[colour]):
					self.time_bonus = self.time_bonus+10
					self.score = self.score+500
					self.bonus = self.bonus+5

				# You need three or more tiles to score
				if len(chain) >= 3:
					top = 0
					bottom = 0
					left = 0
					right = 0
					for tile in chain:
						x,y = tile
						if x == 0:
							top = 1
						if x == 350:
							bottom = 1
						if y == 0:
							left = 1
						if y == 350:
							right = 1
	
						self.remove_tile(tile)
						if tile not in replacements:
							replacements.append(tile)

					# Now check for any edge-to-edge groups.
					# The group can be in any order so we need to check
					# every link in the chain for edge contact
					if top and bottom:
						self.score = self.score+(len(chain)*5) + 100
						self.bonus = self.bonus+1
					elif left and right:
						self.score = self.score+(len(chain)*5) + 100
						self.bonus = self.bonus+1
					else:
						self.score = self.score+(len(chain)*5)

					self.time_bonus = self.time_bonus+len(chain)

		if self.time_bonus == 0:
			self.time_bonus = self.time_bonus - 5
			self.penalty_sound.play()

		self.replacements = replacements

		if bonus_found:
			self.bonus_sound.play()

		if penalty_found:
			self.penalty_sound.play()

	def clear_board(self,board):
		"""Empty the board at the end of a game"""
		self.board = board
		for tile in self.board.sprites():
			self.remove_tile(tile.rect)

	def remove_tile(self,pos):
		"""Remove each processed tile from the board at the end of a round"""
		self.marker.rect[0] = pos[0]
		self.marker.rect[1] = pos[1]
		rectlist = pygame.sprite.spritecollide(self.marker,self.board,1)
		pygame.display.update(rectlist)
		self.sound.play()
		pygame.time.wait(50)

	def reset(self):
		self.bonus = 0
		self.score = 0
		self.time_bonus = 0
		self.replacements = []

	def update(self):
		self.image = self.font.render("Score: %d" % self.score, 1, (255,255,255))
		self.rect = self.image.get_rect()
		self.rect = self.rect.move([410,5])

class Tile(pygame.sprite.Sprite):
	def __init__(self,colour,pos,simple=1):
		"""Initialise a tile - the basic game unit"""
		pygame.sprite.Sprite.__init__(self)

		self.colour = colour
		self.image = pygame.Surface( (49,49) )
		self.image.fill(colour)
		self.rect = self.image.get_rect()
		self.rect = self.rect.move(pos)

		if simple:
			self.special = False
		else:
			if self.colour == RED:
				colour = 'red'
			elif self.colour == GREEN:
				colour = 'green'
			elif self.colour == BLUE:
				colour = 'blue'
			elif self.colour == YELLOW:
				colour = 'yellow'
			elif self.colour == ORANGE:
				colour = 'orange'
			elif self.colour == PURPLE:
				colour = 'purple'

			special_tiles = [ 'horizontal', 'vertical', 'all', 'plus_one', 'time_penalty' ]
			random.shuffle(special_tiles)
			self.special = special_tiles.pop()
			self.image = pygame.image.load('images/' + self.special + '_' + colour + '.png').convert()

	def move(self,pos):
		"""Only move the square if it is a direct neighbour of a blank space"""

		x = pos[0] - (pos[0] % 50)
		y = pos[1] - (pos[1] % 50)

		if x > self.rect[0] or y > self.rect[1]:
			if x > self.rect[0] + 50 or y > self.rect[1] + 50:
				return None

		if x < self.rect[0] or y < self.rect[1]:
			if x < self.rect[0] - 50 or y < self.rect[1] - 50:
				return None

		# Diagonal movements not allowed
		if ( x > self.rect[0] and y > self.rect[1] ) or ( x < self.rect[0] and y < self.rect[1] ):
			return None

		if ( x > self.rect[0] and y < self.rect[1] ) or ( x < self.rect[0] and y > self.rect[1] ):
			return None

		self.rect[0] = x
		self.rect[1] = y

if __name__ == '__main__':
	Game = Game()
	Game.demo_mode()