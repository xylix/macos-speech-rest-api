# say and hear worker server

Simple python HTTP server to allow calling of macOS `say` utility and [hear](https://github.com/sveinbjornt/hear) through HTTP API.

Doesn't use audio files - just executes the commands immediately.


## Docs:

### Quickstart:

run `python main.py`
- Send requests: `curl -X POST http://localhost:3000/say -H "Content-Type: application/json" -d '{"voice": "Karen", "text": "Hello, how are you today?"}'`
- Or from browser console (on a site where CORS allows requests to localhost): 
    say: `fetch('http://localhost:3000/say', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ voice: 'Alex', text: 'Hello, this is a test' }) }).then(res => res.json()).then(data => console.log(data));`
    hear: `fetch('http://localhost:3000/hear', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ locale: 'en_US', timeout: '10', exitWord: 'stop' }) }).then(res => res.json()).then(data => console.log(data));`




### /say:
Example:
```bash
curl -X POST http://localhost:3000/say \
  -H "Content-Type: application/json" \
  -d '{"voice": "Karen", "text": "Hello, how are you today?"}'

  ```
Send in a json body containing voice and text fields.

Arguments:
    - voice: String describing the name of the voice to use. To list out supported voices: run `say --v=?`.
    - text: The text to speak.

You can install more voices and adjust the default voice on your system through Settings -> Accessibility -> Spoken content -> System voice -> (the (i) symbol on the left)

The enhanced and Premium voice files are larger and usually provide better sound quality.

### /hear
The hear functionality requires the `hear` command to be installed system-wide.
```bash
curl -X POST http://localhost:3000/hear \
  -H "Content-Type: application/json" \
  -d '{"locale": "en_US", "timeout": "10", "exitWord": "stop"}'
```


Arguments:
    - timeout: Integer, timeout in seconds after user stops speaking to stop the processing
    - locale: Locale code for the language to recognize.
To list supported locales: `hear -s`
