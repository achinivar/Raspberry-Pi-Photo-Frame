# Raspberry-Pi-Photo-Frame
Raspberry Pi Photo Frame slideshow with touchscreen support"

A lightweight, full-screen photo slideshow application for Raspberry Pi with automatic touchscreen gesture support and hourly photo refresh. Includes a web-based photo server for remote photo upload and management. Designed to run efficiently on Raspberry Pi hardware without overheating.

## Features

- **Full-screen slideshow** using `feh` (lightweight image viewer)
- **Automatic touchscreen detection** — enables gesture controls if a touchscreen is present
- **Touchscreen gestures**:
  - Swipe left → next photo
  - Swipe right → previous photo
  - Single-finger swipe down → exit slideshow
- **Hourly refresh** — automatically restarts every hour to pick up newly added photos
- **Auto-detection** of Wayland display server
- **Random photo order** on each run
- **Auto-rotation** of photos based on EXIF data
- **Background operation** — runs all processes in the background
- **Web photo server** — Flask-based web interface for uploading and managing photos from any device on your network

## Requirements

- Raspberry Pi OS (or compatible Debian-based distribution)
- Wayland display server
- Optional: Touchscreen for gesture navigation

## Installation

1. **Make the script executable:**

   ```bash
   chmod +x pi_photo_frame.sh
   ```

2. **Run the installer:**

   ```bash
   ./pi_photo_frame.sh -install
   ```

   This will:
   - Install `feh` (image viewer)
   - Install `libinput-tools` (for touchscreen support)
   - Install `wtype` (simulates keyboard input for Wayland)
   - If a touchscreen is detected, install `lisgd` (gesture daemon) from system repositories

## Usage

### Basic Usage

You can control the photo frame using either the GUI controller or the command-line script.

### GUI Controller

A simple Tkinter GUI (`photo_frame_gui.py`) provides an easy way to control both the server and slideshow.

#### Requirements

- `python3-tk` (install system-wide): `sudo apt-get install python3-tk`

#### Usage

Run the GUI:

```bash
python3 photo_frame_gui.py
```

The GUI provides:
- **Start/Stop Server** button — Controls the Flask web server
- **Start/Stop Slideshow** button — Controls the photo slideshow
- **IP Address display** — Shows the server URL for network access

The GUI automatically:
- Creates a virtual environment if missing
- Installs dependencies when starting the server
- Makes the slideshow script executable if needed
- Updates button colors (green for start, red for stop) based on process status

### Using the photo frame script

Start the slideshow with a photo directory:

```bash
./pi_photo_frame.sh -run -dir /path/to/photos
```

#### Custom Delay

Set how many seconds each photo displays (default is 15 seconds):

```bash
./pi_photo_frame.sh -run -dir /path/to/photos -delay 15
```

#### Stop the Slideshow

Stop all running photo frame processes:

```bash
./pi_photo_frame.sh -stop
```

## How It Works

The slideshow automatically refreshes every hour to pick up new photos. If a touchscreen is detected, gesture controls are enabled. 

## Autostart on Boot

To start the slideshow automatically when the Raspberry Pi boots, add it to your desktop environment's autostart:

### For LXDE (Raspberry Pi OS Desktop):

```bash
mkdir -p ~/.config/lxsession/LXDE-pi
cat >> ~/.config/lxsession/LXDE-pi/autostart <<EOF
@/home/pi/path/to/pi_photo_frame.sh -run -dir /path/to/photos
EOF
```

Replace `/home/pi/path/to/` with the actual path to the script and `/path/to/photos` with your photo directory.

## Troubleshooting

### Photos Not Displaying

- Verify the directory path is correct and contains image files (`.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.webp`)
- Check that `feh` is installed: `which feh`
- Ensure you're running from a graphical session (not SSH without X forwarding)

### Touchscreen Gestures Not Working

- Verify touchscreen is detected: The script will log "Starting lisgd on..." if detected
- Check that `lisgd` is running: `pgrep -x lisgd`
- Ensure your user has access to input devices (may need to be in `input` group):
  ```bash
  sudo gpasswd -a "$USER" input
  ```
  Then log out and back in.

### Display Issues

- Ensure `wtype` is installed for Wayland keyboard simulation
- Verify you're running Wayland: `echo $XDG_SESSION_TYPE` should output "wayland"

### Photos Not Updating After Adding New Ones

- The slideshow refreshes every hour automatically
- To force an immediate refresh, stop and restart the slideshow

## Configuration

Modify variables at the top of the script: `DEFAULT_DELAY=15` (seconds per photo) and `REFRESH_SECS=3600` (refresh interval).

## Supported Image Formats

JPEG, PNG, GIF, BMP, TIFF, WebP

## Web Photo Server

The project includes a Flask-based web server for uploading and managing photos remotely.

### Setup

1. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the server:**
   ```bash
   python app.py
   ```

4. **Access from any device:**
   - Open browser: `http://localhost:5000` (on the Pi)
   - Or from other devices: `http://PI_IP_ADDRESS:5000`

### Features

Upload multiple photos, view gallery, delete photos, automatic image optimization, mobile-friendly interface.

Photos uploaded via the web server are stored in the `uploads/` directory and will appear in the slideshow after the next hourly refresh.

---

This script is provided as-is for use on Raspberry Pi systems.
