import google.generativeai as genai
import PIL.Image

# 1. Setup
genai.configure(api_key="AIzaSyCoVyIzi_SwLvtUdp54hVQzrfEPH3t3P5o")
model = genai.GenerativeModel('gemini-3-flash-preview') # Flash is perfect for fast verification

def verify_challenge(image_path, challenge_description):
    # Load the image
    img = PIL.Image.open(image_path)

    # 2. Craft a structured prompt
    prompt = f"""
    Task: Act as a challenge verification system for a travel app in Egypt.
    Challenge Description: {challenge_description}

    Instruction:
    1. Analyze the provided image.
    2. Determine if the image clearly shows the user completing the challenge.
    3. Look for specific landmarks, objects, or actions mentioned in the description.

    Return your response in this exact format:
    Status: [Verified / Not Verified]
    Reason: [One short sentence explaining why]
    """

    # 3. Call the API
    response = model.generate_content([prompt, img])
    return response.text

# Example Usage:
# result = verify_challenge("user_upload.jpg", "Take a photo of the main gate of the Citadel")
# print(result)