'''
Updated on 6 Feb 2016

@author: Patrick Janssen
'''
import os
import csv
import string
import datetime
import shutil
import math
import subprocess

import write_rad

class Rad(object):
    def __init__(self, base_file_path, data_folder_path):
        #paths
        self.base_file_path = base_file_path
        self.data_folder_path = data_folder_path
        if not os.path.isdir(data_folder_path):
            os.mkdir(data_folder_path)     
        #sky parameters
        self.sky_method = None
        self.gensky_command = None
        self.gendaylit_command = None
        self.sky_colour = None
        self.ground_colour = None
        self.cal_file_name = None
        #data
        self.surfaces = []
        self.sensor_positions = None
        self.sensor_normals = None
        #input files
        self.sensor_file_path = None
        self.rad_file_path = None
        self.sky_file_path = None
        self.oconv_file_path = None        
        #daysim stuff
        self.hea_result = None
        self.hea_filename = None
        #output files
        self.result_file = None        
             
    def set_sensor_points(self, sensor_positions,sensor_normals):
        self.sensor_positions = sensor_positions
        self.sensor_normals = sensor_normals
        
    def set_env_colours(self, sky_colour, ground_colour):
        self.sky_colour = sky_colour
        self.ground_colour = ground_colour
        
    def set_sky_method(self, sky_method):
        self.sky_method = sky_method
        
    def set_gensky_command(self, month, day, hour, latitude, longitude, meridian, sky_type):
        self.gensky_command = "!gensky " + str(month) + " " + str(day) + " +" + str(hour) +\
            " " + sky_type + " -a " + str(latitude) + " -o " + str(longitude) + " -m " + str(meridian)
        
    def set_gendaylit_command(self, month, day, hour, wea_file_path):
        #wea file has data for 30 mins past the hour, i.e. 0.5, 1.5, 2.5, 3.5 etc
        hour = math.floor(hour) + 0.5
        #read the data in the wea file
        with open(wea_file_path, "r") as wea_file:
            for line in wea_file:
                if line.startswith("latitude"):
                    latitude = line.split()[1]
                elif line.startswith("longitude"):
                    longitude = line.split()[1]
                elif line.startswith("time_zone"):
                    meridian = line.split()[1]
                elif line.startswith(str(month) + " " + str(day) + " " + str(hour)):
                    values = line.split()[3:]
        #print self.latitude, self.longitude, self.meridian, self.values
        self.gendaylit_command = "!gendaylit " + str(month) + " " + str(day) + " +" + str(hour) +\
            " -a " + str(latitude) + " -o " + str(longitude) + " -m " + str(meridian) + " -G " + values[0] + " " + values[1] + " -O 1"
      
    def copy_cal_file(self, cal_file_path):
        self.cal_file_name = os.path.basename(cal_file_path)
        #TODO: this is not a full proof test for checking if two paths point to the same file
        cal_folder_path = os.path.dirname(cal_file_path)
        if os.path.abspath(cal_folder_path).lower() != os.path.abspath(self.data_folder_path).lower():
            shutil.copy(cal_file_path, self.data_folder_path)
        
    def create_sensor_input_file(self):
        self.sensor_file_path = os.path.join(self.data_folder_path, "sensor_points.pts")
        with open(self.sensor_file_path,  "w") as sensor_file:
            sensor_pts_data = write_rad.sensor_file(self.sensor_positions, self.sensor_normals)
            sensor_file.write(sensor_pts_data)
        
    def create_rad_input_file(self, interior = True):
        self.rad_file_path = os.path.join(self.data_folder_path, "geometry.rad")
        rad_building_data = []
        with open(self.rad_file_path,  "w") as rad_file:
            for surface in self.surfaces:
                if interior == True:
                    rad_data = surface.rad()
                else:
                    rad_data = surface.rad(interior = False)
                rad_building_data.append(rad_data)
                
            for data in rad_building_data:
                rad_file.write(data)
        
    def create_sky_input_file(self):
        self.sky_file_path = os.path.join(self.data_folder_path, "sky.rad")
        with open(self.sky_file_path,  "w") as sky_file:
            sky_glow = write_rad.glow("sky_glow", self.sky_colour)
            grd_glow = write_rad.glow("ground_glow", self.ground_colour)
            sky_source = write_rad.source("sky", "sky_glow", (0,0,1))
            grd_source = write_rad.source("ground", "ground_glow", (0,0,-1))
            if self.sky_method == 0:
                sky_data = self.gensky_command + "\n\n" + sky_glow + "\n\n" + grd_glow + "\n\n" + sky_source + "\n\n" + grd_source
            elif self.sky_method == 1:
                sky_data = self.gendaylit_command + "\n\n" + sky_glow + "\n\n" + grd_glow + "\n\n" + sky_source + "\n\n" + grd_source
            else:
                sky_brightfunc = write_rad.brightfunc(self.cal_file_name)
                sky_data = sky_brightfunc + "\n\n" + sky_glow + "\n\n" + grd_glow + "\n\n" + sky_source + "\n\n" + grd_source
            sky_file.write(sky_data)

    def execute_oconv(self): 
        self.create_sky_input_file()
        self.create_rad_input_file() #what about interior??
        self.oconv_file_path = os.path.join(self.data_folder_path, "input.oconv")
        command = "oconv " + self.base_file_path + " "\
        + self.sky_file_path + " " + self.rad_file_path +\
        " " + ">" + " " + self.oconv_file_path
        #print command + "\n\n\n"
        operating_sys = os.name
        if operating_sys == "posix":
            oconv_sh_file_path = os.path.join(self.data_folder_path, "run_oconv.sh")
            with open(oconv_sh_file_path, "w") as oconv_sh_file:
                oconv_sh_file.write("cd " + self.data_folder_path + "\n")
                oconv_sh_file.write(command + "\n")
            subprocess.call(". " + oconv_sh_file_path)#EXECUTE!
        elif operating_sys == "nt":
            oconv_bat_file_path = os.path.join(self.data_folder_path, "run_oconv.bat")
            with open(oconv_bat_file_path, "w") as oconv_bat_file:
                oconv_bat_file.write(self.data_folder_path[:2] + "\n")
                oconv_bat_file.write("cd " + self.data_folder_path + "\n")
                oconv_bat_file.write(command + "\n")
            subprocess.call(oconv_bat_file_path)#EXECUTE!
    
    def execute_rtrace(self, dict_parm):
        if self.oconv_file_path == None:
            raise Exception("oconv file is missing")
        #execute rtrace 
        self.create_sensor_input_file()
        self.result_file_path = os.path.join(self.data_folder_path, "results.txt")
        command = "rtrace -h -w -I+ -ab " +  dict_parm["ab"] + " -aa " + dict_parm["aa"] +\
        " -ar " + dict_parm["ar"] + " -ad " + dict_parm["ad"] + " -as " + dict_parm["as"] +\
        " " + self.oconv_file_path + " " + " < " + self.sensor_file_path +\
        " " + " > " + " " + self.result_file_path 
        #print command + "\n\n\n"
        operating_sys = os.name
        if operating_sys == "posix":
            rtrace_sh_file_path = os.path.join(self.data_folder_path, "run_rtrace.sh")
            with open(rtrace_sh_file_path, "w") as rtrace_sh_file:
                rtrace_sh_file.write("cd " + self.data_folder_path + "\n")
                rtrace_sh_file.write(command + "\n")
            subprocess.call(". " + rtrace_sh_file_path)#EXECUTE!
        elif operating_sys == "nt":
            rtrace_bat_file_path = os.path.join(self.data_folder_path, "run_rtrace.bat")
            with open(rtrace_bat_file_path, "w") as rtrace_bat_file:
                rtrace_bat_file.write(self.data_folder_path[:2] + "\n")
                rtrace_bat_file.write("cd " + self.data_folder_path + "\n")
                rtrace_bat_file.write(command + "\n")
            subprocess.call(rtrace_bat_file_path)#EXECUTE!
        
    def execute_rvu(self, vp, vd, dict_parm):
        if self.oconv_file_path == None:
            raise Exception("oconv file is missing")
        #execute rvu
        operating_sys = os.name
        if operating_sys == "posix":
            command = "rvu -vp " + vp + " -vd " + vd +\
            " -ab " + dict_parm["ab"] + " -aa " + dict_parm["aa"] +\
            " -ar " + dict_parm["ar"] + " -ad " + dict_parm["ad"] + " -as " + dict_parm["as"] +\
            " -pe " + dict_parm["exp"] + " " + self.oconv_file_path + " &"
        elif operating_sys == "nt":
            command = "rview -vp " + vp + " -vd " + vd +\
            " -ab " + dict_parm["ab"] + " -aa " + dict_parm["aa"] +\
            " -ar " + dict_parm["ar"] + " -ad " + dict_parm["ad"] + " -as " + dict_parm["as"] +\
            " -pe " + dict_parm["exp"] + " " + self.oconv_file_path + " &"
        subprocess.call(command)#EXECUTE!!
         
    def execute_rpict(self, filename, x_resolution, y_resolution, vp, vd, dict_parm):
        if self.oconv_file_path == None:
            raise Exception("oconv file is missing")
        #execute rpict
        image_folder_path = os.path.join(self.data_folder_path,"images")
        if not os.path.isdir(image_folder_path):
            os.mkdir(image_folder_path)
        image_file_path = os.path.join(image_folder_path, filename)
        
        command1 = "rpict -x " + x_resolution + " -y " + y_resolution + " -vp " + vp +\
         " -vd " + vd +\
         " -ab " +  dict_parm["ab"] + " -aa " + dict_parm["aa"] +\
         " -ar " + dict_parm["ar"] + " -ad " + dict_parm["ad"] + " -as " + dict_parm["as"] +\
         " -i " + self.oconv_file_path + " > " + image_file_path + "out_i.hdr" 
          
        command2 = "rpict -x " + x_resolution + " -y " + y_resolution + " -vp " +\
         vp + " -vd " + vd +\
         " -ab " +  dict_parm["ab"] + " -aa " + dict_parm["aa"] +\
        " -ar " + dict_parm["ar"] + " -ad " + dict_parm["ad"] + " -as " + dict_parm["as"] +\
         " " + self.oconv_file_path + " > " + image_file_path + "out.hdr"
          
        command3 = "pfilt -e " + dict_parm["exp"] + " " + image_file_path + "out_i.hdr" + " > " +\
         image_file_path + "out_i_filt.hdr"
         
        command4 = "pfilt -e " + dict_parm["exp"] + " " + image_file_path + "out.hdr" + " > " +\
         image_file_path + "out_filt.hdr"

        subprocess.call(command1)#EXECUTE!!  
        subprocess.call(command2)#EXECUTE!!  
        subprocess.call(command3)#EXECUTE!!  
        subprocess.call(command4)#EXECUTE!!  
        
    def execute_falsecolour(self,i_basefilename, l_basefilename, filename, range_max, 
                            range_division, illuminance = True):
        image_folder_path = os.path.join(self.data_folder_path, "images")
        if not os.path.isdir(image_folder_path):
            os.mkdir(image_folder_path)
        i_base_image_path = os.path.join(image_folder_path, i_basefilename)
        l_base_image_path = os.path.join(image_folder_path, l_basefilename)
        falsecolour_folder_path = os.path.join(image_folder_path, "falsecolour")
        if not os.path.isdir(falsecolour_folder_path):
            os.mkdir(falsecolour_folder_path)
        falsecolour_file_path = os.path.join(falsecolour_folder_path, filename)
        if illuminance == True:
            command = "falsecolor -i " + i_base_image_path + " -p " +\
             l_base_image_path + " -cl -n " + range_division + " -s " + range_max +\
             " -l lux > " + falsecolour_file_path + "_illum.hdr"
        else:
            command = "falsecolor -ip " + l_base_image_path +\
             " -cl -n " + range_division + " -s " + range_max +\
             " -l cd/m2 > " + falsecolour_file_path + "_luminance.hdr"
        subprocess.call(command)#EXECUTE!!   
        
    def eval_rad(self):
        if self.result_file_path == None:
            raise Exception
        with open(self.result_file_path, "r") as results:
            irradiance_list = []        
            illuminance_list = []
            for result in results:
                words  = result.split()
                numbers = map(float, words)
                #IRRADIANCE RESULTS 
                irradiance = round((0.265 * numbers[0]) + (0.670 * numbers[1]) + (0.065 * numbers[2]), 1)
                irradiance_list.append(irradiance)
                #ILLUMINANCE RESULTS            
                illuminance = irradiance * 179
                illuminance_list.append(illuminance)
        return irradiance_list, illuminance_list
    
class Surface(object):
    def __init__(self, name, points, material):
        self.name = name
        self.points = points
        self.material = material
    
class RadSurface(Surface):
    def __init__(self, name, points, material, radgeom):
        super(RadSurface, self).__init__(name,  points, material)
        self.radgeom = radgeom
        radgeom.surfaces.append(self)
        
    def rad(self, interior = True):
        name = self.name
        material = self.material
        points = self.points[:]
        if interior == True:
            points.reverse()
        return write_rad.surface(name, material, points)

