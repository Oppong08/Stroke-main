import os
import subprocess
import sys

def run_command(command):
    subprocess.run(command, shell=True, check=True)

def main():
    # Create virtual environment
    print("Creating virtual environment...")
    run_command("python -m venv venv")
    
    # Activate virtual environment
    if sys.platform == "win32":
        run_command(".\\venv\\Scripts\\activate")
    else:
        run_command("source venv/bin/activate")
    
    # Install requirements
    print("Installing requirements...")
    run_command("pip install -r requirements.txt")
    
    # Create Django project
    print("Creating Django project...")
    run_command("django-admin startproject stroke_unit_system .")
    
    # Create Django app
    print("Creating Django app...")
    run_command("python manage.py startapp patientsystem")

if __name__ == "__main__":
    main() 