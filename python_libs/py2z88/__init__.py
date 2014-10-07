'''
Link to Z88 Aurora
'''
import os
import csv
import string
import datetime

#template
z88_dyn_template = """DYNAMIC START
---------------------------------------------------------------------------
Z88 new version 14.0                   Z88 neue Version 14.0
---------------------------------------------------------------------------

---------------------------------------------------------------------------
LANGUAGE            SPRACHE
---------------------------------------------------------------------------
ENGLISH
---------------------------------------------------------------------------
Common entries for all modules         gemeinsame Daten fuer alle Module
---------------------------------------------------------------------------
  COMMON START
    MAXKOI          500000
    MAXK            60000
    MAXE            30000
    MAXNEG          10
    MAXGP           1000000
    MAXOTE          150000
    MAXSTRUGEOELE   100
    MAXLASTF        1
    MAXSTLK         50000
    MAXMAT          100
    MAXXEPTHE       100
    MAXXEPMAT       100
    MAXMAPAR        100
    MAXMMREG        5000
    MAXSTAT         20
    MAXFREQ         20
    MAXNFG          180000
    MAXRBD          2000
    MAXPR           1000
    MAXPRT          1
  COMMON END
DYNAMIC END
"""

#template
z88manage_txt_template = """DYNAMIC START
---------------------------------------------------------------------------
Z88aurora Version 1
---------------------------------------------------------------------------

---------------------------------------------------------------------------
GLOBAL
---------------------------------------------------------------------------

GLOBAL START
   SIMCASE         1
   NEG             1
   IQFLAG          0
   LOADCASE        1
   LOADSELECT      0
   LOADADD         0
GLOBAL END

---------------------------------------------------------------------------
LINEAR SOLVER
---------------------------------------------------------------------------

SOLVER START
   ICFLAG          1
   MFLAG           0
   MAXIT           10000
   EPS             1e-007
   RALPHA          0.0001
   ROMEGA          1.1
   ICORE           1
   OOCFLAG         0
   OUTPATH         ".\out_of_core\"
   DUMPMAX         1000
SOLVER END

---------------------------------------------------------------------------
STRESS
---------------------------------------------------------------------------

STRESS START
   NINTO         0
   KSFLAG        0
   ISFLAG        1
STRESS END

DYNAMIC END
"""

