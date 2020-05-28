import cv2
import pytesseract
from pytesseract import Output

input_folder = "img-input/"
output_folder = "/Users/luudat/Downloads/temp/test-tesseract-and-abby/tesseract/text-blocks/"

for index in range(2, 12):
    print(f'Processing {index}.jpg')
    input_img_path = input_folder + f'{index}.jpg'
    img = cv2.imread(input_img_path)

    d = pytesseract.image_to_data(img, lang='vie', output_type=Output.DICT)
    n_boxes = len(d['text'])

    for i in range(n_boxes):
        if int(d['conf'][i]) > 60:
            (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            # print(f'{x} {y} {w} {y}')
            img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    # h, w, c = img.shape
    # boxes = pytesseract.image_to_boxes(img) 
    # for b in boxes.splitlines():
    #     b = b.split(' ')
    #     img = cv2.rectangle(img, (int(b[1]), h - int(b[2])), (int(b[3]), h - int(b[4])), (0, 255, 0), 2)

    output_img_path = output_folder + f'{index}-tesseract.png'
    cv2.imwrite(output_img_path, img)
    print(f'DONE!\n---------------------------')
