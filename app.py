import streamlit as st
import os
import time
import Finale_backend_hardcodellm

print(os.listdir())
# Define directory where the backend saves the output
OUTPUT_DIR = r"C:\Tools\New folder\NLP_2_Dashboard\venv\uploaded_files"

st.set_page_config(page_title="VizGenie", layout="wide")
st.title("VizGenie")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# File upload section
uploaded_file = st.file_uploader("Upload a file", type=["txt", "pdf", "docx", "xlsx", "pbit"])
prompt = st.text_area("Enter your prompt:")

process_button = st.button("Process")
response="Generating an insightful dashboard with powerful visuals—Cards, Donut Chart, Bar Chart, Area Chart, Line Chart, and Pie Chart—crafted from the credit analysis dataset to reveal key trends in age, income, home ownership, loan intent, and credit history!"

if process_button and uploaded_file and prompt:

    # Save uploaded file
    file_path = os.path.join(OUTPUT_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": f"Prompt: {prompt}\nUploaded file: {uploaded_file.name}"})

    # Display user message
    with st.chat_message("user"):
        st.markdown(f"Prompt: {prompt}")
        st.markdown(f"Uploaded File: {uploaded_file.name}")
    
    base_name, _ = os.path.splitext(uploaded_file.name)

# Construct the processed file path dynamically
    processed_file_path = os.path.join(OUTPUT_DIR, f"{base_name}.pbit")
    # Simulate backend processing time
    time.sleep(2)
    Finale_backend_hardcodellm.main()
    time.sleep(3)
    st.write(response)
    time.sleep(5)
    st.write("Waiting for the processed file to be generated...")
    print(f"Checking for file: {processed_file_path}")
    timeout = 60  # Maximum wait time (adjust as needed)
    elapsed_time = 0
    while not os.path.exists(processed_file_path) and elapsed_time < timeout:
        time.sleep(1)  # Check every second
        elapsed_time += 1

    if os.path.exists(processed_file_path):
        st.success("File processed")
    else:
        st.error("Processing timed out. The file was not generated.")
    

    if os.path.exists(processed_file_path):
        with st.chat_message("assistant"):
            st.markdown(f"Processing complete! Your file `{os.path.basename(processed_file_path)}` is ready for download.")

        # Provide download button for the actual processed file
        with open(processed_file_path, "rb") as file:
            st.download_button(
                label="Download Processed File",
                data=file,
                file_name=os.path.basename(processed_file_path),
                mime="application/octet-stream"
            )
    else:
        st.error("Error: Processed file not found. Please check if the backend has generated the output.")
