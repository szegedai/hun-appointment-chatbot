import json

def parse_conversation(file_path: str) -> None:

  file_name = file_path.split('.')[0]

  with open(file_path, encoding="utf-8") as f:
    data = json.load(f)

  with open(f"{file_name}_parsed.txt", 'w+', encoding='utf-8') as f_out:
    for d in data.get('events'):
      if d.get('event') == 'user':
        f_out.write(f"Felhasználó: {d['text']}\n")
      elif d.get('event') == 'bot':
        f_out.write(f"Chatbot: {d['text']}\n")
