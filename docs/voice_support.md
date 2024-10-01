# Voice support in assistant

## Voice input
Apart from writing your own questions, user can use own voice to ask 
questions. The voice will be transcribed to text and displayed in the
question text field.

After that user can press the `Ask` button and the assistant will 
answer the question.

Voice transcription is implemented via a speech-to-text model from [`faster-whisper`](https://github.com/SYSTRAN/faster-whisper)   
This model is an optimized version of the [`OpenAI's whisper model`](https://github.com/openai/whisper)

The code using it can be found in `speech_to_text` function in [`app.py`](../app/app.py).

**_Note:_** during development, Gemini was also tested for doing transcription of audio files (using prompt `Please transcribe this recording:` + audio).   
But the results were worse than `faster-whisper`.

## Voice output
All answers are voiced out along with displaying a text version.

Voice output is implemented via text-to-speech library from [`MeloTTS`](https://github.com/myshell-ai/MeloTTS)

The code using it can be found in `text_to_speech` function in [`app.py`](../app/app.py).