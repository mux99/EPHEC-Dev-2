import bin.fcts as fcts
from classes.piece import Piece
from classes.game_logic import GameLogic
from time import time

from random import randint
import pyglet


class App(GameLogic):
	"""
		---TBD---
	"""
	def __init__(self):
		self._current_player = "white"
		self._player_scores = {"white": 0, "black": 0}
		self._winner = None
		self.paused = False

		# pieces
		self._pieces = []  # list all pieces on the board
		self._ghost_pieces = []  # pieces representing potential moves

		# coords
		self._last_click = None
		self._last_click_time = 0
		self._possible_takes = []
		self._possible_moves = []

		# textures
		self.textures = {"black": None, "white": None}
		self._scale = 1
		self._select_opacity = 180

		# scaling
		self._tile_height = 1

	def __str__(self):
		return f"player:{self._current_player}\nboard:{self._pieces}"

	def rescale(self, height):
		"""
			recalculate and update all scaling of pieces and distances
		"""
		self._tile_height = height / 6.25
		self._scale = height / 2600
		for i in self._pieces:
			i.scale = self._scale

		for i in self._ghost_pieces:
			i.scale = self._scale

	def draw_textures(self):
		"""
			draw all pieces on the board
		"""
		# draw pieces
		for i in self._pieces:
			i.draw(self._tile_height)

		# draw ghosts
		for i in self._ghost_pieces:
			i.draw(self._tile_height)

	def init_board(self):
		"""
			fill board with pieces at their correct starting positions
		"""
		pos = fcts.get_starting_pos(8)
		for i in pos[0]:
			self._pieces.append(Piece(coord=i, player="white", texture=self.textures["white"],
										texture2 = self.textures["white_queen"] ,scale=self._scale, promotion=True))
		for i in pos[1]:
			self._pieces.append(Piece(coord=i, player="black", texture=self.textures["black"],
										texture2 = self.textures["black_queen"], scale=self._scale))

	def select(self, new_click):
		"""
			change the piece selected based on games state and click coordinates
		"""
		# click must be on a piece possessed by current player
		if not self.is_piece(new_click) or self.get_piece(new_click).player != self._current_player:
			return

		# something was already selected
		if self._last_click is not None:
			self.get_piece(self._last_click).opacity = 255
			# remove previous takes
			for i in self._possible_takes:
				self.get_piece(i).opacity = 255

		# select new piece
		self._last_click = new_click
		self._last_click_time = time()
		self.get_piece(self._last_click).opacity = self._select_opacity

		if self.get_piece(self._last_click).promotion:
			self._possible_moves = self.get_moves_queen(self._last_click,self._current_player)
		else:
			self._possible_moves = self.get_moves(self._last_click,self._current_player)

	def move(self, new_click):
		"""
			move selected piece so clicked location (if valid)
		"""
		if not self.is_piece(new_click) and self._last_click is not None:
			# only if move is valid
			if new_click in self._possible_moves:
				# remove taken pieces
				taken_pieces = 0
				for i in self.get_takes(self._last_click, new_click, self._current_player):
					taken_pieces += 1
					self.take_piece(i)
				if taken_pieces > 0:
					self._player_scores[self._current_player] += fcts.takes_score(taken_pieces)

				# move player
				self.get_piece(self._last_click).coord = new_click
				self.get_piece(new_click).opacity = 255
				self._last_click = None
				self._current_player = fcts.other_player(self._current_player)

	def update(self, new_click):
		"""

		"""
		# remove previous takes
		for i in self._possible_takes:
			try:
				self.get_piece(i).opacity = 255
			except AttributeError:
				# the piece doesn't exist anymore (killed)
				pass

		# update gamestate
		self._ghost_pieces = []
		if self._last_click is not None:
			# generate ghost pieces
			for i in self._possible_moves:
				tmp = Piece(texture=self.textures[self._current_player],scale=self._scale)
				tmp.coord = i
				tmp.opacity = 150
				self._ghost_pieces.append(tmp)

			# mark new takes
			self._possible_takes = self.get_all_takes(self._last_click,self._current_player)
			for i in self._possible_takes:
				self.get_piece(i).opacity = 200

		if self._last_click is None:
			self._possible_takes = []
		if self.game_is_finished():
			self._winner = self.game_is_finished()
			pieces_left = len(self._pieces)
			queens = 0
			for p in self._pieces:
				if p.promotion:
					queens += 1
			self._player_scores[self._winner] += fcts.get_pieces_bonus(pieces_left, queens)
			print(F"Score black: {self._player_scores['black']}\n Score white: {self._player_scores['white']}")
			print("Game finished")

	def promotion(self):
		"""
			promote all pieces corresponding to criteria
		"""
		for i in self._pieces:
			if not i.promotion and i.player == "white":
				if i.coord[0] == 7:
					i.promote()
			elif not i.promotion and i.player == "black":
				if i.coord[0] == 0:
					i.promote()

	def click(self, screen_x, screen_y):
		"""
			receive coords of a click on screen and takes action on it based on curent game state
		"""
		new_click = fcts.screen_to_board(screen_x, screen_y, self._tile_height)
		#print(new_click)

		# discard invalid clicks
		if not fcts.validate_coords(new_click):
			return

		# discard click twice
		if self._last_click == new_click:
			return

		self.select(new_click)
		self.move(new_click)
		self.update(new_click)
		self.promotion()
		self._last_click_time = time() - self._last_click_time
		self._player_scores[self._current_player] += fcts.get_time_bonus(self._last_click_time)

	def AI_move(self):
		"""
			temporary-- to be replaced by multiplayer turns
		"""
		if self._last_click is not None:
			return

		moves = []

		# list all possible moves
		for i in self._pieces:
			if i.player == "black":
				if i.promotion:
					potential_moves = self.get_moves_queen(i.coord, "black")
				else:
					potential_moves = self.get_moves(i.coord, "black")
				for j in potential_moves:
					moves.append((i.coord, j))

		# select a random move
		if len(moves) > 0:
			move = moves[randint(0,len(moves)-1)]
			for i in self.get_takes(move[0],move[1],"black"):
				self.take_piece(i)
			self.get_piece(move[0]).coord = move[1]

	def game_is_finished(self):
		"""
			checks if either of the players has no pieces left
		"""
		black_pieces = [p for p in self._pieces if p.player == "black"]
		white_pieces = [p for p in self._pieces if p.player == "white"]
		return "white" if len(black_pieces) == 0 else "black" if len(white_pieces) == 0 else False
