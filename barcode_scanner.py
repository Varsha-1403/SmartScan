import cv2
from pyzbar.pyzbar import decode

def extract_barcode(image_path):
    image = cv2.imread(image_path)
    barcodes = decode(image)

    if barcodes:
        return barcodes[0].data.decode("utf-8")
    return None