class Z88(object):
    
    def __init__(self, data_folder_path):
        self.data_folder_path = data_folder_path
        self.nodes = []
        self.elements = []
        self.materials = []
        self.conditions = []
        self.element_params = []
        self.z88i1_header = None
        self.z88i2_header = None
        self.z88i3_header = None
        self.node_displacements = None
        self.node_forces = None
        self.elem_stress = None 
        
        
    def set_z88i1_header(self, header):
        self.z88i1_header = header
        
    def set_z88i2_header(self, header):
        self.z88i2_header = header
        
    def set_z88i3_header(self, header):
        self.z88i3_header = header
        
    def add_node(self, node):
        self.nodes.append(node)
        
    def add_element(self, element):
        self.elements.append(element)
        
    def add_material(self, material):
        self.materials.append(material)
        
    def add_condition(self, condition):
        self.conditions.append(condition)
        
    def add_element_param(self, element_param):
        self.element_params.append(element_param)
        
    def write_input_files(self):
        #create folder
        if not os.path.isdir(self.data_folder_path):
            os.mkdir(self.data_folder_path)
        
        #create  z88.dyn
        z88_dyn_file_path = os.path.join(self.data_folder_path, "z88.dyn")
        z88_dyn_file = open(z88_dyn_file_path, "w")
        z88_dyn_file.write(z88_dyn_template)
        z88_dyn_file.close()
        
        #create  z88manage.txt
        z88manage_txt_file_path = os.path.join(self.data_folder_path, "z88manage.txt")
        z88manage_txt_file = open(z88manage_txt_file_path, "w")
        z88manage_txt_file.write(z88manage_txt_template)
        z88manage_txt_file.close()
        
        #create z88i1.txt
        z88i1_file_path = os.path.join(self.data_folder_path, "z88i1.txt")
        z88i1_file = open(z88i1_file_path, "w")
        z88i1_file.write(self.z88i1_header.get_str())
        for node in self.nodes:
            z88i1_file.write(node.get_str())
        for element in self.elements:
            z88i1_file.write(element.get_str())
        for material in self.materials:
            z88i1_file.write(material.get_z88i1_str())
        z88i1_file.close()
        
        #create z88i2.txt
        z88i2_file_path = os.path.join(self.data_folder_path, "z88i2.txt")
        z88i2_file = open(z88i2_file_path, "w")
        z88i2_file.write(self.z88i2_header.get_str())
        for condition in self.conditions:
            z88i2_file.write(condition.get_str())
        z88i2_file.close()
        
        #create z88mat.txt
        z88mat_file_path = os.path.join(self.data_folder_path, "z88mat.txt")
        z88mat_file = open(z88mat_file_path, "w")
        z88mat_file.write(str(len(self.materials)) + "\n")
        for material in self.materials:
            z88mat_file.write(material.get_z88mat_str())
        z88mat_file.close()
        
        #create csv files
        for material in self.materials:
            csv_file_path = os.path.join(self.data_folder_path, material.name + ".csv")
            csv_file = open(csv_file_path, "w")
            csv_file.write(material.get_csv_str())
            csv_file.close()
        
        #create z88elp.txt
        z88elp_file_path = os.path.join(self.data_folder_path, "z88elp.txt")
        z88elp_file = open(z88elp_file_path, "w")
        z88elp_file.write(str(len(self.element_params)) + "\n")
        for element_param in self.element_params:
            z88elp_file.write(element_param.get_str())
        z88elp_file.close()
        
        #create z88i3.txt
        z88i3_file_path = os.path.join(self.data_folder_path, "z88i3.txt")
        z88i3_file = open(z88i3_file_path, "w")
        z88i3_file.write(self.z88i3_header.get_str())
        z88i3_file.close()
        
    def execute_z88(self):
    
        #EXECUTE Z88 
        operating_sys = os.name
        if operating_sys == "posix":
            raise Exception

        elif operating_sys == "nt":
            #fix path problem
            data_folder_path = os.path.normpath(self.data_folder_path)
            #generate bat file
            bat_file_path = os.path.join(data_folder_path, "run_z88.bat")
            bat_file = open(bat_file_path, "w")
            bat_file.write(data_folder_path[0:2] + "\n")
            bat_file.write("cd " + data_folder_path + "\n")
            bat_file.write("z88r.exe -t -siccg\n")
            bat_file.write("z88r.exe -c -siccg\n")
            bat_file.close()
            os.system(bat_file_path)
        
    def read_output_files(self):
        self.read_z88o2()
        self.read_z88o3()
        self.read_z88o4()
    
    def read_z88o2(self):
        #print "read_z88o2"
        content = self.read_z88o_file(2)
        content = content
        
        node_displacements = {}
        for node_counter in range(len(self.nodes)):
            row_num = 5 + node_counter
            words = content[row_num].split()
            id = int(words[0])
            displacements = [float(x) for x in words[1:]]
            node_displacements[id] = displacements
        self.node_displacements =  node_displacements
        #print self.node_displacements
        
    def read_z88o3(self):
        #print "read_z88o3"
        content = self.read_z88o_file(3)
        
        elem_stress = {}
        for elem_counter in range(len(self.elements)):
            row_num = (elem_counter * 6) + 4
            elem_id = int(content[row_num + 1].split()[3])
            point_stress = []
            for point_counter in range(3):
                words = content[row_num + point_counter + 3].split()
                point_stress.append([float(x) for x in words])
            elem_stress[elem_id] = point_stress
        self.elem_stress =  elem_stress
        #print self.elem_stress
        
    def read_z88o4(self):
        #print "read_z88o4"
        content = self.read_z88o_file(4)
        
        """
        elem_forces = {}
        for elem_counter in range(len(self.elements)):
            row_num = (elem_counter * 9) + 5
            elem_id = int(content[row_num + 1].split()[3])
            node_forces = {}
            for node_counter in range(6):
                words = content[row_num + node_counter + 3].split()
                node_id = int(words[0])
                node_forces[node_id] = [float(x) for x in words[1:]]
            elem_forces[elem_id] = node_forces
        """
         
        node_forces = {}
        for node_counter in range(len(self.nodes)):
            row_num = (len(self.elements) * 9) + 10 + node_counter
            words = content[row_num].split()
            id = int(words[0])
            forces = [float(x) for x in words[1:]]
            node_forces[id] = forces
            
        self.node_forces = node_forces
        #print self.node_forces
        
    def read_z88o_file(self, num):
        #check to see if the file exists
        result_file_path = os.path.join(self.data_folder_path, "z88o"+str(num)+".txt")
        if not os.path.exists(result_file_path):
            print "Error reading " + result_file_path
            raise Exception
        #read the csv file 
        f = open(result_file_path, "r")
        content = f.readlines()
        f.close()
        return content
        
    def get_results(self, result_category, display):
        if self.content == None:
            raise Exception
        content = self.content
        res_list = []
        return res_list
            
#-------------------------------------------------------------------------------
class Z88i1Header(object):
    def __init__(self,dimension,num_nodes,num_elements,num_dof,num_materials,
            KFLAG=0,IBFLAG=0,IPFLAG=0,IQFLAG=0,IHFLAG=0):
        self.dimension = dimension
        self.num_nodes = num_nodes
        self.num_elements = num_elements
        self.num_dof = num_dof
        self.num_materials = num_materials
        self.KFLAG = KFLAG
        self.IBFLAG = IBFLAG
        self.IPFLAG = IPFLAG
        self.IQFLAG = IQFLAG
        self.IHFLAG = IHFLAG
        
    def get_str(self):
        result = [
            self.dimension, self.num_nodes, self.num_elements,self.num_dof,self.num_materials,
            self.KFLAG,self.IBFLAG,self.IPFLAG,self.IQFLAG,self.IHFLAG]
        result = " ".join(map(str, result)) + "\n"
        return result
           
