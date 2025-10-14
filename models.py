import google.generativeai as genai

genai.configure(api_key="AIzaSyCYhLtL657bmo1d6-aYg5Wb92eViDdj3Bs")
for m in genai.list_models():
    print(m.name)
