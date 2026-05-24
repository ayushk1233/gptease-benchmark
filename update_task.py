import re

path = '/Users/ayuwat/.gemini/antigravity/brain/ccbc88af-ca9a-4cfe-adb3-0389c7354b69/task.md'
with open(path, 'r') as f:
    content = f.read()

content = content.replace('- `[/]` Implement detailed per-dimension reporting (CSV/JSON/Markdown)', '- `[x]` Implement detailed per-dimension reporting (CSV/JSON/Markdown)')
content = content.replace('- `[ ]` Verify changes with tests and dry-runs', '- `[/]` Verify changes with tests and dry-runs')

with open(path, 'w') as f:
    f.write(content)
