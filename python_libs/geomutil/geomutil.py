import numpy as np
import math

d_tol = 1e-12
a_tol = 1e-12

#==============================================================================================================================================================
# Vectors
#==============================================================================================================================================================

def vector(start, end, normalise=True):
    """Creates a new vector.
    Arguments:
    ---------
    start -- the start point of the vector (2d or 3d)
    end -- the end point of the vector (2d or 3d)
    normalise -- boolean, if true the vector is normalised
    """
    vec = np.array(end) - np.array(start)
    if normalise:
        vec = vec / np.linalg.norm(vec)
    return tuple(vec.tolist())

def flip_vector(vec):
    """Reverse the direction of a vector.
    Arguments:
    ---------
    vec -- the vector to be flipped
    """
    return tuple((np.array(vec) * -1).tolist())

def normalise_vector(vec):
    """Normalise a vector.
    Arguments:
    ----------
    vec -- the vector to normalise (2d or 3d)
    """
    vec = np.array(vec)
    return tuple((vec / np.linalg.norm(vec)).tolist())

def rotate_vector2d(vec, angle):
    """Rotate a by a specific angle. 
    Arguments:
    ---------
    vec -- the 2d vector to normalise
    angel -- a clockwise angle of rotation, in degrees
    """
    np_vec = np.array(vec)
    theta = np.radians(rot)
    c, s = np.cos(theta), np.sin(theta)
    r = np.matrix([[c, -s], [s, c]])
    return tuple(r.dot(np_vec).tolist()[0])

def transform_vector3d(vec, matrix):
    """Transform a vector with a numpy transofrmation matrix.
    Arguments:
    ---------
    vec -- the 3d vector to be transformed
    matrix -- the numpy transformation matrix
    """
    vec = np.append(np.array(vec), [1])
    return tuple(matrix.dot(vec).tolist()[0][:3])

def angle_vector3d(vec1, vec2):
    """Calculate the angle between two vectors.
    """
    vecs = [np.array(vec1), np.array(vec2)]
    vecs = [vec / np.linalg.norm(vec) for vec in vecs]
    print np.dot(*vecs)
    return 180 * (math.acos(np.dot(*vecs)) / math.pi)

def are_parallel_vector3d(vec1, vec2):
    """Calculate the vectors are parallel to one another (but not necessarily pointing in teh same direction).
    """
    vecs = [np.array(vec1), np.array(vec2)]
    vecs = [vec / np.linalg.norm(vec) for vec in vecs]
    return (abs(np.dot(*vecs)) - 1.0) < a_tol

# LINES =======================================================================================================================================================

def thicken_line3d(line, width_left, width_right, vec):
    """Creates a rectangular polygon from a 3d line. The rectangle lies on the line, and is perpendicular to the vector. 
    Arguments:
    ---------
    line - two 3d points
    width_left -- the width from the line ot the left side of the rectabgle
    width_right -- the width from the line to the right side of the rectangle
    """
    npt1, npt2 = [np.array(line[0]), np.array(line[1])]
    perp = np.cross(npt2 - npt1, vec)
    width_vec = perp / np.linalg.norm(perp)
    rectangle = [npt1 + width_vec * width_left, npt2 + width_vec * width_left, npt2 - width_vec * width_right, npt1 - width_vec * width_right]
    return [tuple(pt.tolist()) for pt in rectangle]

def thicken_perp_line3d(line, width_left, width_right, vec):
    """Creates a parallelogram polygon from a 3d line. The parallelogram lies on the line, and is perpendicular to the vector. The ends of the parallelogram 
    remain perpendicular to the line, when projected onto the xy plane.
    Arguments:
    ---------
    line - two 3d points
    width_left -- the width from the line ot the left side of the rectabgle
    width_right -- the width from the line to the right side of the rectangle
    """
    npt1, npt2 = [np.array(line[0]), np.array(line[1])]
    line_vec = npt2 - npt1
    line_vec[-1] = 0
    perp = np.cross(line_vec, vec)
    width_vec = perp / np.linalg.norm(perp)
    rectangle = [npt1 + width_vec * width_left, npt2 + width_vec * width_left, npt2 - width_vec * width_right, npt1 - width_vec * width_right]
    return [tuple(pt.tolist()) for pt in rectangle]

