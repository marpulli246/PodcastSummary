import streamlit as st
import modal
import json
import os

def main():

    st.markdown(
        """
        <div style="background-color:#464E5F;padding:10px;border-radius:10px;margin-bottom:10px">
            <h1 style="color:white;text-align:center;">🎙 - - POD BRIEFS - - 🎙</h1>
            <h4 style="color:white;text-align:center;">Podcasts Minimized - Value Maximized</h4>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    available_podcast_info = create_dict_from_json_files('.')
    
    # Custom Sidebar Style
    st.sidebar.markdown(
        """
        <style>
            .css-17eq0hr a, .css-17eq0hr a:hover {
                font-family: 'Montserrat', sans-serif;
                font-size: 12px;
                color: white;
                background-color: #4A90E2;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


    st.sidebar.subheader("Available Podcasts Feeds")

    
    # Using st.sidebar.radio instead of st.sidebar.selectbox

    sorted_podcasts = sorted(available_podcast_info.keys())
    selected_podcast = st.sidebar.radio("Available Podcasts", sorted_podcasts)

    #selected_podcast = st.sidebar.radio("Available Podcasts", list(available_podcast_info.keys()))
   
    #st.title("Newsletter Dashboard")

    #available_podcast_info = create_dict_from_json_files('.')

    # Left section - Input fields
    #st.sidebar.header("Podcast RSS Feeds")

    # Dropdown box
    #st.sidebar.subheader("Available Podcasts Feeds")
    #selected_podcast = st.sidebar.selectbox("Select Podcast", options=available_podcast_info.keys())

    if selected_podcast:

        podcast_info = available_podcast_info[selected_podcast]

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
            st.image(podcast_info['podcast_details']['episode_image'], caption="Podcast Cover", width=300, use_column_width=True)

        # Display the podcast guest and their details in a side-by-side layout
        col3, col4 = st.columns([3, 7])

        with col3:
            st.subheader("Podcast Guest")
            st.write(podcast_info['podcast_guest']['name'])
            #st.write(podcast_info['podcast_guest'])

        with col4:
            st.subheader("Podcast Guest Details")
            st.write(podcast_info["podcast_guest"]['summary'])

        # Display the five key moments
        st.subheader("Key Moments")
        key_moments = podcast_info['podcast_highlights']
        for moment in key_moments.split('\n'):
            st.markdown(
                f"<p style='margin-bottom: 5px;'>{moment}</p>", unsafe_allow_html=True)

    # User Input box
    st.sidebar.subheader("Add and Process New Podcast Feed")
    url = st.sidebar.text_input("Link to RSS Feed")

    #process_button = st.sidebar.button("Process Podcast Feed") #original
    #New style buttom
    process_button = """
    <style>
        .btn-custom {
            background-color: #4CAF50; /* Green background */
            border: none; /* No border */
            color: white; /* White text */
            padding: 12px 24px; /* Some padding */
            cursor: pointer; /* Pointer/hand icon on hover */
            font-size: 16px; /* Increase font size */
            border-radius: 4px; /* Rounded corners */
        }

        .btn-custom:hover {
            background-color: #45a049; /* Darker green on hover */
        }
    </style>
    <button class="btn-custom" id="processButton">Process Podcast Feed</button>
    """
    
    st.markdown(process_button, unsafe_allow_html=True)
    #New style button ends
    
    st.sidebar.markdown("""
    <style>
        .note-style {
            font-family: Montserrat, sans-serif;
            font-size: 10px;
            color: yellow;  # Optional: change color if needed
        }
    </style>
    <div class="note-style">**Note**: Podcast processing can take up to 5 mins, please be patient.</div>
    """, 
    unsafe_allow_html=True
)


    if process_button:

        # Call the function to process the URLs and retrieve podcast guest information
        podcast_info = process_podcast_info(url)

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
            st.image(podcast_info['podcast_details']['episode_image'], caption="Podcast Cover", width=300, use_column_width=True)

        # Display the podcast guest and their details in a side-by-side layout
        col3, col4 = st.columns([3, 7])

        with col3:
            st.subheader("Podcast Guest")
            st.write(podcast_info['podcast_guest']['name'])

        with col4:
            st.subheader("Podcast Guest Details")
            st.write(podcast_info["podcast_guest"]['summary'])

        # Display the key moments
        st.subheader("Key Moments")
        key_moments = podcast_info['podcast_highlights']
        for moment in key_moments.split('\n'):
            st.markdown(
                f"<p style='margin-bottom: 5px;'>{moment}</p>", unsafe_allow_html=True)

    # Footer
    st.markdown(
        """
        <div style="position: relative; bottom: 0; left: 0; right: 0; background-color: #464E5F; padding: 10px;">
            <div style="text-align: center;">
                <a href="https://twitter.com" target="_blank" style="margin-right: 15px;">🐦 Twitter</a>
                <a href="https://facebook.com" target="_blank" style="margin-right: 15px;">📘 Facebook</a>
                <a href="https://instagram.com" target="_blank">📸 Instagram</a>
            </div>
            <p style="text-align:center; color:white;">© 2023 - Contact Us</p>
        </div>
        """,
        unsafe_allow_html=True,
    )        

def create_dict_from_json_files(folder_path):
    json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
    data_dict = {}

    for file_name in json_files:
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'r') as file:
            podcast_info = json.load(file)
            podcast_name = podcast_info['podcast_details']['podcast_title']
            # Process the file data as needed
            data_dict[podcast_name] = podcast_info

    return data_dict

def process_podcast_info(url):
    f = modal.Function.lookup("corise-podcast-project", "process_podcast")
    output = f.call(url, '/content/podcast/')
    return output

if __name__ == '__main__':
    main()
