import os
import ctypes
import subprocess
import platform
# --------------------------------------------------------------------------------
# SetEnv tool
# --------------------------------------------------------------------------------
#http://www.codeproject.com/Articles/12153/SetEnv

# --------------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------------
def run_setenv(*args):
    args = ['SetEnv'] + list(args)
    p = subprocess.Popen(
        args, 
        shell=False, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.STDOUT)
    for line in p.stdout.readlines():
        print "    ", line,
    retval = p.wait()    

def fix_path(path):
    path = os.path.expandvars(path)
    path = os.path.normcase(path)
    #I found that if there is a ~ in the path, it does not work
    #http://stackoverflow.com/questions/2738473/compare-two-windows-paths-one-containing-tilde-in-python
    if "~" in path:
        path = unicode(path)
        GetLongPathName = ctypes.windll.kernel32.GetLongPathNameW
        buffer = ctypes.create_unicode_buffer(GetLongPathName(path, 0, 0))
        GetLongPathName(path, buffer, len(buffer))
        path = buffer.value
    return path

def setenv_add_values(name, values, are_paths=True, prepend=True):
    name = name.upper()
    if type(values) == str:
        values = [values]
    if are_paths:
        values = [fix_path(i) for i in values]
    for value in values:
        if prepend:
            run_setenv('-uap', name, '%' + value)
        else:
            run_setenv('-ua', name, '%' + value)
        print
        print "Added '" + value + "'"
        print "to the '" + name + "' environment variable."
        
def setenv_del_variable(name):
    name = name.upper()
    run_setenv('-ud', name)
    print 
    print "Deleted '" + name + "' environment variable."

def setenv_del_matches(name, matches):
    name = name.upper()
    if type(matches) == str:
        matches = [matches]
    existing_values = os.getenv(name)
    if existing_values:
        existing_values = existing_values.split(";")
    else:
        existing_values = []
    for match in matches:
        for existing_value in existing_values:
            if match.lower() in existing_value.lower():
                run_setenv('-ud', name, '%' + existing_value)
                print 
                print "Deleted '" + existing_value + "'"
                print "from the '" + name + "' environment variable."

# --------------------------------------------------------------------------------
# MAIN SCRIPT
# --------------------------------------------------------------------------------
def main():
    # --------------------------------------------------------------------------------
    # Get paths
    # --------------------------------------------------------------------------------

    current_dir =  os.path.split(os.getcwd())[0] #go back one dir
    platform_type = platform.architecture()[0]

    # --------------------------------------------------------------------------------
    # Set up Houdarcs paths
    # --------------------------------------------------------------------------------

    #add binary libs
    setenv_del_matches("PATH", "houdarcs")
    if platform_type == "32bit":
        lib_bin_dir_2 = current_dir + "\\bin_win_libs_32bit"
    else:
        lib_bin_dir_2 = current_dir + "\\bin_win_libs_64bit"
    setenv_add_values("PATH", lib_bin_dir_2)

    #set PYTHONPATH
    setenv_del_matches("PYTHONPATH", "houdarcs")
    setenv_add_values("PYTHONPATH", current_dir + "\\python_libs")

    #set HOUDINI_OTLSCAN_PATH
    setenv_del_matches("HOUDINI_OTLSCAN_PATH", "houdarcs")
    setenv_add_values("HOUDINI_OTLSCAN_PATH", "&", are_paths=False)
    setenv_add_values("HOUDINI_OTLSCAN_PATH", current_dir + "\\otls")

    # --------------------------------------------------------------------------------

main()