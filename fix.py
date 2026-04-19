import re

path = r'C:\Users\Rupesh Pandey\.gemini\antigravity\brain\f5310f34-f1fe-4462-a65b-820d3300a0c6\.system_generated\logs\overview.txt'
with open(path, 'r', encoding='utf-8') as f:
    log = f.read()

# Find the exact code block the user pasted!
match = re.search(r'<USER_REQUEST>\nimport os\n.*?\ncode hai ye\n</USER_REQUEST>', log, re.DOTALL)
if match:
    code = match.group(0)
    # Strip wrappers
    code = code.replace('<USER_REQUEST>\n', '')
    code = code.replace('\ncode hai ye\n</USER_REQUEST>', '')
    
    # Fix the SQLite URI for Local Windows
    code = code.replace(
        'app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///careermantra.db")',
        'app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///careermantra.db"'
    )

    with open(r'c:\Users\Rupesh Pandey\OneDrive\Desktop\CareerMantra AI\career-mantra-ai\app.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Perfectly recovered full app.py!")
else:
    print("User block not found.")
