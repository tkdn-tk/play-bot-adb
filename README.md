# Cookie Run Classic — ADB Reroll Bot
![Bot Status](https://img.shields.io/badge/status-active-success.svg)
![Platform](https://img.shields.io/badge/platform-windows-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)

An automated reroll bot for Cookie Run Classic running on MuMu Player (Android emulator). It uses Python, OpenCV template matching, and **ADB (Android Debug Bridge)** to interact with the game in the background. This allows the bot to send clicks directly to the emulator without taking over your actual mouse, meaning you can use your PC normally while the bot runs!

## Features
- **Background Interaction**: Uses ADB to send clicks to the emulator window without stealing your mouse cursor.
- **Visual Recognition**: Uses OpenCV to strictly interact with the UI based on visual state.
- **One-Click Install**: Easy setup using the provided `run.bat` script.
- **Email Notifications**: Can automatically email you when a desired account is rolled.

## Setup Instructions

### 1. Emulator Configuration (CRITICAL)

The bot relies on template images matching the exact size of the buttons on your screen. Therefore, your emulator must be set to a specific resolution.

1. Open **MuMu Player**.
2. Go to **Settings** (usually a menu in the top right).
3. Under the **Display** or **Resolution** tab, set the resolution to exactly **1280 × 720**.
4. Save and restart the emulator.
5. Ensure **ADB debugging** (or "Root permission") is enabled in your emulator settings so the bot can connect to it.

### 2. Installation & Running

This project uses a one-click setup script that handles installing dependencies and managing the virtual environment.

1. Ensure you have **Python 3.10+** installed on your computer.
2. Double-click the `run.bat` file.
3. On the first run, it will automatically:
   - Create a virtual environment (`venv`).
   - Install required packages from `requirements.txt`.
   - Copy `config.example.yaml` to `config.yaml` and prompt you to edit it.

### 3. Configuration

Open `config.yaml` in a text editor to set up your preferences:
- **Emulator Settings**: Ensure `emulator_window_title` matches your MuMu player window title.
- **ADB Settings**: You can specify an exact ADB serial or let the bot find it.
- **Desired Items**: Tell the bot which cookies/pets to look for by editing the `criteria` section. Place cropped screenshots of these desired items in the `templates/desired/` folder (with matching filenames).
- **Email Notifications**: Add your SMTP credentials to receive emails on successful rolls.

### 4. Running the Bot

1. Start Cookie Run Classic on the emulator and sit at the Login screen.
2. Double-click `run.bat`.
3. The bot will connect via ADB and start rerolling in the background. You can move the emulator window aside and do other things on your PC!
4. **Emergency Stop:** Press **F7** (configurable in `config.yaml`) to immediately stop the bot. Press **F8** to pause/resume.

## Adding Templates

UI elements can look slightly different depending on rendering settings. The `templates/` folder contains standard buttons. If the bot struggles to find buttons on your machine, you can run the built-in capture tool:
```cmd
run.bat capture
```
Or directly via Python:
```cmd
python main.py capture
```
See `CAPTURE_GUIDE.md` for detailed instructions on updating templates.

## Logs

Every completed reroll session is logged to `logs/reroll_log.json`. When the bot finds an account that matches your desired criteria, it will stop, play an alert sound, and notify you (if emails are enabled).
