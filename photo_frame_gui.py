#!/usr/bin/env python3
"""
Raspberry Pi Photo Frame GUI Controller
Simple GUI to start/stop the photo server and slideshow
"""

import subprocess
import os
import sys
import socket
from pathlib import Path

# Check for tkinter before importing
try:
    import tkinter as tk
    from tkinter import ttk, messagebox
except ImportError:
    print("Error: tkinter is not installed.")
    print("Please install it with: sudo apt-get install python3-tk")
    print("Note: tkinter must be installed system-wide, not via pip.")
    sys.exit(1)

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.absolute()
VENV_PYTHON = SCRIPT_DIR / "venv" / "bin" / "python"
APP_PY = SCRIPT_DIR / "app.py"
SLIDESHOW_SCRIPT = SCRIPT_DIR / "pi_photo_frame.sh"

class PhotoFrameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Raspberry Pi Photo Frame")
        self.root.geometry("400x200")
        self.root.resizable(False, False)
        
        # Store process references
        self.server_process = None
        self.slideshow_process = None
        
        # Create UI
        self.create_widgets()
        
        # Check initial state
        self.update_button_states()
        
        # Periodically check process status
        self.root.after(2000, self.check_processes)
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Photo Frame Controller", 
                                font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 5))
        
        # IP address label (always visible)
        local_ip = self.get_local_ip()
        self.ip_label = ttk.Label(main_frame, text=f"{local_ip}:5000", 
                                  font=("Arial", 10), foreground="gray")
        self.ip_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # Server button
        self.server_button = tk.Button(main_frame, text="Start Server", 
                                      command=self.toggle_server,
                                      width=20,
                                      font=("Arial", 10, "bold"),
                                      foreground="green")
        self.server_button.grid(row=2, column=0, columnspan=2, pady=10, padx=20, sticky="ew")
        
        # Slideshow button
        self.slideshow_button = tk.Button(main_frame, text="Start Slideshow", 
                                         command=self.toggle_slideshow,
                                         width=20,
                                         font=("Arial", 10, "bold"),
                                         foreground="green")
        self.slideshow_button.grid(row=3, column=0, columnspan=2, pady=10, padx=20, sticky="ew")
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="", foreground="gray")
        self.status_label.grid(row=4, column=0, columnspan=2, pady=(10, 0))
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def is_server_running(self):
        """Check if the Flask server is running"""
        try:
            result = subprocess.run(
                ["pgrep", "-f", "python.*app.py"],
                capture_output=True,
                text=True
            )
            return bool(result.stdout.strip())
        except:
            return False
    
    def is_slideshow_running(self):
        """Check if the slideshow script is running"""
        try:
            result = subprocess.run(
                ["pgrep", "-f", "pi_photo_frame.sh"],
                capture_output=True,
                text=True
            )
            return bool(result.stdout.strip())
        except:
            return False
    
    def get_local_ip(self):
        """Get the local IP address of this machine"""
        try:
            # Connect to a remote address to determine local IP
            # This doesn't actually send data, just determines the route
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            # Fallback: try hostname
            try:
                hostname = socket.gethostname()
                ip = socket.gethostbyname(hostname)
                return ip
            except Exception:
                return "localhost"
    
    def start_server(self):
        """Start the Flask server in virtual environment"""
        # Create virtual environment if it doesn't exist
        if not VENV_PYTHON.exists():
            self.status_label.config(text="Creating virtual environment...", foreground="blue")
            self.root.update()  # Update GUI to show status
            
            try:
                # Create virtual environment
                result = subprocess.run(
                    ["python3", "-m", "venv", str(SCRIPT_DIR / "venv")],
                    cwd=str(SCRIPT_DIR),
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    messagebox.showerror("Error", 
                                       f"Failed to create virtual environment:\n{result.stderr}")
                    self.status_label.config(text="", foreground="gray")
                    return False
                
                # Install dependencies
                self.status_label.config(text="Installing dependencies...", foreground="blue")
                self.root.update()
                
                requirements_file = SCRIPT_DIR / "requirements.txt"
                if not requirements_file.exists():
                    messagebox.showerror("Error", "requirements.txt not found!")
                    self.status_label.config(text="", foreground="gray")
                    return False
                
                venv_pip = SCRIPT_DIR / "venv" / "bin" / "pip"
                result = subprocess.run(
                    [str(venv_pip), "install", "--upgrade", "pip"],
                    cwd=str(SCRIPT_DIR),
                    capture_output=True,
                    text=True
                )
                
                result = subprocess.run(
                    [str(venv_pip), "install", "-r", str(requirements_file)],
                    cwd=str(SCRIPT_DIR),
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    messagebox.showerror("Error", 
                                       f"Failed to install dependencies:\n{result.stderr}")
                    self.status_label.config(text="", foreground="gray")
                    return False
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to set up virtual environment: {str(e)}")
                self.status_label.config(text="", foreground="gray")
                return False
        
        try:
            # Start server in background
            self.server_process = subprocess.Popen(
                [str(VENV_PYTHON), str(APP_PY)],
                cwd=str(SCRIPT_DIR),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start server: {str(e)}")
            return False
    
    def stop_server(self):
        """Stop the Flask server"""
        try:
            subprocess.run(["pkill", "-f", "python.*app.py"], 
                         capture_output=True)
            self.status_label.config(text="Server stopped", foreground="gray")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop server: {str(e)}")
            return False
    
    def start_slideshow(self):
        """Start the slideshow script"""
        if not SLIDESHOW_SCRIPT.exists():
            messagebox.showerror("Error", "Slideshow script not found!")
            return False
        
        # Make slideshow script executable if it isn't already
        if not os.access(SLIDESHOW_SCRIPT, os.X_OK):
            try:
                os.chmod(SLIDESHOW_SCRIPT, 0o755)
            except Exception as e:
                messagebox.showerror("Error", 
                                   f"Failed to make slideshow script executable: {str(e)}")
                return False
        
        try:
            # Start slideshow in background
            # Note: The script needs a photo directory, but we'll let it handle defaults
            self.slideshow_process = subprocess.Popen(
                [str(SLIDESHOW_SCRIPT), "-run", "-dir", str(SCRIPT_DIR / "uploads")],
                cwd=str(SCRIPT_DIR),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start slideshow: {str(e)}")
            return False
    
    def stop_slideshow(self):
        """Stop the slideshow"""
        try:
            # Find and kill processes related to the slideshow
            # Get process IDs for pi_photo_frame.sh
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True
            )
            
            killed_any = False
            for line in result.stdout.split('\n'):
                if 'pi_photo_frame' in line and 'grep' not in line:
                    parts = line.split()
                    if len(parts) > 1:
                        try:
                            pid = int(parts[1])
                            os.kill(pid, 15)  # SIGTERM
                            killed_any = True
                        except (ValueError, ProcessLookupError, PermissionError):
                            pass
            
            # Also kill feh and lisgd processes
            for process_name in ['feh', 'lisgd']:
                result = subprocess.run(
                    ["ps", "aux"],
                    capture_output=True,
                    text=True
                )
                for line in result.stdout.split('\n'):
                    if process_name in line and 'grep' not in line:
                        parts = line.split()
                        if len(parts) > 1:
                            try:
                                pid = int(parts[1])
                                os.kill(pid, 15)  # SIGTERM
                                killed_any = True
                            except (ValueError, ProcessLookupError, PermissionError):
                                pass
            
            if killed_any:
                self.status_label.config(text="Slideshow stopped", foreground="gray")
            else:
                self.status_label.config(text="No slideshow process found", foreground="gray")
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop slideshow: {str(e)}")
            return False
    
    def toggle_server(self):
        """Toggle server on/off"""
        if self.is_server_running():
            self.stop_server()
        else:
            self.start_server()
        self.update_button_states()
    
    def toggle_slideshow(self):
        """Toggle slideshow on/off"""
        if self.is_slideshow_running():
            self.stop_slideshow()
        else:
            self.start_slideshow()
        self.update_button_states()
    
    def update_button_states(self):
        """Update button text based on current process status"""
        if self.is_server_running():
            self.server_button.config(text="Stop Server", foreground="red")
        else:
            self.server_button.config(text="Start Server", foreground="green")
        
        if self.is_slideshow_running():
            self.slideshow_button.config(text="Stop Slideshow", foreground="red")
        else:
            self.slideshow_button.config(text="Start Slideshow", foreground="green")
    
    def check_processes(self):
        """Periodically check if processes are still running"""
        self.update_button_states()
        # Check again in 2 seconds
        self.root.after(2000, self.check_processes)

def main():
    root = tk.Tk()
    app = PhotoFrameGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

