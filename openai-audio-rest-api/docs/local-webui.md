# How to use it with local-webui?

0. Install and configure local-webui.

1. Install and start the openai-audio-rest-api: `python main.py`
2. Once it's running succesfully, open local-webui admin panel (top right corner profile picture -> Admin panel)
<img width="1302" alt="Screenshot 2025-03-28 at 13 22 53" src="https://github.com/user-attachments/assets/73919161-c4b3-428a-a319-7ed7c39b2407" />
<img width="255" alt="Screenshot 2025-03-28 at 13 23 15" src="https://github.com/user-attachments/assets/5cadd0b6-6d35-489c-acf4-71e068237c36" />

  - > Settings
  - > Audio
  - > TTS Settings
  - Text-to-speech engine: OpenAI
  - url: http://localhost:8003/v1 (or insert another port if you changed it for the server)
  - You can select a voice here, but it can also be set in the non-admin settings
  - TTS-model setting is ignored
  - Set any string to the API key field. You need to add something or the interface won't let you save.
  - Save the settings (bottom right -> Save)
<img width="1300" alt="Screenshot 2025-03-28 at 13 23 42" src="https://github.com/user-attachments/assets/9a81f7a4-8854-49c1-a8b5-4c888d6558cd" />

3. Go back to the front page.
- Open personal settings: Bottom left or top right corner -> Settings
<img width="261" alt="Screenshot 2025-03-28 at 13 25 45" src="https://github.com/user-attachments/assets/c702eb1e-7623-4c22-9eb8-816d42144908" />
- Ensure that Text-to-speech-engine is set to default
- Write in the desired voice model. I personally recommend Karen out of the ones that macOS has installed by default.
<img width="915" alt="Screenshot 2025-03-28 at 13 26 25" src="https://github.com/user-attachments/assets/8b633baa-efda-418b-b88e-06deef819d46" />

4. Open a chat, and press the text-to-speech button. The AI should start reading shortly.
    <img width="1194" alt="Screenshot 2025-03-28 at 13 28 19" src="https://github.com/user-attachments/assets/f57d89b8-13a8-4f41-8b1c-96c481c2e05d" />
