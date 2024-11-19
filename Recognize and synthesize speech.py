#Environment Variable
SPEECH_KEY=
SPEECH_REGION=

#Code
from dotenv import load_dotenv
from datetime import datetime
import os
import azure.cognitiveservices.speech as speech_sdk
from playsound import playsound

def main():
    try:
        global speech_config
        
        # Load environment variables from the .env file
        load_dotenv()
        ai_key = os.getenv('SPEECH_KEY')  # Retrieve the Azure Speech API key
        ai_region = os.getenv('SPEECH_REGION')  # Retrieve the Azure region for the Speech service
        
        # Configure the Azure Speech service
        speech_config = speech_sdk.SpeechConfig(ai_key, ai_region)
        print('Ready to use speech service in:', speech_config.region)
        
        # Get spoken input from the user
        command = TranscribeCommand()
        
        # Check if the command is asking for the current time
        if command.lower() == 'what time is it?':
            TellTime()
    
    except Exception as ex:
        print(ex)  # Print any errors that occur

def TranscribeCommand():
    command = ''
    
    # Configure the speech recognition to use the default microphone
    audio_config = speech_sdk.AudioConfig(use_default_microphone=True)
    speech_recognizer = speech_sdk.SpeechRecognizer(speech_config, audio_config)
    
    print('Speak now...')
    
    # Play an audio file prompt (time.wav) to indicate when to speak
    current_dir = os.getcwd()  # Get the current working directory
    audioFile = current_dir + '\\time.wav'  # Path to the audio file
    playsound(audioFile)  # Play the audio file
    
    # Reconfigure audio settings to use the specified audio file
    audio_config = speech_sdk.AudioConfig(filename=audioFile)
    speech_recognizer = speech_sdk.SpeechRecognizer(speech_config, audio_config)
    
    # Process the spoken input
    speech = speech_recognizer.recognize_once_async().get()
    
    if speech.reason == speech_sdk.ResultReason.RecognizedSpeech:
        command = speech.text  # Store the recognized speech text
        print(command)
    else:
        # Handle different recognition outcomes
        print(speech.reason)
        if speech.reason == speech_sdk.ResultReason.Canceled:
            cancellation = speech.cancellation_details
            print(cancellation.reason)  # Print the cancellation reason
            print(cancellation.error_details)  # Print any error details
    
    # Return the recognized command
    return command

def TellTime():
    # Get the current date and time
    now = datetime.now()
    
    # Create a response text with the current time
    response_text = 'The time is {}:{:02d}'.format(now.hour, now.minute)
    
    # Configure the speech synthesis voice
    speech_config.speech_synthesis_voice_name = 'en-GB-LibbyNeural'  # Choose a voice for synthesis
    speech_synthesizer = speech_sdk.SpeechSynthesizer(speech_config)
    
    # Synthesize spoken output for the time
    speak = speech_synthesizer.speak_text_async(response_text).get()
    
    if speak.reason != speech_sdk.ResultReason.SynthesizingAudioCompleted:
        print(speak.reason)  # Print if synthesis was not successful
    
    # Create an SSML (Speech Synthesis Markup Language) response for detailed synthesis
    responseSsml = (
        "<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>"
        "<voice name='en-GB-LibbyNeural'>"
        "{}"
        "<break strength='weak'/>"
        "Time to end this lab!"
        "</voice>"
        "</speak>"
    ).format(response_text)
    
    # Synthesize spoken output using SSML
    speak = speech_synthesizer.speak_ssml_async(responseSsml).get()
    
    if speak.reason != speech_sdk.ResultReason.SynthesizingAudioCompleted:
        print(speak.reason)  # Print if SSML synthesis was not successful
    
    # Print the response text
    print(response_text)

# Run the main function when the script is executed
if _name_ == "_main_":
    main()
