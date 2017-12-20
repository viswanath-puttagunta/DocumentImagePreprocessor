from PIL import Image, ImageFilter
import sys
import os

WINDOW_HEIGHT = 25
THRESHOLD = 0.01
STRIDE_HEIGHT = 10
SEGMENTS_IN_BAND = 5

def grey_scale_color_invert(in_img):
    '''
    in_img: Input image. Only single color band
    out_img: Output Image. Only single color band
    '''
    out_img = Image.new(in_img.mode, in_img.size)
    in_data = list(in_img.getdata())
    out_data = [255-x for x in in_data]
    out_img.putdata(out_data)
    return out_img

def signal_in_band(region, window_width, threshold=THRESHOLD):
    width, height = region.size
    num_iterations = width /window_width - 1
    for i in range(num_iterations):
        box = (i*window_width, 0, (i+1)*window_width - 1,height)
        sub_region = region.crop(box)
        pixels = list(sub_region.getdata())
        avg = sum(pixels) / float(len(pixels))
        if avg > threshold:
            return True
    return False

def remove_white_bands(original, 
                       window_height=WINDOW_HEIGHT, 
                       stride_height = STRIDE_HEIGHT,
                       segments_in_band = SEGMENTS_IN_BAND):
    #Sanity Check (Make sure size of images are same)
    # TBD
    #Have a white region
    white_region = Image.new(original.mode, (original.width, window_height))
    out_image = Image.new(original.mode, original.size)
    window_width = original.width/segments_in_band
    num_iterations = original.height / stride_height
    input_y = 0
    output_y = 0
    for i in range(num_iterations):
        #Select input band from original
        box = (0,input_y, original.width, input_y + window_height)
        region = original.crop(box)
        if(signal_in_band(region, window_width) == True):
            #Copy this region to output
            out_image.paste(white_region, (0,output_y, original.width, region.height+output_y))
            out_image.paste(region, (0,output_y, original.width, region.height+output_y))
            #Update outputy
            output_y = output_y + stride_height
        #Update input_y regardless
        input_y = input_y + stride_height
    return out_image

def get_jpgs_dir(input_dir):
    outlist = list()
    for fname in os.listdir(input_dir):
        if fname.split(".")[-1] == "jpg":
            img = Image.open(input_dir + "/" + fname).split()[0]
            outlist.append(img)
    return outlist

def club_imgs(img_list):
    max_width = max([img.width for img in img_list])
    max_height = sum([img.height for img in img_list])
    clubbed_img = Image.new(img_list[0].mode, (max_width, max_height))
    img_y = 0
    for img in img_list:
        clubbed_img.paste(img, (0, img_y, img.width, img_y + img.height))
        img_y = img_y + img.height
    return clubbed_img

def process_jpgs_dir(input_dir):
    jpgfiles = get_jpgs_dir(input_dir)
    jpgfiles = [grey_scale_color_invert(x) for x in jpgfiles]
    clubbedjpg = club_imgs(jpgfiles)
    outjpg = remove_white_bands(clubbedjpg)
    return grey_scale_color_invert(outjpg)

