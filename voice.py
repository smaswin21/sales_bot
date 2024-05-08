from humeai_assistant import Assistant

def start_conversation():
    assistant = Assistant(api_key="ujSS3uUuG8p3EbBoQoyaH3Q2GUzyng9vHnCMmcCdqyFmxAfS")
    audio_device = assistant.detect_audio_device()
    assistant.start_conversation(tts="hume_ai", device=audio_device, system_prompt="prompt.txt")

if __name__ == "__main__":
    start_conversation()
    