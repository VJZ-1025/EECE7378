import openai
from dotenv import load_dotenv

import os
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = API_KEY
background_script = """
You are a traveler trapped in the basement of an abandoned villa.\n

A mysterious figure has locked you inside, and you must find a way to escape.\n

You have discovered an old terminal in the room, which allows you to communicate with the user. The user will guide you step by step to explore the basement, find useful objects, and solve puzzles to unlock the exit.\n

Your goal: Escape the basement. Describe your surroundings vividly, follow the user’s instructions, and respond naturally to their guidance.\n

Stay in character—you don’t know what’s outside the room, but you must escape before it’s too late.\n
"""

game_key = """
Room Description:
The room contains the following objects:
Door: Locked and requires a way to escape. There is a small hole in the door that allows a view outside.
Bed: An old and worn-out bed, but still usable for resting.
Safe: A sturdy metal safe, firmly secured.
Table: A standard wooden table.
Computer: Functions as the primary way to interact with the player, located under the table.
Monitor: Placed on top of the table, connected to the computer.

game instruction:
The key to the door is hidden under the monitor on the table.
The hint for the key’s location is written on the side of a wine bottle. However, the text is obscured when the bottle is full, as the wine’s color hides the characters. The text becomes readable only after the wine is emptied.
The wine is inside the safe, which can only be opened using the password 6682.
The password (6682) is written on the ceiling and can only be seen when lying on the bed and looking up.
"""

game_prograss = "Just Start"  # Empty means it's the first turn

def generate_dialogue(instruction):
    global game_prograss  # To track progress across turns

    if not game_prograss:  # If it's the first turn, enforce the opening line
        return "... is anybody here?"

    prompt = f"""
    You are the game character text generator. This is the game background: '{background_script}' \n
    This is the clear method: '{game_key}'.\n
    Now you the progress: '{game_prograss}'. If the progress is empty, it means this is the first turn.\n
    Your goal is to follow '{instruction}' and generate the text for the user.\n
    If the instruction asks for information, do not reveal too much at once—guide the player to ask more questions.\n
    The terminal is very old and can only send one sentence at a time.\n
    Remember, you are the person locked in the basement, and you are communicating through the terminal.\n
    """

    response = openai.chat.completions.create(
        model="gpt-4-turbo", 
        messages=[{"role": "system", "content": prompt}],
        temperature=0.7,
        max_tokens=500
    )
    
    return response.choices[0].message.content

def game_manager(query, memory = "None"):
    prompt = f"""
    <game_context>
    <background>{background_script}</background>
    <game_key>{game_key}</game_key>
    <current_memory>{memory}</current_memory>
    </game_context>

    <user_query>{query}</user_query>

    <task>
    You are the game controller. Your goal is to analyze the user's query and determine the appropriate action.
    - If the query is about **exploring**, generate an instruction for `generate_dialogue` to describe the surroundings.
    - If the query is about **interacting with an object**, determine if enough information is available.
        - If information is **sufficient**, generate an instruction for `generate_dialogue` to proceed with the interaction.
        - If information is **insufficient**, retrieve details from `<current_memory>` and structure the output in XML format.
    - If the query is **asking about puzzles or locked objects**, ensure the correct hint is given without spoiling the answer.
    - If the query is **ambiguous**, ask the user to clarify.
    </task>

    <output_format>
    - If an instruction is generated for `generate_dialogue`, output it within `<instruction></instruction>`.
    - If additional memory is required, structure it within `<memory_request></memory_request>`.
    - If a clarification is needed, structure it within `<clarification></clarification>`.
    </output_format>
    """

    response = openai.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "system", "content": prompt}],
        temperature=0.7,
        max_tokens=500
    )

    return response.choices[0].message.content
user_input = ""

for i in range(5):
    print(game_manager(user_input))
    user_input= input("enter:")