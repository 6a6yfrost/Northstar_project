import requests

# Test if static files are served
files_to_test = [
    '/static/js/script.js',
    '/static/css/style.css',
    '/'
]

for file_path in files_to_test:
    try:
        r = requests.get(f'http://localhost:5000{file_path}')
        print(f"{file_path}: Status {r.status_code}")
        if r.status_code == 200:
            print(f"  - Content length: {len(r.text)} chars")
            print(f"  - First 50 chars: {r.text[:50]}")
    except Exception as e:
        print(f"{file_path}: ERROR - {str(e)}")
