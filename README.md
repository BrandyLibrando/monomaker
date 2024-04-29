# MonoMaker
An image to byte array converter script using Python, mainly to be used for displaying images in monochrome displays such as the SSD1306.


## Description and Use
This script allows converting images -- monochromatic or not -- into monochrome images represented as a byte array (in hex). It computes the luminance manually, while allowing transparency values to be included in the computation, if there exists an alpha channel. Additionally, the threshold for luminance can be specified by the user, which can be helpful for converting colored images (with enough contrast between the colors). However, the features are quite limited; *please refer to the "Caveats/Notes" and "Configurations" to see if the script can be used to your needs.*

*Simply download and move the "main.py" script to a directory/folder that contains the image you would like to convert, then run the script and enter the desired configuration settings as asked.* It is suggested that the script and the image are isolated in a dedicated directory to ensure a smooth operation. You may rename the script to whatever filename you like. You may run the .py directly which will cause a terminal to appear, or run the script through an IDE of your choice.

The output of the program is a .txt file containing C code that has the configuration settings entered by the user (as a comment), 2 variables containing the width and height, and the byte array for the image itself. The output byte array is based on byte arrays as used by the Adafruit SSD1306 library. You may then copy the output string containing the dimensions and the byte array into your code, and manipulate it however you like.


## Caveats/Notes
- Image file should be located in the same directory/folder as the script.
- A subdirectory named "out" will be generated by the script to store the outputs. If a folder named "out" already exists in the same directory as the script, the outputs will be stored there.
- Palettized images will not work (indexed color mode). As a consequence, GIFs are not supported.
- Animated image types are not supported.
- Not all image files are guaranteed to work (e.g., palettized PNGs might fail). But in general, PNGs, BMPs, and JPGs/JPEGs should work.
- Transparency is supported.
- Other features not specified in the "Configurations" section, such as file resizing and endianness, are not included.


## Configurations
Upon executing the .py file, the user will be asked for several inputs, which will affect the output of the program. All the inputs are detailed below:
- ### Filename
  `Please enter the filename, including the file extension:`

  The filename and extension of your image. Case-insensitive.
- ### Luminance Threshold
  `Type in the luminance threshold (a number from 0 to 1, default = 0.5):`

  The threshold for luminance. A value closer to 0 will make the converter stricter in perceiving darks (e.g., a value of 0.01 would only consider colors very close to black as "dark", a gray like #777 will be considered "light"). Likewise, a value closer to 1 will make the script stricter to lights. Proceeding without an input will use a threshold of 0.5. For purely black and white photos, simply use the default.
- ### Invert Image
  `Type 'y' if dark colors are treated as 1, 'n' if 0:`

  To put it short, typing "y" inverts the picture, while typing "n" does not, assuming that you would like to draw the "whites" on the display.

  Normally, darks are treated as "0" and lights as "1", which is helpful if the color you'd like to draw on the display is light. This applies for most cases anyway, and if it applies to you, simply enter "n". However, if the image is, say, "black-on-white", and you'd like to draw the darks instead, you'll want to invert the treatment and have the darks be considered as "1" instead. Enter "y" if this is the case.
- ### Transparency Handling
  `Type 'y' if transparency is treated as lightness, 'n' if as darkness:`

  Entering "y" will cause the transparency to be treated as "lightness" (i.e., the more transparent, the more "white" the pixel is). Entering "n" will make the script treat transparency as a "dark" color. Helpful for images with transparent backgrounds, especially "black-on-clear" or "white-on"clear". The luminance value coming from the transparency is added to the luminance from the RGB values.
- ### Array Name
  `Input the name of your array:`

  The name of your byte array. This will also be the name of the dimension variables, with the names "width" and "height" appended at the end of the name. For example, entering "brandy" would make a byte array named "brandy[]", a width variable "brandywidth", and a height variable "brandyheight".
- ### Newlines per Row in Byte Array
  `Type 'y' if newlines to be added per row of pixel in output file, 'n' if none (Default: N):`
  In most cases, you'll want to use the default (entering "n" or entering a blank input), which does not add a new line per row of pixels in the byte array string output. This will put the byte array contents in a single line. 
- ### Output Filename
  `Please enter the filename of the output
(no file extension, file is saved as .txt):`

  The filename of the output .txt file. If a file with the same filename entered already exists, the user will be asked to confirm overwrite. Entering "y" will overwrite the file; entering "n" will cause the script to ask for a new filename.


## Dependencies
This script uses Pillow and Numpy. Kindly install them if you do not already have them using `pip install`. Windows users may do so by entering the following in their terminal/command prompt:
- `py -m pip install Pillow`
- `py -m pip install numpy`
