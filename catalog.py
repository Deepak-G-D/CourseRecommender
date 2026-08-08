import json

#loads the courses and careers from the JSON files in the data folder
def load_courses():
    with open("data\courses.json", "r") as file:
        return json.load(file)

def load_careers():
    with open("data\careers.json", "r") as file:
        return json.load(file)