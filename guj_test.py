
import asyncio
import edge_tts
import pygame

async def main():

    text = "નમસ્તે! મારું નામ નિરંજન છે. હું તમારો ગુજરાતી AI સહાયક છું. આપનું સ્વાગત છે!"

    voice = "gu-IN-NiranjanNeural"

    communicate = edge_tts.Communicate(
        text,
        voice,
        rate="-5%",
        pitch="-5Hz"
    )

    await communicate.save("gujarati_test.mp3")

    pygame.mixer.init()
    pygame.mixer.music.load("gujarati_test.mp3")
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    pygame.mixer.quit()

asyncio.run(main())
