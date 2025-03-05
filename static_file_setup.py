import os
import shutil
from pathlib import Path

def setup_static_files():
    """Set up necessary static files for the application"""
    # Create directories if they don't exist
    base_dir = Path(__file__).resolve().parent
    static_dir = base_dir / 'static'
    images_dir = static_dir / 'images'
    
    # Create directories
    os.makedirs(images_dir, exist_ok=True)
    
    # Add a README file to images directory advising to add a school-bg.jpg
    readme_path = images_dir / 'README.txt'
    with open(readme_path, 'w') as f:
        f.write("Add a 'school-bg.jpg' file to this directory to use as the background image for the landing page.\n")
        f.write("The ideal size is 1920x1080 pixels with a dark overlay to ensure text visibility.\n")

if __name__ == "__main__":
    setup_static_files()
    print("Static file directories have been set up.")
    print("Please add a school-bg.jpg to the static/images directory for the landing page background.")
