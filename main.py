"""
命令行入口：通过终端和Agent对话
"""

from agent import SmartAgent


def main():
    print("=" * 60)
    print("🌟 小智 - 全能AI助手（命令行版）🌟")
    print("=" * 60)

    # 初始化Agent
    agent = SmartAgent()

    # 使用说明
    print("\n📖 命令说明：")
    print("-" * 40)
    print("  直接输入  → 和AI对话")
    print("  'clear'   → 清空对话记忆")
    print("  'rebuild' → 重建知识库（更新文档后用）")
    print("  'quit'    → 退出")
    print("-" * 40)
    print(f"  可用工具：{', '.join(agent.get_tool_names())}")
    # join() 把列表用指定分隔符连接成字符串
    # ['a','b','c'] → "a, b, c"
    print()

    while True:
        user_input = input("\n👤 你：").strip()

        if not user_input:
            continue

        if user_input.lower() == "quit":
            print("\n👋 再见！")
            break

        if user_input.lower() == "clear":
            agent.clear_history()
            print("🗑️ 对话记忆已清空！")
            continue

        if user_input.lower() == "rebuild":
            print("🔄 正在重建知识库...")
            agent.rebuild_knowledge_base()
            continue

        # 调用Agent
        answer, tools_used = agent.chat(user_input)

        # 显示使用的工具
        if tools_used:
            print(f"\n  📎 使用了 {len(tools_used)} 个工具：")
            for tool_info in tools_used:
                print(f"     🔧 {tool_info['name']}: {tool_info['result'][:80]}")

        print(f"\n🤖 小智：{answer}")


if __name__ == "__main__":
    main()