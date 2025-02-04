import cv2
import pytesseract
import numpy as np
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

def read_text(image_path='data/IMG.png',read_mode='w+'):
    img=cv2.imread(image_path)
    if img is None:
       print("Failed to read image.")
    print(f"Image shape after reading: {img.shape}")

    print(f"Image shape before cvtColor: {img.shape}")
    gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    _, thresh1=cv2.threshold(gray,0,255,cv2.THRESH_OTSU|cv2.THRESH_BINARY_INV)

    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))
    dilation = cv2.dilate(thresh1, rect_kernel, iterations = 1)

    contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    im2=img.copy()

    file = open("data/recognized.txt", read_mode)
    file.write("")
    file.close()
    text = pytesseract.image_to_string(dilation,config='--psm 6')
    file = open("data/recognized.txt", "w+")
    file.write(text)
    file.write("\n")
    file.close()

    for cnt in contours:
        cv2.imshow(cnt)
        x, y, w, h = cv2.boundingRect(cnt)
    
        rect = cv2.rectangle(im2, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
        cropped = im2[y:y + h, x:x + w]
    
        file = open("data/recognized.txt", "a")
    
        text = pytesseract.image_to_string(cropped)
    
        file.write(text)
        file.write("\n")
    
        file.close()
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def read():
    # Clear the output file before processing
    with open("data/recognized.txt", "w") as file:
        file.write("")  # Clear file content

    # Read the input image and convert it to grayscale
    img = cv2.imread('data/IMG.png')
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise (helps improve thresholding)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Otsu's thresholding to segment the image
    ret, work_img = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Optionally, apply dilation to make the text thicker if it's thin
    dilated_img = cv2.dilate(work_img, np.ones((3, 3), np.uint8))
    cv2.imshow('Preprocessed Image', dilated_img)  # Display the preprocessed image
    
    # Use Tesseract OCR to extract text from the processed image
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(dilated_img, config=custom_config)

    # Write the recognized text to the output file
    with open("data/recognized.txt", "w") as file:
        file.write(text)

    # Optionally, show the image (you can close or save it after inspection)
    cv2.waitKey(0)
    cv2.destroyAllWindows()