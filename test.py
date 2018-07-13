from PIL import Image
from pytesser import *
 

# image_file = Image.open('fnord.tif').convert('L')
# image_file.show()
# image_file.save('fnord-gs.png')


image_file = 'phototest.tif'
im = Image.open(image_file)
text = image_to_string(im)
text = image_file_to_string(image_file)
text = image_file_to_string(image_file, graceful_errors=True)

print("=====output=======\n")
print(text)