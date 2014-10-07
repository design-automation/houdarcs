# Functions for writing EnergyPlus (IDF) input files

# ================================================================================
def write_surface(
        name, 
        type,
        construction, 
        zone, 
        boundary,
        boundary_object, 
        sun_exp, 
        wind_exp, 
        points): # list of lists with three numbers

    surface ="! ==== BUILDING SURFACE\n" +\
    "BuildingSurface:Detailed,\n"+\
    "  "+name+",\n" +\
    "  "+type+",\n" +\
    "  "+construction+",\n" +\
    "  "+zone+",\n" +\
    "  "+boundary+",\n" +\
    "  "+boundary_object+",\n" +\
    "  "+sun_exp+",\n" +\
    "  "+wind_exp+",\n" +\
    "  autocalculate,\n"+\
    "  "+str(len(points))+",\n"
    for counter in range(len(points)):
        point = points[counter]
        text_point = str(point[0])+","+str(point[1])+","+str(point[2])
        if counter < len(points)-1:
            surface = surface + "  "+text_point+",\n"
        else:
            surface = surface + "  "+text_point+";\n\n"
    return surface

# ================================================================================
def write_window(
        name, 
        construction, 
        surface,
        shading,
        frame,
        points):

    window ="! ==== WINDOW\n"+\
    "FenestrationSurface:Detailed,\n"+\
    "  "+name+",\n"+\
    "  Window,\n"+\
    "  "+construction+",\n"+\
    "  "+surface+",\n"+\
    "  ,\n"+\
    "  autocalculate,\n"+\
    "  "+shading+",\n"+\
    "  "+frame+",\n"+\
    "  1.0,\n"+\
    "  "+str(len(points))+",\n"
    for counter in range(len(points)):
        point = points[counter]
        text_point = str(point[0])+","+str(point[1])+","+str(point[2])
        if counter < len(points)-1:
            window = window + "  "+text_point+",\n"
        else:
            window = window + "  "+text_point+";\n\n" 
    return window

# ================================================================================
def write_building_shade(
        name, 
        transmittance, 
        points):
    
    building_shade ="! ==== BUILDING SHADE\n"+\
    "Shading:Building:Detailed,\n"+\
    "  "+name+",\n"+\
    "  "+transmittance+",\n"+\
    "  "+str(len(points))+",\n"
    for counter in range(len(points)):
        point = points[counter]
        text_point = str(point[0])+","+str(point[1])+","+str(point[2])
        if counter < len(points)-1:
            building_shade = building_shade + "  "+text_point+",\n" 
        else:
            building_shade = building_shade + "  "+text_point+";\n\n" 
    return building_shade

# ================================================================================
def write_shadingoverhang(
        name,
        window_name,
        height_above_window,
        tilt_angle,
        left_extension,
        right_extension,
        depth):
    
    overhang = "! ==== SHADING OVERHANG\n\n"+\
    "Shading:Overhang,\n"+\
    "    " + name + ",\n"+\
    "    " + window_name + ",\n"+\
    "    " + height_above_window + ",\n"+\
    "    " + tilt_angle+ ",\n"+\
    "    " + left_extension+ ",\n"+\
    "    " + right_extension + ",\n"+\
    "    " + depth + ";\n\n"
    return overhang

# ================================================================================
def write_zone(name):
    
    zone = "! ==== BUILDING ZONE\n"+\
    "Zone,\n"+\
    "  "+name+",\n"+\
    "  0,\n"+\
    "  0, 0, 0, \n"+\
    "  1,\n"+\
    "  1,\n"+\
    "  autocalculate,\n"+\
    "  autocalculate;\n\n"
    return zone 

# ================================================================================
def write_zone_shade(
        name, 
        base_surface, 
        transmittance, 
        points):

    zone_shade ="! ==== SHADING ZONE DETAILED\n"+\
    "Shading:Zone:Detailed,\n"+\
    "    "+name+",\n"+\
    "    "+base_surface+",\n"+\
    "    "+transmittance+",\n"+\
    "    "+str(len(points))+",\n"
    for counter in range(len(points)):
        point = points[counter]
        text_point = str(point[0])+","+str(point[1])+","+str(point[2])
        if counter < len(points)-1:
            zone_shade = zone_shade + "    "+text_point+",\n" 
        else:
            zone_shade = zone_shade + "    "+text_point+";\n\n" 
    return zone_shade

