import json

# Open the JSON file
with open('kanji_list.json') as file:
    # Load the JSON data
    data = json.load(file)

# Transform the list into a dictionary
dictionary = {obj["kanji"]: obj["rtk_order"] for obj in data}

# Print the resulting dictionary
print(dictionary)
