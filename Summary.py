from pydub import AudioSegment
from openai import OpenAI 
from moviepy.editor import *
import os


# Load the video file
video = VideoFileClip("Coach_Summaries_Test_Call.mp4")
# Extract the audio
audio = video.audio
# Save the audio as an MP3 file
audio.write_audiofile("Coach_Summaries_Test_Call_Audio.mp3")

path ='Coach_Summaries_Test_Call_Audio.mp3'
client = OpenAI(api_key = 'Put your OpenAI API key here')

def slice_audio(file_path, slice_duration):
    audio = AudioSegment.from_mp3(file_path)
    slices = []
    for i in range(0, len(audio), slice_duration):
        audio_slice = audio[i:i + slice_duration]
        slice_path = f"slice_{i // slice_duration}.mp3"
        audio_slice.export(slice_path, format="mp3")
        slices.append(slice_path)
    return slices

sliced_files = slice_audio(path, 10*60*1000)

def transcribe_audio(file_path):
    
    audio_file= open(file_path, "rb")
    transcription = client.audio.transcriptions.create(
    model="whisper-1", 
    file=audio_file)
    return transcription.text


transcriptions = []
for slice_file in sliced_files:
    transcription_text = transcribe_audio(slice_file)
    transcriptions.append(transcription_text)
    print(f"Transcription for {slice_file}: {transcription_text}")
    with open(f"{slice_file}.txt", 'w')as f:
        f.write(transcription_text)


# Optionally, combine all transcriptions into one
full_transcription = "\n".join(transcriptions)
print("Full Transcription:\n", full_transcription)


response = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are a helpful assistant that can make a summary which contains given sub-points."},
    {"role": "user", "content": f"Summarize following text decently:{full_transcription}. Split the Summary into 10 points which will be entiteled as follow: SMART Goal, Motivation, Expectations, General Information, Lifestyle history and significant events, Nutriution, Exercise, Recovery and relaxation, Mental health, Special circumstances, Personal action plans, To be discussed next time. Please make every point a separate paragraph with specific title. If one of the points is not mentioned in the text, then write it down as 'not mentioned'."},
  ]
)
with open("output.txt", "w") as f:
    f.write(response.choices[0].message.content)

