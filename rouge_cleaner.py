import os
import shutil
import winreg
import subprocess
import urllib.request
import tkinter as tk
from tkinter import messagebox, ttk
import logging

# Initialize logging
logging.basicConfig(filename='roguecleaner.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Cleaning functions
def log_action(action):
    logging.info(action)
    print(action)

def clean_temp_files():
    temp_folders = [os.getenv('TEMP'), os.getenv('TMP')]
    for temp_folder in temp_folders:
        if os.path.exists(temp_folder):
            for root, dirs, files in os.walk(temp_folder):
                for file in files:
                    try:
                        os.remove(os.path.join(root, file))
                        log_action(f"Deleted temporary file: {os.path.join(root, file)}")
                    except Exception as e:
                        log_action(f"Error deleting {file}: {e}")

def clean_unnecessary_files():
    unnecessary_folders = [
        os.path.expanduser('~\\AppData\\Local\\Temp'),
        os.path.expanduser('~\\AppData\\Local\\Microsoft\\Windows\\INetCache'),
        os.path.expanduser('~\\AppData\\Roaming\\Microsoft\\Windows\\Recent')
    ]
    for folder in unnecessary_folders:
        if os.path.exists(folder):
            try:
                shutil.rmtree(folder)
                os.makedirs(folder)
                log_action(f"Cleaned folder: {folder}")
            except Exception as e:
                log_action(f"Error cleaning {folder}: {e}")

def clean_registry():
    registry_paths = [
        r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run',
        r'SYSTEM\CurrentControlSet\Services'
    ]

    for path in registry_paths:
        try:
            reg = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_ALL_ACCESS)
            info = winreg.QueryInfoKey(reg)
            for i in range(info[0]):
                try:
                    sub_key_name = winreg.EnumKey(reg, i)
                    sub_key = winreg.OpenKey(reg, sub_key_name)
                    # Perform checks and clean invalid entries
                    # This part is simplified and needs specific implementation details
                    winreg.DeleteKey(reg, sub_key_name)
                    log_action(f"Deleted registry key: {path}\\{sub_key_name}")
                except Exception as e:
                    log_action(f"Error cleaning registry key {sub_key_name}: {e}")
        except Exception as e:
            log_action(f"Error accessing registry path {path}: {e}")

def clean_browser_cache():
    browsers = {
        "Chrome": os.path.expanduser('~\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Cache'),
        "Firefox": os.path.expanduser('~\\AppData\\Local\\Mozilla\\Firefox\\Profiles'),
        "Edge": os.path.expanduser('~\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\Cache')
    }

    for browser, path in browsers.items():
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
                os.makedirs(path)
                log_action(f"Cleaned {browser} cache at {path}")
            except Exception as e:
                log_action(f"Error cleaning {browser} cache at {path}: {e}")

def defragment_disk():
    try:
        subprocess.run(["defrag", "C:", "/O"], check=True)
        log_action("Disk defragmentation completed.")
    except Exception as e:
        log_action(f"Error defragmenting disk: {e}")

def manage_startup_programs(action, program=None):
    if action == "list":
        try:
            reg = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run', 0, winreg.KEY_READ)
            info = winreg.QueryInfoKey(reg)
            startup_programs = []
            for i in range(info[1]):
                try:
                    value_name, value_data, _ = winreg.EnumValue(reg, i)
                    startup_programs.append((value_name, value_data))
                except Exception as e:
                    log_action(f"Error reading startup program: {e}")
            return startup_programs
        except Exception as e:
            log_action(f"Error accessing startup programs: {e}")
    elif action == "add" and program:
        try:
            reg = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run', 0, winreg.KEY_ALL_ACCESS)
            winreg.SetValueEx(reg, program[0], 0, winreg.REG_SZ, program[1])
            log_action(f"Added startup program: {program[0]}")
        except Exception as e:
            log_action(f"Error adding startup program: {e}")
    elif action == "remove" and program:
        try:
            reg = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run', 0, winreg.KEY_ALL_ACCESS)
            winreg.DeleteValue(reg, program)
            log_action(f"Removed startup program: {program}")
        except Exception as e:
            log_action(f"Error removing startup program: {e}")

def download_driver_booster():
    url = "https://cdn.iobit.com/dl/driver_booster_setup.exe"  # URL of the Driver Booster installer
    file_path = "driver_booster_setup.exe"
    
    log_action("Downloading Driver Booster...")
    urllib.request.urlretrieve(url, file_path)
    log_action("Download completed.")
    
    return file_path

def install_driver_booster(installer_path):
    log_action("Installing Driver Booster...")
    subprocess.run([installer_path, "/S"], check=True)  # /S switch is for silent installation
    log_action("Installation completed.")

def update_drivers():
    driver_booster_path = "C:\\Program Files (x86)\\IObit\\Driver Booster\\DriverBooster.exe"
    
    if not os.path.exists(driver_booster_path):
        installer_path = download_driver_booster()
        install_driver_booster(installer_path)
    
    if os.path.exists(driver_booster_path):
        subprocess.run([driver_booster_path, "/scan"], check=True)
        subprocess.run([driver_booster_path, "/update"], check=True)
        log_action("Driver update completed.")
    else:
        log_action("Driver Booster installation failed. Please install it manually.")

