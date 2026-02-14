import subprocess
import sys
import os
import time

# Paths
ROOT = os.path.dirname(os.path.abspath(__file__))             # src/
GIBS_PROJECT = os.path.join(ROOT, "gibs_map_project")         # src/gibs_map_project

WMTS_SCRIPT = os.path.join(GIBS_PROJECT, "gibs_wmts.py")      # src/gibs_map_project/gibs_wmts.py
FLASK_SCRIPT = os.path.join(GIBS_PROJECT, "netcdf_generator.py")
LAYERS_JSON = os.path.join(GIBS_PROJECT, "layers", "layers_info.json")


def run():
    print("\n==============================")
    print(" STEP 1: Running gibs_wmts.py ")
    print("==============================\n")

    # Run gibs_wmts.py to generate layers JSON
    subprocess.run([sys.executable, WMTS_SCRIPT], check=True)

    # Wait until layers_info.json exists
    print("\nWaiting for layers_info.json to be created...")
    while not os.path.exists(LAYERS_JSON):
        time.sleep(0.5)
    print("layers_info.json found!")

    print("\n==============================")
    print(" STEP 2: Starting Flask server ")
    print("==============================\n")

    flask_process = subprocess.Popen(
        [sys.executable, FLASK_SCRIPT],
        cwd=GIBS_PROJECT
    )

    print("\n=========================================")
    print(" STEP 3: Starting frontend HTTP server   ")
    print("=========================================\n")

    http_process = subprocess.Popen(
        [sys.executable, "-m", "http.server", "8000"],
        cwd=GIBS_PROJECT
    )

    print("\n============================================")
    print(" All systems running!                        ")
    print(" Flask → http://127.0.0.1:5000               ")
    print(" Frontend → http://127.0.0.1:8000/index.html ")
    print(" Press CTRL+C to stop everything             ")
    print("============================================\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        flask_process.terminate()
        http_process.terminate()
        print("Done.")


if __name__ == "__main__":
    run()
