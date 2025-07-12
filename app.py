
import gradio as gr
import requests
import os

# 你后端 FastAPI 服务的地址（本地测试用 http://127.0.0.1:8000，部署到 Hugging Face 用 Space 的 API 地址）
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000/v1/chat/completions")

def chat_with_gemini(message, history):
    messages = [{"role": "user", "content": message}]
    payload = {
        "model": "gemini-2.5-pro",  # 你支持的模型名
        "messages": messages,
        "stream": False
    }
    try:
        resp = requests.post(BACKEND_URL, json=payload, timeout=30)
        data = resp.json()
        if "choices" in data and data["choices"]:
            reply = data["choices"][0]["message"]["content"]
        else:
            reply = "未获取到有效回复。"
    except Exception as e:
        reply = f"请求出错: {e}"
    return reply

with gr.Blocks(title="Gemini AI 聊天助手") as demo:
    gr.Markdown("# Gemini AI 聊天助手\n体验 Gemini 模型的自然语言对话。")
    chatbot = gr.Chatbot()
    msg = gr.Textbox(label="输入你的问题")
    send = gr.Button("发送")
    clear = gr.Button("清空对话")

    def respond(user_message, chat_history):
        reply = chat_with_gemini(user_message, chat_history)
        chat_history = chat_history + [[user_message, reply]]
        return "", chat_history

    send.click(respond, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: ([], ""), None, [chatbot, msg])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)