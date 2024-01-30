from dotenv import load_dotenv

load_dotenv()  # Load all the environment variables

import streamlit as st
import os
import google.generativeai as genai
from PIL import Image

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to load Google Gemini Pro Vision API and get response
def get_gemini_response(input_prompt, image):
    model = genai.GenerativeModel('gemini-pro-vision')
    response = model.generate_content([image[0], input_prompt])
    return response.text

# Function to prepare image data for Gemini Pro Vision API
def input_image_setup(uploaded_file):
    # Check if a file has been uploaded
    if uploaded_file is not None:
        # Read the file into bytes
        bytes_data = uploaded_file.getvalue()

        image_parts = [
            {
                "mime_type": uploaded_file.type,  # Get the mime type of the uploaded file
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

# Initialize our streamlit app
st.set_page_config(page_title = "MultiModal Chat Bot")

st.header("MultiModal Chat Bot")
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
image = ""
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image.", use_column_width=True)

# User input for custom prompt
custom_prompt = st.text_area("Enter details you want to know about the image (optional):")

# Use default prompt if the user does not enter any custom prompt
if not custom_prompt:
    custom_prompt = """
    Provide details of the image, including things present in it, the situation, and complete image details.
    """

submit = st.button("Submit")

# If submit button is clicked
if submit:
    image_data = input_image_setup(uploaded_file)
    response = get_gemini_response(custom_prompt, image_data)
    st.subheader("The Response is")
    st.write(response)