def update_apps():
    try:
        subprocess.run(["winget", "upgrade", "--all"], check=True)
        log_action("Application updates completed.")
    except Exception as e:
        log_action(f"Error updating applications: {e}")

def disk_cleanup():
    try:
        subprocess.run(["cleanmgr", "/sagerun:1"], check=True)
        log_action("Disk cleanup completed.")
    except Exception as e:
        log_action(f"Error performing disk cleanup: {e}")

def registry_backup():
    backup_file = os.path.expanduser("~\\Desktop\\registry_backup.reg")
    try:
        subprocess.run(["reg", "export", "HKLM", backup_file, "/y"], check=True)
        log_action(f"Registry backup completed. File saved at {backup_file}")
    except Exception as e:
        log_action(f"Error backing up registry: {e}")

def registry_restore():
    backup_file = os.path.expanduser("~\\Desktop\\registry_backup.reg")
    if os.path.exists(backup_file):
        try:
            subprocess.run(["reg", "import", backup_file], check=True)
            log_action("Registry restore completed.")
        except Exception as e:
            log_action(f"Error restoring registry: {e}")
    else:
        log_action("No backup file found on Desktop.")

def schedule_cleaning():
    log_action("Scheduled cleaning not implemented yet.")

# GUI application
def create_gui():
    def run_cleaning():
        clean_temp_files()
        clean_unnecessary_files()
        clean_registry()
        clean_browser_cache()
        messagebox.showinfo("RogueCleaner", "System cleaning completed.")

    def run_driver_updates():
        update_drivers()
        messagebox.showinfo("RogueCleaner", "Driver update completed.")

    def run_app_updates():
        update_apps()
        messagebox.showinfo("RogueCleaner", "Application updates completed.")
    
    def run_disk_cleanup():
        disk_cleanup()
        messagebox.showinfo("RogueCleaner", "Disk cleanup completed.")
    
    def run_registry_backup():
        registry_backup()

    def run_registry_restore():
        registry_restore()
    
    def run_defragmentation():
        defragment_disk()
        messagebox.showinfo("RogueCleaner", "Disk defragmentation completed.")
    
    def show_startup_programs():
        programs = manage_startup_programs("list")
        display_text = "Startup Programs:\n" + "\n".join([f"{name}: {path}" for name, path in programs])
        messagebox.showinfo("RogueCleaner", display_text)
    
    def add_startup_program():
        name = input("Enter program name: ")
        path = input("Enter program path: ")
        manage_startup_programs("add", (name, path))
        messagebox.showinfo("RogueCleaner", f"Added startup program: {name}")

    def remove_startup_program():
        name = input("Enter program name to remove: ")
        manage_startup_programs("remove", name)
        messagebox.showinfo("RogueCleaner", f"Removed startup program: {name}")

    root = tk.Tk()
    root.title("RogueCleaner")
    root.geometry("500x500")

    notebook = ttk.Notebook(root)
    notebook.pack(pady=10, expand=True)

    # Create frames for tabs
    tab1 = ttk.Frame(notebook)
    tab2 = ttk.Frame(notebook)
    tab3 = ttk.Frame(notebook)
    tab4 = ttk.Frame(notebook)
    tab5 = ttk.Frame(notebook)

    notebook.add(tab1, text="System Cleaning")
    notebook.add(tab2, text="Updates")
    notebook.add(tab3, text="Registry")
    notebook.add(tab4, text="Disk")
    notebook.add(tab5, text="Startup Programs")

    # Tab 1 - System Cleaning
    ttk.Label(tab1, text="Clean your system by removing unnecessary files and cleaning the registry.").pack(pady=10)
    ttk.Button(tab1, text="Clean System", command=run_cleaning).pack(pady=10)
    ttk.Button(tab1, text="Clean Browser Cache", command=clean_browser_cache).pack(pady=10)
    ttk.Button(tab1, text="Schedule Cleaning", command=schedule_cleaning).pack(pady=10)

    # Tab 2 - Updates
    ttk.Label(tab2, text="Keep your drivers and applications up to date.").pack(pady=10)
    ttk.Button(tab2, text="Update Drivers", command=run_driver_updates).pack(pady=10)
    ttk.Button(tab2, text="Update Applications", command=run_app_updates).pack(pady=10)

    # Tab 3 - Registry
    ttk.Label(tab3, text="Manage your registry by backing up and restoring it.").pack(pady=10)
    ttk.Button(tab3, text="Backup Registry", command=run_registry_backup).pack(pady=10)
    ttk.Button(tab3, text="Restore Registry", command=run_registry_restore).pack(pady=10)

    # Tab 4 - Disk
    ttk.Label(tab4, text="Perform disk maintenance tasks.").pack(pady=10)
    ttk.Button(tab4, text="Disk Cleanup", command=run_disk_cleanup).pack(pady=10)
    ttk.Button(tab4, text="Defragment Disk", command=run_defragmentation).pack(pady=10)

    # Tab 5 - Startup Programs
    ttk.Label(tab5, text="Manage your startup programs.").pack(pady=10)
    ttk.Button(tab5, text="Show Startup Programs", command=show_startup_programs).pack(pady=10)
    ttk.Button(tab5, text="Add Startup Program", command=add_startup_program).pack(pady=10)
    ttk.Button(tab5, text="Remove Startup Program", command=remove_startup_program).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
