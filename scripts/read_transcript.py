import json

path = r'C:\Users\mail2\.gemini\antigravity-ide\brain\bd88d57b-ac23-459d-9846-9d02d0ce9caa\.system_generated\logs\transcript.jsonl'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

for line in lines:
    try:
        obj = json.loads(line)
        if obj.get('type') == 'USER_INPUT':
            step = obj.get('step_index', '?')
            content = obj.get('content', '')[:400]
            print(f'=== STEP {step} ===')
            print(content)
            print()
    except Exception as e:
        pass
