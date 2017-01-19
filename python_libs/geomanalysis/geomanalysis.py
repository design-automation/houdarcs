import copy, math
import numpy as np
import shapely as sh

D_TOL = 0.0001
A_TOL = 0.0001

#==============================================================================================================================================================
# Geometry classes
#==============================================================================================================================================================
class Vector3d:
	"""A vector in 3d space
	"""
	def __init__(self, vector):
		# Convert vertices to floats and crete vector
		if isinstance(vector, np.ndarray):
			self.vector = np.copy(vector)
		elif isinstance(vector[0], np.ndarray):
			assert len(vector) == 2
			self.vector = vector[1] - vector[0]
		elif isinstance(vector[0], tuple):
			assert len(vector) == 2
			vector = [tuple(float(i) for i in vertex) for vertex in vector]
			self.vector = np.array(vector[1]) - np.array(vector[0])
		else:
			assert len(vector) == 3
			vector = [float(i) for i in vector]
			self.vector = np.array(vector)

	def normalise(self):
		self.vector = self.vector / np.linalg.norm(self.vector)

	def length(self):
		return np.linalg.norm(self.vector)

	def flip(self):
		self.vector = self.vector * -1

	def transform(self, matrix):
		self.vector = matrix.dot(self.vector)

	def angle(self, vec2):
		vecs = [np.copy(self.vector), np.copy(vec2.vector)]
		vecs = [vec / np.linalg.norm(vec) for vec in vecs]
		return (math.acos(np.dot(*vecs)) / math.pi) * 180.0

	def is_horizontal(self):
		return 89.0 <= self.angle(UP_VEC) <= 91.0

	def is_vertical_up(self):
		return self.angle(UP_VEC) <= 1.0

	def is_vertical_down(self):
		return self.angle(UP_VEC) >= 179.0

	def is_sloping_up(self):
		return 45.0 <= self.angle(UP_VEC) < 89.0

	def is_leaning_up(self):
		return 1.0 < self.angle(UP_VEC) < 45.0

	def is_sloping_down(self):
		return 91.0 < self.angle(UP_VEC) <= 135.0

	def is_leaning_down(self):
		return 135 < self.angle(UP_VEC) < 179.0

	def to_tuple(self):
		return tuple(self.vector.tolist())

	def __str__(self):
		return str(self.to_tuple())

UP_VEC = Vector3d((0,0,1))

#==============================================================================================================================================================
class Line3d:
	"""An line with two vertices in 3d.
	"""
	def __init__(self, vertices):
		assert len(vertices) == 2
		# If verts are numpy, make copies
		if isinstance(vertices[0], np.ndarray):
			self.vertices = [np.copy(vertex) for vertex in vertices]
		# Otherwise create numpy verts
		else:
			# Convert vertices to floats
			vertices = [tuple(float(i) for i in vertex) for vertex in vertices]
			# Create points
			self.vertices = [np.array(vertex) for vertex in vertices]

	def length(self):
		return np.linalg.norm(self.vertices[1] - self.vertices[0])

	def to_vector(self):
		return Vector3d(self.vertices)

	def to_tuples(self):
		return [tuple(vertex.tolist()) for vertex in self.vertices]

	def __str__(self):
		return str(self.to_tuples())

#==============================================================================================================================================================
def create_vertex_list(vertices):
	# Rotate points so the first set of vertices have the lowest z
	pairs = zip(vertices[:], (vertices + [vertices[0]])[1:])
	heights = [(pair[0][2] + pair[1][2])/2. for pair in pairs]
	index = np.argmin(heights)
	vertices = vertices[index:] + vertices[:index]
	return vertices

def create_edges(vertices):
	exploded = zip(vertices[:], (vertices + [vertices[0]])[1:])
	edges = [Line3d(edge) for edge in exploded]
	return edges

def create_normal(vertices):
	origin, pt1, pt2 = [vertices[0], vertices[1], vertices[-1]]
	vec1 = pt1 - origin
	vec2 = pt2 - origin
	normal = np.cross(vec1, vec2)
	normal =  (normal / np.linalg.norm(normal))
	return Vector3d(normal)

def create_matrix(vertices):
	origin, pt1, pt2 = [vertices[0], vertices[1], vertices[-1]]
	pt1_moved = pt1 - origin
	pt2_moved = pt2 - origin
	vec_x = pt1_moved / np.linalg.norm(pt1_moved)
	vec_t = pt2_moved / np.linalg.norm(pt2_moved)
	vec_z = np.cross(vec_x, vec_t)
	vec_z = vec_z / np.linalg.norm(vec_z)
	vec_y = np.cross(vec_z, vec_x)
	vec_y = vec_y / np.linalg.norm(vec_y)
	rot = np.matrix([
		[vec_x[0],vec_y[0],vec_z[0],0],
		[vec_x[1],vec_y[1],vec_z[1],0],
		[vec_x[2],vec_y[2],vec_z[2],0],
		[0,0,0,1]]).transpose()
	move = np.matrix([
		[1,0,0,-origin[0]],
		[0,1,0,-origin[1]],
		[0,0,1,-origin[2]],
		[0,0,0,1]])
	matrix = rot * move
	return matrix

