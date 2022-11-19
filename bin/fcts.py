from math import sqrt, ceil, pi


def screen_to_board(x, y, tile_height):
	"""
	translate the coord on screen to x,y,z hexagonal axis
	"""
	x -= sqrt(3)*tile_height * 1.25
	y -= tile_height/2
	board_x = ((2*y)/3)/(tile_height/2)
	board_z = ((x*sqrt(3) - y)/3)/(tile_height/2)
	board_y = - board_x - board_z
	return (round(board_x), round(board_y), round(board_z))


def vector_add(vector1, vector2):
	"""
		add 2 3D vectors together
	"""
	return (vector1[0] + vector2[0], vector1[1] + vector2[1], vector1[2] + vector2[2])


def vector_sub(vector1, vector2):
	"""
		subtract 2 3D vectors together
	"""
	return (vector1[0] - vector2[0], vector1[1] - vector2[1], vector1[2] - vector2[2])


def vector_cross_product(a, b):
	"""
		find the cross product of 2 vectors
	"""
	return (a[1]*b[2] - a[2]*b[1],
			a[2]*b[0] - a[0]*b[2],
			a[0]*b[1] - a[1]*b[0])


def is_the_right_parallel(a, b):
	"""
		determines if a vector is the parallel we are looking for
	"""
	for i in range(len(a)):
		if a[i] < 0 < b[i] or b[i] < 0 < a[i]:
			return False
	return True  # if you can't prove it's False it's True


def other_player(player):
	"""
		return the opposite player
	"""
	if player == "black":
		return "white"
	elif player == "white":
		return "black"


def board_to_screen(x, y, z, tile_height):
	"""
		translate the coords of hex tiles to their screen coords
	"""
	screen_x = (-((sqrt(3)*y)+(sqrt(3)*x/2)) * tile_height/2) + (sqrt(3)*tile_height*1.25)
	screen_y = ((3/2) * x * tile_height/2) + (tile_height/2)
	return (screen_x, screen_y)


def get_starting_pos(n):
	"""
		generate a list of starting locations for each player
	"""
	whites = []
	blacks = []

	for i in range(n):
		whites.append((0, -i, i))
		whites.append((1, -i, i-1))

		blacks.append((6, -i-3, i-3))
		blacks.append((7, -i-3, i-4))

	return (whites, blacks)


def test_get_starting_pos(n):
	"""
		made for testing/debugging purpose only
	"""
	whites = [(4, -5, 1)]
	blacks = [(4, -4, 0), (4, -6, 2), (5, -5, 0), (5, -6, 1), (3, -4, 1), (3, -5, 2),
				(2, -6, 4), (5, -8, 3), (2, -2, 0), (3, -2, -1), (3, -7, 4), (6, -8, 2), (1, -3, 2),
				(1, -4, 3), (5, -3, -2), (6, -4, -2)]
	return (whites, blacks)


def validate_coords(coords):
	"""
		return True if the coordinate are valid, False if not
		usable tiles coords follow a pattern like that:
		if x = 0 | 1 -> y = 0 to -7
		if x = 2 | 3 -> y = -1 to -8
		if x = 4 | 5 -> y = -2 to -9
		if x = 6 | 7 -> y = -3 to -10
		z isn't relevant since it depends on the value of x and y at the same time
		can't really check that without a big match statement with hardcoded values or lots of ifs :/
		works at least i guess ¯\_(ツ)_/¯
	"""
	x = coords[0]
	y = coords[1]
	z = coords[2]

	if (x + y + z) != 0:
		print("Illegal Coordinates")
		return False

	if x == 0:
		return -8 <= y <= 2
	elif x in (1, 2):
		return -9 <= y <= 1
	elif x in (3, 4):
		return -10 <= y <= 0
	elif x in (5, 6):
		return -11 <= y <= -1
	elif x == 7:
		return -12 <= y <= -2
	else:
		return False


def warp(coords):
	"""
		gives the coordinates of the tile they can warp to
	"""
	x = coords[0]
	y = coords[1]
	z = coords[2]

	if 1 <= x <= 7 and 2 >= y >= -1:
		return vector_add(coords, (0, -11, 11))
	elif 0 <= x <= 6 and -9 <= y <= -12:
		return vector_add(coords, (0, 11, -11))
	return None


def takes_score(pieces_taken):
	"""
		returns the score to add for x takes
		it's functionally the same as doing 100*2**(x-1) but it makes you look smarter
	"""
	return 100 << pieces_taken


def get_pieces_bonus(pieces_left, queens):
	"""
		gives bonus points based on pieces left and queens
	"""
	return 100 << (queens ^ pieces_left) if (queens ^ pieces_left) > pieces_left else 100 << queens


def get_time_bonus(time_spent):
	"""
		calculates the bonus points for time spent before playing
	"""
	return ceil(time_spent ** pi) if time_spent <= 30 else ceil(time_spent % pi)
