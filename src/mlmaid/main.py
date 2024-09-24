
########################
#       ML MAID        #
# (Aakash Singh Bais)  #
#  Date : 1.7.2024     #
########################

"""
README

🟢 What I can currently do?
- Check Python version is correct.
- Automatically get imported modules list, install them one by one.

🟡 What more I need to do?
- Automatically make the Python venv for user. (Atleast guide the user on how to create the venv, for Linux and Windows)
- Have 2 modes : "dev" and "stable"
    - Save the module names and versions as environment.json.
    - If a person runs in stable mode, install exact module versions from environment.json to recreate the env.
- Automatically get the installation name of a package from its import name (for ex for PIL, import name is "pillow")

🔴 Issues :
    - Cannot handle import format : "import module1, module2, module3"
    - Remove the unpacked Python source files from the current dir after Python installation is complete
    - If possible add a relative path to the python executable in the shebang, rather than the absolute path.
"""

IGNORE_THESE_PKGS = [
                        'autoinstall_dependencies', # Self
                     ]
import subprocess, pkgutil, sys, os, platform, importlib, traceback


# Satisfy Self Dependencies
SELF_DEPENDENCIES = [
        'setuptools',
        'tabulate',
        'tqdm',
        'wheel', # This is not a self-dep but is an essential package
        ]

# Function to import module at the runtime 
#def dynamic_import(module): 
#    return importlib.import_module(module)

SELF_FILE_NAME = __file__.split('/')[-1]
tprint = print
tqdm = None
tabulate = None
ENV_HAS_CHANGED = False
STDLIB_PKGS = []
INSTALLED_PKGS = {}

def get_cwd():
    script_directory = os.path.dirname(os.path.abspath(__file__))
    return script_directory

def get_python_version(python_executable_path:str):
    try:
        # Run the python executable with the --version argument
        result = subprocess.run([python_executable_path, '--version'], capture_output=True, text=True, check=True)
        # Extract the version string from the output
        version_string = result.stdout.strip()
        if not version_string:
            version_string = result.stderr.strip()
        if 'python' in version_string.lower():
            version_string = version_string.lower().replace('python', '').strip()
        return version_string
    except subprocess.CalledProcessError as e:
        print("Error occurred: ", e)
        exit()
        return None

def sanitize_module_name(module_name:str):
    if ',' in module_name:
        module_name = module_name.replace(',', '')
    return module_name

def install_self_dependencies():
    global tprint, tqdm, tabulate
    try:
        import subprocess
    except:
        print(SELF_FILE_NAME, " : Installing self-dependency : subprocess.")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', "subprocess"])
        import subprocess
    print(SELF_FILE_NAME + " : Imported : subprocess")
    import pkg_resources # Depends on setuptools (pip install setuptools)

    try:
        import tabulate
    except:
        print(SELF_FILE_NAME + " : Installing self-dependency : tabulate.")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', "tabulate"])
        import tabulate
    print(SELF_FILE_NAME + " : Imported : tabulate")

    try:
        import tqdm
    except:
        print(SELF_FILE_NAME + " : Installing self-dependency : tqdm.")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', "tqdm"])
        import tqdm
    print(SELF_FILE_NAME + " : Imported : tqdm")

    tprint = tqdm.tqdm.write

    try:
        import wheel
    except:
        print(SELF_FILE_NAME + " : Installing essential package : wheel")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'wheel'])
        print(SELF_FILE_NAME + " : Installed package wheel.")

"""
DESCRIPTION
-----------
This module reads all the Python files in a given folder, and attempts to automatically install all the 
imported modules.

NEED ? (Since modules can be installed via requirements.txt)
------
Why should I need to create a separate requirements.txt and complicate things?
I will put the requirements within the Python import statements (versions as a comment)
"""