class Polygon3d:
	""" A closed planar polygon in 3d.
	"""
	def __init__(self, vertices):
		assert len(vertices) > 2
		# If verts are numpy, make copies
		if isinstance(vertices[0], np.ndarray):
			self.vertices = [np.copy(vertex) for vertex in vertices]
		else:
			# Convert all values to floats and creates numpy vertices
			vertices = [tuple(float(i) for i in vertex) for vertex in vertices]
			self.vertices = [np.array(vertex) for vertex in vertices]
		# Rotate the vertices
		self.vertices = create_vertex_list(self.vertices)
		# Create edges
		self.edges = create_edges(self.vertices)
		# Create normal
		self.normal = create_normal(self.vertices)
		# Create matrix to convert to 2d
		self.matrix = create_matrix(self.vertices)

	def transform(self, matrix):
		vertices4 = [np.append(vertex,[1]) for vertex in self.vertices]
		result = [np.array(matrix.dot(vertex))[0][:3] for vertex in vertices4]
		self.vertices = result
		# Rotate the vertices
		self.vertices = create_vertex_list(self.vertices)
		# Create edges
		self.edges = create_edges(self.vertices)
		# Create normal
		self.normal = create_normal(self.vertices)
		# Create matrix to convert to 2d
		self.matrix = create_matrix(self.vertices)

	def is_planar(self):
		polygon_copy = copy.deepcopy(self)
		polygon_copy.transform(self.matrix)
		return sum([abs(vertex[2]) > D_TOL for vertex in polygon_copy.vertices]) == 0

	def is_coplanar(self, polygon):
		polygon_copy = copy.deepcopy(polygon)
		polygon_copy.transform(self.matrix)
		return sum([abs(vertex[2]) > D_TOL for vertex in polygon_copy.vertices]) == 0

	def is_rectanglar(self):
		if len(self.vertices) != 4:
			return False
		diag1, diag2 = [Line3d([self.vertices[0], self.vertices[2]]), Line3d([self.vertices[1], self.vertices[3]])]
		if abs(diag1.length() - diag2.length()) > D_TOL:
			return False
		if abs(self.edges[0].length() - self.edges[2].length()) > D_TOL:
			return False
		if abs(self.edges[1].length() - self.edges[3].length()) > D_TOL:
			return False
		return True

	def is_stable(self):
		return self.edges[0].to_vector().is_horizontal()

	def is_horizontal(self):
		return self.normal.is_vertical_up() or self.normal.is_vertical_down()

	def is_vertical(self):
		return self.normal.is_horizontal()

	def is_sloping(self):
		return self.normal.is_leaning_up() or self.normal.is_leaning_down()

	def is_leaning(self):
		return self.normal.is_sloping_up() or self.normal.is_sloping_down()

	def to_tuples(self):
		return [tuple(vertex.tolist()) for vertex in self.vertices]

	def is_convex(self):
		pass

	def contains_polygn(self, polygon):
		pass

	def contains_line(self, line):
		pass

	def __str__(self):
		return str(self.to_tuples())

#==============================================================================================================================================================
# Tests
#==============================================================================================================================================================

def test_vectors():
	v = Vector3d((0,0,10))
	print v.length()
	v.normalise()
	print v.length()
	print v
	v.flip()
	print v
	v2 = copy.deepcopy(v)
	v2.flip()
	print "===Vector 0==="
	v0 = Vector3d((1,0.5,0))
	print "horizontal", v0.is_horizontal()
	print "===Vector 2==="
	print "v2", v2
	print "v", v
	print v.is_vertical_up()
	print v.is_vertical_down()
	print "===Vector 3==="
	v3 = Vector3d((1,0,1.5))
	print v3, UP_VEC
	print "angle", v3.angle(UP_VEC)
	print 'sloping', v3.is_sloping_up()
	print 'leaning', v3.is_leaning_up()
	print "===Vector 4==="
	v3.flip()
	print v3, UP_VEC
	print "angle", v3.angle(UP_VEC)
	print 'sloping', v3.is_sloping_up()
	print 'leaning', v3.is_leaning_up()
	print 'sloping down', v3.is_sloping_down()
	print 'leaning down', v3.is_leaning_down()

def test_line():
	l = Line3d([(10,0,0),(10,0,10)])
	print l
	print l.length()
	print l.to_vector()

def test_polys():
	rect_pts1 = [(0,0,0),(10,0,0),(10,0,10),(0,0,10)]
	p = Polygon3d(rect_pts1)
	print p
	print p.matrix
	p.transform(p.matrix)
	print p.vertices

	p2 = Polygon3d(rect_pts1)
	print "planar", p2.is_planar()
	print "rect", p2.is_rectanglar()

	tri_pts1 = [(0,0,0),(10,0,0),(5,0,11)]
	p3 = Polygon3d(tri_pts1)
	print p3.normal.angle(UP_VEC)
	print "horiz", p3.is_horizontal()
	print "sloping", p3.is_sloping()
	print "leaning", p3.is_leaning()
	print "vertical", p3.is_vertical()
	print "rect", p3.is_rectanglar()

	tri_pts2 = [(0,0,0),(10,0,0),(5,0,11)]
	p4 = Polygon3d(tri_pts2)
	print "stable", p4.is_stable()

	rect_pts2 = [(10,0,0),(10,0,10),(0,0,10),(0,0,0)]
	p5 = Polygon3d(rect_pts2)
	print p5

if __name__ == "__main__":
	test_polys()