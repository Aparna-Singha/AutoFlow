from google import genai

# initialize the client
client = genai.Client(api_key="YOUR_GEMINI_API_KEY")

# generate text
response = client.models.generate_content(
    model="gemini-2.5-flash",          # example model name
    contents="Explain how AI works in simple terms."
)

print(response.text)