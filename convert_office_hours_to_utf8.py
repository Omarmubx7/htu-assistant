import sys
import codecs

input_file = 'office_hours.json'
output_file = 'office_hours_utf8.json'

# Try to read with utf-8-sig, then utf-16, fallback to latin1
encodings = ['utf-8-sig', 'utf-16', 'latin1']
for enc in encodings:
    try:
        with codecs.open(input_file, 'r', encoding=enc) as f:
            data = f.read()
        break
    except Exception as e:
        data = None
        continue

if data is None:
    print('Failed to read office_hours.json with common encodings.')
    sys.exit(1)

# Write as utf-8
with codecs.open(output_file, 'w', encoding='utf-8') as f:
    f.write(data)

print(f'Converted {input_file} to UTF-8 as {output_file}') 