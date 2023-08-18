import streamlit as st
import os
import json

# Function to load JSON files from the given directory
def load_json_files(path):
    return [f for f in os.listdir(path) if f.endswith('.json')]

# Function to load content of a JSON file
def load_json_data(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Sidebar
st.sidebar.title("Podcast Processor")

# Input field for podcast URL and button
podcast_url = st.sidebar.text_input("Enter the podcast URL:")
if st.sidebar.button("Process Podcast"):
    # Your processing logic here
    st.sidebar.text('Podcast processed!')

# Dropdown to select a JSON file
path_to_json_files = '/content/podcast/'
json_files = load_json_files(path_to_json_files)
selected_file = st.sidebar.selectbox('Choose a podcast summary:', json_files)

# Load and display the content of the selected JSON file
if selected_file:
    data = load_json_data(os.path.join(path_to_json_files, selected_file))

    # Display in a modern layout using columns
    col1, col2 = st.beta_columns(2)

    # Display podcast icon on the left column
    col1.image(data['podcast_details']['episode_image'], caption='Podcast Icon', use_column_width=True)
    
    # Display titles and summary on the right column
    col2.markdown(f"## {data['podcast_details']['podcast_title']}")
    col2.markdown(f"### {data['podcast_details']['episode_title']}")
    col2.markdown(f"**Podcast Summary**: {data['podcast_summary']}")
    col2.markdown(f"**Episode Summary**: {data['podcast_details']['episode_transcript']}")
    col2.markdown(f"**Episode Highlights**: {data['podcast_highlights']}")
    col2.markdown(f"**Guest Information**: {data['podcast_guest']}")

# Styling
st.markdown("""
<style>
    h1 {
        color: navy;
    }
    h2 {
        color: teal;
    }
    body {
        background-color: #EAEDED;
    }
</style>
""", unsafe_allow_html=True)