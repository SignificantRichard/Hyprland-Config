import os

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFERS_OFFLINE"] = "1"

import json
from laya import Router
from talk import listen_until_over
from start import launch

# 1. Get the raw text from speech
raw_text = listen_until_over()

# 2. Cleanly strip "over" from the end if present (case-insensitive)
cleaned_text = raw_text.strip()
if cleaned_text.lower().endswith("over"):
    # Remove the word "over" and any trailing punctuation/spaces before it
    cleaned_text = cleaned_text[:-4].strip()
    cleaned_text = cleaned_text.rstrip(".,!?").strip()

state = {"text": cleaned_text}
print(f"Processed State Text: '{state['text']}'")

router = Router(preload=["english"])

questions = {
    "weather": {
        "type": "noul", 
        "instructions": "Does the user ask about the weather?"
    },
    "date": {
        "type": "noul", 
        "instructions": "Does the user ask about the date"
    }
}

router_result = router.predict(state, questions)

highest = 0
answer = "NONE"

for category in router_result["answers"]:
    data = router_result["answers"][category]
    print(category, data)
    if highest < data["noul"]:
        answer = category
        highest = data["noul"]

if answer == "weather":
    pass
elif answer == "date":
    launch(0)

print(answer, highest)