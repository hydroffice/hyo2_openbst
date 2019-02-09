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

subprocess.run(['make.bat', 'latex'], shell=True, env=my_env, cwd=cwd)

miktex_bin_path = os.path.join(os.environ["ProgramFiles"], "MiKTeX 2.9", "miktex", "bin", "x64")
if not os.path.exists(miktex_bin_path):
    print("unable to locate: %s" % miktex_bin_path)
    miktex_bin_path = os.path.join(os.environ["LOCALAPPDATA"], "Programs", "MiKTeX 2.9", "miktex", "bin", "x64")
    if not os.path.exists(miktex_bin_path):
        print("unable to locate: %s" % miktex_bin_path)
        exit(-1)

my_env["PATH"] = miktex_bin_path + os.pathsep + my_env["PATH"]

latex_cwd = os.path.join(cwd, "_build", "latex")
latex_path = os.path.join(latex_cwd, "HydrOfficeOpenBST.tex")
subprocess.run(['pdflatex', latex_path], shell=True, env=my_env, cwd=latex_cwd)

pdf_path = os.path.join(latex_cwd, "HydrOfficeOpenBST.pdf")
webbrowser.open_new('file://%s' % pdf_path)
