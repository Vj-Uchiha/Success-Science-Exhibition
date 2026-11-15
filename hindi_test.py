
import asyncio
import edge_tts
import pygame
import os

async def test_voice():

    text = "नमस्ते! मैं नेक्सस हूँ। आप कैसे हैं?"

    voice = "hi-IN-SwaraNeural"

    filename = "hindi_test.mp3"

    print("Generating Hindi voice...")

    communicate = edge_tts.Communicate(
        text,
        voice
    )

    await communicate.save(filename)

    print("Playing Hindi voice...")

    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    pygame.mixer.quit()

    os.remove(filename)

    print("Hindi voice test completed!")


asyncio.run(test_voice())