# ================================================================================
def write_hvac_ideal_load_air_system(
        zone_name,
        thermostat):
    
    hvac = "! ==== ZONE PURCHASED AIR\n"+\
    "HVACTemplate:Zone:IdealLoadsAirSystem,\n"+\
    "    "+zone_name+",\n"+\
    "    "+thermostat + ";\n\n"
        
    return hvac
    
# ================================================================================

def write_people_by_area(
        zone_name,
        area_per_person,
        area_schedule_name,
        activity_schedule_name,
        work_schedule_name,
        clothing_schedule_name,
        air_schedule_name):
    
    people = "! ==== PEOPLE\n" +\
    "People,\n"+\
    "    "+zone_name+"_people_by_area,\n"+\
    "    "+zone_name+",\n"+\
    "    "+area_schedule_name +",\n"+\
    "    Area/Person,\n"+\
    "    ,\n"+\
    "    ,\n"+\
    "    "+area_per_person+",\n"+\
    "    0.3,\n"+\
    "    autocalculate,\n"+\
    "    "+activity_schedule_name +",\n"+\
    "    ,\n"+\
    "    No,\n"+\
    "    ZoneAveraged,\n"+\
    "    ,\n"+\
    "    "+work_schedule_name +",\n"+\
    "    "+clothing_schedule_name +",\n"+\
    "    "+air_schedule_name +",\n"+\
    "    FANGER;\n\n"
        
    return people
    
        
# ================================================================================
def write_zone_infiltration(
        zone_name,
        schedule_name,
        ach):
        
    other_equipment = "! ====  ZONE INFILTRATION: DESIGN FLOW RATE\n" +\
    "ZoneInfiltration:DesignFlowRate,\n"+\
    "    "+zone_name+"_zone_infiltration,\n"+\
    "    "+zone_name+",\n"+\
    "    "+schedule_name +",\n"+\
    "    AirChanges/Hour,\n"+\
    "    ,\n"+\
    "    ,\n"+\
    "    ,\n"+\
    "    "+ach+",\n"+\
    "    ,\n"+\
    "    ,\n"+\
    "    ,\n"+\
    "    ;\n\n"
        
    return other_equipment
# ================================================================================
def write_internal_gains_other_equipment(
        zone_name,
        schedule_name,
        watts_per_m2):
        
    other_equipment = "! ==== INTERNAL GAINS OTHER EQUIPMENT\n" +\
    "OtherEquipment,\n"+\
    "    "+zone_name+"_internal_gains_oe,\n"+\
    "    "+zone_name+",\n"+\
    "    "+schedule_name +",\n"+\
    "    Watts/Area,\n"+\
    "    ,\n"+\
    "    "+watts_per_m2+",\n"+\
    "    ,\n"+\
    "    0.0,\n"+\
    "    0.3,\n"+\
    "    0.0;\n\n"
        
    return other_equipment
    
# ================================================================================
def write_internal_gains_electric_equipment(
        zone_name,
        schedule_name,
        watts_per_m2):
        
    electric_equipment = "! ==== INTERNAL GAINS OTHER EQUIPMENT\n" +\
    "ElectricEquipment,\n"+\
    "    "+zone_name+"_internal_gains_ee,\n"+\
    "    "+zone_name+",\n"+\
    "    "+schedule_name +",\n"+\
    "    Watts/Area,\n"+\
    "    ,\n"+\
    "    "+watts_per_m2+",\n"+\
    "    ,\n"+\
    "    0.0,\n"+\
    "    0.3,\n"+\
    "    0.0;\n\n"
        
    return electric_equipment
# ================================================================================
def write_version(version):
    
    version_str = "! ==== VERSION\n" +\
    "Version,"+version+";\n\n"
    
    return version_str
    
# ================================================================================
def write_time_step(time_step):
    
    time_step_str = "! ==== TIME STEP\n" +\
    "Timestep,"+time_step+";\n\n"
    
    return time_step_str
    
# ================================================================================
def write_ground_temp_bldg_srf(ground_temp):
    
    ground_temp_str = "! ==== GROUND TEMP\n" +\
    "Site:GroundTemperature:BuildingSurface,"+','.join(ground_temp)+";\n\n"
    
    return ground_temp_str
    
# ================================================================================
def write_shadow_calc(calc_frequency, max_figures):
    
    shadow_calc_str = "! ==== SHADOW CALCULATION\n" +\
    "ShadowCalculation,"+calc_frequency+","+max_figures+";\n\n"
    
    return shadow_calc_str
    
