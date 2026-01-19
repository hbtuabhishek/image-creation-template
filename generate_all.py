import subprocess
import sys
import os

# Configuration for the generation run
PYTHON_EXEC = sys.executable if sys.executable else "python3.13"
SCRIPT_NAME = "generateSS.py"

# Common Data
DATE_TIME = "Tue, Jan 15, 01:50"
TITLE = "New Delhi World Book Fair 2026 - A Celebration of Literature, Culture, and History across the Ages"
BASE_DESCRIPTION = "Bharat Mandampam | Jan 10-18 | Entry Free | Theme: valour & Wisdom"
APP_NAME = "iZooto Demo App"
ICON_FILE = "assets/icons/bell-icon.png" 
BANNER_FILE = "assets/banners/World-Book-Fair-2026-1536x1536-1.jpg"

def run_gen(tid, description_suffix=""):
    """
    Runs generateSS.py for a specific template ID.
    Ensures all 7 arguments are always passed.
    """
    
    # Construct description (user was varying this per template: @75, @76, @77)
    full_desc = f"{BASE_DESCRIPTION}{description_suffix}"
    
    # For Template 4, even if it doesn't strictly use Title/Desc in the config 
    # (depending on setup), the script REQUIRES these arguments positionally.
    # We pass them to avoid the "Usage" error.
    
    cmd = [
        PYTHON_EXEC,
        SCRIPT_NAME,
        str(tid),           # 1. Template ID
        DATE_TIME,          # 2. Date Time
        TITLE,              # 3. Title
        full_desc,          # 4. Description
        APP_NAME,           # 5. App Name
        ICON_FILE,          # 6. Icon File
        BANNER_FILE         # 7. Banner File
    ]
    
    print(f"🔹 Generating Template {tid}...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Success: output/generated_t{tid}.png")
        else:
            print(f"❌ Failed Template {tid}")
            print(result.stderr)
            print(result.stdout)
    except Exception as e:
        print(f"❌ Execution Error: {e}")

def main():
    print("🚀 Starting Batch Generation for Templates...\n")
    
    if not os.path.exists(SCRIPT_NAME):
        print(f"Error: {SCRIPT_NAME} not found in current directory.")
        return

    # Run for each template
    run_gen(1)
    run_gen(2)
    run_gen(3)
    run_gen(4)
    
    print("\n✨ All tasks completed.")

if __name__ == "__main__":
    main()
