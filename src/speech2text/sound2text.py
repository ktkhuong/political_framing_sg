import speech_recognition as sr
import os
from pydub import AudioSegment
import math

def single_split(audio, from_min, to_min, split_filename):
    t1 = from_min * 60 * 1000
    t2 = to_min * 60 * 1000
    split_audio = audio[t1:t2]
    split_audio.export(f'audio_chunks\\{split_filename}', format="wav")

def multiple_split(audio, min_per_split, filename):
    total_mins = math.ceil(audio.duration_seconds / 60)
    for i in range(0, total_mins, min_per_split):
        split_fn = str(i) + '_' + filename
        single_split(audio, i, i+min_per_split, split_fn)
        print(str(i) + ' Done')
        if i == total_mins - min_per_split:
            print('All splited successfully')


def main():
    #sound = AudioSegment.from_mp3("a-conversation-with-sean-francis-han.mp3")
    #sound.export("test.wav", format="wav")
    
    #audio = AudioSegment.from_wav("test.wav")
    #multiple_split(audio, 1, "test.wav")

    file_paths = [f"audio_chunks\\{f}" for f in os.listdir("audio_chunks")]
    for fp in file_paths:
        r = sr.Recognizer()
        with sr.AudioFile(fp) as source:
            audio_data = r.record(source)
            try:
                # try converting it to text
                text = r.recognize_google(audio_data)
                print(text)
    
            # catch any errors.
            except sr.UnknownValueError:
                print("Could not understand audio")
    
            except sr.RequestError as e:
                print("Could not request results. check your internet connection")

if __name__ == "__main__":
    main()