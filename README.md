# Cookie Run AutoPlay Bot

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)]()

An advanced, fully automated ADB-based bot for Cookie Run, designed to run seamlessly on the **MuMu Player** emulator. The bot continuously plays the game, optionally handles buff purchasing and macro execution, and automatically manages sending and receiving gifts on a configurable schedule!

## Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Setup & Installation](#setup--installation)
- [Usage](#usage)
- [Capture Tool](#capture-tool)
- [Contributing](#contributing)
- [License](#license)

## Features
- **Endless AutoPlay**: Navigates the main menu, prepares play, runs macros (optional), and handles result screens automatically.
- **Smart Gift Management**: Automatically sends and receives gifts at a configurable interval (supports both minutes and hours).
- **Fast Start & Buff Purchasing**: Can be configured to spam-click the center during startup (Fast Start) and auto-purchase buffs.
- **ADB Integration**: Uses background ADB commands (`input swipe`, `input click`) directly to the emulator. It works even if the window is in the background.
- **Dynamic Instance Selection**: Automatically scans memory and window handles to detect and connect to your MuMu Player instance.
- **Image Recognition**: Uses OpenCV template matching to navigate the game robustly.

## Requirements
- **Python 3.8+**
- **MuMu Player** (The bot currently targets MuMu Player's specific process and window structures).
- Emulator Resolution must match the `config.yaml` settings exactly (Default: **856x521**).

## Setup & Installation

1. **Clone the Repository** and open a terminal in the folder.
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure the Bot**:
   Copy `config.example.yaml` to `config.yaml`.
   Modify the settings as needed (especially the gift intervals, delays, and emulator settings).
4. **Start MuMu Player** and open Cookie Run.

## Usage

The easiest way to use the bot is via the **Web UI**. Run:
```bash
python webui.py
```
This will automatically open a control panel in your browser (`http://localhost:8000`) and minimize the console to your system tray.

Alternatively, you can start the bot in CLI mode using the included batch script (which automatically handles dependencies):
```bash
run.bat
```
Or run the Python script directly:
```bash
python main.py
```

### Interactive Prompts
Upon launching, the bot will ask you:
1. **Which MuMu instance to connect to?** (If multiple are found).
2. **Bot Mode**: Default or Fast Start (spam click to start faster).
3. **Macro Execution**: Skip Macro or Run Macro.
4. **Buffs**: Skip Buy Buffs or Buy Buffs.

### Hotkeys
While the bot is running, you can control it with your keyboard:
- **`F11`**: Pause / Resume the bot.
- **`F12`**: Emergency Stop / Exit the bot.
*(You can change these hotkeys inside `config.yaml`)*

## Capture Tool
If you need to update or replace the template images the bot looks for (e.g. because of an emulator update or UI change), use the built-in Capture Tool!
Check out the [Capture Tool Guide](CaptureGuide.md) for more info.

## Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the issues page. 
If you want to contribute, please fork the repository and use a feature branch. Pull requests are warmly welcome.

## License
This project is licensed under the MIT License.
