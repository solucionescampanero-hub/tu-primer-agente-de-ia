from openai import OpenAI
from dotenv import load_dotenv
from agent import Agent
import os

load_dotenv()

print("Mi primer agente de IA — versión gratuita con Gemini")

client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
    base_url=os.environ.get("OPENAI_BASE_URL")
)
agent = Agent()
model = os.environ.get("MODEL_NAME", "gemini-2.5-flash-lite-preview-06-17")

while True:
    user_input = input("Tú: ").strip()
    if not user_input:
        continue
    if user_input.lower() in ("salir", "exit", "bye", "sayonara"):
        print("Hasta luego!")
        break

    agent.messages.append({"role": "user", "content": user_input})

    while True:
        response = client.chat.completions.create(
            model=model,
            messages=agent.messages,
            tools=agent.tools
        )
        called_tool = agent.process_response(response)
        if not called_tool:
            break