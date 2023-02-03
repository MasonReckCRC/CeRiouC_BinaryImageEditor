# Editor Tool Object


import pygame
from ast import literal_eval
import collections


class Editor:
    """
    Changeable Values
        Feel free to edit these values to your liking
    """

    """
    isReadRowByRow Information:
        Hex data is read either horizontally or vertically
    
    If you are creating a normal Bitmap
        isReadHorizontally = False
        
    If you are creating a Font
        isReadHorizontally = True
    """
    isReadHorizontally = False

    """
    The next variables edit the tint of the Monochrome Colors.
    Smaller Number = Darker, Larger Number = Lighter
    """
    background = 55
    dark = 10
    light = 245
    highlight = 164
    selectionDark = 64
    selectionLight = 100
    screenColor = [dark, light, highlight, selectionDark, selectionLight]

    maxBrushSize = 32

    # Determines how much border there is between each pixel
    borderSize = 2

    # The max amount of screens the program will save for undo action
    maxHistory = 100

    # Determines how many values there are per line in your CSV files
    numHexValuesPerLine = 30

    # Enumerate the different pixel types
    DARK = 0
    LIGHT = 1
    HIGHLIGHT = 2
    SELECT_DARK = 3
    SELECT_LIGHT = 4

    """INITIALIZE"""

    def __init__(self, screenMultiplier, widthOLED, heightOLED):
        self.screenMultiplier = screenMultiplier
        self.width = widthOLED
        self.height = heightOLED

        """INITIALIZE DATASTRUCTURES"""
        self.pixelsBinary = 0
        self.pixelsDisplay = 0
        self.history = collections.deque()
        self.historyIndex = 0
        self.totalRows = 0
        self.totalCols = 0
        self.totalBytes = 0
        self.binary = 0
        self.hex = 0
        self.initDatastructures()

        """Editor Values"""
        self.editorState = "Editing"
        self.x = 0
        self.y = 0
        self.brushSize = 1
        self.action = Act.IDLE
        self.moving = Dir.IDLE
        self.selectMode = Select.COPY
        self.buttonsDown = [False, False, False, False]

        """File I/O"""
        self.hexDataLoc = "Data/hexData.csv"
        self.saveFileName = "backup.csv"
        pass

    def initDatastructures(self):
        """
        Brief
            :var self.pixelsBinary/pixelsDisplay is a multidimensional array containing the current value for each pixel
                    on the OLED screen. Binary is raw 1 or 0. Display is what the user sees (includes highlights)
                    The first dimension is the X axis and the second dimension is the Y axis
            ### :var self.selection is the X1, Y1, X2, Y2 Rectangular coordinates of a user selection
            :var self.totalRows is the number of rows of information stored
            :var self.totalCols is the number of columns of information stored
            :var self.binary is a multidimensional array containing each pixel's value      1 = colored | 0 = blank
                The first dimension is the byte index, and the second is the bit index      [ByteIndex][BitIndex]
                Note: :var self.binary is different from :var self.pixels in that self.binary stores the data exactly
                how the OLED screen will need it. See :method translateBinary for an explanation on how the OLED will
                read the data differently from the straightforward way this program handles pixels.
            :var self.hex is a single-dimensional array containing each pixel's value
                When translated to binary, you will get the same result as :var self.binary where each index of
                self.hex is a byte of information in hexadecimal
        """
        self.pixelsBinary = [[0 for i in range(self.height)] for j in range(self.width)]
        self.pixelsDisplay = [[0 for i in range(self.height)] for j in range(self.width)]
        self.saveScreenToHistory()

        # Display in bytes, use truncation, and add a row if there's not a complete octet row at the end
        self.totalRows = int(self.height / 8)
        if not self.height % 8 == 0:
            self.totalRows += 1
        self.totalCols = int(self.width / 8)
        if not self.width % 8 == 0:
            self.totalCols += 1

        if Editor.isReadHorizontally:
            self.totalBytes = self.totalCols * self.height
        else:
            self.totalBytes = self.totalRows * self.width

        self.binary = [[0 for i in range(8)] for j in range(self.totalBytes)]
        self.hex = [0x00 for i in range(self.totalBytes)]
        for i in range(self.width):
            for j in range(self.height):
                self.pixelsBinary[i][j] = 0

    """INPUT HANDLING"""

    def handleMouse(self, event, screen):
        LEFT_CLICK = 1
        WHEEL_CLICK = 2
        RIGHT_CLICK = 3

        """MOUSE BUTTON DOWN"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == LEFT_CLICK:  # Left Click will draw to the screen
                self.action = Act.DRAWING
                pygame.mouse.set_cursor(*pygame.cursors.tri_left)

            if event.button == RIGHT_CLICK:  # Right Click will erase from the screen
                self.action = Act.ERASING
                pygame.mouse.set_cursor(*pygame.cursors.broken_x)

            if event.button == WHEEL_CLICK:  # Middle Mouse Button will make a selection
                self.action = Act.SELECTING
                pygame.mouse.set_cursor(*pygame.cursors.diamond)

            if event.button == LEFT_CLICK or event.button == RIGHT_CLICK or event.button == WHEEL_CLICK:
                self.copySelectionToPixelsBinary()
                self.clearSelection()

        """MOUSE BUTTON UP"""
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == LEFT_CLICK or event.button == RIGHT_CLICK or event.button == WHEEL_CLICK:
                self.saveScreenToHistory()
                self.action = Act.IDLE
                pygame.mouse.set_cursor(*pygame.cursors.tri_left)

        """MOUSE WHEEL"""
        # Mouse Wheel will change the size of your brush
        if event.type == pygame.MOUSEWHEEL:
            self.brushSize += event.y

            # Asser that the brush is a certain size
            if self.brushSize < 1:
                self.brushSize = 1
            if self.brushSize > Editor.maxBrushSize:
                self.brushSize = Editor.maxBrushSize

        pass

    def handleKeyboard(self, event, screen):
        if event.type == pygame.KEYDOWN:

            # Save Image to CSV Bitmap
            if event.key == pygame.K_PAGEUP:
                self.translateHexadecimal(True)
                # self.translateBinary(True)

            # Load Image from CSV Bitmap
            if event.key == pygame.K_PAGEDOWN:
                location = input("Input image location to load (Enter nothing to cancel): ")
                if location == "":
                    return False

                # Try to safely find the file specified by the user
                try:
                    self.loadImgFromFile(location)
                    self.saveFileName = location
                except FileNotFoundError:
                    try:
                        self.loadImgFromFile("Data/" + location)
                        self.saveFileName = location
                    except FileNotFoundError:
                        print("File was not found")
                return True

            # Clear Selections
            if event.key == pygame.K_ESCAPE:
                self.copySelectionToPixelsBinary()
                self.clearSelection()
                self.saveScreenToHistory()

            # Undo
            if event.key == pygame.K_z:
                self.undo()

            # Redo
            if event.key == pygame.K_y:
                self.redo()

            # Cut
            if event.key == pygame.K_x or event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                self.cut()
                self.saveScreenToHistory()

            # Move Image Using Arrow Keys
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.moving = Dir.NORTH
                self.buttonsDown[0] = True
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                self.moving = Dir.EAST
                self.buttonsDown[1] = True
            if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.moving = Dir.SOUTH
                self.buttonsDown[2] = True
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                self.moving = Dir.WEST
                self.buttonsDown[3] = True

            # We want to move the selection on the frame that we press a button to move it
            if event.key == pygame.K_UP or event.key == pygame.K_w \
                    or event.key == pygame.K_RIGHT or event.key == pygame.K_d \
                    or event.key == pygame.K_DOWN or event.key == pygame.K_s \
                    or event.key == pygame.K_LEFT or event.key == pygame.K_a:
                self.moveSelection(self.moving)

        if event.type == pygame.KEYUP:
            # Move Image Using Arrow Keys
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.buttonsDown[0] = False
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                self.buttonsDown[1] = False
            if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.buttonsDown[2] = False
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                self.buttonsDown[3] = False

            if self.allButtonsUp():
                self.moving = Dir.IDLE

            if self.oneButtonDown():
                if self.buttonsDown[0]:
                    self.moving = Dir.NORTH
                if self.buttonsDown[1]:
                    self.moving = Dir.EAST
                if self.buttonsDown[2]:
                    self.moving = Dir.SOUTH
                if self.buttonsDown[3]:
                    self.moving = Dir.WEST

        return False

    def allButtonsUp(self):
        return not (self.buttonsDown[0] or self.buttonsDown[1] or self.buttonsDown[2] or self.buttonsDown[3])

    def oneButtonDown(self):
        counter = 0
        for i in range(4):
            if self.buttonsDown[i]:
                counter += 1
        return counter == 1

    def saveScreenToHistory(self):

        # You don't want to be able to redo after you make a new action
        while self.historyIndex > 0:
            self.history.pop()
            self.historyIndex -= 1

        # Make a copy of the current screen and save it in memory
        self.history.appendleft([[0 for i in range(self.height)] for j in range(self.width)])
        for i in range(self.width):
            for j in range(self.height):
                self.history[0][i][j] = self.pixelsBinary[i][j]

        # Make sure to limit the size of the Deque
        if len(self.history) > Editor.maxHistory:
            self.history.pop()

        # print(self.history[0])
        # self.history.

        return

    def undo(self):
        # You can't undo if there's nothing to undo
        # print(self.historyIndex+1, len(self.history))
        if self.historyIndex + 1 >= len(self.history):
            return

        self.historyIndex += 1
        self.copyHistoryToPixelsBinary()
        self.copyPixelsBinaryToDisplay()
        return

    def redo(self):
        # You can't redo something if there's nothing to redo
        if self.historyIndex < 1:
            return

        self.historyIndex -= 1

        self.copyHistoryToPixelsBinary()
        self.copyPixelsBinaryToDisplay()

        return

    def cut(self):
        for i in range(self.width):
            for j in range(self.height):
                if self.pixelsDisplay[i][j] == Editor.SELECT_DARK or self.pixelsDisplay[i][j] == Editor.SELECT_LIGHT:
                    self.pixelsBinary[i][j] = Editor.DARK
        return

    """UPDATE"""

    def update(self):
        """
        Brief
            Retrieves user mouse location and either draws or erases pixels depending on if the user is pressing
            the left or right mouse button respectively.

        Note
            Whether the left or right mouse button is pressed is determined by the "handleMouse" function
        """

        pos = pygame.mouse.get_pos()
        x_index = 0
        y_index = 1

        # Clear the highlights from last frame
        self.clearHighlights()

        # Raw x/y position
        self.x = pos[x_index]
        self.y = pos[y_index]

        # The resolution needs to be downscaled to have your mouse correspond with the correct pixel
        pixelX = int(self.x / self.screenMultiplier)
        pixelY = int(self.y / self.screenMultiplier)

        startX = pixelX - int(self.brushSize / 2)
        endX = pixelX + int(self.brushSize / 2)
        startY = pixelY - int(self.brushSize / 2)
        endY = pixelY + int(self.brushSize / 2)

        # Update each pixel that the user is editing
        self.editPixel(pixelX, pixelY)
        for i in range(startX, endX):
            for j in range(startY, endY):
                if 0 <= i < self.width and 0 <= j < self.height:
                    self.editPixel(i, j)

        return

    def editPixel(self, i, j):
        if self.action == Act.DRAWING:
            self.pixelsDisplay[i][j] = Editor.LIGHT
            self.pixelsBinary[i][j] = Editor.LIGHT
        if self.action == Act.ERASING:
            self.pixelsDisplay[i][j] = Editor.DARK
            self.pixelsBinary[i][j] = Editor.DARK
        if self.action == Act.IDLE:
            if self.pixelsDisplay[i][j] == Editor.DARK:
                self.pixelsDisplay[i][j] = Editor.HIGHLIGHT
        if self.action == Act.SELECTING:
            if self.pixelsBinary[i][j] == Editor.LIGHT:
                self.pixelsDisplay[i][j] = Editor.SELECT_LIGHT
            if self.pixelsBinary[i][j] == Editor.DARK:
                self.pixelsDisplay[i][j] = Editor.SELECT_DARK
        return

    def moveSelection(self, direction):
        """
        Brief
            Translate the image in the four cardinal directions

        :param direction: Determined by the user input arrow keys
        :return Whether the selection is moving
        """
        if direction == Dir.IDLE:
            return False

        oldPixelsDisplay = [[0 for j in range(self.height)] for i in range(self.width)]

        for i in range(self.width):
            for j in range(self.height):
                oldPixelsDisplay[i][j] = self.pixelsDisplay[i][j]

        for i in range(self.width):
            for j in range(self.height):
                if direction == Dir.NORTH:
                    if j + 1 < self.height:
                        if self.isSelected(oldPixelsDisplay[i][j + 1]):
                            self.pixelsDisplay[i][j] = oldPixelsDisplay[i][j + 1]
                            self.pixelsDisplay[i][j + 1] = Editor.DARK
                    else:
                        self.pixelsDisplay[i][j] = Editor.DARK

                if direction == Dir.WEST:
                    if i + 1 < self.width:
                        if self.isSelected(oldPixelsDisplay[i + 1][j]):
                            self.pixelsDisplay[i][j] = oldPixelsDisplay[i + 1][j]
                            self.pixelsDisplay[i + 1][j] = Editor.DARK
                    else:
                        self.pixelsDisplay[i][j] = Editor.DARK

        for i in range(self.width - 1, -1, -1):
            for j in range(self.height - 1, -1, -1):
                if direction == Dir.EAST:
                    if i - 1 >= 0:
                        if self.isSelected(oldPixelsDisplay[i - 1][j]):
                            self.pixelsDisplay[i][j] = oldPixelsDisplay[i - 1][j]
                            self.pixelsDisplay[i - 1][j] = Editor.DARK
                    else:
                        self.pixelsDisplay[i][j] = Editor.DARK

                if direction == Dir.SOUTH:
                    if j - 1 >= 0:
                        if self.isSelected(oldPixelsDisplay[i][j - 1]):
                            self.pixelsDisplay[i][j] = oldPixelsDisplay[i][j - 1]
                            self.pixelsDisplay[i][j - 1] = Editor.DARK
                    else:
                        self.pixelsDisplay[i][j] = Editor.DARK

        return True

    def clearHighlights(self):
        """
        Brief
            Clears the highlights drawn to the screen in the last frame
        """

        for i in range(self.width):
            for j in range(self.height):
                if self.pixelsDisplay[i][j] == Editor.HIGHLIGHT:
                    self.pixelsDisplay[i][j] = Editor.DARK
        return

    def clearSelection(self):
        """
        Brief
            Clears the selections drawn with the middle mouse button
        """
        for i in range(self.width):
            for j in range(self.height):
                if self.pixelsDisplay[i][j] == Editor.SELECT_LIGHT:
                    self.pixelsDisplay[i][j] = Editor.LIGHT

                if self.pixelsDisplay[i][j] == Editor.SELECT_DARK:
                    self.pixelsDisplay[i][j] = Editor.DARK

        return

    """DRAW TO SCREEN"""

    def draw(self, pyScreen):
        """
        Brief
            Draws a single frame to screen
        """

        pyScreen.fill(Editor.getColorFromTint(Editor.background))

        for i in range(self.width):
            for j in range(self.height):
                x = i * self.screenMultiplier
                y = j * self.screenMultiplier

                color = Editor.getColorFromTint(Editor.screenColor[self.pixelsBinary[i][j]])
                if self.isSelected(self.pixelsDisplay[i][j]) or self.pixelsDisplay[i][j] == Editor.HIGHLIGHT:
                    color = Editor.getColorFromTint(Editor.screenColor[self.pixelsDisplay[i][j]])
                size = self.screenMultiplier - Editor.borderSize
                pygame.draw.rect(pyScreen, color, pygame.Rect(x, y, size, size), 10)
        pass

    def isProtectedPixel(self, i, j):
        return self.pixelsDisplay[i][j] == Editor.LIGHT or \
               self.pixelsDisplay[i][j] == Editor.SELECT_LIGHT or \
               self.pixelsDisplay[i][j] == Editor.SELECT_DARK

    """DATA CONVERSIONS"""

    def translateBinary(self, printBinary):
        """
            Translate the 1/0 pixel values of the screen into an array of Octets
            The screen on the xmegaC3-Xplained starts drawing in the top left corner,
            Draws one byte of information vertically, then moves one pixel right and does it again.
            Therefore, because this tool renders our pixels array to the screen differently,
            We need to translate it.

            1 ||||||||||||||||||||
            2 ||||||||||||||||||||
            3 ||||||||||||||||||||
            4 ||||||||||||||||||||

            If this is our screen above, we need to store all of our information from line 1,
            then from line 2, then line 3, and finally line 4. Keep in mind that each pipe '|'
            consists of 8 pixels (A byte of information). Thus, this example would be 32 pixels in height
        """

        if self.isReadHorizontally:
            for i in range(self.height):
                for j in range(self.width):
                    byteIndex = (i * self.totalCols) + int((j / 8))
                    bitIndex = 7 - (j % 8)
                    self.binary[byteIndex][bitIndex] = self.pixelsBinary[j][i]
        else:
            for i in range(self.totalRows):
                rowY = i * 8  # The top y coordinate of the row is the row index * 8
                for j in range(self.width):
                    for k in range(rowY, rowY + 8):
                        byteIndex = (i * self.width) + j
                        bitIndex = k % 8
                        if k >= self.height:  # If your selected screen height is not a multiple of 8
                            self.binary[byteIndex][bitIndex] = 0  # Fill in the array with 0
                        else:
                            self.binary[byteIndex][bitIndex] = self.pixelsBinary[j][k]

        if printBinary:
            for i in range(self.totalBytes):
                print(self.binary[i])
        pass

    def translateHexadecimal(self, printHex):
        """
        Brief
            See "translateBinary()" for a deeper explanation of the data. This function just
            translates the data created there into hexadecimal
        :param printHex: Whether you will print the data to a file
        """
        self.translateBinary(False)

        # This is just a calculator that sums up the binary value into decimal, then just uses the hex() function
        # to translate the decimal form to hex. A little inefficient, but simple.
        for i in range(self.totalBytes):
            total = 0
            for j in range(8):
                exp = j % 8
                if self.binary[i][j]:
                    total += pow(2, exp)

            self.hex[i] = hex(total)

        if printHex:
            try:
                self.saveImgToFile("Data/", "")
            except FileNotFoundError:
                try:
                    self.saveImgToFile("", "")
                except FileNotFoundError:
                    print("File location entered is not valid")
        pass

    def saveImgToFile(self, directory, file):
        """
        Brief
            Saves your image to a comma separated value file in groups of hexadecimal octets (0-255 | 0x00 - 0xFF)
        :param directory: Name of the directory to save the file
        :param file: What the name of the file should be
        """
        location = directory + file
        if file == "":
            file = input("Enter a file location to save your data: ")
            if file == "":
                location = self.hexDataLoc
            else:
                location = directory + file

        self.saveFileName = file

        hexData = open(location, 'w')
        hexData.write("{},\n".format(self.width))
        hexData.write("{},\n".format(self.height))
        hexData.write("{},\n".format(Editor.numHexValuesPerLine))
        totalLines = int(self.totalBytes / Editor.numHexValuesPerLine)
        if not totalLines % Editor.numHexValuesPerLine == 0:
            totalLines += 1
        hexData.write("{},\n".format(totalLines))
        hexData.write("{},\n".format(self.totalBytes))

        for i in range(self.totalBytes):
            hexData.write("{:>4}, ".format(self.hex[i]))  # Don't change {:>4} unless you change the file reader
            if i % Editor.numHexValuesPerLine == Editor.numHexValuesPerLine - 1:
                hexData.write("\n")
            # hexData.write("{:>4}, ".format(self.hex[i]))  # Don't change {:>4} unless you change the file reader
        hexData.close()
        pass

    def loadImgFromFile(self, location):
        hexData = open(location, 'r')

        """Read File Settings"""
        self.width = int(hexData.readline().removesuffix(",\n"))
        self.height = int(hexData.readline().removesuffix(",\n"))
        numHexValuesPerLine = int(hexData.readline().removesuffix(",\n"))
        numLines = int(hexData.readline().removesuffix(",\n"))
        numBytes = int(hexData.readline().removesuffix(",\n"))

        hexArray = []

        """Read Hex Values"""
        k = 0
        for i in range(numLines):
            if k < numBytes:
                hexArray.append(literal_eval(hexData.read(5).removeprefix(" ").removesuffix(",")))
            k += 1
            for j in range(numHexValuesPerLine - 1):
                if k < numBytes:
                    hexArray.append(literal_eval(hexData.read(6).removeprefix(" ").removeprefix(" ").removesuffix(",")))
                k += 1
            hexData.readline()

        hexData.close()
        self.initDatastructures()
        self.setPixelsFromHex(hexArray)
        self.copyPixelsBinaryToDisplay()
        return

    def setPixelsFromHex(self, hexArray):
        """
        Brief
            Sets the pixels on the screen to match the
            :parameter hexArray (hexadecimal array)
        """
        self.binary = self.getBinaryFromHex(hexArray)

        if Editor.isReadHorizontally:
            for i in range(self.height):
                for j in range(self.width):
                    byteIndex = (i * self.totalCols) + int((j / 8))
                    bitIndex = j % 8
                    self.pixelsBinary[j][i] = self.binary[byteIndex][bitIndex]
        else:
            for i in range(self.totalRows):
                for j in range(self.width):
                    for k in range(8):
                        byteIndex = (i * self.width) + j
                        y = 8 * i + (7 - k)
                        if y < self.height:
                            self.pixelsBinary[j][y] = self.binary[byteIndex][k]
        return

    def getBinaryFromHex(self, hexArray):
        """
        Brief
            :returns a multidimensional array of binary values that match the data specified within the
            single dimensional array :parameter hexArray
        """
        binaryArray = [[0 for i in range(8)] for j in range(self.totalBytes)]

        # Convert into binary
        for i in range(self.totalBytes):
            for j in range(8):
                binaryValue = pow(2, (7 - j))
                if i < len(hexArray):
                    if hexArray[i] >= binaryValue:
                        binaryArray[i][j] = 1
                        hexArray[i] -= binaryValue
                    else:
                        binaryArray[i][j] = 0
                else:
                    binaryArray[i][j] = 0
        return binaryArray

    # getBinFromHex is NOT FUNCTIONAL in its current state
    def getBinFromHex(self, hexArray):
        binaryArray = [self.totalBytes]
        # Convert into binary
        for i in range(self.totalBytes):
            if i < len(hexArray):
                binaryArray[i] = bin(hexArray[i])
            else:
                binaryArray[i] = int('00000000', 2)

        for i in range(self.totalRows):
            rowY = i * 8  # The top y coordinate of the row is the row index * 8
            for j in range(self.width):
                for k in range(rowY, rowY + 8):
                    byteIndex = (i * self.width) + j
                    if binaryArray[byteIndex] % 2 == 0:
                        self.pixelsBinary[j][k] = 0
                    else:
                        self.pixelsBinary[j][k] = 1
                    binaryArray[byteIndex] >> 1
        return binaryArray

    """SCREEN CONVERSIONS"""

    def copyPixelsBinaryToDisplay(self):
        for i in range(self.width):
            for j in range(self.height):
                self.pixelsDisplay[i][j] = self.pixelsBinary[i][j]

    def copyPixelsDisplayToBinary(self):
        for i in range(self.width):
            for j in range(self.height):
                newValue = Editor.DARK
                if self.pixelsDisplay[i][j] == Editor.LIGHT or self.pixelsDisplay[i][j] == Editor.SELECT_LIGHT:
                    newValue = Editor.LIGHT
                self.pixelsBinary[i][j] = newValue

    def copySelectionToPixelsBinary(self):
        for i in range(self.width):
            for j in range(self.height):
                if self.pixelsDisplay[i][j] == Editor.SELECT_LIGHT:
                    self.pixelsBinary[i][j] = Editor.LIGHT
                if self.pixelsDisplay[i][j] == Editor.SELECT_DARK:
                    self.pixelsBinary[i][j] = Editor.DARK

    def copyHistoryToPixelsBinary(self):
        for i in range(self.width):
            for j in range(self.height):
                self.pixelsBinary[i][j] = self.history[self.historyIndex][i][j]

        return

    @staticmethod
    def getColorFromTint(tint):
        return tint, tint, tint

    @staticmethod
    def isSelected(value):
        return value == Editor.SELECT_DARK or value == Editor.SELECT_LIGHT


from enum import Enum


class Dir(Enum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3
    IDLE = -1


class Act(Enum):
    IDLE = 0
    DRAWING = 1
    ERASING = 2
    SELECTING = 3


class Select(Enum):
    COPY = 0
    CUT = 1


class Pix(Enum):
    DARK = 0
    LIGHT = 1
    HIGHLIGHT = 2
    SELECTION = 3
    SELECTION_LIGHT = 4
