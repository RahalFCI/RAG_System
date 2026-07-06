from google import genai
from google.genai import types
from ..helpers.Config import Settings
import PIL.Image

settings = Settings()
client = genai.Client(api_key=settings.api_key)

def verify_challenge(image_bytes, challenge_description):

    prompt = f"""
    Task: Act as a challenge verification system for a travel app in Egypt.
    Challenge Description: {challenge_description}

    Instruction:
    1. Analyze the provided image.
    2. Determine if the image clearly shows the user completing the challenge.
    3. Look for specific landmarks, objects, or actions mentioned in the description.

    Return your response in this exact format:
     True / False
    """

    # response = model.generate_content([prompt, img])
    response = client.models.generate_content(
    model='gemini-2.5-flash-lite',
    contents=[
        types.Part.from_text(text=prompt),
        types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
    ]
)
    return response.text

