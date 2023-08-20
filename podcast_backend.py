import modal

def download_whisper():
  # Load the Whisper model
  import os
  import whisper
  print ("Download the Whisper model")

  # Perform download only once and save to Container storage
  whisper._download(whisper._MODELS["medium"], '/content/podcast/', False)


stub = modal.Stub("corise-podcast-project")
corise_image = modal.Image.debian_slim().pip_install("feedparser",
                                                     "https://github.com/openai/whisper/archive/9f70a352f9f8630ab3aa0d06af5cb9532bd8c21d.tar.gz",
                                                     "requests",
                                                     "ffmpeg",
                                                     "openai",
                                                     "tiktoken",
                                                     "wikipedia",
                                                     "googlesearch-python",
                                                     "ffmpeg-python").apt_install("ffmpeg").run_function(download_whisper)

@stub.function(image=corise_image, gpu="any", timeout=600)
def get_transcribe_podcast(rss_url, local_path):
  print ("Starting Podcast Transcription Function")
  print ("Feed URL: ", rss_url)
  print ("Local Path:", local_path)

  # Read from the RSS Feed URL
  import feedparser
  podcast_feed = feedparser.parse(rss_url)
  podcast_title = podcast_feed['feed']['title']
  #podcast_title = podcast_feed['feed'].get('title', 'Unknown title')
  episode_title = podcast_feed.entries[0]['title']
  episode_image = podcast_feed['feed']['image'].href
  for item in podcast_feed.entries[0].links:
    if (item['type'] == 'audio/mpeg'):
      episode_url = item.href
  episode_name = "podcast_episode.mp3"
  print ("RSS URL read and episode URL: ", episode_url)

  # Download the podcast episode by parsing the RSS feed
  from pathlib import Path
  p = Path(local_path)
  p.mkdir(exist_ok=True)

  print ("Downloading the podcast episode")
  import requests
  with requests.get(episode_url, stream=True) as r:
    r.raise_for_status()
    episode_path = p.joinpath(episode_name)
    with open(episode_path, 'wb') as f:
      for chunk in r.iter_content(chunk_size=8192):
        f.write(chunk)

  print ("Podcast Episode downloaded")

  # Load the Whisper model
  import os
  import whisper

  # Load model from saved location
  print ("Load the Whisper model")
  model = whisper.load_model('medium', device='cuda', download_root='/content/podcast/')

  # Perform the transcription
  print ("Starting podcast transcription")
  result = model.transcribe(local_path + episode_name)

  # Return the transcribed text
  print ("Podcast transcription completed, returning results...")
  output = {}
  output['podcast_title'] = podcast_title
  output['episode_title'] = episode_title
  output['episode_image'] = episode_image
  output['episode_transcript'] = result['text']
  return output

@stub.function(image=corise_image, secret=modal.Secret.from_name("my-openai-secret"))
def get_podcast_summary(podcast_transcript):
  import openai
  import tiktoken
  ## ADD YOUR LOGIC HERE TO RETURN THE SUMMARY OF THE PODCAST USING OPENAI
  ##from getpass import getpass
  ##openai.api_key = my-openai-secret
  print("Starting the OpenAI summary creation")
  enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
  print ("Number of tokens in input prompt ", len(enc.encode(podcast_transcript)))
  instructPrompt = """
  You have been assigned an interesting podcast. You need to summarize the podcast transcript.
  Identify the hot or trending topics discussed in the podcast. Study and understand the topic of the podcast well enough.
  Find the main takeaways or lessons learned from the podcast.
  Using all above write a short summary in a concise paragraph.
  Limit your response to around 500 tokens and make it sound very appealing for a reader. Idea is to attract the reader to listen the podcast.
  See transcript below.
  """
  request = instructPrompt + podcast_transcript
  chatOutput = openai.ChatCompletion.create(model="gpt-3.5-turbo-16k",
                                            messages=[{"role": "system", "content": "You are a helpful assistant."},
                                                      {"role": "user", "content": request}
                                                      ]
                                            )

  podcastSummary = chatOutput.choices[0].message.content
  print ("Podcast summary completed")
  return podcastSummary

