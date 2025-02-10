import os
import sys
import subprocess
import platform
import argparse
from pathlib import Path


def get_nuke_python():
    """Get the path to Nuke's Python executable"""
    system = platform.system()

    if system == "Windows":
        # Look for Nuke installations in Program Files
        program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
        nuke_dirs = [d for d in os.listdir(program_files) if d.startswith("Nuke")]

        if not nuke_dirs:
            raise RuntimeError("No Nuke installation found in Program Files")

        # Get latest version based on directory name
        latest_nuke = sorted(nuke_dirs)[-1]
        python_path = os.path.join(program_files, latest_nuke, "python.exe")

        if not os.path.exists(python_path):
            raise RuntimeError(f"Python not found in {python_path}")

        return python_path

    elif system == "Darwin":  # macOS
        # Common Nuke installation paths on macOS
        potential_paths = [
            "/Applications/Nuke*/python",
            "/opt/Nuke*/python"
        ]

        for path_pattern in potential_paths:
            from glob import glob
            matches = sorted(glob(path_pattern))
            if matches:
                return matches[-1]

        raise RuntimeError("No Nuke installation found on macOS")

    else:  # Linux
        # Common Nuke installation paths on Linux
        potential_paths = [
            "/usr/local/Nuke*/python",
            "/opt/Nuke*/python"
        ]

        for path_pattern in potential_paths:
            from glob import glob
            matches = sorted(glob(path_pattern))
            if matches:
                return matches[-1]

        raise RuntimeError("No Nuke installation found on Linux")


def install_dependencies():
    """Install required dependencies using Nuke's Python"""
    try:
        nuke_python = get_nuke_python()
        print(f"Using Nuke Python: {nuke_python}")

        # Create library directory if it doesn't exist
        lib_path = os.path.join(os.path.dirname(__file__), "library")
        os.makedirs(lib_path, exist_ok=True)

        # Core dependencies required for the tool
        dependencies = [
            "open3d",
            "numpy",
            "Pillow",
            "imageio",
            "opencv-python"
        ]

        # Optional development dependencies
        dev_dependencies = [
            "pytest",
            "pytest-qt",
            "pytest-cov",
            "black",
            "flake8"
        ]

        def install_package(package):
            try:
                print(f"Installing {package}...")
                subprocess.check_call([
                    nuke_python,
                    "-m", "pip",
                    "install",
                    "--target", lib_path,
                    package
                ])
                print(f"Successfully installed {package}")
            except subprocess.CalledProcessError as e:
                print(f"Error installing {package}: {e}")
                return False
            return True

        # Install core dependencies
        print("\nInstalling core dependencies...")
        for dep in dependencies:
            if not install_package(dep):
                print(f"Warning: Failed to install {dep}")

        # Install development dependencies if requested
        if "--dev" in sys.argv:
            print("\nInstalling development dependencies...")
            for dep in dev_dependencies:
                if not install_package(dep):
                    print(f"Warning: Failed to install development dependency {dep}")

        # Add library path to Python path
        if lib_path not in sys.path:
            sys.path.append(lib_path)

        print("\nSetup completed successfully!")

    except Exception as e:
        print(f"Error during setup: {e}")
        sys.exit(1)


def setup_environment():
    """Setup additional environment configurations"""
    # Add any environment setup code here
    pass

# "C:\Program Files\Nuke14.1v3\python.exe" -m pip install open3d
# "C:\Program Files\Nuke14.1v3\python.exe" -m pip install opencv-python

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Setup Nuke Importer tool")
    parser.add_argument("--dev", action="store_true", help="Install development dependencies")
    args = parser.parse_args()

    install_dependencies()
    setup_environment()