def install_module_unit(module_name:str, version:str, env_type:str='system', executable_path:str='/usr/bin/python3', modules_path:str=''):
    """
    This function runs the module installation
    1. Module_versions = 
        - 'latest' : installs the latest version of the module
        - 'x.x.x' (anything else) : install module_name==anything_else
    2. Env type:
        - 'system' : executable_path = '/usr/bin/python3'
        - 'conda' : conda_path 
        - 'portable' : (appimage) executable_path = appimage executable path (module_path = custom, needs to be specified)
        - 'python_venv' : python_venv, executable path = python_venv_dir/bin/python3, modules_path = standard (we dont need to specify)
    """
    # Define the module specifier
    if version == '':
        return
    if version != 'latest':
        module_specifier = str(module_name) + "==" + str(version)
    else:
        module_specifier = module_name
    
    # Install the module_specifier
    if env_type in ['system', 'python_venv', 'conda']:    
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", module_specifier])
        except:
            tprint("✘ UNABLE : " + str(sys.executable) + " -m pip install " + str(module_specifier) + ". Skipping.")
    elif env_type == 'portable':
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", module_specifier, "--target=" + str(modules_path)])
        except:
            tprint("✘ UNABLE : " + str(sys.executable) + " -m pip install " + str(module_specifier) + " --target=" + str(modules_path) + ". Skipping.")
    tprint("[-->] Installed : " + str(module_name) + "==" + str(version))
    pass

def uninstall_module_unit(module_name:str, env_type:str='system', executable_path:str='/usr/bin/python3', modules_path:str=''):
    """
    This function uninstalls an existing module
    """
    if env_type in ['system', 'conda', 'python_venv']:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", module_name])
        except:
            tprint("✘ UNABLE : " + str(sys.executable) + " -m pip uninstall -y " + str(module_name) + ". Skipping.")
    elif env_type == 'portable':
        # Delete the module directory # TODO
        pass
    tprint("[<--] Uninstalled : "+ str(module_name))
    pass

def install_module_wrapper(module_name:str, version:str, is_installed:bool=False, version_is_right:bool=False):
    """
    This function decides whether to uninstall existing module.
    """
    global ENV_HAS_CHANGED
    if is_installed:
        if not version_is_right:
            if version == 'latest':
                tprint("[---] Module " + str(module_name) + " is installed. Ignoring. Current version : " + str(version))
                ENV_HAS_CHANGED = False
                return
            else:
                tprint("[info] Module " + str(module_name) + " is installed, version mismatch. Installing v" + str(version))
                # Uninstall the module
                uninstall_module_unit(module_name)
                # Install the right version of the module
                install_module_unit(module_name, version)
                ENV_HAS_CHANGED = True
    else: 
        # Install the module
        install_module_unit(module_name, version)
        ENV_HAS_CHANGED = True

    #tprint(f'Installing module : {module_name}={version}')
    pass

def get_stdlib_packages():
    global STDLIB_PKGS
    stdlib_packages = set()
    stdlib_dir = os.path.dirname(os.__file__)
    
    # Get using iter_modules
    for _, module_name, _ in pkgutil.iter_modules([stdlib_dir]):
        stdlib_packages.add(module_name)
    
    # Try getting modules using sys.stdlib_module_names (works only for Python > 3.10),
    # but is a better list and includes built-in modules like "time" not reported in the above
    directly_obtatined_modules = set()
    try:
        directly_obtatined_modules = set(sys.stdlib_module_names)
    except:
        tprint("Couldn't get modules names from sys.stdlib_module_names, you are probably running Python < 3.10. Skipping.")
    stdlib_packages = stdlib_packages.union(directly_obtatined_modules)
    STDLIB_PKGS = sorted(list(stdlib_packages))
    return STDLIB_PKGS

#def get_stdlib_packages():
#    stdlib_packages = set(module.name for module in pkgutil.iter_modules())
#    return sorted(stdlib_packages)

