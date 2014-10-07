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

class RadSurface(object):
    def __init__(self, name, points, material):
        self.name = name
        self.points = points
        self.material = material
        
    def to_str(self, interior = True):
        if interior == True:
            self.points.reverse()
        return write_rad.surface(self.name, self.material, self.points)
        
class Daysim(object):

    def __init__(self, data_folder_path):
        #paths
        self.data_folder_path = data_folder_path
        if not os.path.isdir(data_folder_path):
            os.mkdir(data_folder_path)     
        self.sensor_file_path = None
        self.viewpoints_file_path = None
        self.rad_file_path = None 
        self.hea_file_path = None 
        
        #data
        self.surfaces = []
        self.sensor_positions = None
        self.sensor_normals = None
        self.viewpoint_positions = None
        self.viewpoint_normals = None
        
        #input files
        self.material_file_path = None
        self.sensor_file_path = None
        self.rad_file_path = None
        self.hea_file_path = None
        self.daysim_bat_file_path = None

        #name
        self.epw_file_name = None
        self.wea_file_name = None
        self.occ_file_name = None

    def set_surfaces(self, surfaces):
        self.surfaces = surfaces
        
    def append_surface(self, surface):
        self.surfaces.append(surface)
        
    def set_sensor_points(self, sensor_positions, sensor_normals):
        self.sensor_positions = sensor_positions
        self.sensor_normals = sensor_normals
        
    def set_viewpoints(self, viewpoint_positions, viewpoint_normals):
        self.viewpoint_positions = viewpoint_positions
        self.viewpoint_normals = viewpoint_normals
        
    def set_materials(self, materials_data):
        self.materials_data = materials_data

    def set_epw_file_name(self, epw_file_name):
        self.epw_file_name = epw_file_name

    def set_wea_file_name(self, wea_file_name):
        self.wea_file_name = wea_file_name

    def set_occ_file_name(self, occ_file_name):
        self.occ_file_name = occ_file_name

    def _create_sensor_input_file(self):
        sensor_file_path = os.path.join(self.data_folder_path, "sensor_file.pts")
        sensor_file = open(sensor_file_path,  "w")
        sensor_pts_data = write_rad.sensor_file(self.sensor_positions, self.sensor_normals)
        sensor_file.write(sensor_pts_data)
        sensor_file.close()
        self.sensor_file_path = sensor_file_path
        
    def _create_viewpoints_input_file(self):
        if not self.viewpoint_positions:
            return
        viewpoints_file_path = os.path.join(self.data_folder_path, "viewpoints.vf")
        viewpoints_file = open(viewpoints_file_path,  "w")
        viewpoints_data = write_rad.sensor_file(self.viewpoint_positions, self.viewpoint_normals)
        viewpoints_file.write("rview Perspective -vtv ")
        viewpoints_file.write("-vp " + 
            str(self.viewpoint_positions[0][0]) + " " + 
            str(self.viewpoint_positions[0][1]) + " " + 
            str(self.viewpoint_positions[0][2]) + " ")
        viewpoints_file.write("-vd " + 
            str(self.viewpoint_normals[0][0]) + " " + 
            str(self.viewpoint_normals[0][1]) + " " + 
            str(self.viewpoint_normals[0][2]) + " ")
        viewpoints_file.write("-vu 0 0 1 -vh 54 -vv 37 -vs 0 -vl 0 -x 800 -y 600\n")
        viewpoints_file.close()
        self.viewpoints_file_path = viewpoints_file_path
        
    def _create_geometry_input_file(self, interior = True):
        rad_file_path = os.path.join(self.data_folder_path, "geometry.rad")
        rad_building_data = []
        rad_file = open(rad_file_path,  "w")
        for surface in self.surfaces:
            if interior == True:
                rad_data = surface.to_str()
            else:
                rad_data = surface.to_str(interior = False)
            rad_building_data.append(rad_data)
            
        for data in rad_building_data:
            rad_file.write(data)
        rad_file.close()
        self.rad_file_path = rad_file_path 

    def _create_materials_input_file(self):
        materials_file_path = os.path.join(self.data_folder_path, "materials.rad")
        materials_file = open(materials_file_path,  "w")
        materials_file.write(self.materials_data)
        materials_file.close()
        self.materials_file_path = materials_file_path

    def _create_hea_input_file(self, settings_dict):

        #create the file
        hea_file_path = os.path.join(self.data_folder_path, "daysim.hea")
        hea_file = open(hea_file_path, "w")
        hea_file.write("################################\n")
        hea_file.write("#DAYSIM Header\n")
        hea_file.write("################################\n")
        hea_file.write("project_name daysim\n") #TODO check if this needs to match shading names
        hea_file.write("project_directory "+ self.data_folder_path +"\n")
        #TODO: check bin dir
        hea_file.write("tmp_directory "+ self.data_folder_path +"\n")

        hea_file.write("################################\n")
        hea_file.write("#Site information\n")
        hea_file.write("################################\n")
        hea_file.write("place " + os.path.join(self.data_folder_path, self.epw_file_name) + "\n")
        hea_file.write("latitude " + str(settings_dict["latitude"]) + "\n")
        hea_file.write("longitude " + str(settings_dict["longitude"]) + "\n")
        hea_file.write("time_zone " + str(settings_dict["time_zone"]) + "\n")
        hea_file.write("site_elevation " + str(settings_dict["site_elevation"]) + "\n")
        hea_file.write("time_step " + str(settings_dict["time_step"]) + "\n")
        hea_file.write("wea_data_short_file " + self.wea_file_name + "\n")
        hea_file.write("wea_data_short_file_units 1\n")
        hea_file.write("lower_direct_threshold " + str(settings_dict["lower_direct_threshold"]) + "\n")
        hea_file.write("lower_diffuse_threshold " + str(settings_dict["lower_diffuse_threshold"]) + "\n")
        hea_file.write("output_units " + str(settings_dict["output_units"]) + "\n")

        hea_file.write("################################\n")
        hea_file.write("#Bulding information\n")
        hea_file.write("################################\n")
        hea_file.write("material_file materials_daysim.rad\n")
        hea_file.write("geometry_file geometry_daysim.rad\n")
        hea_file.write("radiance_source_files 2, "
            + os.path.join(self.data_folder_path, "materials.rad") + ", "
            + os.path.join(self.data_folder_path, "geometry.rad") +"\n") #TODO replace
        hea_file.write("sensor_file sensor_file.pts\n") # TODO Replace 

        #hea_file.write("viewpoint_file viewpoints.vf\n")
        #hea_file.write("AdaptiveZoneApplies 0\n") # TODO Replace
        #hea_file.write("dgp_image_x_size 500\n") # TODO Replace
        #hea_file.write("dgp_image_y_size 500\n") # TODO Replace

        hea_file.write("################################\n")
        hea_file.write("#Radiance simulation parameters\n")
        hea_file.write("################################\n")
        hea_file.write("ab " + str(settings_dict["rad_ab"]) + "\n")
        hea_file.write("ad " + str(settings_dict["rad_ad"]) + "\n")
        hea_file.write("as " + str(settings_dict["rad_as"]) + "\n")
        hea_file.write("ar " + str(settings_dict["rad_ar"]) + "\n")
        hea_file.write("aa " + str(settings_dict["rad_aa"]) + "\n")
        hea_file.write("lr " + str(settings_dict["rad_lr"]) + "\n")
        hea_file.write("st " + str(settings_dict["rad_st"]) + "\n")
        hea_file.write("sj " + str(settings_dict["rad_sj"]) + "\n")
        hea_file.write("lw " + str(settings_dict["rad_lw"]) + "\n")
        hea_file.write("dj " + str(settings_dict["rad_dj"]) + "\n")
        hea_file.write("ds " + str(settings_dict["rad_ds"]) + "\n")
        hea_file.write("dr " + str(settings_dict["rad_dr"]) + "\n")
        hea_file.write("dp " + str(settings_dict["rad_dp"]) + "\n")

        hea_file.write("################################\n")
        hea_file.write("#User description\n")
        hea_file.write("################################\n")
        hea_file.write("occupancy 5 " + self.occ_file_name + "\n") 
        hea_file.write("minimum_illuminance_level " + str(settings_dict["minimum_illuminance_level"]) + "\n")
        hea_file.write("daylight_savings_time " + str(settings_dict["daylight_savings_time"]) + "\n")

        hea_file.write("################################\n")
        hea_file.write("#Shading control system\n")
        hea_file.write("################################\n")
        hea_file.write("shading 1 no_shading daysim.dc daysim.ill\n") #TODO: check names

        hea_file.write("################################\n")
        hea_file.write("#Daylight results\n")
        hea_file.write("################################\n")
        hea_file.write("daylight_autonomy_active_RGB daysim_autonomy.da\n") #TODO: check names
        #hea_file.write("electric_lighting daysim_electriclighting.htm")
        #hea_file.write("direct_sunlight_file daysim.dir")
        #hea_file.write("thermal_simulation daysim_intgain.csv")

        hea_file.close()
        self.hea_file_path = hea_file_path
        
    def _create_bat_file(self, settings_dict):

        daysim_bat_file_path = os.path.join(self.data_folder_path, "run_daysim.bat")
        daysim_bat_file = open(daysim_bat_file_path, "w")
        daysim_bat_file.write("epw2wea " 
            + os.path.join(self.data_folder_path, self.epw_file_name) + " " 
            + os.path.join(self.data_folder_path, self.wea_file_name) + "\n")
        daysim_bat_file.write("radfiles2daysim " + self.hea_file_path + " -m -g \n")
        daysim_bat_file.write("gen_dc " + self.hea_file_path + " -dif \n")
        daysim_bat_file.write("gen_dc " + self.hea_file_path + " -dir \n")
        daysim_bat_file.write("gen_dc " + self.hea_file_path + " -paste \n")
        daysim_bat_file.write("ds_illum " + self.hea_file_path + "\n")
        #daysim_bat_file.write("gen_directsunlight " + self.hea_file_path + "\n")
        daysim_bat_file.write("ds_el_lighting.exe " + self.hea_file_path + "\n")

        daysim_bat_file.close()
        self.daysim_bat_file_path = daysim_bat_file_path

    def execute_daysim(self, settings_dict):

        # make sure that the following files have been created
        # - hea file
        # - geometry rad file
        # - materials rad file
        # - sensor point file

        #TODO: check that northing is None
        
        #create all the required input files
        self._create_sensor_input_file()
        self._create_viewpoints_input_file()
        self._create_geometry_input_file()
        self._create_materials_input_file()
        self._create_hea_input_file(settings_dict)
        
        # create the bat file and execute it
        #print command + "\n\n\n"
        operating_sys = os.name
        if operating_sys == "posix":
            print "Your OS is not supported"
            return
        elif operating_sys == "nt":
            self._create_bat_file(settings_dict)

        # Execute the bat file
        os.system(self.daysim_bat_file_path)#EXECUTE!
        
    def read_results(self):
        result_file_path = os.path.join(self.data_folder_path, "daysim_autonomy.da")
        results_file = open(result_file_path, "r")
        results = results_file.readlines()
        
        autonomy_list = []        
        for result in results[2:]:
            autonomy  = int(result.split()[3])
            autonomy_list.append(autonomy)
        return autonomy_list
    
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
             
    def set_surfaces(self, surfaces):
        self.surfaces = surfaces
        
    def append_surface(self, surface):
        self.surfaces.append(surface)
             
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
        shutil.copy(cal_file_path, self.data_folder_path)
        self.cal_file_name = os.path.basename(cal_file_path)
        
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
                rad_data = surface.to_str()
            else:
                rad_data = surface.to_str(interior = False)
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
    
    


