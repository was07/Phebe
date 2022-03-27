def random_fact():
  from pathlib import Path
  import json, random, requests
  factfile = Path("facts.json")
  if not factfile.exists():
    import requests 
    facts = requests.get(
      "https://randomwordgenerator.com/json/facts.json",
      headers={
        "referrerPolicy": "strict-origin-when-cross-origin",
      },
    ).json()["data"]
    factfile.write_text(json.dumps(facts))
  facts = json.loads(factfile.read_text())
  fact = random.choice(facts)
  text = fact["fact"]
  source = fact["source_url"]
  return text, source

text, source = random_fact()
print(text)
print("From: " + source)
