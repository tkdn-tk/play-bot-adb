# Template Capture Guide

To make the bot work, it needs to know what the buttons in your game look like. Since games look slightly different on every screen, you need to capture these button images yourself.

## How to Capture an Image (Guided Mode)

We built a tool to make this easy. The tool will walk you through the list below, one by one.

1. **Start the tool**
   Open your terminal and run:
   ```bash
   python main.py capture
   ```
2. **Select Guided Mode**
   Type `1` and press `ENTER` to select Guided Mode.
3. **Read the Prompt**
   The terminal will tell you what button it wants to capture next. 
   *(Example: "NOW CAPTURING: buttons/guest_login")*
4. **Prepare the Game**
   Click around in your MuMu Player until that specific button is visible on the screen.
5. **Take the Screenshot**
   Go back to your terminal window and press `ENTER`. An image window will pop up showing a screenshot of your emulator.
6. **Draw the Box**
   Using your mouse, click and drag to draw a tight green rectangle exactly around the button. Try not to include too much background, just the button itself.
7. **Save or Retry**
   - Press `ENTER` to save the cropped image. The tool will automatically put it in the right folder and move to the next item!
   - Press `R` if you messed up the box and need to redraw it.
   - Press `S` if the button isn't on your screen yet and you want to skip it for now.

---

## Required Image Checklist

The Guided Mode will ask you for all of these automatically, but here is the full list so you know what to expect.

### Login & Tutorial Phase
- [ ] `guest_login` — The Guest Login button on the title screen
- [ ] `confirm_login` — The confirmation popup after clicking guest login (if the game shows one)
- [ ] `play` — The main Play / Tap to Start button
- [ ] `tutorial_confirm` — The button to start/confirm the tutorial
- [ ] `settings` — The gear/settings icon at the top right (you need to click this to skip the tutorial)
- [ ] `quit_tutorial` — The quit/skip tutorial button inside settings
- [ ] `confirm_quit_tutorial` — The confirmation prompt to quit the tutorial

### Account Setup Phase
- [ ] `name_input_field` — The text box where you type your nickname
- [ ] `confirm_name` — The OK/Confirm button after typing your name
- [ ] `close_x` — The generic red 'X' button on daily rewards and popups
- [ ] `close_x_small` — Alternative smaller red X button on some notifications
- [ ] `ok_button` — A generic OK button on notifications
- [ ] `claim_reward` — A generic Claim button on notifications

### Mailbox Phase
- [ ] `mailbox` — The envelope/mailbox icon on the main screen
- [ ] `mailbox_reward_tab` — The 'Reward' tab inside the mailbox
- [ ] `claim_all` — The 'Claim All' button inside the mailbox
- [ ] `mailbox_close` — The Close button specifically for the mailbox window

### Treasure & Pet Draws
- [ ] `draw_menu` — The Gacha/Draw menu button on the main screen
- [ ] `tab_treasure` — The Treasure tab at the top of the draw menu
- [ ] `treasure_draw_btn` — The 1x Free Draw button for regular treasures
- [ ] `treasure_result_bg` — Unique text/background on the result screen (used to know when the draw animation finishes)
- [ ] `confirm_draw` — The OK/Confirm button to exit the draw result screen
- [ ] `tab_special_treasure` — The Special Treasure tab
- [ ] `special_draw_btn` — The 1x Free Draw button for special treasures
- [ ] `special_draw_btn_alt` — The alternate Draw button (e.g., using crystals) for the second special draw
- [ ] `special_result_bg` — Unique text/background on the special treasure result screen
- [ ] `special_treasure_close_alt` — An alternate close button that sometimes appears when closing special treasure
- [ ] `special_treasure_close_small` — The secondary smaller close button that appears after closing special treasure
- [ ] `close_x_treasure_tab` — The close button specifically for the treasure tab
- [ ] `tab_pet` — The Pet tab
- [ ] `pet_hatch_btn` — The Hatch button that must be clicked before drawing a pet
- [ ] `pet_draw_btn` — The 1x Free Draw button for pets
- [ ] `pet_result_bg` — Unique text/background on the pet result screen
- [ ] `pet_close_x_btn` — The X button used to close the pet draw result screen
- [ ] `close_hatch_tab` — The close button specifically for the pet hatch menu popup
- [ ] `close_x_pet_tab` — The close button specifically for the pet tab

### Deletion & Restart Phase
- [ ] `tab_game_info` — The 'Game Info' tab inside settings
- [ ] `delete_account` — The 'Delete Account' button
- [ ] `confirm_delete_active` — The final Confirm button (the one that appears after waiting 60 seconds)
- [ ] `confirm_restart` — The button to restart the game after deletion