def get_installed_packages(env_type:str='system'):
    global INSTALLED_PKGS
    installed_pkgs = str(subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'])).split('\\n')[:-1]
    if len(installed_pkgs) >= 1:
        installed_pkgs[0] = installed_pkgs[0].split("b'")[-1]
    
    #tprint(installed_pkgs)

    installed_pkg_dict = {}
    for pkg in installed_pkgs:
        if '==' in pkg:
            installed_pkg_dict[pkg.split('==')[0]] = pkg.split('==')[1]
        elif ' @ ' in pkg: # locally installed pkg
            installed_pkg_dict[pkg.split(' @ ')[0]] = pkg.split(' @ ')[1] # This would add the location of the package into the dictionary key
    #tprint(installed_pkg_dict)        
    INSTALLED_PKGS = installed_pkg_dict
    return INSTALLED_PKGS

def module_exists(module_name:str, version:str='', env_type:str='system'):
    """
    Check the following:
        1. Module is installed?
        2. Right version is installed?

    Environment type:
        1. system : system installation of Python
        2. python-venv : python-venv virtual environment
        3. conda : conda environment
        4. portable : (appimage) python executable with modules installed in a custom directory
    """
    is_installed = False
    version_is_right = False
    if ENV_HAS_CHANGED:
        installed_pkg_dict = get_installed_packages(env_type)
    else:
        installed_pkg_dict = INSTALLED_PKGS # To save time
    if module_name in installed_pkg_dict.keys():
        is_installed = True
        if installed_pkg_dict[module_name] == version:
            version_is_right = True
    return is_installed, version_is_right

def get_modules(project_dir:str, env_type:str):
    """
    Read all Python files in the project_dir, get all imported modules
    Formats:
        1. from __ import __ # version==x.x.x
        2. import __ # version==x.x.x
        3. from __ import __ as __ # version==x.x.x
        4. import __ as __ # version==x.x.x
    NOTE:
        1. if a module's import name is not same as install name (for example PIL), import it as : from PIL import Image as im # pillow==x.x.x
        2. if an import is a local import, mark it with a local_import flag : import utils # local_import
    """
    modules_dict = {} # Will store module name and version

    # Get all Python files in the folder
    files = sorted([_ for _ in os.listdir(project_dir) if _.endswith('.py')])
    tprint('Found following Python files : ' + str(files))
    # Get all modules imported in the Python file
    for file in files:
        with open(os.path.join(project_dir, file), 'r') as _:
            file_contents = _.readlines()
        for line in file_contents:
            line = line.strip()
            line = line.replace('\n','')
            if not (line.startswith('from ') or line.startswith('import ')):
                continue
            # ELSE
            if line.startswith('from '):    
                keyword = 'from'
            else:
                keyword = 'import'
            module_name = line.split(' ')[line.split(' ').index(keyword) + 1].split('.')[0]
            version = ''
            if '#' in line:
                _ = line.split('#')[-1]
                if 'version==' in _:
                    version = _.split('version==')[-1]
                elif 'local_module' in _:
                    version = ''
                    module_name = ''
                elif '==' in _:
                    version = _.split('==')[-1].strip()
                    module_name = _.split('==')[0].strip()
                else:
                    version = 'latest'
            else:
                version = 'latest'
        
            module_name = sanitize_module_name(module_name)
            if module_name=='' or version=='' or module_name in IGNORE_THESE_PKGS:
                continue
            else: 
                if module_name not in modules_dict:
                    modules_dict[module_name] = version

    sorted_mods = sorted(list(modules_dict.keys()))
    mods_table = [[_+1, sorted_mods[_], modules_dict[sorted_mods[_]]] for _ in range(len(sorted_mods))]
    print(tabulate.tabulate(mods_table, headers=['Sn', 'Module', 'Version'], tablefmt='pretty'))
    tprint('\n')
    
    # Check if the right version of the module is installed, if not install the right version
    stdlib_packages = get_stdlib_packages()
    #tprint(stdlib_packages)
    for module in tqdm.tqdm(sorted(list(modules_dict.keys())), desc="Installing modules", colour="blue", position=0, leave=True):
        # Check if the package is a standard_lib package, if it is - ignore it
        if module in stdlib_packages:
            tprint("[---] Module " + str(module) + " is a standard lib package (ie part of Python installation), ignoring.")
            continue
        is_installed, version_is_right = module_exists(module_name=module, version=modules_dict[module])
        install_module_wrapper(module,  modules_dict[module], is_installed, version_is_right)
    
    return modules_dict

def custom_python_is_correct(python_version:str):
    assert len(python_version.split('.')) == 3, 'Python version provided {python_version} should have three version specifiers.'
    py_path = '/usr/local/bin/python' + '.'.join(python_version.split('.')[:2])
    if not os.path.isfile(py_path):
        return False
    try:
        # Run the python executable with the --version argument
        result = subprocess.run(['which', py_path], capture_output=True, text=True, check=True)
        # Extract the version string from the output
        command_output = result.stdout.strip()
        if not command_output:
            command_output = result.stderr.strip()
        #if 'python' in output.lower():
        #    output = output.lower().replace('python', '').strip()
    except subprocess.CalledProcessError as e:
        print("Error occurred: ", e)
        print(traceback.format_exc())
        exit()
        output = None
    is_correct = (command_output == py_path)
    tprint(is_correct, command_output)
    return is_correct

def is_file_with_root(file_path):
    try:
        # Run the 'test -f' command with sudo to check if the file exists
        tprint("Checking if directory exists using sudo, may require password... : sudo test -f " + str(file_path))
        result = subprocess.run(['sudo', 'test', '-f', file_path], check=True)
        #print(result, result.returncode == 0)
        return result.returncode == 0
    except subprocess.CalledProcessError:
        #print('Subprocess call error.')
        return False

def overwrite_shebang(file_path:str, new_shebang:str):
    """
    This function changes the shebang of the python file to point to the right executable
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Check if the first line is a shebang
    if lines[0].startswith('#!'):
        lines[0] = new_shebang + '\n'
        tprint("Changing the file shebang from " + str(lines[0]) + " to " + str(new_shebang))
    else:
        lines.insert(0, new_shebang + '\n')
        tprint("Adding fresh shebang to file : " + str(new_shebang))

    with open(file_path, 'w') as file:
        file.writelines(lines)

    # Make the script executable
    tprint('Making the script executable.')
    subprocess.check_call(['chmod', 'u+x', file_path])
    tprint('-----')
    tprint("Done. Now, directly execute the script. Command = \n" + str(file_path))
    tprint("If in the correct directory, just run : \n./" + str(file_path.split("/")[-1]))

def rebase_script_execution(script_path:str, venv_path:str):
    tprint('IMPORTANT : The python script {script_path} is now being rebased to the right venv {correct_venv_path}.')
    # Command to activate the virtual environment and run the new script
    command = "source " + str(os.path.join(venv_path, 'bin', 'activate')) + " && python " + str(script_path)

    # Run the command in a detached process
    subprocess.Popen(['bash', '-c', command],
                     stdout=None,  # Keep stdout as None to let it print to the current shell
                     stderr=None,  # Keep stderr as None to let it print to the current shell
                     preexec_fn=os.setpgrp)

def python_help(script_path:str, version_required:str='3.10.12'):
    #host_os = input('Please enter the host os : (linux / win)')
    if os.name == 'posix': # For unix like systems
        tprint("Unix like system detected. Running helper...")
        if len(version_required.split('.')) == 2 and version_required.split('.')[-1] != '': 
            if not input("NOTE\nThe following process will require your sudo password, but rest assured, your password will be used by your system shell directly.\nThis Python script cannot access it. Press y to continue.") == 'y':
                tprint('Aborting...')
                exit()
            input("\n(Step-1) Adding deadsnakes repo (needed to install python" + str(version_required) + ") : \nsudo add-apt-repository ppa:deadsnakes/ppa \n(press Enter, you will be asked for sudo password)")
            subprocess.check_call(['sudo', 'add-apt-repository', 'ppa:deadsnakes/ppa']) # Will ask for sudo passwords
            input("\n(Step-2) Running apt-update to update package list : \nsudo apt update\n(press Enter) ")
            try:
                subprocess.check_call(['sudo', 'apt', 'update'])
            except:
                tprint("Last command has some errors, which you can fix at your convenience. Ignoring errors in updating repos other than deadsnakes, continuing.")
            input("\n(Step-3) Installing Python " + str(version_required) + " : \nsudo apt install python" + str(version_required) + "\n(press Enter) ")
            subprocess.check_call(['sudo', 'apt', 'install', "python" + str(version_required)])
            input("\n(Step-4) Installing venv package : \nsudo apt install python" + str(version_required) + "-venv\n(press Enter) ")
            subprocess.check_call(['sudo', 'apt', 'install', "python" + str(version_required) + "-venv"])
        elif len(version_required.split('.')) == 3 and version_required.split('.')[-1] != '':
            """
            Do the following:
                1. Check if the python executable is present in /usr/local/bin, for example : /usr/local/bin/python-3.10
                2. If it is installed, check for venv, else install python at /usr/local/bin
                3. Once Python is installed, check if a venv is present in the current dir (venv folder name format : pyvenv_3.10.12).
                4. If a venv is present, change its Python executable symbolic link to the python just installed in /usr/local/bin. (change all 3 : bin/python, bin/python3, bin/python-3.10)
            """
            # Check if Python version is present in /usr/local/bin/ , for example /usr/local/bin/python3.10 : TODO , if not then install it from source
            py_path = "/usr/local/bin/python" + str(version_required.split(".")[0]) + "." + str(version_required.split(".")[1])
            
            if not (custom_python_is_correct(version_required) and get_python_version(py_path) == version_required):
                tprint("Python installation NOT found at " + str(py_path) + ". Attempting install...")

                #tprint('-----\nIf python venv exists, please manually create a symbolic by running "ln -s /usr/local/bin/python3.x my_venv_path/bin/python3" , else create python venv.\n-----')
                # Install Python version from source
                tprint("Installing Python " + str(version_required) + " from source...")
                command = '''
                sudo apt-get update
                sudo apt-get install -y \\
                build-essential \\
                libssl-dev \\
                zlib1g-dev \\
                libncurses5-dev \\
                libncursesw5-dev \\
                libreadline-dev \\
                libsqlite3-dev \\
                libgdbm-dev \\
                libdb5.3-dev \\
                libbz2-dev \\
                libexpat1-dev \\
                liblzma-dev \\
                tk-dev \\
                libffi-dev \\
                libgmp-dev \\
                wget
                '''
                input("Installing apt requirements : \n" + str(command) + "\n(press Enter, you may be asked for your sudo password)")
                os.system(command)
                input("Getting the Python " + str(version_required) + " source code : wget https://www.python.org/ftp/python/" + str(version_required) + "/Python-" + str(version_required) + ".tgz\n(press Enter)")
                subprocess.check_call(['wget', "https://www.python.org/ftp/python/" + str(version_required) + "/Python-" + str(version_required) + ".tgz"])
                input("Extracting source code tar... : \ntar -xvf Python-" + str(version_required) + ".tgz (press ENTER)")
                subprocess.check_call(['tar', '-xvf', "Python-" + str(version_required) + ".tgz"])
                command = \
                "\ncd Python-" + str(version_required) + \
                "\n./configure --enable-optimizations" + \
                "\nmake -j$(nproc)" + \
                "\nsudo make altinstall"
                
                input("Configuring and intalling : \n" + str(command) + " \n(press Enter) ")
                os.system(command)
                tprint('Python installation complete...')
                if version_required == get_python_version(py_path):
                    tprint("Installation verified, correct version installed.")
                else:
                    tprint("Verification UNSUCCESSFUL : " + str(version_required) + " (required) != " + str(get_python_version(py_path)) + " (installed). Please manually check installation : " + str(py_path))
                    exit()
            else:
                tprint("Correct python version already installed at : " + str(py_path))
            
            # Check if venv exists
            venv_path = os.path.join(os.getcwd(), "pyvenv_" + str(version_required))
            tprint("Checking if the venv is present at : " + str(venv_path))
            if not os.path.isdir(venv_path):
                tprint("Python venv not found at " + str(venv_path) + "... Creating a venv")
                tprint("Executing : " + str(py_path) + " -m venv " + str(venv_path))
                subprocess.check_call([py_path, '-m', 'venv', venv_path])
            else:
                tprint("Python venv already present.")
                tprint("TODO : Re-link symbolic links of the venv (" + str(venv_path) + " to the installation at " + str(py_path))
            
        # Re-run the Python script using the executable from the venv, terminate this script.
        #tprint('TODO : re-run the script from the binary available in venv.')
        #rebase_script_execution(script_path=script_path, venv_path=venv_path)
        overwrite_shebang(file_path=script_path, new_shebang="#!" + str(os.path.join(venv_path, "bin", "python")))
        exit()

    else: # For windows
        tprint("Windows OS detected. This is currently NOT supported. Exiting.")

def install_cuda():
    """
    This function does the following:
        1. Check if CUDA is available.
        2. If not, install the required version of CUDA toolkit.
        3. Add CUDA_HOME and LD_LIBRARY to bashrc / zshrc, export these variables via Python.
    """
    tprint('TODO : Install cuda. This function is in development. Please manually install CUDA.')
    # Check if cuda is available
    # Download CUDA runfile installer : URL format : https://developer.nvidia.com/cuda-11-8-0-download-archive?target_os=Linux&target_arch=x86_64&Distribution=Ubuntu&target_version=22.04&target_type=runfile_local
    # Install CUDA : Default install directory sample =  /usr/local/cuda-11.8/
        # To uninstall : To uninstall the CUDA Toolkit, run cuda-uninstaller in /usr/local/cuda-11.8/bin
    # Add CUDA_HOME and LD_LIBRARY env variables, export env variables from Python

    return 

def install_git():
    tprint('TODO : Install and setup git. This function is in development. Please manually install git.')
    return

def install(script_path:str, executable_path:str='/usr/bin/python3', modules_path:str='', env_type:str='', python_version:str='any', sys_reqs:list=[]) -> None:
    project_dir = '/'.join(script_path.split('/')[:-1])
    print("\n SETTING UP SYSTEM REQS")
    print("------------------------------\n")
    supported_sys_reqs = ['cuda', 'git']
    
    for sys_req in sys_reqs:
        if sys_req not in supported_sys_reqs:
            print("ERROR : " + str(sys_req) + " not supported. Support available for " + str(supported_sys_reqs))
        if sys_req == 'cuda':
            install_cuda()
        elif sys_req == 'git':
            install_git()

    print("\nSETTING UP PYTHON DEPENDENCIES")
    print("------------------------------\n")

    # Check if module is imported from interactive shell, if so then exit
    import __main__ as main
    if hasattr(main, '__file__'):
        # Check if module is imported from Jupyter NB
        # Check Python version
        if python_version == "any":
            print("INFO : Python version check bypassed, requirement = " + str(python_version))
            pass
        elif platform.python_version().startswith(python_version):
            # Check if the Python version matches current
            print("INFO : Correct Python version found : " + str(platform.python_version()) + ", expected : " + str(python_version) + "x")
            if str(sys.executable).startswith('/usr/bin/python'):
                print('..but, current python binary is system binary : ' + str(sys.executable) + '. Need to install separate binary.')
                python_help(version_required=python_version, script_path=script_path)
        else:
            print("ERROR : Wrong Python version found " + str(platform.python_version()) + ", expected : " + str(python_version) + "x")
            python_help(version_required=python_version, script_path=script_path)
        
        install_self_dependencies()

        # Check project  directory
        if not project_dir:
            raise Exception('Project directory NOT provided.')
        if modules_path == '':
            target_flag = ''
        else:
            target_flag = '--target=' + str(modules_path)
        
        # Get the modules_dict, install the modules
        modules_dict = get_modules(project_dir=project_dir, env_type=env_type)
    else:
        tprint("You seem to be running ML MAID from an interactive shell. Please use via Python script instead. This may also be cause by using the spawn start method in multiprocessing.")
    tprint('-'*5 + ' Module installation complete. ' + '-'*5 + '\n')
    return

if __name__ == '__main__':
    pass