def thicken_line2d(line, width_left, width_right):
    """Creates a rectangular polygon from a 3d line. The width of the rectangle is defined by the pair of doubles
    from the distances arg.
    Arguments:
    ---------
    line -- two 2d points
    width_left -- the width from the line ot the left side of the rectabgle
    width_right -- the width from the line to the right side of the rectangle
    """
    npt1, npt2 = [np.array(line[0]), np.array(line[1])]
    perp = np.cross(npt2 - npt1, np.array([0,0,1]))[0:2]
    width_vec = perp / np.linalg.norm(perp)
    rectangle = [npt1 + width_vec * width_left, npt2 + width_vec * width_left, npt2 - width_vec * width_right, npt1 - width_vec * width_right]
    return [tuple(pt.tolist()) for pt in rectangle]

def offset_line2d(line, distance):
    """Offsets a line, by creating a parallel line.
    Arguments:
    ---------
    line -- two 2d points
    distances -- a float, the offset distance to the right of the line
    """
    npt1, npt2 = [np.array(line[0]), np.array(line[1])]
    perp = np.cross(npt2 - npt1, np.array([0,0,1]))[0:2]
    vec = perp / np.linalg.norm(perp) * distance
    line = [npt1 + vec, npt2 + vec]
    return [tuple(pt.tolist()) for pt in line]

def line_length(line):
    """Calculate the length of a line.
    Arguments:
    ---------
    line -- two points (2d or 3d)
    """
    npt1, npt2 = [np.array(line[0]), np.array(line[1])]
    return np.linalg.norm(npt2 - npt1)

# POLYGONS ====================================================================================================================================================

def shift_polygon(polygon, index):
    """Creates  a copy of the polygon, but with the points shifted so that the point at the specified index becomes the first point.
    Arguments:
    ---------
    polygon -- a list of points (2d or 3d)
    index -- int, the amount to shift the edges (0 = no change)
    """
    return polygon[index:] + polygon[:index]

def zshift_polygon3d(polygon):
    """Creates  a copy of the polygon, but with the points shifted so that the edge with the lowest z coord becomes the first edge.
    Arguments:
    ---------
    polygon -- a list of coplanar 3d points
    """
    pairs = zip(polygon[:], (polygon + [polygon[0]])[1:])
    heights = [(pair[0][2] + pair[1][2])/2. for pair in pairs]
    index = np.argmin(heights)
    return polygon[index:] + polygon[:index]

def flip_polygon(polygon):
    """Flips the direction of the polygon (and its normal) by reversing tehe list of points.
    Arguments:
    ---------
    polygon -- a list of points (2d or 3d)
    """
    return np.array(polygon)[::-1].tolist()

def explode_polygon(polygon):
    """Breakes a polygon into a list of edge lines, where each line is defined by a pair of points. The last pair consists of items -1 and 0 from the original list. 
    Arguments:
    ---------
    polygon -- a list of points (2d or 3d)
    """
    return zip(polygon[:], (polygon + [polygon[0]])[1:])

def move_polygon(polygon, vec):
    """Moves a polygon, with the direction and distance specified by a vector.
    Arguments:
    ---------
    polygon -- a list of points (2d or 3d)
    vec -- the translation vector (2d ot 3d)
    """
    vec = np.array(vec)
    return [tuple((np.array(pt) + vec).tolist()) for pt in polygon]


def offset_polygon3d(polygon, distance):
    """Offsets a polygon in the direction of the normal. 
    Arguments:
    ---------
    polygon -- a list of coplanar 3d points
    distance -- the offset distance
    """
    polygon = [np.array(pt) for pt in polygon]
    vec = np.cross(polygon[0] - polygon[1], polygon[2] - polygon[1])
    vec = (vec / np.linalg.norm(vec)) * distance
    return [tuple((pt + vec).tolist()) for pt in polygon]

