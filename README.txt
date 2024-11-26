GAME
-the classic game
    align 5 or more squares of the same color to finish a line which disapears and rewards you points equel to the number of squares in the line.
a "wildcard" square can be used to finish any line that is of one color and/or already has the "wild card" square in it.
if for example, there are two 4 square lines in one row and a "wildcard" square is placed to finish both lines, both lines get finished and thats the only situation in which more than one color disapears.
when a move is made 3 random color squares are spawned on random places along the grid.
a random color squares can finish a line.
when i line is finished no random color squares are spawned until next move.
the game finishes when the 9x9 grid is full and no moves can be made.
if the current score is higher that the biggest saved score, it gets saved as the top score apon game save, game over or swich on game mode, but not apon game restart or if game is shut down in a way its not ment to be.

-the bomber mode
    this mode uses less colors than the classic mode.
when a certain score is reached it unlocks the bomb button.
the bomb button is unlocked every time a certain number of points is reacher, or if it stays unused the number of bomb button uses stacks.
the catch of the bomber mode having bomb button and less colors is that it lacks the "wildcard" square.
bomber mode has a seperate score tracking.


WINDOWS
    To run the game in windows, go to main file and hit play button on top right corner.
if resolution needs adjusting it could manualy be done by playing around with the values in os_res method.

ANDROID
    in order to build the game for android os, buildozer needs to be installed.
when app is ready, "buildozer -v android debug" is run in the terminal in the app directory. (it possible the build fails so the command should be run again)
when the app is build, the file is found in "bin" folder in the app directory.
