# ML-MAID : ML - Miniature Automatic Installer for Dependencies
<center>
<img src='banner.svg'/>
</center>

- Install dependencies without having to issue a zillion `pip install` commands.
- Re-implement ML-Maid compliant workflows and repositories without a sweat.
- No need to use Conda and Docker unless you really have to.
- Requirement files don't solve the problem.
- Setup CUDA automatically. <img src='https://img.shields.io/badge/pending-red'/> 

## Why ML MAID ?
ML Maid aimed to be a complete and unique tool that aims to automatically install dependencies in Python with specific focus on ML environments. It aims to solve the problem of environment re-creation from old code without the hassle of manually building docker containers unless really required. The idea behind ML-Maid is to implicitly enforce checks to keep the environment setup as simple as possible, so that it is easy to replicate. It also aims to completely automate the environment replication process. It aims to keep the environment simple starting from the production phase of the software life-cycle to save developer time. 

## Is ML-Maid a Replacement for Docker / Conda / Python Venv : NO
ML Maid aims to automate the use of tools like Docker / Conda / Python venv **without adding any additional complexity** so that the developer can focus on writing code.

## Usage
⚫ In your main Python script add the following to automatically install / check the dependencies before any other code is run:
```python
from mlmaid import install
install(script_path=__file__, python_version='3.10.12', sys_reqs=['cuda==11.8'])
```
(Change Python version and cuda version according to your requirements)

⚫ Import your modules
```python
import my_local_module # local_module
from PIL import Image # pillow==1.0.2
```
- Add the `# local_module` tag to modules that are local imports
- If a module's import name is different from its installation name, just add the installation name as a comment
- By default the latest version of all (non-local) modules will be installed, if you want a specific version, specify it as a comment after import statement. like : `import PIL # pillow==1.0.2`

⚫ Install ML-Maid
In your system Python3, just install ML-Maid once. **After this you probably wont need to install any other Python library again! 🥳🥳**
```bash
pip3 install mlmaid
```

⚫ Run Your Code in System Python3
```bash
python3 my_python_script.py
```
The above will automatically create a python venv with all the packages. It will also make your script executable.
Now, you can simply run your program with fully configured python venv using command:
```bash
./my_python_script.py
```

Enjoy!


