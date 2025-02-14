import os
import base64
import io
from openai import OpenAI
from flask import Flask, request, render_template, session, jsonify, redirect, url_for
from PIL import Image
from pdf2image import convert_from_bytes
from flask_session import Session
import config

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)

#api key so i DONT leak it lol
client = OpenAI(api_key=config.OPENAI_API_KEY)

@app.route('/')
def index():
    """
    Renders the main page for PDF upload and webcam capture.
    """
    return render_template('index.html')

def compress_image(pil_image):
    """Compress and resize the image to reduce its size"""
    if pil_image.mode == 'RGBA':
        pil_image = pil_image.convert('RGB')
    
    max_size = (800, 800)
    ratio = min(max_size[0] / pil_image.size[0], max_size[1] / pil_image.size[1])
    new_size = tuple([int(x * ratio) for x in pil_image.size])
    
    pil_image = pil_image.resize(new_size, Image.Resampling.LANCZOS)
    
    img_byte_arr = io.BytesIO()
    pil_image.save(img_byte_arr, format='JPEG', quality=60, optimize=True)
    return img_byte_arr.getvalue()

#upload a pdf and convert it to a series of images so 4o can read it 
@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    """
    Accepts a PDF file upload and converts it to a series of images
    """
    if 'pdf' not in request.files:
        return "No PDF file provided", 400

    pdf_file = request.files['pdf']
    try:
        pdf_bytes = pdf_file.read()
        pages = convert_from_bytes(pdf_bytes)
        
        first_page_bytes = compress_image(pages[0])
        session['current_page_image'] = base64.b64encode(first_page_bytes).decode('utf-8')
        
        session['current_page'] = 0
        session['total_pages'] = len(pages)
        session['pdf_bytes'] = base64.b64encode(pdf_bytes).decode('utf-8')
        
        return redirect(url_for('index'))
    except Exception as e:
        return f"Error processing PDF: {str(e)}", 500

# i might put it in the read.md to just upload the part of the pdf you need help with but idk
@app.route('/get_page/<int:page_num>', methods=['GET'])
def get_page(page_num):
    """
    Get a specific page from the PDF
    """
    if 'pdf_bytes' not in session:
        return jsonify({"error": "No PDF uploaded"}), 400
        
    try:
        pdf_bytes = base64.b64decode(session['pdf_bytes'])
        pages = convert_from_bytes(pdf_bytes)
        
        if page_num >= len(pages):
            return jsonify({"error": "Page number out of range"}), 400
            
        page_bytes = compress_image(pages[page_num])
        page_image = base64.b64encode(page_bytes).decode('utf-8')
        
        session['current_page'] = page_num
        session['current_page_image'] = page_image
        
        return jsonify({"page": page_image})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#this is the main function that will be used to analyze the image and the webcam image and generate the next step   
@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Processes the webcam image and current instruction page to generate the next step.
    """
    data = request.get_json()
    webcam_image_data = data.get('image_data')
    if not webcam_image_data:
        return jsonify({"error": "No image data provided"}), 400

    current_page_image = session.get('current_page_image')
    if not current_page_image:
        return jsonify({"error": "No PDF instructions uploaded"}), 400
#prompting to make it yap less to actually help
    prompt = (
        "You are analyzing assembly progress. You have two images:\n"
        "1. The instruction diagram showing how the assembly should look\n"
        "2. A webcam image showing the current state of the assembly\n\n"
        "Please:\n"
        "1. Compare the current state with the instructions\n"
        "2. Identify which step the user is currently on\n"
        "3. Provide clear instructions for the next step\n"
        "4. List any specific parts needed\n"
        "If you cannot determine the exact next step, explain what information is missing."
    )

    response = client.chat.completions.create(
        model="gpt-4o", #the model i am using but you can change it to whatever you want
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{current_page_image}"
                        }
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{webcam_image_data}"
                        }
                    }
                ],
            }
        ],
        max_tokens=500
    )
    
    return jsonify({"next_step": response.choices[0].message.content.strip()})

if __name__ == '__main__':
    app.run(debug=True)