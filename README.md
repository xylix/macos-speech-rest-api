# REST APIs for speech recognition (speech-to-text or STT) and text-to-speech (TTS) on macOS

## OpenAI Audio API compatible implementation: ./openai-audio-rest-api
- Use the OpenAI Audio format:
```json
{example data}
```

pros:
- Easy to integrate with applications that use the OpenAI Audio API, such as local-webui

cons:
- Since it generates full audio files and passes them, the playback will only start once the first sentence has been fully generated.

## Fast and minimal custom API: ./macos-minimal-tts-stt-rest-api

pros: 
- Minimal API: 
```json
{data}
```
- Starts playback and recognition immediately


cons:
