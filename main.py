################################################
#                                              #
#  Mono Maker - Image to Mono Converter        #
#                                              #
#  Author: Julius Alvin (Andy) Librando        #
#  Created: April 22, 2024                     #
#  Last modified: April 28, 2024               #
#                                              #
#  Description:                                #
#  Running this script converts an image into  #
#  a monochrome image represented as a byte    #
#  array, which is mainly used for displays,   #
#  such as the SSD1306.                        #
#                                              #
################################################

from PIL import Image
import numpy as nmp
import os

# Notes:
# - Image file to be converted MUST be located in the same directory as the script.
# - A directory (folder) "out" is created to store the output. Having a folder with the same name would
#   cause the script to use that folder instead.
# - Not all image file types are guaranteed to work, and is programmed so far mainly for
#   PNG, BMP, and JPG/JPEG image files (transparency supported). Other file types may still work
#   since the channels are checked, not the image format (except for PNG).
# - Palettized images will not work. Convert the image to RGB space beforehand.
# - Using animated/multiframe image types will not work.


### Get filename
filename = input("Please enter the filename, including the file extension: ")

### Assign necessary filepaths
dirname = os.path.dirname(os.path.abspath(__file__))
srcpath = os.path.join(dirname, filename)

### Create output directory if none yet
outpath = os.path.join(dirname, 'out')
os.makedirs(outpath, exist_ok = True)


