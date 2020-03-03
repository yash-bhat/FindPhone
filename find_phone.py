from torchvision import transforms
from utils import *
from PIL import Image, ImageDraw, ImageFont
import sys
import cv2
import glob
#CHANGE
# from IPython.display import display

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load model checkpoint
checkpoint = 'checkpoint_ssd300.pth.tar'
checkpoint = torch.load(checkpoint)
start_epoch = checkpoint['epoch'] + 1
print('\nLoaded checkpoint from epoch %d.\n' % start_epoch)
model = checkpoint['model']
model = model.to(device)
model.eval()

# Transforms
resize = transforms.Resize((300, 300))
to_tensor = transforms.ToTensor()
normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])


def detect(original_image, min_score, max_overlap, top_k, suppress=None):
    """
    Detect objects in an image with a trained SSD300, and visualize the results.

    :param original_image: image, a PIL Image
    :param min_score: minimum threshold for a detected box to be considered a match for a certain class
    :param max_overlap: maximum overlap two boxes can have so that the one with the lower score is not suppressed via Non-Maximum Suppression (NMS)
    :param top_k: if there are a lot of resulting detection across all classes, keep only the top 'k'
    :param suppress: classes that you know for sure cannot be in the image or you do not want in the image, a list
    :return: annotated image, a PIL Image
    """

    # Transform
    image = normalize(to_tensor(resize(original_image)))

    # Move to default device
    image = image.to(device)

    # Forward prop.
    predicted_locs, predicted_scores = model(image.unsqueeze(0))

    # Detect objects in SSD output
    det_boxes, det_labels, det_scores = model.detect_objects(predicted_locs, predicted_scores, min_score=min_score,
                                                             max_overlap=max_overlap, top_k=top_k)

    # print('det_boxes',float(det_boxes[0][0][0]),float(det_boxes[0][0][1]),float(det_boxes[0][0][2]),float(det_boxes[0][0][3]))
    a,b,c,d = float(det_boxes[0][0][0]),float(det_boxes[0][0][1]),float(det_boxes[0][0][2]),float(det_boxes[0][0][3])
    # a,b,c,d = det_boxes[0]
    # print('center:')
    cx,cy = round((a+c)/2,4),round((b+d)/2,4) 
    # print(cx,cy)

    # Move detections to the CPU
    det_boxes = det_boxes[0].to('cpu')

    # Transform to original image dimensions
    original_dims = torch.FloatTensor(
        [original_image.width, original_image.height, original_image.width, original_image.height]).unsqueeze(0)
    det_boxes = det_boxes * original_dims

    # Decode class integer labels
    det_labels = [rev_label_map[l] for l in det_labels[0].to('cpu').tolist()]

    # If no objects found, the detected labels will be set to ['0.'], i.e. ['background'] in SSD300.detect_objects() in model.py
    if det_labels == ['background']:
        # Just return original image
        return original_image

    # Annotate
    annotated_image = original_image
    draw = ImageDraw.Draw(annotated_image)

    # draw.point((0.1947, 0.2908), 'red')


    #CHANGE
    # font = ImageFont.truetype("./calibril.ttf", 15)
    font = ImageFont.truetype("./arial.ttf", 15)

    # Suppress specific classes, if needed
    for i in range(det_boxes.size(0)):
        if suppress is not None:
            if det_labels[i] in suppress:
                continue

        # Boxes
        box_location = det_boxes[i].tolist()
        # print('box_location',box_location)
        draw.rectangle(xy=box_location, outline=label_color_map[det_labels[i]])
        # draw.point(xy=[95.39,167.26],fill='purple')
        # draw.point(xy=[142.48,167.26],fill='red')
        # draw.point(xy=[142.48,222.67],fill='green')
        # draw.point(xy=[95.39,222.67],fill='blue')
        # #center
        # draw.point(xy=[(142.48 + 95.39)//2,(222.67 + 167.26)//2],fill='orange')

        
        # draw.rectangle(xy=[l + 1. for l in box_location], outline=label_color_map[
        #     det_labels[i]])  # a second rectangle at an offset of 1 pixel to increase line thickness
        # draw.rectangle(xy=[l + 2. for l in box_location], outline=label_color_map[
        #     det_labels[i]])  # a third rectangle at an offset of 1 pixel to increase line thickness
        # draw.rectangle(xy=[l + 3. for l in box_location], outline=label_color_map[
        #     det_labels[i]])  # a fourth rectangle at an offset of 1 pixel to increase line thickness

        # Text
        text_size = font.getsize(det_labels[i].upper())
        text_location = [box_location[0] + 2., box_location[1] - text_size[1]]
        textbox_location = [box_location[0], box_location[1] - text_size[1], box_location[0] + text_size[0] + 4.,
                            box_location[1]]
        draw.rectangle(xy=textbox_location, fill=label_color_map[det_labels[i]])
        draw.text(xy=text_location, text=det_labels[i].upper(), fill='white',
                  font=font)
    del draw

    #display(annotated_image)
    annotated_image.show()


    return annotated_image, (cx,cy)


if __name__ == '__main__':
    #CHANGE 
    # img_path = './data/JPEGImages/1.jpg'
    labels = []
    inputs = []
    img_path = sys.argv[1]


    # for filename in glob.glob(img_path+'/*.jpg'):
    #     # print(filename)
    #     img=Image.open(filename,mode='r')
    #     inputs.append(img)

    #     # for inp in inputs:


    #     # for input in inputs:
    original_image = Image.open(img_path, mode='r')
    # original_image = img
    original_image = original_image.convert('RGB')
    # original_image.show()

    #CHANGE
    # detect(original_image, min_score=0.2, max_overlap=0.5, top_k=200).show()
    im, c = detect(original_image, min_score=0.6, max_overlap=0.5, top_k=200)
    # labels.append(c)
    print(c[0],c[1])
    # im.show()


