import streamlit as st
import os
import google.generativeai as genai
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from datetime import datetime, timedelta
import csv
import pandas as pd 

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    st.warning("dotenv module not found. Please make sure to install it using 'pip install python-dotenv'.")

# Define the path to the CSV file
csv_file_path = 'question_history.csv'

# Function to store questions in CSV file
def store_question(question, sector):
    try:
        current_time = datetime.now()
        expiration_time = current_time + timedelta(days=7)  # Auto delete after a week

        # Format the data (question, sector, expiration time)
        data = [question, sector, expiration_time.strftime('%Y-%m-%d %H:%M:%S')]

        # Append the data to the CSV file
        with open(csv_file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data)
    except Exception as e:
        st.error(f"An error occurred while storing the question: {e}")

# Function to read question history from CSV file
def read_question_history():
    try:
        with open(csv_file_path, mode='r') as file:
            reader = csv.reader(file)
            history_data = list(reader)
        return history_data
    except FileNotFoundError:
        return []

# Configure API key
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
except Exception as e:
    st.warning(f"An error occurred while configuring the API key: {e}")

# Define sector-specific prompts
prompts = {
    "educational": "As an expert in education, please provide comprehensive information on",
    "healthcare": "As a seasoned medical professional, offer accurate and insightful responses regarding health and medical topics.",
    "agriculture": "Leveraging your expertise in agriculture, assist with inquiries related to farming, crops, livestock, and sustainable practices.",
    "hr": "With your proficiency in human resources, share valuable insights and guidance on HR practices, recruitment, employee relations, and workplace management.",
    "ats": "As an authority in applicant tracking systems (ATS), elucidate the features and functionalities of ATS, highlighting their applications in recruitment.",
    "general": "Positioned as a knowledgeable and informative resource, respond comprehensively and helpfully to the user's query, drawing from various fields of knowledge.",
}

# Function to detect the sector of a query
def detect_sector(text):
    try:
        # Preprocess text (lowercase, remove stopwords)
        text = text.lower()
        words = word_tokenize(text)
        filtered_words = [word for word in words if word not in stopwords.words('english')]

        # Define sector-specific keywords
        sector_keywords = {
            "educational": ["education", "school", "learning", "teaching", "academic", "curriculum"],
            "healthcare": ["health", "medical", "doctor", "disease", "treatment", "wellness"],
            "agriculture": ["farming", "crop cultivation", "livestock", "agricultural practices", "sustainable farming", "agroecology"],
            "hr": ["human resources", "recruitment", "employee management", "workplace culture", "talent acquisition", "HR policies"],
            "ats": ["applicant tracking system", "recruitment software", "candidate management", "hiring automation", "resume parsing", "job application tracking"],
        }

        # Match keywords and return the most likely sector
        sector = "general"
        max_matches = 0
        for key, value in sector_keywords.items():
            matches = len(set(filtered_words) & set(value))
            if matches > max_matches:
                max_matches = matches
                sector = key

        return sector
    except Exception as e:
        st.error(f"An error occurred while detecting the sector: {e}")

# Function for educational chat using Google Gemini Pro API
def gemini_pro(input_text, prompt):
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content([prompt, input_text])
        return response.text
    except Exception as e:
        st.error(f"An error occurred during educational chat: {e}")

# Initialize Streamlit app
st.set_page_config(page_title="Multi-Domain Chat Bot")

# Sidebar with features
st.sidebar.title("Chat Bot Features")
st.sidebar.markdown("- Ask questions in various domains.")
st.sidebar.markdown("- View responses based on your query.")
st.sidebar.markdown("- Store and view your question history.")

# Display main content
st.header("Multi-Domain Chat Bot")


# Set a default value for the text input
input_text_value = "Ask a question or provide a topic"
input_text = st.text_input("Input:", placeholder=input_text_value, key="text_input")

# Check if the "Send Message" button is clicked
if st.button("Send Message"):
    if not input_text:
        st.warning("Please enter a question or topic.")
    else:
        # Detect sector
        sector = detect_sector(input_text)

        # Choose appropriate prompt
        prompt = prompts[sector]

        # Store question in CSV file
        store_question(input_text, sector)

        # Generate response
        response = gemini_pro(input_text, prompt)

        # Display response and sector
        st.subheader("Answer:")
        st.write(response)
        st.subheader("Sector:")
        st.write(sector)

# Display last 5 rows of question history with column names
history_data = read_question_history()
if history_data:
    st.subheader("Recent Search History")
    
    # Convert the list of lists to a DataFrame
    df = pd.DataFrame(history_data, columns=["Question", "Sector", "Timestamp"])
    
    # Display the last 5 rows in reverse order
    st.write(df.tail(5).iloc[::-1])
else:
    st.info("No question history available.")
