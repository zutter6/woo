from src.main import app as fastapi_app
import gradio as gr
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware

# 定义 Gradio 聊天界面
def create_gradio_app():
    with gr.Blocks(title="Gemini AI 聊天助手") as demo:
        gr.Markdown("# Gemini AI 聊天助手\n体验 Gemini 模型的自然语言对话。")
        chatbot = gr.Chatbot(type='messages')
        msg = gr.Textbox(label="输入你的问题")
        send = gr.Button("发送")
        clear = gr.Button("清空对话")
        def respond(user_message, chat_history):
            # 这里只做演示，实际可调用你的API
            return "", chat_history
        send.click(respond, [msg, chatbot], [msg, chatbot])
        clear.click(lambda: ([], ""), None, [chatbot, msg])
    return demo

gradio_app = create_gradio_app()

# 创建 FastAPI 应用，并挂载 Gradio 到 /ui
app = FastAPI()
app.mount("/ui", WSGIMiddleware(gradio_app.server_app))
app.mount("/", fastapi_app)  

