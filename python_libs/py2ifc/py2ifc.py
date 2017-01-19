import ifcopenshell
import uuid
import numpy as np

#==============================================================================================================================================================
# Numpy utility functions
#==============================================================================================================================================================
def guid():
    return ifcopenshell.guid.compress(uuid.uuid1().hex)

# VECTORS =====================================================================================================================================================

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
    vec -- the vector to normalise (2d or 3d)
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

#==============================================================================================================================================================
# Class for writing ifcfiles
#==============================================================================================================================================================
class IfcFileWriter:
    # CONSTANTS
    RECTANGLE = 0
    CIRCLE = 1
    ARBITRARY = 2

    FLOOR = 'FLOOR'
    ROOF = 'ROOF'
    LANDING = 'LANDING'
    BASESLAB = 'BASESLAB'
    NOTDEFINED = 'NOTDEFINED'

    # CONSTRUCTOR
    def __init__(self, filepath):

        ifc_template = """ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('ViewDefinition [CoordinationView]'),'2;1');
FILE_NAME('$filename','$timestamp',('$owner','$email'),('$company'),'IfcOpenShell','IfcOpenShell','');
FILE_SCHEMA(('IFC2X3'));
ENDSEC;
DATA;
#1=IFCPERSON($,$,'$owner',$,$,$,$,$);
#2=IFCORGANIZATION($,'$company',$,$,$);
#3=IFCPERSONANDORGANIZATION(#1,#2,$);
#4=IFCAPPLICATION(#2,'$version','Houdini3D','118df2cf_ed21_438e_a41');
#5=IFCOWNERHISTORY(#3,#4,$,.ADDED.,$,#3,#4,$now);
#6=IFCCARTESIANPOINT((0.,0.));
#7=IFCDIRECTION((1.,0.));
#8=IFCDIRECTION((0.,1.));
#9=IFCAXIS2PLACEMENT2D(#6,#7);
#10=IFCCARTESIANPOINT((0.,0.,0.));
#11=IFCDIRECTION((1.,0.,0.));
#12=IFCDIRECTION((0.,1.,0.));
#13=IFCDIRECTION((0.,0.,1.));
#14=IFCDIRECTION((0.,0.,-1.));
#15=IFCAXIS2PLACEMENT3D(#10,#13,#11);
#16=IFCGEOMETRICREPRESENTATIONCONTEXT($,'Model',3,1.E-05,#15,#12);
#17=IFCDIMENSIONALEXPONENTS(0,0,0,0,0,0,0);
#18=IFCSIUNIT(*,.LENGTHUNIT.,$,.METRE.);
#19=IFCSIUNIT(*,.AREAUNIT.,$,.SQUARE_METRE.);
#20=IFCSIUNIT(*,.VOLUMEUNIT.,$,.CUBIC_METRE.);
#21=IFCSIUNIT(*,.PLANEANGLEUNIT.,$,.RADIAN.);
#22=IFCMEASUREWITHUNIT(IFCPLANEANGLEMEASURE(0.017453292519943295),#16);
#23=IFCCONVERSIONBASEDUNIT(#17,.PLANEANGLEUNIT.,'DEGREE',#22);
#24=IFCUNITASSIGNMENT((#18,#19,#20,#23));
#25=IFCPROJECT('$projectid',#5,'$project',$,$,$,$,(#16),#24);
ENDSEC;
END-ISO-10303-21;
"""
        #read the ifctemplate and write it to a file 
        self.filepath = filepath
        with open(filepath,"wb") as f:
            f.write(ifc_template)
        self.openshell = ifcopenshell.open(filepath) #where does this get closed???
        #Save entities in ifcfile
        self.ifc_2d_origin = self.openshell.by_type("IFCCARTESIANPOINT")[0]
        self.ifc_2d_x_dir = self.openshell.by_type("IFCDIRECTION")[0]
        self.ifc_2d_y_dir = self.openshell.by_type("IFCDIRECTION")[1]
        self.ifc_global_a2p2d = self.openshell.by_type("IFCAXIS2PLACEMENT2D")[0]
        self.ifc_east_dir = self.openshell.by_type("IFCDIRECTION")[2]
        self.ifc_north_dir = self.openshell.by_type("IFCDIRECTION")[3]
        self.ifc_up_dir = self.openshell.by_type("IFCDIRECTION")[4]
        self.ifc_down_dir = self.openshell.by_type("IFCDIRECTION")[5]
        self.ifc_origin = self.openshell.by_type("IFCCARTESIANPOINT")[1]
        self.ifc_global_a2p3d = self.openshell.by_type("IFCAXIS2PLACEMENT3D")[0]
        self.ifc_history = self.openshell.by_type("IFCOWNERHISTORY")[0]
        self.ifc_geomrep = self.openshell.by_type("IFCGEOMETRICREPRESENTATIONCONTEXT")[0]
        self.ifc_project = self.openshell.by_type("IFCPROJECT")[0]
        # Hierarchy
        self.sites = []
        self.buildings = []
        self.storeys = []
        self.materials = [] # a mix of layerset objects and material objects

    #==============================================================================================================================================================
    # IFC Utility methods
    #==============================================================================================================================================================

    def create_axis2placement2d(self, pt, dir1):
        """Create IfcAxisToPlacement2d.
        """
        pt = self.create_point(pt)
        dir1 = self.create_direction(dir1)
        return self.openshell.createIfcAxis2Placement2D(pt,dir1)

    def create_axis2placement3d(self, pt, dir1, dir2):
        """Create IfcAxis2Placement3d.
        """
        pt = self.create_point(pt)
        dir1 = self.create_direction(dir1)
        dir2 = self.create_direction(dir2)
        return self.openshell.createIfcAxis2Placement3D(pt,dir1,dir2)

    def create_point(self, pt):
        """Create IfcCartesianPoint.
        """
        if isinstance(pt, list) or isinstance(pt, tuple):
            pt = tuple([float(i) for i in pt])
            pt = self.openshell.createIfcCartesianPoint(pt)
        return pt

    def create_points(self, pt_list):
        """Create a list of IfcCartesianPoint.
        """
        ifc_pts = []
        for pt in pt_list:
            ifc_pts.append(self.create_point(pt))
        return ifc_pts

    def create_direction(self, dir1):
        """Create IfcDirection.
        """
        if isinstance(dir1, list) or isinstance(dir1, tuple):
            dir1 = tuple([float(i) for i in dir1])
            dir1 = self.openshell.createIfcDirection(dir1)
        return dir1

    def create_polyline(self, pt_list):
        """Create IfcPolyline.
        """
        ifc_pts = self.create_points(pt_list)
        return self.openshell.createIfcPolyLine(ifc_pts)

    def create_polygon(self, pt_list):
        """Create IfcPolygon.
        """
        ifc_pts = self.create_points(pt_list)
        ifc_pts.append(ifc_pts[0])
        return self.openshell.createIfcPolyLine(ifc_pts)

    def create_face(self, pt_list):
        """Create an IfcpolyLoop, then a IfcFaceOuterBound, and finally an IfcFace.
        """
        pt_list = [tuple([float(i) for i in pt]) for pt in pt_list]
        ifc_pts = self.create_points(pt_list)
        ifc_poly_loop = self.openshell.createIfcPolyLoop(ifc_pts)
        ifc_face = self.openshell.createIfcFaceOuterBound(ifc_poly_loop,True)
        return self.openshell.createIfcFace([ifc_face])

    def create_shell(self, faces, open_shell=True):
        """Create a list of IfcFace, and then IfcOpenShell or IfcClosedShell.
        """
        ifc_face_list = []
        for face in faces:
            ifc_face = self.create_face(face)
            ifc_face_list.append(ifc_face)
        if open_shell:
            return self.openshell.createIfcOpenShell(ifc_face_list)
        return self.openshell.createIfcClosedShell(ifc_face_list)

    def create_axis_shaperep(self, pt_list):
        """Create an IfcPolyline, and then an IfcShapeRepresentation.
        """
        ifc_polyline = self.create_polyline(pt_list)
        return self.openshell.createIfcShapeRepresentation(self.ifc_geomrep, "AXIS","CURVE2D", [ifc_polyline])

    def create_extrusion_shaperep(self, profile_type, profile_args, dir1, dist, clipping_planes=None, csg_solids=None):
        """Creates a 2D profile and extrudes it into an IfcExtrudedAreaSolid, and then creates and IFCShapeRepresentation. For the IfcAxis2Placement3d,
        the global coordinate system is used. 
        Arguments:
        ----------
        profile_type -- int, IfcWriter.RECTANGLE, IfcWriter.CIRCLE, IfcWriter.ARBITRARY
        profile_args --  a list of Arguments: for creating the profie, which vary depening on the profile type
        dir1 -- a tuple of floats, the extrusion direction
        dist -- float, the extrusion distance
        clipping_planes -- a list of clipping planes, to clip solid (the volume that lies above the clipping plane is removed)
        csg_solids -- a list of csg solids, to be subtracted from the solid
        """
        # create the 2d profile
        if profile_type == self.RECTANGLE:
            ifc_a2p2d = self.create_axis2placement2d(self.ifc_2d_origin, rotate_vector2d((1.,0.), profile_args[0]))
            ifc_profile = self.openshell.createIfcRectangleProfileDef("AREA", None, ifc_a2p2d, profile_args[1], profile_args[2])
        elif profile_type == self.CIRCLE:
            ifc_profile = self.openshell.createIfcCircleProfileDef("AREA", None, self.ifc_global_a2p2d, profile_args[0])
        elif profile_type == self.ARBITRARY:
            ifc_polyline = self.create_polygon(profile_args)
            ifc_profile = self.openshell.createIfcArbitraryClosedProfileDef("AREA", None, ifc_polyline)
        else:
            raise Exception
        # create the 3d extrusion
        dir1 = self.create_direction(dir1)
        dist = float(dist)
        ifc_extrusion = self.openshell.createIfcExtrudedAreaSolid(ifc_profile, self.ifc_global_a2p3d, dir1, dist)
        # no csg, create a swept solid
        if not csg_solids:
            return self.openshell.createIfcShapeRepresentation(self.ifc_geomrep, "BODY", "SWEPTSOLID", [ifc_extrusion])
        # csg the extrusion, create a CSG solid
        else:
            for body in csg:
                shell = self.create_shell(body, False)
                brep = self.openshell.createIfcFacetedBRep(shell)
                ifc_extrusion = self.openshell.createIfcBooleanResult("DIFFERENCE", ifc_extrusion, brep)
            return self.openshell.createIfcShapeRepresentation(self.ifc_geomrep, "BODY", "CSG", [ifc_extrusion])
        
    #==============================================================================================================================================================
    # Site, Building, Storey
    #==============================================================================================================================================================
    class Site:
        def __init__(self, ifc_site):
            self.ifc= ifc_site
            self.guid = ifc_site[0]
            self.ifc_localplacement = ifc_site[5]
            self.buildings = []

    class Building:
        def __init__(self, ifc_building):
            self.ifc= ifc_building
            self.guid = ifc_building[0]
            self.ifc_localplacement = ifc_building[5]
            self.stories = []

    class Storey:
        def __init__(self, ifc_storey):
            self.ifc= ifc_storey
            self.guid = ifc_storey[0]
            self.ifc_localplacement = ifc_storey[5]
            self.elevation = ifc_storey[9]
            self.elements = []

    def create_site_by_surface(self, polys):
        """Create an IfcOpenShell, and then an IfcSite.
        """
        # create ifc shape
        ifc_open_shell = self.create_shell(polys)
        ifc_face_based_srf_model = self.openshell.createIfcFaceBasedSurfaceModel([ifc_open_shell])
        ifc_shaperep = self.openshell.createIfcShapeRepresentation(self.ifc_geomrep,'Facetation','SurfaceModel',[ifc_face_based_srf_model])
        # create ifc site
        localplacement = self.openshell.createIfcLocalPlacement(None, self.ifc_global_a2p3d)
        product_def = self.openshell.createIfcProductDefinitionShape(None,None,[ifc_shaperep])
        site = self.openshell.createIfcSite(guid(), self.ifc_history,'Site', 'Description of Site', 
            None, localplacement, product_def, None, 'ELEMENT', None,None,None,None,None)
        # create object and append to list
        site_obj = self.Site(site)
        self.sites.append(site_obj)
        return site_obj

    def create_building(self, site):
        """Create IfcBuilding.
        """
        # create ifc building
        localplacement = self.openshell.createIfcLocalPlacement(site.ifc_localplacement, self.ifc_global_a2p3d)
        building = self.openshell.createIfcBuilding(guid(), self.ifc_history,'Default Building', 'Description of Default Building',
            None,localplacement,None,None,"ELEMENT",None,None,None)
        # create object and append to list
        building_obj = self.Building(building)
        self.buildings.append(building_obj)
        return building_obj

    def create_storey(self, elevation, name, building):
        """Create IfcBuildingStorey.
        """
        # create ifc building storey
        a2p3d = self.create_axis2placement3d((0,0,elevation), self.ifc_up_dir, self.ifc_east_dir)
        localplacement = self.openshell.createIfcLocalPlacement(building.ifc_localplacement, a2p3d)
        storey = self.openshell.createIfcBuildingStorey(guid(), self.ifc_history, name, "Description of"+ name,
            None,localplacement,None,None,"ELEMENT",float(elevation))
        # create object and append to list
        storey_obj = self.Storey(storey)
        self.storeys.append(storey_obj)
        return storey_obj

    #==============================================================================================================================================================
    # Walls
    #==============================================================================================================================================================
    class Wall:
        def __init__(self, ifc_wall, offset, material_layerset, storey):
            self.ifc= ifc_wall
            self.guid = ifc_wall[0]
            self.ifc_localplacement = ifc_wall[5]
            self.offset = offset
            self.material_layerset = material_layerset
            self.storey = storey

    def create_vertwall_by_axis(self, axis, elevation, height, offset, material_layerset, storey, trims=None):
        """
        Arguments:
        ----------
        axis -- a pair of 2d points, representing the start and end of the wall (left is inside, right is outside)
        elevation -- a double, the vertical elevation above or below the level of the storey
        height -- a double, the height that the plan will be extruded
        offset -- a double, representing an offset from the axis (0 = centered, +ve = to the outside)
        material_layerset -- the material_layerset object, representing a material_layerset usage
        storey -- the storey object that this wall belongs to
        """
        # create the wall sahpe, the bottom of the wall will be level with the axis
        offset_axis = offset_line2d(axis, offset)
        plan = thicken_line2d(offset_axis, material_layerset.thickness)
        body = self.create_extrusion_shaperep(self.ARBITRARY, plan, self.ifc_up_dir, height, trims)
        axis = self.create_axis_shaperep(axis)
        # create ifc wall
        a2p3d = self.create_axis2placement3d((0.,0.,elevation), self.ifc_up_dir, self.ifc_east_dir) 
        localplacement = self.openshell.createIfcLocalPlacement(storey.ifc_localplacement, a2p3d)
        product_def = self.openshell.createIfcProductDefinitionShape(None,None,[axis, body])
        wall = self.openshell.createIfcWallStandardCase(guid(), self.ifc_history, "Wall","Standard Case Wall", 
            None, localplacement, product_def, None)
        # create wall object
        wall_obj = self.Wall(wall, offset, material_layerset, storey)
        storey.elements.append(wall_obj)
        material_layerset.elements.append(wall_obj)
        return wall_obj

    def create_vertwall_by_rectangle(self, rectangle, offset, material_layerset, storey):
        """
        Arguments:
        ----------
        rectangle -- a list of 3d points defining a vertical stable rectangle
        offset -- a double, representing an offset from the axis (0 = centered, +ve = to the outside)
        material_layerset -- the material_layerset object, representing a material_layerset layerset usage
        storey -- the storey object that this wall belongs to
        """
        lines = explode_polygon(zshift_polygon3d(rectangle))
        axis = [(pt[0], pt[1]) for pt in lines[0]]
        height = lines[2][0][2] - lines[0][0][2]
        elevation = lines[0][0][2] - storey.elevation
        return self.create_vertwall_by_axis(axis, elevation, height, offset, material_layerset, storey)

    #==============================================================================================================================================================
    # Slabs
    #==============================================================================================================================================================
    class Slab:
        def __init__(self, ifc_slab, slab_type, material_layerset, storey):
            self.ifc= ifc_slab
            self.guid = ifc_slab[0]
            self.ifc_localplacement = ifc_slab[5]
            self.material_layerset = material_layerset
            self.storey = storey

    def create_flatslab_by_plan(self, slab_type, plan, elevation, material_layerset, storey):
        """
        Arguments:
        ----------
        slab_type -- string, can be 'FLOOR', 'ROOF', 'LANDING', 'BASESLAB', and 'NOTDEFINED' (TODO: I am not sure about 'USERDEFINED')
        plan -- a list of 2d points, representing the plan of the slab
        elevation -- a double, the vertical elevation above or below the level of the storey
        material_layerset -- the material_layerset object, representing a material_layerset layerset usage
        storey -- the storey object that this wall belongs to
        """
        # create ifc shape
        body = self.create_extrusion_shaperep(self.ARBITRARY, plan, self.ifc_down_dir, material_layerset.thickness)
        # create ifc slab
        a2p3d = self.create_axis2placement3d((0.,0.,elevation), self.ifc_up_dir, self.ifc_east_dir) 
        localplacement = self.openshell.createIfcLocalPlacement(storey.ifc_localplacement, a2p3d)
        product_def = self.openshell.createIfcProductDefinitionShape(None,None,[body])
        slab = self.openshell.createIfcSlab(guid(),self.ifc_history, "Slab", "Standard Slab",
            None, localplacement, product_def, None, slab_type)
        # create slab object
        slab_obj = self.Slab(slab, slab_type, material_layerset, storey)
        storey.elements.append(slab_obj)
        material_layerset.elements.append(slab_obj)
        return slab_obj

    def create_flatslab_by_polygon(self, slab_type, polygon, material_layerset, storey):
        """
        Arguments:
        ----------
        slab_type -- string, can be 'FLOOR', 'ROOF', 'LANDING', 'BASESLAB', and 'NOTDEFINED' (TODO: I am not sure about 'USERDEFINED')
        polygon -- a list of 3d points, representing a planar horizontal polygon
        material_layerset -- the material_layerset object, representing a material_layerset layerset usage
        storey -- the storey object that this wall belongs to
        """
        plan = [(pt[0],pt[1]) for pt in polygon]
        elevation = polygon[0][2] - storey.elevation
        return self.create_flatslab_by_plan(slab_type, plan, elevation, material_layerset, storey)

    def create_slab_by_polygon(self, slab_type, polygon, material_layerset, storey):
        """
        Arguments:
        ----------
        slab_type -- string, can be 'FLOOR', 'ROOF', 'LANDING', 'BASESLAB', and 'NOTDEFINED' (TODO: I am not sure about 'USERDEFINED')
        polygon -- a list of 3d points, representing a planar polygon (at any angle)
        material_layerset -- the material_layerset object, representing a material_layerset layerset usage
        storey -- the storey object that this wall belongs to
        """
        # transform polygon
        polygpn = zshift_polygon3d(polygon)
        origin = polygon[0]
        elevation = origin[2] - storey.elevation
        matrix = polygon3d_matrix(polygon)
        normal = flip_vector(polygon3d_normal(polygon))
        x_dir = vector(polygon[0], polygon[1])
        plan = transform_polygon3d(polygon, matrix)
        plan = [(pt[0], pt[1]) for pt in plan]
        # create ifc shape
        edge_dir = self.ifc_down_dir
        # edge_dir = transform_vector3d((0,0,1), matrix)
        body = self.creaedge_dir = self.create_extrusion_shaperep(self.ARBITRARY, plan, edge_dir, material_layerset.thickness)
        # create ifc slab
        a2p3d = self.create_axis2placement3d((origin[0], origin[1], elevation), normal, x_dir) 
        localplacement = self.openshell.createIfcLocalPlacement(storey.ifc_localplacement, a2p3d)
        product_def = self.openshell.createIfcProductDefinitionShape(None,None,[body])
        slab = self.openshell.createIfcSlab(guid(),self.ifc_history, "Slab", "Standard Slab",
            None, localplacement, product_def, None, slab_type)
        # create slab object
        slab_obj = self.Slab(slab, slab_type, material_layerset, storey)
        storey.elements.append(slab_obj)
        material_layerset.elements.append(slab_obj)
        return slab_obj

    #==============================================================================================================================================================
    # Openings, Windows, and Doors (Windoors)
    #==============================================================================================================================================================
    class Opening:
        def __init__(self, ifc_opening, ifc_rel_voids_element, wall):
            self.ifc= ifc_opening
            self.guid = ifc_opening[0]
            self.ifc_localplacement = ifc_opening[5]
            self.ifc_rel = ifc_rel_voids_element
            self.wall = wall

    class Windoor:
        def __init__(self, ifc_windoor, ifc_rel_fills_element, iswindow, material_layerset, opening):
            self.ifc = ifc_windoor
            self.guid = ifc_windoor[0]
            self.ifc_localplacement = ifc_windoor[5]
            self.ifc_rel = ifc_rel_fills_element
            self.material_layerset = material_layerset
            self.opening = opening

    def create_flatslab_opening_by_plan(self, plan, slab):
        """
        Arguments:
        ----------
        plan -- a list of 2d points, representing the opening plan
        slab -- the slab object that this opening belongs to
        """
        # create shape
        extrusion = self.create_extrusion_shaperep(self.ARBITRARY, plan, self.ifc_up_dir, slab.material_layerset.thickness)
        # create ifc opening
        a2p3d = self.create_axis2placement3d((0.,0.,-slab.material_layerset.thickness), self.ifc_up_dir, self.ifc_east_dir) 
        localplacement = self.openshell.createIfcLocalPlacement(slab.ifc_localplacement, a2p3d)
        product_def = self.openshell.createIfcProductDefinitionShape(None,None,[extrusion])
        opening = self.openshell.createIfcOpeningElement(guid(), self.ifc_history, "Opening", "Flatslab Opening", 
            None, localplacement, product_def, None)
        # create the relationship with the wall
        rel = self.openshell.createIfcRelVoidsElement(guid(),self.ifc_history, None, None, slab.ifc, opening)
        # create opening object
        return self.Opening(opening, rel, slab)

    def create_flatslab_opening_by_polygon(self, polygon, slab):
        """
        Arguments:
        ----------
        polgon -- a list of 3d points, representing the opening
        slab -- the slab object that this opening belongs to
        """
        plan  = [(pt[0],pt[1]) for pt in polygon]
        return create_flatslab_opening_by_plan(plan, slab)

    def create_vertwall_opening_by_axis(self, axis, elevation, height, wall):
        """
        Arguments:
        ----------
        axis -- a pair of 2d points, representing the start and end of the opening (left is inside, right is outside)
        elevation -- a double, the vertical elevation above the level of the storey
        height -- a double, the height of the opening
        wall -- the wall object that this opening belongs to
        """
        # create shape
        offset_axis = offset_line2d(axis, wall.offset)
        plan = thicken_line2d(offset_axis, wall.material_layerset.thickness)
        extrusion = self.create_extrusion_shaperep(self.ARBITRARY, plan, self.ifc_up_dir, height)
        # create ifc opening
        a2p3d = self.create_axis2placement3d((0.,0.,elevation), self.ifc_up_dir, self.ifc_east_dir) 
        localplacement = self.openshell.createIfcLocalPlacement(wall.ifc_localplacement, a2p3d)
        product_def = self.openshell.createIfcProductDefinitionShape(None,None,[extrusion])
        opening = self.openshell.createIfcOpeningElement(guid(), self.ifc_history, "Opening", "Wall Opening", 
            None, localplacement, product_def, None)
        # create the relationship with the wall
        rel = self.openshell.createIfcRelVoidsElement(guid(),self.ifc_history, None, None, wall.ifc, opening)
        # create opening object
        return self.Opening(opening, rel, wall)

    def create_vertwall_windoor_by_axis(self, iswindow, axis, elevation, height, offset, material_layerset, wall):
        """
        Arguments:
        ----------
        iswindow -- boolean value, if true create a window, otherwise create a door
        axis -- a pair of 2d points, representing the start and end of the window (left is inside, right is outside)
        elevation -- a double, the vertical elevation above the level of the storey
        height -- a double, the height of the window
        offset -- a double, representing an offset from the axis (0 = centered, +ve = to the outside)
        material_layerset -- the material_layerset object, representing a material_layerset layerset usage
        opening -- the opening object that this window belongs to
        """
        # create the opening 
        opening = self.create_vertwall_opening_by_axis(axis, elevation, height, wall) 
        # create shape
        offset_axis = offset_line2d(axis, offset)
        plan = thicken_line2d(offset_axis, material_layerset.thickness)
        extrusion = self.create_extrusion_shaperep(self.ARBITRARY, plan, self.ifc_up_dir, height)
        # create ifc windoor
        localplacement = self.openshell.createIfcLocalPlacement(opening.ifc_localplacement, self.ifc_global_a2p3d)
        product_def = self.openshell.createIfcProductDefinitionShape(None,None,[extrusion])
        if iswindow:
            windoor = self.openshell.createIfcWindow(guid(), self.ifc_history, "Window",  "Standard Window", 
                None, localplacement, product_def, None, None)
        else:
            windoor = self.openshell.createIfcDoor(guid(), self.ifc_history, "Door",  "Standard Door", 
                None, localplacement, product_def, None, None)
        # create the relationship beteeen the window and the opening
        rel = self.openshell.createIfcRelFillsElement(guid(), self.ifc_history, None, None, opening.ifc, windoor)
        # create windoor object
        windoor_obj = self.Windoor(windoor, rel, iswindow, material_layerset, opening)
        material_layerset.elements.append(windoor_obj)
        return windoor_obj

    def create_vertwall_windoor_by_rectangle(self, iswindow, rectangle, offset, material_layerset, wall):
        """
        Arguments:
        ----------
        iswindow -- boolean value, if true create a window, otherwise create a door
        rectangle -- a list of 3d points defining a vertical stable rectangle
        offset -- a double, representing an offset from the axis (0 = centered, +ve = to the outside)
        material_layerset -- the material_layerset object, representing a material_layerset layerset usage
        wall -- the wall object that this opening and window belongs to
        """
        lines = explode_polygon(zshift_polygon3d(rectangle))
        axis = [(pt[0], pt[1]) for pt in lines[0]]
        axis = offset_line2d(axis, offset)
        elevation = lines[0][0][2] - wall.storey.elevation
        height = lines[2][0][2] - lines[0][0][2]
        return self.create_vertwall_windoor_by_axis(iswindow, axis, elevation, height, offset, material_layerset, wall)

    #==============================================================================================================================================================
    # Columns and Beams
    #==============================================================================================================================================================
    class Column:
        def __init__(self, ifc_column, profile_type, material, storey):
            self.ifc = ifc_column
            self.guid = ifc_column[0]
            self.ifc_localplacement = ifc_column[5]
            self.profile_type = profile_type
            self.material = material
            self.storey = storey

    class Beam:
        def __init__(self, ifc_beam, profile_type, material, storey):
            self.ifc = ifc_beam
            self.guid = ifc_beam[0]
            self.ifc_localplacement = ifc_beam[5]
            self.profile_type = profile_type
            self.material = material
            self.storey = storey

    def create_col_by_centerline(self, centerline, profile_type, profile_args, material, storey):
        """
        Arguments:
        ----------
        centerline -- a pair of 3d points, representing the centerline
        profile_type -- int from 0 to 2 (IfcFileWriter.RECTANGLE, IfcFileWriter.CIRCLE, IfcFileWriter.ARBITRARY,)
        profile_args -- a list of Arguments: for rectangles, two dimensions; for circles, one radius; for arbitrary, a list of 2d points
        material -- the material object, representing a material of the column
        storey -- the storey object that this wall belongs to
        """
        # create shape
        bottom, top = centerline
        length = line_length(centerline)
        elevation = bottom[2] - storey.elevation
        origin = (bottom[0], bottom[1], elevation)
        direction = vector(bottom, top)
        extrusion = self.create_extrusion_shaperep(profile_type, profile_args, direction, length)
        # create ifc column
        a2p3d = self.create_axis2placement3d(origin, self.ifc_up_dir, self.ifc_east_dir) 
        localplacement = self.openshell.createIfcLocalPlacement(storey.ifc_localplacement, a2p3d)
        product_def = self.openshell.createIfcProductDefinitionShape(None,None,[extrusion])
        column = self.openshell.createIfcColumn(guid(), self.ifc_history, "Column", "Column type: " + str(profile_type), 
            None, localplacement,product_def, None)
        # create column object
        column_obj = self.Column(column, profile_type, material, storey)
        storey.elements.append(column_obj)
        material.elements.append(column_obj)
        return column_obj

    def create_beam_by_centerline(self, id, centerline, profile_type, profile_args, material, storey):
        """
        Arguments:
        ----------
        centerline -- a pair of 3d points, representing the centerline
        profile_type -- int from 0 to 2 (IfcFileWriter.RECTANGLE, IfcFileWriter.CIRCLE, IfcFileWriter.ARBITRARY,)
        profile_args -- a list of Arguments: for rectangles, two dimensions [height, width]; for circles, one radius; for arbitrary, a list of 2d points
        material -- the material object, representing a material of the column
        storey -- the storey object that this wall belongs to
        """
        # create shape
        start, end = centerline
        length = line_length(centerline)
        elevation = start[2] - storey.elevation
        origin = (start[0], start[1], elevation)
        direction = vector(start, end)
        extrusion = self.create_extrusion_shaperep(profile_type, profile_args, self.ifc_up_dir, length)
        # create ifc beam
        a2p3d = self.create_axis2placement3d(origin, direction, self.ifc_up_dir) 
        localplacement = self.openshell.createIfcLocalPlacement(storey.ifc_localplacement, a2p3d)
        product_def = self.openshell.createIfcProductDefinitionShape(None,None,[extrusion])
        beam = self.openshell.createIfcBeam(guid(), self.ifc_history, "Beam", "Beam type: " + str(profile_type), 
            None, localplacement,product_def, None)
        # create beam object
        beam_obj = self.Beam(beam, profile_type, material, storey)
        storey.elements.append(beam_obj)
        material.elements.append(beam_obj)
        return beam_obj

    #==============================================================================================================================================================
    # Materials
    #==============================================================================================================================================================
    class Material:
        def __init__(self, ifc_material):
            self.ifc = ifc_material
            self.name = ifc_material[0]
            self.elements = []

    class MaterialLSU:
        def __init__(self, ifc_material_layerset_usage, material_names, material_thicknesses):
            self.ifc = ifc_material_layerset_usage
            self.name = str(sum(material_thicknesses)) + "_".join(material_names)
            self.thickness = sum(material_thicknesses)
            self.material_names = material_names
            self.material_thicknesses = material_thicknesses
            self.elements = []

    def create_material(self, name):
        material = self.openshell.createIfcMaterial(name)
        material_obj = self.Material(material)
        self.materials.append(material_obj)
        return material_obj

    def create_material_layerset(self, material_names, material_thicknesses):
        layers = []
        for name, thickness in zip(material_names, material_thicknesses):
            material = self.openshell.createIfcMaterial(name)
            layers.append(self.openshell.createIfcMaterialLayer(material, thickness, None))
        layerset = self.openshell.createIfcMaterialLayerSet(layers, str(sum(material_thicknesses)) + "_".join(material_names))
        layerset_usage = self.openshell.createIfcMaterialLayerSetUsage(layerset, "AXIS2", "POSITIVE", (sum(material_thicknesses)/2)*-1)
        layerset_usage_obj = self.MaterialLSU(layerset_usage, material_names, material_thicknesses)
        self.materials.append(layerset_usage_obj)
        return layerset_usage_obj

    #==============================================================================================================================================================
    # Write
    #==============================================================================================================================================================
    def write(self):
        # Relationships between project and sites
        self.openshell.createIfcRelAggregates(guid(), self.ifc_history, 
            "Project Container","Contains Sites", self.ifc_project, [site.ifc for site in self.sites])
        # Relationships between sites and buildings
        for site in self.sites:
            self.openshell.createIfcRelAggregates(guid(), self.ifc_history, 
                "Site Container","Contains Buildings", site.ifc, [building.ifc for building in self.buildings])
        # Relationships between buildings and storeys
        for building in self.buildings:
            self.openshell.createIfcRelAggregates(guid(), self.ifc_history, 
                "Building Container","Contains Storeys", building.ifc, [storey.ifc for storey in self.storeys])
        # Relationships between storeys and elements
        for storey in self.storeys:
            self.openshell.createIfcRelContainedInSpatialStructure(guid(), self.ifc_history, 
                "Building","Contents of Building Storey", [element.ifc for element in storey.elements], storey.ifc)
        # Relationships between materials and elements
        for material in self.materials:
            self.openshell.createIfcRelAssociatesMaterial(guid(), self.ifc_history, 
                material.name, None, [element.ifc for element in material.elements], material.ifc)
        # Write the file
        self.openshell.write(self.filepath)
        print "File written!."
        # no need to close?

