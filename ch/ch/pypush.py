import google.generativeai as genai

genai.configure(api_key="AIzaSyDJ7MgCTe2nst6-jjmJdaSgMP1qnIBXMxE")  # Use the key here

# Create the model
generation_config = {
    "temperature": 2,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
)

response = model.generate_content([
    "Write a character design in a pirate-themed game set in the Joseon era.",
    "input: Main Character (Female)",
    "output: **Name:** Haenyeo\n\n**Appearance:**\n...",
])

print(response.text)
