'''
Created on Aug 16, 2010

@author: dexen
'''
import os
import csv
import string
import datetime
import shutil

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
        
    def set_gensky_command(self, gensky_command):
        self.gensky_command = gensky_command
        
    def set_cal_file(self, cal_file_path):
        self.cal_file_name = os.path.basename(cal_file_path)
        #TODO: this is not a full proof test for checking if two paths point to the same file
        cal_folder_path = os.path.dirname(cal_file_path)
        if os.path.abspath(cal_folder_path).lower() != os.path.abspath(self.data_folder_path).lower():
            shutil.copy(cal_file_path, self.data_folder_path)
        
    def create_sensor_input_file(self):
        sensor_file_path = os.path.join(self.data_folder_path, "sensor_points.pts")
        sensor_file = open(sensor_file_path,  "w")
        sensor_pts_data = write_rad.sensor_file(self.sensor_positions, self.sensor_normals)
        sensor_file.write(sensor_pts_data)
        sensor_file.close()
        self.sensor_file_path = sensor_file_path
        
    def create_rad_input_file(self, interior = True):
        rad_file_path = os.path.join(self.data_folder_path, "geometry.rad")
        rad_building_data = []
        rad_file = open(rad_file_path,  "w")
        for surface in self.surfaces:
            if interior == True:
                rad_data = surface.rad()
            else:
                rad_data = surface.rad(interior = False)
            rad_building_data.append(rad_data)
            
        for data in rad_building_data:
            rad_file.write(data)
        rad_file.close()
        self.rad_file_path = rad_file_path 
        
    
    def create_sky_input_file(self):
        sky_file_path = os.path.join(self.data_folder_path, "sky.rad")
        sky_file = open(sky_file_path,  "w")
        sky_glow = write_rad.glow("sky_glow", self.sky_colour)
        grd_glow = write_rad.glow("ground_glow", self.ground_colour)
        sky_source = write_rad.source("sky", "sky_glow", (0,0,1))
        grd_source = write_rad.source("ground", "ground_glow", (0,0,-1))
        if self.sky_method == 0:
            sky_data = self.gensky_command + "\n\n" + sky_glow + "\n\n" + grd_glow + "\n\n" + sky_source + "\n\n" + grd_source
        else:
            sky_brightfunc = write_rad.brightfunc(self.cal_file_name)
            sky_data = sky_brightfunc + "\n\n" + sky_glow + "\n\n" + grd_glow + "\n\n" + sky_source + "\n\n" + grd_source
        sky_file.write(sky_data)
        sky_file.close()
        self.sky_file_path = sky_file_path

    def execute_oconv(self): 
        self.create_sky_input_file()
        self.create_rad_input_file() #what about interior??
        oconv_file_path = os.path.join(self.data_folder_path, "input.oconv")
        command = "oconv " + self.base_file_path + " "\
        + self.sky_file_path + " " + self.rad_file_path +\
        " " + ">" + " " + oconv_file_path
        #print command + "\n\n\n"
        os.system(command) #EXECUTE!!
        self.oconv_file_path = oconv_file_path 
    
    def execute_rtrace(self, dict_parm):
        if self.oconv_file_path == None:
            raise Exception("oconv file is missing")
        #execute rtrace 
        self.create_sensor_input_file()
        result_file_path = os.path.join(self.data_folder_path, "results.txt")
        command = "rtrace -h -w -I+ -ab " +  dict_parm["ab"] + " -aa " + dict_parm["aa"] +\
        " -ar " + dict_parm["ar"] + " -ad " + dict_parm["ad"] + " -as " + dict_parm["as"] +\
        " " + self.oconv_file_path + " " + " < " + self.sensor_file_path +\
        " " + " > " + " " + result_file_path 
        #print command + "\n\n\n"
        operating_sys = os.name
        if operating_sys == "posix":
            rtrace_sh_file_path = os.path.join(self.data_folder_path, "run_rtrace.sh")
            rtrace_sh_file = open(rtrace_sh_file_path, "w")
            rtrace_sh_file.write("cd " + self.data_folder_path + "\n")
            rtrace_sh_file.write(command + "\n")
            rtrace_sh_file.close()
            os.system(". " + rtrace_sh_file_path)#EXECUTE!
        elif operating_sys == "nt":
            rtrace_bat_file_path = os.path.join(self.data_folder_path, "run_rtrace.bat")
            rtrace_bat_file = open(rtrace_bat_file_path, "w")
            rtrace_bat_file.write(self.data_folder_path[:2] + "\n")
            rtrace_bat_file.write("cd " + self.data_folder_path + "\n")
            rtrace_bat_file.write(command + "\n")
            rtrace_bat_file.close()
            os.system(rtrace_bat_file_path)#EXECUTE!
        self.result_file_path = result_file_path 
        
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
        os.system(command)#EXECUTE!!
         
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

        os.system(command1)#EXECUTE!!  
        os.system(command2)#EXECUTE!!  
        os.system(command3)#EXECUTE!!  
        os.system(command4)#EXECUTE!!  
        
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
        os.system(command)#EXECUTE!!   
        
    def eval_rad(self):
        if self.result_file_path == None:
            raise Exception
        results = open(self.result_file_path, "r")
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
    
    """
    def execute_hea(self, basefile_path, basefilename, filename, daysim_dir, weather_filename,
                    zone_area, occupancy_start, occupancy_end, min_illum_level):
        if self.sensor_file_path == None or self.rad_file_path == None:
            raise NameError("run .create_rad function before running .execute_hea function")
        
        #CREATE THE NECCESSARY FOLDERS FOR THE OUTPUT OF THE VARIOUS RESULTS
        heaout = os.path.join(basefile_path, filename + "/")
        hea_file_path = os.path.join(heaout, filename + "_out.hea")
        
        if not os.path.isdir(heaout):
            os.mkdir(heaout)
        sub_hea_folders = ["pts", "rad", "res","tmp", "wea"]
        for folder in range(len(sub_hea_folders)):
            sub_hea_folder = sub_hea_folders[folder]
            sub_hea_folders_path = os.path.join(heaout,sub_hea_folder)
            if not os.path.isdir(sub_hea_folders_path):
                os.mkdir(sub_hea_folders_path)
            if os.path.isdir(sub_hea_folders_path):
                files_in_dir = os.listdir(sub_hea_folders_path)
                for file in files_in_dir:
                    rmv_path = os.path.join(sub_hea_folders_path, file)
                    os.remove(rmv_path)
        
        #APPEND THE BASEFILE 
        base_filepath = os.path.join(basefile_path, basefilename + ".hea") 
        base_file = open(base_filepath, "r")
        base_stuff = base_file.read()
        base_file.close()
        hea_data = []
        hea_data.append(base_stuff)
        
        #WRITE THE HEA INFORMATION 
        tmp_dir = os.path.join(heaout, "tmp/")
        proj_info = daysimlink.write_proj_info(filename, heaout, tmp_dir)
        hea_data.append(proj_info)
        
        #WRITE THE ZONE AREA AND USER DESCRIPTION
        zone_size = daysimlink.write_zone_area(zone_area)
        hea_data.append(zone_size)
        user_description = daysimlink.write_user_description(occupancy_start, 
                                                             occupancy_end, 
                                                             min_illum_level)
        hea_data.append(user_description)
        
        #WRITE THE WEATHER DATA 
        wea_file_dir = os.path.join(daysim_dir,"wea", weather_filename) # in order to change the weather file input the 60min .wea dir, do the conversion from epw to wea using execute_epw2wea(bin_dir, source_file, destination_file)
        short_wea_name = weather_filename + "_5min.wea" # change the output .wea name respectively 
        weather_data = daysimlink.write_weather_data(wea_file_dir, 0.2, short_wea_name)
        hea_data.append(weather_data)
        
        #WRITE THE GEOMETRY INFO
        sensor_file_path = self.sensor_file_path 
        rad_file_path = self.rad_file_path 
        rad_file_dir_list = [self.base_file_path, rad_file_path]
        geometry_data = daysimlink.write_geometry_info(filename, sensor_file_path, rad_file_dir_list)
        hea_data.append(geometry_data)
        
        #WRITE THE RESULTS INFO
        result_data = daysimlink.write_result_file(filename)
        hea_data.append(result_data)
        
        #WRITE THE RESULT FILE 
        hea_file = open(hea_file_path,  "w")
        for data in hea_data:
            hea_file.write(data)
        hea_file.close()
        
        #EXECUTE DAYSIM
        bin_dir = os.path.join(daysim_dir,"bin") 
        os.chdir(bin_dir)
        command1 =  "./ds_shortterm " +  hea_file_path
        os.system(command1)
        command2 = "./radfiles2daysim " +  "'" + hea_file_path +"'" + " -g -m -d"
        os.system(command2)
        command3 = "./gen_dc " +  "'" + hea_file_path +"'"
        os.system(command3)
        command4 = "./ds_illum " +  "'" + hea_file_path +"'" 
        os.system(command4)
        command5 = "./gen_directsunlight " +  "'" + hea_file_path +"'" 
        os.system(command5)
        command6 = "./ds_autonomy " +  "'" + hea_file_path +"'" 
        os.system(command6)
        
        self.hea_result = os.path.join(heaout, "res")
        self.hea_filename = filename
        
    def eval_hea(self):
        if self.hea_result == None or self.hea_filename == None :
            raise Exception
        da_path = os.path.join(self.hea_result,self.hea_filename + ".da")
        da_results = open(da_path, "r")
        da_result_stuff = da_results.readlines()
        num_da_list = []
        #daysim results processing average the DA
        for line in range(len(da_result_stuff)-2): 
            lines =  da_result_stuff[2+line][78:83] 
            numbers_da = float(lines)
            num_da_list.append(round(numbers_da, 1))
        return num_da_list
    """
    
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

