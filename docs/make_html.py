import sys
import os
import subprocess
import webbrowser

python_exec = sys.executable
python_folder = os.path.dirname(python_exec)

my_env = os.environ.copy()
my_env["PATH"] = python_folder + os.pathsep + \
                 os.path.join(python_folder, "Scripts") + os.pathsep + \
                 my_env["PATH"]

cwd = os.path.abspath(os.path.dirname(__file__))

subprocess.run(['make.bat', 'html'], shell=True, env=my_env, cwd=cwd)

index_path = os.path.join(cwd, "_build", "html", "index.html")
webbrowser.open_new_tab('file://%s' % index_path)