@stub.function(image=corise_image, secret=modal.Secret.from_name("my-openai-secret"))
def get_podcast_guest(podcast_transcript):
  import openai
  import wikipedia
  import json
  from googlesearch import search  ##in case Wikipedia has nothing we use Google as backup
  import warnings

  warnings.filterwarnings("ignore", category=UserWarning, module='wikipedia')
  print ("Let's get more information about guest(s).")
  ## ADD YOUR LOGIC HERE TO RETURN THE PODCAST GUEST INFORMATION
  request = podcast_transcript[:7000]
  ##enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
  ##print ("Number of tokens in input prompt ", len(enc.encode(request)))
  completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": request}],
    functions=[
    {
        "name": "get_podcast_guest_information",
        "description": "Get information on the podcast guest using their full name and the name of the organization they are part of to search for them on Wikipedia or Google",
        "parameters": {
            "type": "object",
            "properties": {
                "guest_name": {
                    "type": "string",
                    "description": "The full name of the guest who is speaking in the podcast",
                },
                "guest_organization": {
                    "type": "string",
                    "description": "The full name of the organization that the podcast guest belongs to or runs",
                },
                "guest_title": {
                    "type": "string",
                    "description": "The title, designation or role of the podcast guest in their organization",
                },
            },
            "required": ["guest_name"],
        },
     }
   ],
   function_call={"name": "get_podcast_guest_information"}
  )
  response_message = completion["choices"][0]["message"]
  podcast_guest = ""
  podcast_guest_org = ""
  podcast_guest_title = ""

  if response_message.get("function_call"):
    function_name = response_message["function_call"]["name"]
    function_args = json.loads(response_message["function_call"]["arguments"])
    podcast_guest=function_args.get("guest_name")
    podcast_guest_org=function_args.get("quest_organization")
    podcast_guest_title=function_args.get("guest_title")

  if (podcast_guest is not None):
    if (podcast_guest_org is None):
      podcast_guest_org = ""
    if (podcast_guest_title is None):
      podcast_guest_title = ""

    try:
      input = wikipedia.page(podcast_guest + " " + podcast_guest_org + " " + podcast_guest_title, auto_suggest=False)
      podcast_guest_summary = input.summary
    except (wikipedia.DisambiguationError, wikipedia.PageError):
      ##in case Wikipedia has nothing we use Google as backup
      search_results = list(search(podcast_guest, num_results=1))
      if search_results:
          podcast_guest_summary = f"Could not find detailed information about {podcast_guest} on Wikipedia. However, you can learn more about the guest here: {search_results[0]}"
      else:
          podcast_guest_summary = f"Could not find detailed information about {podcast_guest} on both Wikipedia and Google."

  print ("Guest information retrieved.", podcast_guest_summary)
  podcastGuest = {}
  podcastGuest['name'] = podcast_guest
  podcastGuest['org'] = podcast_guest_org
  podcastGuest['title'] = podcast_guest_title
  podcastGuest['summary'] = podcast_guest_summary
  print (podcastGuest['summary'])
  return podcastGuest

@stub.function(image=corise_image, secret=modal.Secret.from_name("my-openai-secret"))
def get_podcast_highlights(podcast_transcript):
  import openai
  print ("Let's find the podcast highlights and hot topics.")
  ### ADD YOUR LOGIC HERE TO RETURN THE HIGHLIGHTS OF THE PODCAST
  instructPrompt = """
  We need two things here.
  Highlights: Do a host or a guest have any opinions that might create more discussion in audience. Write a short summary in a concise paragraph, maximum 100 tokens.  
  Keynotes: Find three most interesting keynotes from the podcast transcript. List them always in list like below.
    1. Keynote 1
    2. Keynote 2
    3. Keynote 3
  """
  request = instructPrompt + podcast_transcript
  chatOutput = openai.ChatCompletion.create(model="gpt-3.5-turbo-16k",
                                            messages=[{"role": "system", "content": "You are a helpful assistant."},
                                                      {"role": "user", "content": request}
                                                      ]
                                            )
  podcastHighlights = chatOutput.choices[0].message.content
  print ("Highlights completed")
  return podcastHighlights

@stub.function(image=corise_image, secret=modal.Secret.from_name("my-openai-secret"), timeout=1200)
def process_podcast(url, path):
  output = {}
  podcast_details = get_transcribe_podcast.call(url, path)
  podcast_summary = get_podcast_summary.call(podcast_details['episode_transcript'])
  podcast_guest = get_podcast_guest.call(podcast_details['episode_transcript'])
  podcast_highlights = get_podcast_highlights.call(podcast_details['episode_transcript'])
  output['podcast_details'] = podcast_details
  output['podcast_summary'] = podcast_summary
  output['podcast_guest'] = podcast_guest
  output['podcast_highlights'] = podcast_highlights
  return output

@stub.local_entrypoint()
def test_method(url, path):
  output = {}
  podcast_details = get_transcribe_podcast.call(url, path)
  print ("Podcast Summary: ", get_podcast_summary.call(podcast_details['episode_transcript']))
  print ("Podcast Guest Information: ", get_podcast_guest.call(podcast_details['episode_transcript']))
  print ("Podcast Highlights: ", get_podcast_highlights.call(podcast_details['episode_transcript']))