#==============================================================================================================================================================
# Test
#==============================================================================================================================================================

# test utility functions
def test0():
    # x = [ (0,10,0),(0,10,5),(0,0,5),(0,0,0) ]
    # print explode(x)
    # print offset(x, 5)

    # y = (1.,0)
    # print rotate_vector(y, 45)

    # x = zthicken_polygon3d([(0,0,0),(3,0,0), (3,3,0), (0,3,0)], 4)
    # for i in x:
    #     print "   ", i

    # x = thicken_line3d([[10,0,0],[0,0,0]], 3, (0,0,1))

    # print x
    # for i in stretch_polygon(x, 4):
    #     print "   ", i

    p = [(0, 0, 0), (0, 10, 0), (10, 10, 10), (10, 0, 10)]
    m = polygon3d_matrix(p)
    print p
    print m
    print transform_polygon3d(p, m)


    # v = polygon3d_normal(p)
    # print v
    # print transform_vector(v, m)

# test standard walls floors, etc
def test1():
    writer = IfcFileWriter("d:/temp/test.ifc")

    base = [(0,0,0), (10,0,0),(10,10,0),(0,10,0)] #anticlockwise

    # Create materials
    mat_lsu1 = writer.create_material_layerset(["Concrete","bb","cc"], [.1,.1,.2])
    mat_lsu2 = writer.create_material_layerset(["gg"], [.1])
    concrete = writer.create_material("Concrete")

    # Create site, building, storeys
    site = writer.create_site_by_surface([base])
    bldg = writer.create_building(site)
    storey1 = writer.create_storey(1, "floor_A", bldg)
    storey2 = writer.create_storey(4.2, "floor_B", bldg)

    # Create wall and window by axis
    axis1 = [(5,10),(5,0)]
    wall1a = writer.create_vertwall_by_axis(axis1, 0, 3.2, 0, mat_lsu1, storey1)
    opening_axis1 = [(5,1),(5,9)]
    win1 = writer.create_vertwall_windoor_by_axis(True, opening_axis1, .7, 2, 0, mat_lsu2, wall1a)

    # Create wall on 1stf floor by axis with some openings
    wall1b = writer.create_vertwall_by_axis(axis1, 0, 3.2, 0, mat_lsu1, storey2)
    opening_axis1b = writer.create_vertwall_opening_by_axis(opening_axis1, .7, 2, wall1b)

    # Create wall and door by rectangle
    rect1 = [(5,0,1),(10,0,1),(10,0,4.2),(5,0,4.2)]
    wall2 = writer.create_vertwall_by_rectangle(rect1, 0, mat_lsu1, storey1)
    open_rect1 = [(6,0,1),(8,0,1),(8,0,3.7),(6,0,3.7)]
    door1 = writer.create_vertwall_windoor_by_rectangle(False, open_rect1, 0, mat_lsu2, wall2)

    # Create floor slabs
    plan1 = [(5,0), (10,0),(10,10),(5,10)]
    floor1 = writer.create_flatslab_by_plan(writer.FLOOR, plan1, 0, mat_lsu1, storey1)
    floor2 = writer.create_flatslab_by_plan(writer.FLOOR, plan1, 0, mat_lsu1, storey2)
    polygon1 = [(5,0,7.4), (10,0,7.4),(10,10,7.4),(5,10,7.4)]
    floor3 = writer.create_flatslab_by_polygon(writer.FLOOR, polygon1, mat_lsu1, storey2)

    # Create an opening in the slab
    plan1 = [(6,1), (9,1),(9,9),(6,9)]
    opening = writer.create_flatslab_opening_by_plan(plan1, floor3)

    # Create columns
    centerline1 = [(9.9,0.1,4.2),(9.9,3.1,7.4)]
    writer.create_col_by_centerline(centerline1, writer.CIRCLE, [0.1], concrete, storey2)
    centerline2 = [(9.9,9.9,4.2),(9.9,9.9,7.4)]
    writer.create_col_by_centerline(centerline2, writer.RECTANGLE, [45, 0.2, 0.2], concrete, storey2)
    profile = [(0,0),(.3,0),(0,.3)]
    centerline3 = [(0,0,0),(0,0,5)]
    writer.create_col_by_centerline(centerline3, writer.ARBITRARY, profile, concrete, storey1)

    # Create beams
    centerline_beam1 = [(0,0,5),(5,5,5)]
    writer.create_beam_by_centerline("1abc", centerline_beam1, writer.RECTANGLE, [0, 0.1, 0.3], concrete, storey2)
    centerline_beam2 = [(0,0,5),(0,10,5)]
    writer.create_beam_by_centerline("2def", centerline_beam2, writer.RECTANGLE, [0, 0.1, 0.3], concrete, storey2)
    centerline_beam3 = [(0,10,5),(5,10,5)]
    writer.create_beam_by_centerline("3ghi", centerline_beam3, writer.RECTANGLE, [0, 0.1, 0.3], concrete, storey2)

    # Write the file
    writer.write();

