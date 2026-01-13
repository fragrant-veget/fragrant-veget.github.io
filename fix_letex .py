""" 建议使用之前先把要转换的文档备份，将该脚本放在hexo根目录里，使用的时候修改一下要转换文件的相对路径，如果不修改就是转换source文件夹里面的所有文档"""
import re
import os
import sys
from pathlib import Path
def escape_backslashes_in_math(content: str) -> str:
    """
    在 Markdown 的数学公式中将 \\ 替换为 \\\\，跳过代码块。
    """
    # 1. 提取所有代码块（包括行内和多行），临时替换为占位符
    placeholders = []

    def replace_code_block(match):
        temp_placeholder = f"__CODE_BLOCK_{len(placeholders)}__"
        placeholders.append(match.group(0))
        return temp_placeholder

    # 匹配多行代码块：``` ... ```
    content = re.sub(r'```[\s\S]*?```', replace_code_block, content)

    # 匹配行内代码：`...`
    content = re.sub(r'`[^`]*`', replace_code_block, content)

    # 2. 在非代码区域中处理数学公式
    def replace_display_math(match):
        # match.group(1) 是 $$...$$ 中的内容
        inner = match.group(1)
        # 将 \ 转义为 \\，但注意：原始 \\ 在字符串中是 "\\\\"，所以我们要找 "\\"
        # 实际上在 raw string 中，我们匹配 r'\\' 即可
        fixed_inner = re.sub(r'\\\\', r'\\\\\\\\', inner)
        return '$$' + fixed_inner + '$$'

    def replace_inline_math(match):
        inner = match.group(1)
        fixed_inner = re.sub(r'\\\\', r'\\\\\\\\', inner)
        return '$' + fixed_inner + '$'

    # 处理行间公式：$$ ... $$
    content = re.sub(r'\$\$(.*?)\$\$', replace_display_math, content, flags=re.DOTALL)

    # 处理行内公式：$ ... $
    content = re.sub(r'\$(.*?)\$', replace_inline_math, content)

    # 3. 恢复代码块
    for i, code in enumerate(placeholders):
        placeholder = f"__CODE_BLOCK_{i}__"
        content = content.replace(placeholder, code, 1)

    return content


def process_file(file_path: Path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    new_content = escape_backslashes_in_math(content)

    if new_content != content:
        print(f"✅ 已修复: {file_path}")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
    else:
        print(f"⏩ 无变化: {file_path}")


def main():
    # 默认处理 Hexo 的文章目录
    posts_dir = Path("source/_posts/线性代数/矩阵/")

    if not posts_dir.exists():
        print(f"❌ 目录不存在: {posts_dir.absolute()}")
        print("请将脚本放在 Hexo 项目根目录下运行。")
        sys.exit(1)

    md_files = list(posts_dir.rglob("*.md"))
    if not md_files:
        print("⚠️ 未找到 .md 文件")
        return

    print(f"🔍 找到 {len(md_files)} 个 Markdown 文件，开始处理...")
    for md_file in md_files:
        process_file(md_file)

    print("🎉 所有文件处理完成！")


if __name__ == "__main__":
    main()