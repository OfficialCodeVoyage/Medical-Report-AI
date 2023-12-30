from flask import Flask, render_template, request, redirect, url_for,flash,send_from_directory
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
import getpass
import os
from PIL import Image 
import requests
from langchain_core.messages import HumanMessage
from io import BytesIO
import tempfile
import time
from dotenv import load_dotenv

load_dotenv()
apikey = os.environ.get("API_KEY")


app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def generate_summary_with_image(image_url):
    llm = ChatGoogleGenerativeAI(model="gemini-pro-vision", google_api_key=apikey)
    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": "Generate a concise summary for the following medical report",
            },
            {"type": "image_url", "image_url": image_url},
        ]
    )
    result = llm.invoke([message]).content
    return result

@app.route('/', methods=['GET', 'POST'])
def index():
    show_result = False  # Flag to indicate whether to display the result or not

    if request.method == 'POST':
        if 'medicalReport' not in request.files:
            return redirect(request.url)

        medical_report = request.files['medicalReport']

        if medical_report.filename == '':
            return redirect(request.url)

        if medical_report:
            # Create a temporary file to save the uploaded image
            temp_file = tempfile.NamedTemporaryFile(delete=False, dir=app.config['UPLOAD_FOLDER'], suffix=".jpg")
            temp_file_path = temp_file.name

            medical_report.save(temp_file_path)
            temp_file.close()
            # Get the absolute URL for the temporary file
            temp_url = f"{request.url_root}{url_for('uploaded_file', filename=os.path.basename(temp_file_path))}"
            # print('check', temp_url)

            # Call the Google API function with the temporary file URL
            result = generate_summary_with_image(temp_url)
            show_result = True
            try:
                # Remove the temporary file after processing
                os.remove(temp_file_path)
            except Exception as e:
                print(f"Error removing file: {e}")

            
            return render_template('index.html',data=result,show_result=show_result)

    return render_template('index.html',show_result=show_result)

if __name__ == '__main__':

	# run() method of Flask class runs the application 
	# on the local development server.
	app.run(debug=True)
    