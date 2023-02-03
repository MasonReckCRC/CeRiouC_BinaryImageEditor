# CeRiouC_BinaryImageEditor
Image Editor and Painting Tool for small microcontroller binary pixel screens written in python
IDE used is PyCharm, I will make a runnable application for this soon (check if there is one already). 


Tool will store image data as bitmaps ordered in the fashion that small binary displays generally read. 


            To translate the 1/0 pixel values of the screen into an array of Octets
            These small displays generally start drawing in the top left corner,
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
