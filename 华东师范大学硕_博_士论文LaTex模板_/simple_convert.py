import os
import requests
import base64
import zlib
from pathlib import Path

def encode_plantuml(text):
    compressed = zlib.compress(text.encode('utf-8'))
    encoded = base64.b64encode(compressed).decode('ascii')
    return encoded

def convert_file(puml_file):
    puml_path = Path(puml_file)
    output_dir = puml_path.parent
    
    with open(puml_path, 'r', encoding='utf-8') as f:
        plantuml_text = f.read()
    
    encoded_text = encode_plantuml(plantuml_text)
    url = f"http://www.plantuml.com/plantuml/png/{encoded_text}"
    
    print(f"Converting {puml_path.name}...")
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            png_file = output_dir / f"{puml_path.stem}.png"
            with open(png_file, 'wb') as f:
                f.write(response.content)
            print(f"Success: {png_file}")
            return True
        else:
            print(f"Failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

# 转换所有puml文件
fig_dir = Path("chapters/fig-0")
puml_files = list(fig_dir.glob("*.puml"))

print(f"Found {len(puml_files)} PlantUML files")

for puml_file in puml_files:
    convert_file(puml_file)

print("Conversion complete!")
