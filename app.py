from src.main import app as fastapi_app
import gradio as gr
from fastapi import FastAPI

# 定义 Gradio 聊天界面
def create_gradio_app():
    with gr.Blocks(title="Gemini AI 聊天助手") as demo:
        gr.Markdown("# Gemini AI 聊天助手\n体验 Gemini 模型的自然语言对话。")
        chatbot = gr.Chatbot(type='messages')
        msg = gr.Textbox(label="输入你的问题")
        send = gr.Button("发送")
        clear = gr.Button("清空对话")
        def respond(user_message, chat_history):
            return "", chat_history
        send.click(respond, [msg, chatbot], [msg, chatbot])
        clear.click(lambda: ([], ""), None, [chatbot, msg])
    return demo

gradio_app = create_gradio_app()

# 创建 FastAPI 应用
app = FastAPI()
# 挂载 Gradio 到 /ui
import gradio
app = gradio.mount_gradio_app(app, gradio_app, path="/ui")
# 挂载你的 API 路由
app.mount("/", fastapi_app)