### Open image file
try:
    with Image.open(srcpath) as im:
        image = im
        
        ### Process image file
        data = nmp.array(image)
        
        ### List for storing binary representation of monochrome picture
        binarylist = list()
        
        
        ### Identifying luminance threshold for classifying pixel class
        fixed = False
        while True:
            try:
                threshold = input("\nType in the luminance threshold (a number from 0 to 1, default = 0.5): ").strip(' \t\n\r')
                # Assign default value if input is empty
                if threshold == "":
                    threshold = 0.5
                    fixed = True
                else:
                    threshold = float(threshold)
            except ValueError:
                print("Please enter a numeric input, between the range specified.")
                continue
            else: break
        
        ### Determining threshold if input is outside [0, 1]
        if threshold < 0 and not fixed: threshold = 0
        elif threshold > 1 and not fixed: threshold = 1
        
        
        ### Ask for input if darker colors corresponds to 1 or 0
        dark_is_zero = True
        dark_in = input("\nType \'y\' if dark colors are treated as 1, \'n\' if 0: ").strip(' \t\n\r')
        while dark_in.lower() != 'y' and dark_in.lower() != 'n':
            dark_in = input("Please choose between \'y\' or \'n\'.\n\nType \'y\' if dark colors are treated as 1, \'n\' if 0: ").strip(' \t\n\r')
        if dark_in.lower() == 'y': dark_is_zero = False
        else: dark_is_zero = True
        
        
        ### Ask for input if transparent pixels are treated as bright or dark
        alpha_factor = 0
        alpha_in = input("\nType \'y\' if transparency is treated as lightness, \'n\' if as darkness: ").strip(' \t\n\r')
        while alpha_in.lower() != 'y' and alpha_in.lower() != 'n':
            alpha_in = input("Please choose between \'y\' or \'n\'.\n\nType \'y\' if transparency is treated as lightness, \'n\' if as darkness: ").strip(' \t\n\r')
        if alpha_in.lower() == 'y': alpha_factor = 1
        else: alpha_factor = 0
        
        
        ### Display review of image information
        print("\n**************************\n  IMAGE REVIEW\n  Bands/Channels: " + ''.join(image.getbands()) + "\n  Format: " + str(image.format) +
              "\n  Width: " + str(image.width) + "\n  Height: " + str(image.height) + "\n**************************")
        
        
        ### Pixel value parsing and processing
        # Setting binary representation of darks and lights
        if dark_is_zero: darks, lights = '0', '1'
        else: darks, lights = '1', '0'
            
        # Check for PNG image files with RGBA channels
        if image.format == "PNG" and len(image.getbands()) == 4:
            threshold *= 2   # Threshold is multiplied by two to accomodate the additional criteria of transparency
            for x in data:
                for xy in x:
                    RGBA = (xy[0] / 255.0, xy[1] / 255.0, xy[2] / 255.0, xy[3] / 255.0)   # Express RGBA values of a pixel as ratios to maximum values
                    L = RGBA[0]*0.2126 + RGBA[1]*0.7152 + RGBA[2]*0.0722 + (alpha_factor - RGBA[3])   # R+G+B constitutes 1, A constitutes 1
                    
                    if L >= threshold: binarylist.append(lights)
                    else: binarylist.append(darks)
        
        # Check for grayscale image files 
        elif image.getbands()[0] == 'L':
            if len(''.join(image.getbands()).strip(' ')) == 2:   # If alpha channel exists
                for x in data:
                    for y in x:
                        L = (y[0] / 255.0) + (alpha_factor - (y[1] / 255.0))   # Express "grayscale-ness" of a pixel as a ratio to maximum value -> 255
                        if L >= threshold: binarylist.append(lights)
                        else: binarylist.append(darks)
            else:
                for x in data:
                    for y in x:
                        L = y / 255.0   # Express "grayscale-ness" of a pixel as a ratio to maximum value -> 255
                        if L >= threshold: binarylist.append(lights)
                        else: binarylist.append(darks)
                    
        # Check for black and white image files
        elif image.getbands()[0] == '1':
            for x in data:
                for L in x:
                    if L: binarylist.append(lights)   # PIL recognizes white as "True"
                    else: binarylist.append(darks)
                    
        # Check for other image files, intended for image files with 3 channels (i.e., no alpha channel)
        # TODO: Add more conditions to satisfy other image files and properties that are not caught properly
        else:
            for x in data:
                for xy in x:
                    RGB = (xy[0] / 255.0, xy[1] / 255.0, xy[2] / 255.0)
                    L = RGB[0]*0.2126 + RGB[1]*0.7152 + RGB[2]*0.0722
                    
                    if L >= threshold: binarylist.append(lights)
                    else: binarylist.append(darks)
        
        # Setting parameters to be used for the output file generation
        width = image.width
        count = 0
        
        # Final width  -> width of the resulting byte array image is the nearest higher multiple of 8
        # Final height -> expected to be equal to the initial height of the image
        final_width = width if width % 8 == 0 else width + (8 - (width % 8))
        final_height = 0
        
        
        ### Processing output hex array in string form
        # Ask for input for the byte array name
        arrname = input("\nInput the name of your array: ")
        
        # Ask for input if newlines are to be added for every row of pixels generated in the byte array
        newline = 0   # Default is to not add newlines per row
        arrline = input("\nType \'y\' if newlines to be added per row of pixel in output file, \'n\' if none (Default: N): ").strip(' \t\n\r')
        while arrline.lower() != 'y' and arrline.lower() != 'n' and arrline.strip(' \t\n\r') != "":
            arrline = input("Please choose between \'y\' or \'n\'.\n\nType \'y\' if newlines to be added per row of pixel in output file, \'n\' if none: ").strip(' \t\n\r')
        if arrline.lower() == 'y': newline = 1
        else: newline = 0
        
        # Reverting threshold value back to the input if manipulated,
        # for setting up configuration settings in the output file
        threshold = threshold / 2.0 if image.format == "PNG" and len(image.getbands()) == 4 else threshold
        
        # Printing configuration settings,
        # which are basically the inputs of the user upon using this program
        output = "/**\nCONFIGURATION\n\nLuminance Threshold: " + str(threshold) + "\nDark is 0: " + str(bool(dark_is_zero))
        output += "\nTransparent is Dark: " + str(bool(not alpha_in)) + "\n**/\n\n"
        
        # Printing declaration of byte array
        output += "const unsigned char PROGMEM " + arrname + "[] = \n{\n"
        
        # Iteration through the binary list to construct the byte array
        while len(binarylist) > 0:
            if len(binarylist) >= 8:
                
                # The conditional checks if taking 8 bits would result to taking some bits from the next row,
                # which happens when the original width is not a multiple of 8.
                # The if clause is executed if not satisfied, which simply takes the next 8 bits as the next byte.
                if (count + 8) <= width:
                    temp = hex(int(''.join(binarylist[0:8]), 2))
                    binarylist = binarylist[8:]
                    count = count + 8 if count + 8 < width else 0   # Count := 0 if count == width since EOL is reached
                    
                # If satisfied, the else clause is executed, which takes the next few bits until the end of the row,
                # then pads it with additional zeroes until a complete byte (8 bits) is formed.
                else:
                    templist = list(binarylist[0:width - count])
                    for i in range(8 - (width - count)):
                        templist.append('0')
                    temp = hex(int(''.join(templist), 2))
                    binarylist = binarylist[width - count:]
                    count = 0
                    
                # Generated byte is appended to the output byte array string
                output += temp
                
                # Commas are added if there are still bits to be added
                if len(binarylist) > 0:
                    output += ", "
                    
                # Final height is incremented when a new row is reached
                if count == 0:
                    if newline: output += "\n" 
                    final_height += 1
            else:
                while len(binarylist) < 8:
                    binarylist.append('0')
                
        # Printing the last part of output and some useful variables
        # containing the width and height of the image formed by the resulting byte array 
        output += "\n};\n"
        output += "const int " + arrname + "width = " + str(final_width) + ";\n"
        output += "const int " + arrname + "height = " + str(final_height) + ";\n"
        
        
        ### Save output to a txt file
        while True:
            outname = input("\nPlease enter the filename of the output\n(no file extension, file is saved as .txt): ") + ".txt"
            outfilepath = os.path.join(outpath, outname)
            
            try:
                file = open(outfilepath, 'x')
            except FileExistsError:
                print("\nFile already exists. If you proceed, the file will be overwritten.")
                out_in = input("Would you like to proceed? [Y]es or [N]o: ").strip(' \t\n\r')
                while out_in.lower() != 'y' and out_in.lower() != 'n':
                    out_in = input("Please choose between \'y\' or \'n\'.\nWould you like to proceed? [Y]es or [N]o: ").strip(' \t\n\r')
                if out_in.lower() == 'y':
                    file = open(outfilepath, 'w')
                    file.write(output)
                    break
                else: continue
            else:
                file.write(output)
                break
        
        file.close()
        
        ### END OF PROGRAM IF NO ERRORS
        
            
### Show exception details if file cannot be opened
### (due to being nonexistent in the same directory as the script,
###  or being an unsupported file type).
except FileNotFoundError:
    print("ERROR: File \"" + filename + "\" not found. (Address: " + srcpath + ")")
except OSError:
    print("ERROR: File \"" + filename + "\" cannot be opened.")
