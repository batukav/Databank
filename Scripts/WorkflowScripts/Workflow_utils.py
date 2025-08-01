import subprocess
import sys
import os

"""
Contains methods used for python scripts related to workflows.

.. note::
   This module is only used by automated workflows. Users of the Databank
   repository can safely ignore it.
"""

def run_command(command, error_message="Command failed", working_dir=None):
    """
    Run a shell command and exit on failure.

    :param command: The shell command to execute (string).
    :param error_message: Message to display if the command fails.
    :param working_dir: Optional working directory in which to run the command.
    :raises SystemExit: Exits with code 1 if the command fails.
    """
    try:
        subprocess.run(command, shell=True, check=True, cwd=working_dir)
    except subprocess.CalledProcessError:
        print(error_message)
        sys.exit(1)

def run_python_script(script_path, args=None, error_message="Python script failed", working_dir=None):
    """
    Execute a Python script with the current interpreter and optional arguments.

    :param script_path: Path to the Python script to run.
    :param args: List of arguments to pass to the script (defaults to []).
    :param error_message: Message to display if execution fails.
    :param working_dir: Optional working directory in which to run the script.
    :raises SystemExit: Exits with code 1 if the script execution fails.
    """
    if args is None:
        args = []
    try:
        subprocess.run(
            [sys.executable, script_path, *args],
            check=True,
            cwd=working_dir  
        )
    except subprocess.CalledProcessError:
        print(error_message)
        sys.exit(1)

def get_databank_paths(NMLDB_ROOT_PATH):
    """
    Retrieve relevant paths from databank.

    :param NMLDB_ROOT_PATH: Root path of the database repository.
    :return: Dictionary mapping descriptive keys to full paths of databank components.
    :rtype: dict
    """
    Builddatabank_path = os.path.join(NMLDB_ROOT_PATH, "Scripts", "BuildDatabank")
    AddData_path = os.path.join(Builddatabank_path, "AddData.py")
    AnalyzeDatabank_path = os.path.join(NMLDB_ROOT_PATH, "Scripts", "AnalyzeDatabank")
    calcProperties_path = os.path.join(AnalyzeDatabank_path, "calcProperties.sh")
    searchDATABANK_path = os.path.join(Builddatabank_path, "searchDATABANK.py")
    QualityEvaluation_path = os.path.join(Builddatabank_path, "QualityEvaluation.py")
    makeRanking_path = os.path.join(Builddatabank_path, "makeRanking.py")

    return {
        "Builddatabank_path": Builddatabank_path,
        "AddData_path": AddData_path,
        "AnalyzeDatabank_path": AnalyzeDatabank_path,
        "calcProperties_path": calcProperties_path,
        "searchDATABANK_path": searchDATABANK_path,
        "QualityEvaluation_path": QualityEvaluation_path,
        "makeRanking_path": makeRanking_path
    }
            
def delete_info_file(info_file_path):
    """
    Delete an information file at the specified path, warning on failure.

    :param info_file_path: Path to the info file to be removed.
    :raises OSError: Prints a warning if the file cannot be deleted.
    """
    try:
        os.remove(info_file_path)
        print(f"Deleted info file: {info_file_path}")
    except OSError as e:
        print(f"Warning: could not delete {info_file_path}: {e}")
