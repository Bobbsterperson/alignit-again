# **ALIGN IT GAME**

## **The Classic Game**
- Align 5 or more squares of the same color to finish a line, which disappears and rewards you points equal to the number of squares in the line.
- A **"wildcard" square** can be used to finish any line that:
  - Is of one color, or
  - Already has the "wildcard" square in it.
- For example:
  - If there are two 4-square lines in one row and a "wildcard" square is placed to finish both lines, both lines disappear. This is the **only situation** where more than one color disappears.
- After a move is made, **3 random color squares** spawn in random places on the grid.
  - A random color square can finish a line.
  - When a line is finished, no random squares spawn until the next move.
- The game finishes when the **9x9 grid** is full and no moves can be made.
- If the current score is higher than the biggest saved score, it gets saved as the **top score** upon:
  - Game save.
  - Game over.
  - Switching game modes.
- The score does **not** save upon:
  - Game restart.
  - Shutting down the game improperly.

---

## **The Bomber Mode**
- This mode uses **fewer colors** than the classic mode.
- A **bomb button** unlocks when a certain score is reached.
  - If the bomb button remains unused, the number of bomb uses **stacks**.
- The **wildcard square** is **not available** in bomber mode.
- Bomber mode has a **separate score tracker**.

---

## **How to Run the Game**

### **Windows**
-The game is not build to run on windows, but it can be run from the Integrated Development Environments.
1. Open the main file and press the **play button** in the top-right corner.
2. If resolution needs adjusting, it can be manually updated by modifying values in the `os_res` method.

### **Android**
1. Install **Buildozer**.
2. Build the app by running the following command in the terminal within the app directory:  
   ```bash
   buildozer -v android debug
3. The game file can be located in the `bin` folder in app directory.
4. Place the game file in an android mobile device, locate it and install it.
