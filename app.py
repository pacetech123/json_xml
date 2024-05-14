from fastapi import FastAPI, File, UploadFile, Response
from fastapi.responses import HTMLResponse
import xml.etree.ElementTree as ET
import shutil
import json
import os

def is_json(my_str):
    try:
        json.loads(my_str)
    except ValueError as e:
        return False
    return True

def get_value_type(value):

    value_type = ''

    if value == 'true' or value == 'false':
        value = bool(value)
        value_type = "BOOLEAN"
    else:
        try:
            if len(value.split('.')) > 1:
                value = float(value)
            else:
                value = int(value)

            value_type = "NUMBER"
        except:
            value = str(value)
            value_type = "STRING"
            if is_json(value):
                value = value
                value_type = "JSON"
    
    return value , value_type


app = FastAPI()

html_form = """
<!DOCTYPE html>
<html>
<head>
    <title>File Upload</title>
</head>
<body>
    <form action="/upload/" method="post" enctype="multipart/form-data">
        <input type="file" name="file">
        <input type="submit" value="Upload">
    </form>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTMLResponse(content=html_form, status_code=200)

def process_file(file_path):

    tree = ET.parse(file_path)
    root = tree.getroot()
    data = {}
    for entry in root.findall('entry'):
        key = entry.find('key').text
        value = entry.find('value').text
        data[key] = value

    dict_inner = {}

    for key in data.keys():
        value = data.get(key)
        value , value_type = get_value_type(value)

        temp_dict = {"defaultValue": {"value": value},"valueType": value_type}
        dict_inner[key] = temp_dict

    dict_outer = {"parameters" : dict_inner}
    
    output_file_path = 'output.json'
    with open(output_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(dict_outer, json_file, indent=4) 

    return output_file_path

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    with open(file.filename, "wb") as f:
        shutil.copyfileobj(file.file, f)

    output_file_path = process_file(file.filename)

    # Delete the input file
    os.remove(file.filename)

    with open(output_file_path, "r") as output_file:
        file_content = output_file.read()

    response = Response(content=file_content)
    response.headers["Content-Disposition"] = f"attachment; filename=output.json"
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