def thicken_polygon3d(polygon, thickness_up, thickness_down):
    """Creates a solid by thickening thickens the polygon in the normal direction. For the resulting solid, the direction of the points when viewed
    from outside are ordered anticlockwise.
    Arguments:
    ---------
    polygon -- a list of coplanar 3d points
    thickness_up -- the thickness in the normal direction
    thickness_down -- the thickness in the -normal direction
    """
    off1 = offset_polygon(polygon, thickness_up)
    off2 = offset_polygon(polygon, -thickness_down)
    pairs = zip(explode_polygon(off1), explode_polygon(off2))
    sides = [[pair[0][0], pair[0][1], pair[1][1], pair[1][0]] for pair in pairs]
    return [flip_polygon(off1), off2] + sides

def zthicken_polygon3d(polygon, thickness_up, thickness_down):
    """Creates a solid by thickening thickens the polygon in the z direction. The direction of the points when viewed from outside is anticlockwise.
    Arguments:
    ---------
    polygon -- a list of coplanar 3d points
    thickness_up -- the thickness in the +z direction
    thickness_down -- the thickness in the -z direction
    """
    np_polygon = [np.array(pt) for pt in polygon]
    normal_vec = np.cross(np_polygon[0] - np_polygon[1], np_polygon[2] - np_polygon[1])
    if normal_vec[2] < 0:
        polygon = flip_polygon(polygon)
    up = move_polygon(polygon, np.array((0,0,thickness_up)))
    down = move_polygon(polygon, np.array((0,0,thickness_down)))
    pairs = zip(explode_polygon(up), explode_polygon(down))
    sides = [[pair[0][1], pair[0][0], pair[1][0], pair[1][1]] for pair in pairs]
    return [down, flip_polygon(up)] + sides

def transform_polygon3d(polygon, matrix):
    """Transform the polygon with the matrix.
    Arguments:
    ---------
    polygon -- a list of coplanar 3d points
    matrix -- a numpy 4 x 4 matrix
    """
    np_polygon = [np.append(np.array(pt),[1]) for pt in polygon]
    return [tuple(matrix.dot(np.array(pt)).tolist()[0][:3]) for pt in np_polygon]

def polygon3d_matrix(polygon):
    """Creates a matrix that will transform the polygon onto the xy plane. The first point will be at the xy origin, and the first edge will be aligned
    with the x-axis.
    Arguments:
    ---------
    polygon -- a list of coplanar 3d points, the points should not be colinear 
    """
    origin, pt1, pt2 = [np.array(polygon[0]), np.array(polygon[1]), np.array(polygon[-1])]
    # move the origin to (0,0,0)
    pt1 = pt1 - origin
    pt2 = pt2 - origin
    # create a normalised vecotr along the x axis
    vec_x = pt1 / np.linalg.norm(pt1)
    # create a normalised temporary vector in the plane from pt1 to pt2
    vec_t = pt2 / np.linalg.norm(pt2)
    # create a z vector
    vec_z = np.cross(vec_x, vec_t)
    vec_z = vec_z / np.linalg.norm(vec_z)
    # create the y vector
    vec_y = np.cross(vec_z, vec_x)
    vec_y = vec_y / np.linalg.norm(vec_y)
    # create the matrix
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
    return rot * move

def polygon3d_normal(polygon):
    """Create a normal vector for the polygon.
    Arguments:
    ---------
    polygon -- a list of coplanar 3d points
    """
    pt1, origin, pt2 = [np.array(pt) for pt in polygon[:3]]
    vec1 = pt1 - origin
    vec2 = pt2 - origin
    normal = np.cross(vec1, vec2)
    return tuple((normal / np.linalg.norm(normal)).tolist())


def test1():
    vec1 = (-1,1.01,3)
    vec2 = (10,-10,-30)
    vec3 = (-1,0,0)
    print angle_vector3d(vec1, vec2)
    print angle_vector3d(vec1, vec3)

if __name__ == "__main__":
    test1()