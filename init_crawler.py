import sys
import json

def get_input_json():
    try:
        input_json = sys.argv[1]
        print("Name of input file: ", input_json)
    except:
        print("No input file provided. Exiting program...")
        quit()
    return input_json



input_json = get_input_json()

with open(input_json, "r") as f:
    data = json.load(f)
    print(data["users"])