"""
Mason Reck
Critical Room Control
7/22/2022

This script is made with the intention of converting monochrome images to hex
form for various monochrome displays
"""

import pygame
import screen
import editor

"""
Changeable Values
    Feel free to edit these values to your liking
"""
# Configure how wide and tall your bitmap or character is
widthOLED = 128
heightOLED = 32
# widthOLED = input("Insert width in pixels: ")
# heightOLED = input("Insert height in pixels: ")

# Determines how many pixels on your computer screen will make up 1 OLED screen pixel
screenMultiplier = 9


"""
Setup
"""

# "width" and "height" correspond to the width and height of the tool on your computer screen
editorWidth = widthOLED * screenMultiplier
editorHeight = heightOLED * screenMultiplier
pygame.init()

# Screen Object is created
screen = screen.Screen(editorWidth, editorHeight, 500)

# Editor Object is created
editor = editor.Editor(screenMultiplier, widthOLED, heightOLED)

# Custom Cursor
pygame.mouse.set_cursor(*pygame.cursors.tri_left)


print("\nControls")
print("\t Left Click - Draw")
print("\t Right Click - Erase")
print("\t Scroll Wheel - Change Brush Size")
print("\t Scroll Wheel Button - Select part of the image to copy")
print("\t Escape - cancel Selection")
print("\t Arrow Keys / WASD - Translate selection in Cardinal Directions")
print("\t Z / Y - Undo / Redo respectively")
# print("\t X / C - Switch selection mode to Cut / Copy respectively")
print("\t Page Down (Like Download) - Load Image")
print("\t Page Up (Like Upload) - Save Image\n")




# Tool's Main Loop
autoSave = 20000    # Frequency of auto save (Bigger number = lower freq, lower number = higher freq)
counter = 0
defaultMoveSpeed = 50.0
maxMoveSpeed = 5.0
selectMoveSpeed = defaultMoveSpeed
selectMoveAcceleration = 0.3
moved = False
running = True
while running:

    # START OF FRAME

    # Handle User Input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Handle Mouse and Keyboard Input
        editor.handleMouse(event, screen)
        newRender = editor.handleKeyboard(event, screen)

        if newRender:
            screen.resetScreen(editor.width*screenMultiplier, editor.height*screenMultiplier)


    # Update your screen
    editor.update()
    editor.draw(screen.pyScreen)
    pygame.display.update()
    screen.fpsClock.tick(screen.fps)



    # Moving selections in the editor
    counter += 1
    if counter % int(selectMoveSpeed) == 0:
        moved = editor.moveSelection(editor.moving)

    if moved:
        selectMoveSpeed -= selectMoveAcceleration
        if selectMoveSpeed < maxMoveSpeed:
            selectMoveSpeed = maxMoveSpeed
    else:
        selectMoveSpeed = defaultMoveSpeed


    if counter > autoSave:
        print("Auto-Saving progress to Data/{}".format(editor.saveFileName))
        editor.translateHexadecimal(False)
        editor.saveImgToFile("Data/", editor.saveFileName)
        counter = 0
    # END OF FRAME


















