import requests

url = "https://windskyblue-woo.hf.space/v1/chat/completions"
payload = {
    "model": "gemini-2.5-pro",
    "messages": [{"role": "user", "content": "你好"}],
    "stream": False
}
headers = {"Content-Type": "application/json"}

resp = requests.post(url, json=payload, headers=headers)
print(resp.status_code)
print(resp.text)