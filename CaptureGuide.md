# Capture Tool Guide

This project includes a built-in **Capture Tool** to help you crop perfectly sized template images directly from the running emulator. The bot uses these templates (located in the `templates/` folder) to figure out where it is and what to click.

## When do you need this?
- If the game UI changes in an update.
- If you change your emulator's resolution or DPI settings.
- If the bot is getting stuck because it can't find a button (like the Main Menu button, Start button, etc.).

## How to use

1. Ensure MuMu Player is running and the game is on the screen you want to capture.
2. Open your terminal in the bot folder and run:
   ```bash
   python main.py capture
   ```
3. The tool will connect to the emulator via ADB, take a screenshot, and pop open a new window showing the game screen.

## Controls

When the OpenCV capture window is open, use the following keys:
- **Click & Drag**: Use your mouse to draw a green rectangle around the button or UI element you want to capture.
- **`ENTER`**: Save the cropped region! The tool will prompt you in the terminal for a filename (e.g. `main_menu.png`). Save it directly into the `templates/` folder to overwrite the old one.
- **`R`**: Refresh the screen. This tells the tool to take a fresh screenshot from the emulator (useful if the game screen just changed).
- **`S` or `ESC`**: Skip / Quit the capture tool.

## Tips for good templates
- **Crop tightly**: Don't include too much background around a button, especially if the background is transparent or animates.
- **Avoid text**: If a button has text that changes (like a score or level), try to crop an iconic part of the button (like an icon or the border) instead of the changing text.