class Node(object):
    def __init__(self,node_num,num_dof,x,y,z):
        self.node_num = node_num
        self.num_dof = num_dof
        self.x = x
        self.y = y
        self.z = z
        
    def get_str(self):
        result = [self.node_num, self.num_dof, self.x,self.y,self.z]
        result = " ".join(map(str, result)) + "\n"
        return result
        
class Element(object):
    def __init__(self,elem_num,elem_type,node_nums):
        self.elem_num = elem_num
        self.elem_type = elem_type
        self.node_nums = node_nums

    def get_str(self):
        result1 = " ".join(map(str, [self.elem_num, self.elem_type])) + "\n"
        result2 = " ".join(map(str, self.node_nums)) + "\n"
        return result1 + result2
        
#-------------------------------------------------------------------------------
class Z88i2Header(object):
    def __init__(self,num_conditions,num_cases,MGFLAG,gravity,case_name):
        self.num_conditions = num_conditions
        self.num_cases = num_cases
        self.MGFLAG = MGFLAG
        self.gravity = gravity
        self.case_name = case_name
        
    def get_str(self):
        result = [
            self.num_conditions, self.num_cases, self.MGFLAG, 
            self.gravity[0],self.gravity[1],self.gravity[2],
            self.case_name]
        result = " ".join(map(str, result)) + "\n"
        return result
        
class Condition(object):
    def __init__(self,node_num,dof_num,cond_type,value):
        self.node_num = node_num
        self.dof_num = dof_num
        self.cond_type = cond_type
        self.value = value

    def get_str(self):
        result = [self.node_num, self.dof_num, self.cond_type,self.value]
        result = " ".join(map(str, result)) + "\n"
        return result
        
#-------------------------------------------------------------------------------
class Z88i3Header(object):
    def __init__(self,gauss_points,KSFLAG,ISFLAG):
        self.gauss_points = gauss_points
        self.KSFLAG = KSFLAG      #see page 37 of theory guide
        self.ISFLAG = ISFLAG    #see page 37 of theory guide
        
    def get_str(self):
        result = [self.gauss_points, self.KSFLAG, self.ISFLAG]
        result = " ".join(map(str, result)) + "\n"
        return result

#-------------------------------------------------------------------------------
class Material(object):
    def __init__(self,
            from_elem, to_elem,
            youngs_modulus,
            poisson_ratio,
            integration_order,
            QPARA,
            solid_num,  #for z88mat.txt
            MATFLAG,    #for z88mat.txt
            name = "material"):      #for z88mat.txt
        self.from_elem = from_elem
        self.to_elem = to_elem
        self.youngs_modulus = youngs_modulus
        self.poisson_ratio = poisson_ratio
        self.integration_order = integration_order
        self.QPARA = QPARA
        self.solid_num = solid_num
        self.MATFLAG = MATFLAG
        self.name = name
        
    def get_z88i1_str(self):
        result = [
            self.from_elem, self.to_elem, 
            self.youngs_modulus, self.poisson_ratio, self.integration_order, 
            self.QPARA]
        result = " ".join(map(str, result)) + "\n"
        return result
        
    def get_csv_str(self):
        line1 = str(self.youngs_modulus) + ";" + str(self.poisson_ratio) + ";0\n"
        line2 = "0;0\n"
        return line1 + line2
        
    def get_z88mat_str(self):
        result = [
            self.from_elem, self.to_elem, 
            self.integration_order,self.solid_num,self.MATFLAG,
            self.name + ".csv"]
        result = " ".join(map(str, result)) + "\n"
        return result
#-------------------------------------------------------------------------------
class ElementParam(object):
    def __init__(self,
            from_elem, to_elem,
            QPARA,
            second_inertia_yy, max_dist_yy,
            second_inertia_zz, max_dist_zz,
            second_area, second_modulus):
        self.from_elem = from_elem
        self.to_elem = to_elem
        self.QPARA = QPARA
        self.second_inertia_yy = second_inertia_yy
        self.max_dist_yy = max_dist_yy
        self.second_inertia_zz = max_dist_zz
        self.max_dist_zz = max_dist_zz
        self.second_area = second_area
        self.second_modulus = second_modulus
        
    def get_str(self):
        result = [
            self.from_elem, self.to_elem, self.QPARA, 
            self.second_inertia_yy, self.max_dist_yy,
            self.second_inertia_zz, self.max_dist_zz,
            self.second_area, self.second_modulus
            ]
        result = " ".join(map(str, result)) + "\n"
        return result