# ================================================================================
def write_building(
    terrain,
    solar_dist,
    max_warmup_days):
    
    building = "! ==== BUILDING\n" +\
    "Building,\n" +\
    "    Building,\n"+\
    "    0,\n" +\
    "    "+terrain+",\n"+\
    "    0.04,\n"+\
    "    0.4,\n"+\
    "    "+solar_dist+",\n"+\
    "    "+max_warmup_days+";\n\n"
    
    return building

# ================================================================================
def write_runperiod(
    start_month,
    start_day,
    end_month,
    end_day):
    
    runperiod = "! ==== RUN PERIOD\n" +\
    "RunPeriod,\n"+\
    "    ,\n"+\
    "    " + start_month + ",\n"+\
    "    " + start_day + ",\n"+\
    "    " + end_month + ",\n"+\
    "    " + end_day + ",\n"+\
    "    UseWeatherFile,\n"+\
    "    Yes,\n"+\
    "    Yes,\n"+\
    "    No,\n"+\
    "    Yes,\n"+\
    "    Yes;\n\n"
    
    return runperiod

# ================================================================================
def write_schedule_type_limits(
    name,
    lower_limit,
    upper_limit,
    numeric_type,
    unit_type):
    
    schedule_type_limits = "! ==== SCHEDULE TYPE LIMITS\n" +\
    "ScheduleTypeLimits,\n"+\
    "    " + name + ",\n"+\
    "    " + lower_limit + ",\n"+\
    "    " + upper_limit + ",\n"+\
    "    " + numeric_type + ",\n"+\
    "    " + unit_type + ";\n\n"
    
    return schedule_type_limits
# ================================================================================

def write_constant_schedule(
    name,
    sch_type_limits_name,
    value):
    
    sch_str  = "! ==== SCHEDULE COMPACT CONSTANT\n"

    sch_str = sch_str + "Schedule:Compact,\n" +\
    "    " + name + ",\n"+\
    "    " + sch_type_limits_name + ",\n"+\
    "    Through: 12/31,\n"+\
    "    For: AllDays,\n"+\
    "    Until: 24:00,"+value+";\n\n"

    return sch_str
# ================================================================================
def write_hvacschedule(
    name,
    sch_type_limits_name,
    day_start_time,
    day_end_time,
    setpoint_day,
    setpoint_night):
    
    hvac_sch_str  = "! ==== SCHEDULE COMPACT (HVAC)\n"
    if day_start_time != "0:00" and day_end_time == "24:00":
        hvac_sch_str = hvac_sch_str + "Schedule:Compact,\n" +\
         "    " + name + ",\n"+\
         "    " + sch_type_limits_name + ",\n"+\
         "    Through: 12/31,\n"+\
         "    For: AllDays,\n"+\
         "    Until:" + day_start_time + ", " + setpoint_night + ",\n"+\
         "    Until:" + day_end_time + ", " + setpoint_day + ";\n\n"
         
    elif day_start_time == "0:00" and day_end_time == "24:00":
        hvac_sch_str = hvac_sch_str + "Schedule:Compact,\n" +\
         "    " + name + ",\n"+\
         "    " + sch_type_limits_name + ",\n"+\
         "    Through: 12/31,\n"+\
         "    For: AllDays,\n"+\
         "    Until: 24:00, " + setpoint_day + ";\n\n"
    else:
        hvac_sch_str = hvac_sch_str + "Schedule:Compact,\n" +\
         "    " + name + ",\n"+\
         "    " + sch_type_limits_name + ",\n"+\
         "    Through: 12/31,\n"+\
         "    For: AllDays,\n"+\
         "    Until:" + day_start_time + ", " + setpoint_night + ",\n"+\
         "    Until:" + day_end_time + ", " + setpoint_day + ",\n"+\
         "    Until: 24:00, " + setpoint_night + ";\n\n"
     
    return hvac_sch_str

