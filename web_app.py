"""
Web界面：通过浏览器和Agent对话
使用Gradio框架，几行代码就能创建漂亮的Web界面
"""

import gradio as gr
# gradio 是一个Python库，专门为AI应用快速创建Web界面
# 不需要学前端知识（HTML/CSS/JS），纯Python就能搞定

from agent import SmartAgent
import config


def create_web_app():
    """创建并返回Web应用"""

    print("🌐 正在初始化Web应用...")
    agent = SmartAgent()

    def respond(message: str, chat_history: list) -> tuple:
        """
        处理用户消息的回调函数
        Gradio会自动调用这个函数

        参数：
            message: 用户输入的文字
            chat_history: Gradio维护的对话历史
                格式：[{"role": "user", "content": "..."},
                       {"role": "assistant", "content": "..."}]

        返回：
            (空字符串, 更新后的对话历史)
            空字符串用来清空输入框
        """

        if not message.strip():
            return "", chat_history

        # 调用Agent
        answer, tools_used = agent.chat(message)

        # 如果使用了工具，把工具信息附加到回答后面
        if tools_used:
            tool_info = "\n\n---\n📎 **本次使用的工具：**\n"
            for t in tools_used:
                tool_info += f"- 🔧 **{t['name']}**：`{t['result'][:100]}`\n"
            answer += tool_info

        # 更新Gradio的对话历史格式
        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": answer})

        return "", chat_history
        # 第一个返回值""会清空输入框
        # 第二个返回值更新聊天显示

    def clear_all():
        """清空对话"""
        agent.clear_history()
        return [], ""
        # 返回空列表清空聊天记录，空字符串清空输入框

    def rebuild_kb():
        """重建知识库"""
        agent.rebuild_knowledge_base()
        return "✅ 知识库重建完成！"

    # ============ 构建界面 ============
    # Gradio使用 with 语句来构建界面布局
    # 类似于搭积木，一块一块往上叠

    with gr.Blocks(
        # title=config.WEB_TITLE,
        theme=gr.themes.Soft()
        # theme 设置主题风格，Soft()是柔和风格
    ) as app:



        # 标题
        gr.Markdown(f"# {config.WEB_TITLE}")
        # Markdown() 组件：显示Markdown格式的文字
        # # 是Markdown的一级标题语法

        gr.Markdown(config.WEB_DESCRIPTION)

        # 聊天区域
        chatbot = gr.Chatbot(
            height=500,
            label="对话记录",
            #type="messages"
            # type="messages" 使用新的消息格式
            # 每条消息是 {"role": "user/assistant", "content": "..."}
        )

        # 输入区域：一行放输入框和发送按钮
        with gr.Row():
            # Row() 让里面的组件横向排列
            msg_input = gr.Textbox(
                placeholder="输入你的问题...",
                label="",
                scale=8
                # scale=8 占据8份宽度
            )
            send_btn = gr.Button(
                "发送 📤",
                variant="primary",
                # variant="primary" 主按钮样式（蓝色高亮）
                scale=1
            )

        # 功能按钮区域
        with gr.Row():
            clear_btn = gr.Button("🗑️ 清空对话")
            rebuild_btn = gr.Button("🔄 重建知识库")
            status_text = gr.Textbox(
                label="状态",
                interactive=False
                # interactive=False 用户不能编辑，只用来显示状态
            )

        # ============ 绑定事件 ============
        # 点击发送按钮 → 调用respond函数
        send_btn.click(
            fn=respond,
            # fn 指定要调用的函数
            inputs=[msg_input, chatbot],
            # inputs 指定传给函数的参数（对应函数的参数列表）
            outputs=[msg_input, chatbot]
            # outputs 指定函数返回值要更新哪些组件
        )

        # 按回车键也能发送（和点按钮一样的效果）
        msg_input.submit(
            fn=respond,
            inputs=[msg_input, chatbot],
            outputs=[msg_input, chatbot]
        )

        # 清空按钮
        clear_btn.click(
            fn=clear_all,
            outputs=[chatbot, msg_input]
        )

        # 重建知识库按钮
        rebuild_btn.click(
            fn=rebuild_kb,
            outputs=[status_text]
        )

    return app


# ============ 启动Web应用 ============
if __name__ == "__main__":
    app = create_web_app()

    print("\n" + "=" * 60)
    print(f"🌐 Web界面已启动！")
    print(f"   本机访问：http://localhost:{config.WEB_PORT}")
    print(f"   局域网访问：http://你的IP:{config.WEB_PORT}")
    print("=" * 60)

    app.launch(
        server_name=config.WEB_HOST,
        server_port=config.WEB_PORT,
        share=False
        # share=True 可以生成公网链接（需要外网），这里关闭
    )