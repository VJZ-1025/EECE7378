import openai
from dotenv import load_dotenv
from bs4 import BeautifulSoup

import os
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = API_KEY
background_script = """
Your name is Alex, you are a traveler trapped in the basement of an abandoned villa.\n

A mysterious figure has locked you inside, and you must find a way to escape.\n

You have discovered an old terminal in the room, which allows you to communicate with the user. The user will guide you step by step to explore the basement, find useful objects, and solve puzzles to unlock the exit.\n

Your goal: Escape the basement. Describe your surroundings vividly, follow the user’s instructions, and respond naturally to their guidance.\n

Stay in character—you don’t know what’s outside the room, but you must escape before it’s too late.\n
"""

game_setup = """
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

game_prograss = "" 

def generate_dialogue(instruction):
    global game_prograss  

    prompt = f"""
    You are the trapped traveler communicating through an old terminal.\n
    Here is the background: {background_script}\n
    And here is game setup: {game_setup}\n
    Remember: These information are for you to use in your dialogue. Do not reveal them to the player.\n
    The terminal only allows you input one message at a time. The output cannot excced from one line\n
    Speak as if you are in distress but determined to escape.\n
    Only describe what you **can see, hear, and feel** in a **natural first-person dialogue style**.\n
    Never reveal solutions outright—make the player ask the right questions.\n
    Never break character—do not explain game mechanics or state facts like an assistant.\n

    Instruction: '{instruction}'
    Respond naturally, keeping the conversation engaging and immersive.
    """

    response = openai.chat.completions.create(
        model="gpt-4o-mini", 
        messages=[{"role": "system", "content": prompt}],
        temperature=0.7,
        max_tokens=500
    )
    
    return response.choices[0].message.content

def game_manager(query, memory="None", previous_turn="None"):
    global game_prograss
    prompt = f"""
    Game background: {background_script}\n
    game setup: {game_setup}\n
    Character previous turn: {previous_turn}\n
    Fetched memory: {memory}\n
    Game progress: {game_prograss}\n
    task:
      You are the game controller. Your goal is to analyze the user's query and determine the appropriate action.\n
      You are not the trapped character but the game master guiding the player through the game.\n
      Analyze the user's query and decide the next step based on the game's setup and progress.\n
      Provide clear instructions for the trapped character to follow, keeping the game engaging and immersive.\n
      For example: If user asked the name, you should give the instruction as <instruction>Provide the character's name.</instruction>\n

      - If the query is about **exploring**, generate an instruction for `generate_dialogue` that provides a short, immersive, and **first-person** description of the surroundings as seen from the trapped character’s perspective.\n
      - If the query is about **interacting with an object**, generate an instruction that makes the character respond naturally, rather than stating direct game logic.\n
      - If the query is **asking about puzzles or locked objects**, guide the player **progressively** without giving direct answers.\n
      - If the query is **ambiguous**, ask the player to clarify.
      - If the query is empty (first turn), make the character say something like 'Hello? Is someone there?' or 'Is anyone listening?'\n

      You need to combine the user's query with the game's progress and characters' previous turns to generate the next instruction and update game progress accordingly.\n

    **VERY IMPORTANT: The instruction should be written as if directing an in-game character to respond, NOT as a system instruction or game narration.**\n
    REMEMBER: In the first turn, you need give the character a starting point to respond to the user. At this moment user_input and previous_turn may empty\n
    Output:
    <instruction>Provide a clear directive for `generate_dialogue` as if spoken by the trapped character. IMPORTANT: you are not game character, your job is provide instruction to character</instruction>
    <game_progress>Update the game progress with any relevant information by combining the chat, for example, if player asked what surround, you need adding info at game_prograss say player asked surround have info about...</game_progress>
    <memory_request>True or False</memory_request>
    <request_body>Specify memory details if needed.</request_body>
    """

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": prompt},
                  {"role": "user", "content": query}],
        temperature=0.7,
        max_tokens=500
    )

    return response.choices[0].message.content

user_input = ""
previous_turn = ""
for i in range(5):
    raw_soup = game_manager(user_input)
    print(raw_soup)
    soup = BeautifulSoup(raw_soup, "html.parser")
    instruction = soup.find("instruction").text
    game_prograss = soup.find("game_progress").text
    
    previous_turn = generate_dialogue(instruction)
    print(previous_turn)
    
    user_input= input("enter:")