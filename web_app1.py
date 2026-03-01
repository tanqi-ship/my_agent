"""
Web界面：通过浏览器和Agent对话
使用Gradio框架，几行代码就能创建漂亮的Web界面
"""

import gradio as gr
from agent import SmartAgent
import config


def create_web_app():
    """创建并返回Web应用"""
    print("🌐 正在初始化Web应用...")
    agent = SmartAgent()

    def respond(message: str, chat_history: list) -> tuple:
        if not message.strip():
            return "", chat_history

        answer, tools_used = agent.chat(message)

        if tools_used:
            tool_info = "\n\n---\n📎 **本次使用的工具：**\n"
            for t in tools_used:
                tool_info += f"- 🔧 **{t['name']}**：`{t['result'][:100]}`\n"
            answer += tool_info

        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": answer})

        return "", chat_history

    def clear_all():
        agent.clear_history()
        return [], ""

    def rebuild_kb():
        agent.rebuild_knowledge_base()
        return "✅ 知识库重建完成！"

    # 构建界面（Blocks 不传 theme）
    with gr.Blocks() as app:
        gr.Markdown(f"# {config.WEB_TITLE}")
        gr.Markdown(config.WEB_DESCRIPTION)

        chatbot = gr.Chatbot(height=500, label="对话记录")

        with gr.Row():
            msg_input = gr.Textbox(placeholder="输入你的问题...", label="", scale=8)
            send_btn = gr.Button("发送 📤", variant="primary", scale=1)

        with gr.Row():
            clear_btn = gr.Button("🗑️ 清空对话")
            rebuild_btn = gr.Button("🔄 重建知识库")
            status_text = gr.Textbox(label="状态", interactive=False)

        send_btn.click(fn=respond, inputs=[msg_input, chatbot], outputs=[msg_input, chatbot])
        msg_input.submit(fn=respond, inputs=[msg_input, chatbot], outputs=[msg_input, chatbot])
        clear_btn.click(fn=clear_all, outputs=[chatbot, msg_input])
        rebuild_btn.click(fn=rebuild_kb, outputs=[status_text])

    return app


if __name__ == "__main__":
    app = create_web_app()

    print("\n" + "=" * 60)
    print(f"🌐 Web界面已启动！")
    print(f"   本机访问：http://localhost:{config.WEB_PORT}")
    print(f"   局域网访问：http://你的IP:{config.WEB_PORT}")
    print("=" * 60)

    # theme 放在 launch() 里（Gradio 6+ 要求）
    app.launch(
        server_name=config.WEB_HOST,
        server_port=config.WEB_PORT,
        share=False,
        theme=gr.themes.Soft()
    )