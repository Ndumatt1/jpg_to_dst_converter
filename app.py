from flask import Flask, request, jsonify, send_file
from PIL import Image
import numpy as np
from scipy import ndimage
import pyembroidery
import os

app = Flask(__name__)

def convert_image_to_stitches(image):

    grayscale_image = image.convert('L')

    
    grayscale_array = np.array(grayscale_image)

    
    binary_image = (grayscale_array < 128).astype(np.uint8)

    inverted_image = 1 - binary_image

    design = pyembroidery.EmbPattern()
    height, width = inverted_image.shape
    for y in range(height):
        for x in range(width):
            if inverted_image[y, x]:
                design.add_stitch_absolute(x, y)

    return design

@app.route('/convert', methods=['POST'])
def convert_to_dst():

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    if not file.filename.lower().endswith(('.jpg', '.jpeg')):
        return jsonify({'error': 'Invalid file format'}), 400

    try:
        image = Image.open(file)
    except Exception as e:
        return jsonify({'error': f'Error opening image: {str(e)}'}), 500

    try:
        design = convert_image_to_stitches(image)
    except Exception as e:
        return jsonify({'error': f'Error converting image to stitches: {str(e)}'}), 500

    dst_file_path = 'output.dst'
    try:
    # Check if the design is empty before writing to file
        if design.stitches:
            design.write(dst_file_path)
        else:
            raise ValueError("Design is empty and cannot be saved")
    except Exception as e:
        return jsonify({'error': f'Error saving DST file: {str(e)}'}), 500

    # Return the DST file as a downloadable attachment
    return send_file(dst_file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