# test more complex stuff
def test2():
    writer = IfcFileWriter("d:/temp/test.ifc")

    # Create materials
    mat_lsu1 = writer.create_material_layerset(["Concrete","bb","cc"], [.1,.1,.2])

    # Create site, building, storeys
    site = writer.create_site_by_surface([])
    bldg = writer.create_building(site)
    storey1 = writer.create_storey(0, "floor_A", bldg)

    # Create wall and window by axis with trims
    axis1 = [(0.,0.),(0.,10.)]
    trim1 = stretch_polygon(thicken_line3d_perp([(0.,0.,3.),(0.,5.,3.)], 1., (1.,0.,1.)), 4)
    trim2 = stretch_polygon(thicken_line3d_perp([(0.,5.,3.),(0.,10.,4.)], 1., (1.,0.,1.)), 4)
    wall = writer.create_vertwall_by_axis(axis1, 0, 5, 0, mat_lsu1, storey1, [trim1, trim2])

    # Write the file
    writer.write();

def test3():
    writer = IfcFileWriter("d:/temp/test.ifc")

    # Create materials
    mat_lsu1 = writer.create_material_layerset(["Concrete","bb","cc"], [.1,.1,.2])

    # Create site, building, storeys
    site = writer.create_site_by_surface([])
    bldg = writer.create_building(site)
    storey1 = writer.create_storey(5, "floor_A", bldg)

    # Create sloping roof
    def f(l):
        return [(float(p[0]), float(p[1]), float(p[2])) for p in l]

    polygon1 = [(0, 0, 6), (0, 10, 6), (10, 10, 16), (10, 5, 16)]
    roof1 = writer.create_slab_by_polygon(writer.ROOF, polygon1, mat_lsu1, storey1)
    polygon2 = [(20, 10, 6), (20, 0, 6), (10, 5, 16), (10, 10, 16)]
    roof2 = writer.create_slab_by_polygon(writer.ROOF, polygon2, mat_lsu1, storey1)
    polygon3 = [(20, 0, 6), (0, 0, 6), (10, 5, 16)]
    roof = writer.create_slab_by_polygon(writer.ROOF, polygon3, mat_lsu1, storey1)

    # Write the file
    writer.write();

if __name__ == "__main__":
    test3()