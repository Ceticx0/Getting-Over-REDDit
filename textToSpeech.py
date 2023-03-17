from google.cloud import texttospeech
import os
import ffmpeg


def text_to_speech(text: str, output_file: str, voice_name_code_gender=["en-AU-Neural2-B", "en-AU", texttospeech.SsmlVoiceGender.MALE]):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "creds/tts_key.json"
    # Instantiates a client
    client = texttospeech.TextToSpeechClient()
    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text=text)

    # Build the voice request, select the language code ("en-US") and the ssml
    # voice gender ("neutral")
    voice = texttospeech.VoiceSelectionParams(
        language_code=voice_name_code_gender[1], name=voice_name_code_gender[0], ssml_gender=voice_name_code_gender[2]
    )

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    # The response's audio_content is binary.
    with open(output_file, "wb") as out:
        # Write the response to the output file.
        out.write(response.audio_content)
        # print('Audio content written to file "output.mp3"')


if __name__ == '__main__':
    text_to_speech("If you create an act, create a habit. If you create a habit, you create a character. If you create a", "output.mp3")
    print(ffmpeg.probe("output.mp3")['format']['duration'])

# import pyttsx3
#
#
# def text_to_speech(text: str, output_file: str, rate: int = 150):
#     engine = pyttsx3.init()
#     engine.setProperty("rate", rate)
#     engine.save_to_file(text, output_file)
#     engine.runAndWait()
#
#
# if __name__ == '__main__':
#     text_to_speech("Comment 2 has this audio track", "media/audio2.mp3")
#     text_to_speech("Comment 3 has this audio track, which is different from the first", "media/audio3.mp3")
