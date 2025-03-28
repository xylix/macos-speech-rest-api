# macOS openAPI compatible speech backend

Attempt at making a python http backend that can use the macOS system `say` command and the excellent 3rd party `hear` command to use tts / stt features.

Unpublished prototype because the mp3 support is missing in macOS `say` command, and my perfectionism is unsatisfied if we need an ffmpeg dependency for this package.


## Use case:
Fast and decent quality voice features for open-webui and other applications that integrate with openAI speech api.

## Quickstart & Installation:

- install ffmpeg (`brew install ffmpeg`)
- install `hear` if you want to use the voice recognition functionality
- run the backend with `python main.py`


## Tutorials

- [local-webui tutorial](./documentation/local-webui.md)

## Documentation:

- Maps the OpenAI voice names to macOS voice names:


- You can also use the macOS voice names directly. Run `say --v="?"` on the machine running the server to get a list of voice names. They may contain spaces and parenthesis, that's fine.