# ================================================================================
def write_alldays_schedule(
    name,
    sch_type_limits_name,
    start,
    end):
    
    sch_str  = "! ==== SCHEDULE COMPACT\n"
    if end == "24:00":
        sch_str = sch_str + "Schedule:Compact,\n" +\
        "    " + name + ",\n"+\
        "    " + sch_type_limits_name + ",\n"+\
        "    Through: 12/31,\n"+\
        "    For: AllDays,\n"+\
        "    Until:" + start + ", 0,\n"+\
        "    Until:" + end + ", 1;\n\n"
    else:
        sch_str = sch_str + "Schedule:Compact,\n" +\
        "    " + name + ",\n"+\
        "    " + sch_type_limits_name + ",\n"+\
        "    Through: 12/31,\n"+\
        "    For: AllDays,\n"+\
        "    Until:" + start + ", 0,\n"+\
        "    Until:" + end + ", 1,\n"+\
        "    Until: 24:00, 0;\n\n"
    return sch_str

# ================================================================================
def write_thermostat(
    name,
    heat_sch,
    cool_sch):
    
    thermostat_str = "! ==== THERMOSTAT\n" +\
    "HVACTemplate:Thermostat,\n" +\
    "    " + name + ",\n"+\
    "    " + heat_sch + ",\n"+\
    "    ,\n"+\
    "    " + cool_sch + ",\n"+\
    "    ;\n\n"
     
    return thermostat_str
    
# ================================================================================
def write_outputvar(variable_name, report_frequency):
    return "! ==== OUTPUT VARIABLE\n" +\
    "Output:Variable,*," + variable_name + " ," + report_frequency + ";\n\n"

# ================================================================================
def write_outputmeter(variable_name, report_frequency):
    return "! ==== OUTPUT METER\n" +\
    "Output:Meter," + variable_name + " ," + report_frequency + ";\n\n"

# ================================================================================
def write_output_surfaces_drawing(drawing_type):
    return "! ==== OUTPUT SURFACES DRAWING\n" +\
    "Output:Surfaces:Drawing," + drawing_type + ";\n\n"

# ================================================================================
def write_output_control_table_style(column_sep, unit_conversion):
    return "! ==== OUTPUT CONTROL TABLE STYLE\n" +\
    "OutputControl:Table:Style," + column_sep + " ," + unit_conversion + ";\n\n"

# ================================================================================
def write_output_table_summary_reports(report_types):
    reports_str = "! ==== OUTPUT TABLE SUMMARY REPORTS\n"
    if isinstance(report_types, str):
        return reports_str +\
        "Output:Table:SummaryReports," + report_types + ";\n\n"
    elif isinstance(report_types, list) or isinstance(report_types, tuple):
        return reports_str +\
        "Output:Table:SummaryReports," + " ,".join(report_types) + ";\n\n"

# ================================================================================
def write_electric_load_centre_distribution(
    name, 
    generator_list_name,
    generator_op_scheme_type,
    demand_limit_scheme,
    track_sch_name,
    track_meter_name,
    electric_buss_type,
    inverter_obj_name,
    electrical_obj_name,
    transformer_obj_name
    ):

    distribution_str = "! ==== ELECTRICAL LOAD CENTRE DISTRIBUTION\n" +\
    "ElectricLoadCenter:Distribution,\n" +\
    "    " + name + ",\n"+\
    "    " + generator_list_name + ",\n"+\
    "    " + generator_op_scheme_type + ",\n"+\
    "    " + demand_limit_scheme + ",\n"+\
    "    " + track_sch_name + ",\n"+\
    "    " + track_meter_name + ",\n"+\
    "    " + electric_buss_type + ",\n"+\
    "    " + inverter_obj_name + ",\n"+\
    "    " + electrical_obj_name + ",\n"+\
    "    " + transformer_obj_name + ";\n\n"
     
    return distribution_str

# ================================================================================
def write_electric_load_centre_inverter_simple(
    name, 
    sch_name,
    zone_name,
    radiative_frac,
    inverter_freq
    ):

    inverter_str = "! ==== ELECTRICAL LOAD CENTRE INVERTER SIMPLE \n" +\
    "ElectricLoadCenter:Inverter:Simple,\n" +\
    "    " + name + ",\n"+\
    "    " + sch_name + ",\n"+\
    "    " + zone_name + ",\n"+\
    "    " + radiative_frac + ",\n"+\
    "    " + inverter_freq + ";\n\n"
     
    return inverter_str
# ================================================================================
def write_photovoltaic_performance_simple(
    name, 
    srf_frac,
    input_mode,
    efficiency,
    efficiency_sch_name
    ):

    photovoltaic_str = "! ==== PHOTOVOLTAIC PERFORMANCE SIMPLE \n" +\
    "PhotovoltaicPerformance:Simple,\n" +\
    "    " + name + ",\n"+\
    "    " + srf_frac + ",\n"+\
    "    " + input_mode + ",\n"+\
    "    " + efficiency + ",\n"+\
    "    " + efficiency_sch_name + ";\n\n"
     
    return photovoltaic_str
# ================================================================================
def write_generator_photovoltaic(
    name, 
    srf_name,
    pv_obj_type,
    module_name,
    heat_transfer_mode,
    num_modules_parallel,
    num_modules_serial
    ):

    generator_str = "! ==== GENERATOR PHOTOVOLTAIC \n" +\
    "Generator:Photovoltaic,\n" +\
    "    " + name + ",\n"+\
    "    " + srf_name + ",\n"+\
    "    " + pv_obj_type + ",\n"+\
    "    " + module_name + ",\n"+\
    "    " + heat_transfer_mode + ",\n"+\
    "    " + num_modules_parallel + ",\n"+\
    "    " + num_modules_serial + ";\n\n"
     
    return generator_str
    
# ================================================================================
def write_electrical_load_centre_generators(
    name, 
    generators_data
    ):

    electrical_str = "! ==== ELECTRICAL LOAD CENTRE GENERATORS \n" +\
    "ElectricLoadCenter:Generators,\n" +\
    "    " + name + ",\n"
    
    for i in generators_data:
        electrical_str = electrical_str +\
        "    " + i[0] + ",\n"+\
        "    " + i[1] + ",\n"+\
        "    " + i[2] + ",\n"+\
        "    " + i[3] + ",\n"+\
        "    " + i[4] + ",\n"
    electrical_str = electrical_str[:-2] + ";\n\n"
     
    return electrical_str
# ================================================================================
def write_light(
    name, 
    zone_name,
    sch_name,
    calc_method,
    light_level,
    watts_area,
    watts_person,
    return_air_fracs, # list of 4 strings
    end_use_subcat,
    return_air
    ):

    light_str = "! ==== LIGHTS ==== \n" +\
    "Lights,\n" +\
    "    " + name + ",\n"+\
    "    " + zone_name + ",\n"+\
    "    " + sch_name + ",\n"+\
    "    " + calc_method + ",\n"+\
    "    " + light_level + ",\n"+\
    "    " + watts_area + ",\n"+\
    "    " + watts_person    + ",\n"+\
    "    " + return_air_fracs[0]    + ",\n"+\
    "    " + return_air_fracs[1]    + ",\n"+\
    "    " + return_air_fracs[2]    + ",\n"+\
    "    " + return_air_fracs[3]    + ",\n"+\
    "    " + end_use_subcat    + ",\n"+\
    "    " + return_air    + ";\n\n" 
     
    return light_str
# ================================================================================
def write_daylight_control(
    name, 
    num_points, #integer
    points,# list of list of 3 numbers
    frac_controls, #list of two strings
    illum_setpoints, #list of two strings
    control_type,
    glare_azimuth,
    glare_index,
    dimming_fracs,#list of two strings
    num_steps,
    reset_prob
    ):
    
    if num_points == 1:
        text_point_1 = str(points[0][0])+","+str(points[0][1])+","+str(points[0][2])
        text_point_2 = "0,0,0"
    else:
        text_point_1 = str(points[0][0])+","+str(points[0][1])+","+str(points[0][2])
        text_point_2 = str(points[1][0])+","+str(points[1][1])+","+str(points[1][2])

    control_str = "! ==== DAYLIGHT CONTROLS \n" +\
    "Daylighting:Controls,\n" +\
    "    " + name + ",\n"+\
    "    " + str(num_points) + ",\n"+\
    "    " + text_point_1 + ",\n"+\
    "    " + text_point_2 + ",\n"+\
    "    " + frac_controls[0] + ",\n"+\
    "    " + frac_controls[1] + ",\n"+\
    "    " + illum_setpoints[0] + ",\n"+\
    "    " + illum_setpoints[1] + ",\n"+\
    "    " + control_type + ",\n"+\
    "    " + glare_azimuth + ",\n"+\
    "    " + glare_index + ",\n"+\
    "    " + dimming_fracs[0] + ",\n"+\
    "    " + dimming_fracs[1] + ",\n"+\
    "    " + num_steps + ",\n"+\
    "    " + reset_prob + ";\n\n"
     
    return control_str
# ================================================================================