import streamlit as st
import modal
import os
import json

# Function to load JSON files from the given directory
def load_json_files(path):
      return [f for f in os.listdir('.') if f.endswith('.json')]

# Function to load content of a JSON file
def load_json_data(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def process_podcast_info(url):
    f = modal.Function.lookup("corise-podcast-project", "process_podcast")
    output = f.call(url, '')
    return output

# Sidebar
st.sidebar.title("Podcast Processor")

# Input field for podcast URL and button
podcast_url = st.sidebar.text_input("Enter the podcast URL:")
if st.sidebar.button("Process Podcast"):
    #result = process_podcast_info(podcast_url)
    #st.sidebar.text('Podcast processed!')

    # Call the function to process the URLs and retrieve podcast guest information
    podcast_info = process_podcast_info(podcast_url)

    # Right section - Newsletter content
    st.header("Newsletter Content")

    # Display the podcast title
    st.subheader("Episode Title")
    st.write(podcast_info['podcast_details']['episode_title'])

    # Display the podcast summary and the cover image in a side-by-side layout
    col1, col2 = st.columns([7, 3])

    with col1:
        # Display the podcast episode summary
        st.subheader("Podcast Episode Summary")
        st.write(podcast_info['podcast_summary'])

    with col2:
        st.image(podcast_info['podcast_details']['episode_image'], caption="Podcast Cover", width=150, use_column_width=True)

    # Display the podcast guest and their details in a side-by-side layout
    col3, col4 = st.columns([3, 7])

    with col3:
        st.subheader("Podcast Guest")
        st.write(podcast_info['podcast_guest']['name'])

    with col4:
        st.subheader("Podcast Guest Details")
        st.write(podcast_info["podcast_guest"]['summary'])

    # Display the five key moments
    st.subheader("Key Moments")
    key_moments = podcast_info['podcast_highlights']
    for moment in key_moments.split('\n'):
        st.markdown(
            f"<p style='margin-bottom: 5px;'>{moment}</p>", unsafe_allow_html=True)
     

# Dropdown to select a JSON file
path_to_json_files = os.listdir('.') 
json_files = load_json_files('.')
selected_file = st.sidebar.selectbox('Choose a podcast summary:', json_files)

# Load and display the content of the selected JSON file
if selected_file:
    data = load_json_data(os.path.join('.', selected_file))

    # Display in a modern layout using columns
    col1, col2 = st.columns(2)

    # Display podcast icon on the left column
    col1.image(data['podcast_details']['episode_image'], caption='Podcast Icon', width=150)
    
    # Display titles and summary on the right column
    col2.markdown(f"## {data['podcast_details']['podcast_title']}")
    col2.markdown(f"### {data['podcast_details']['episode_title']}")
    col1.markdown(f"**Podcast Summary**: {data['podcast_summary']}")
    ##col2.markdown(f"**Episode Summary**: {data['podcast_details']}")
    col1.markdown(f"**Episode Highlights**: {data['podcast_highlights']}")
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

