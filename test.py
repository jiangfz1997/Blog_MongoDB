import os
import re

# 匹配中文字符（Unicode 范围）
chinese_pattern = re.compile(r'[\u4e00-\u9fff]')

# 可选：限制扫描的文件扩展名（为空则不限制）
scan_extensions = {'.py', '.txt', '.js', '.java', '.go', '.md'}  # 可修改


def has_chinese(text):
    return chinese_pattern.search(text) is not None


def scan_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return False  # 如遇到无法读取的文件就跳过

    return has_chinese(content)


def scan_directory(root='.'):
    result = []

    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:

            # 扩展名过滤
            _, ext = os.path.splitext(filename)
            if scan_extensions and ext not in scan_extensions:
                continue

            full_path = os.path.join(dirpath, filename)

            if scan_file(full_path):
                result.append(full_path)

    return result


if __name__ == "__main__":
    files = scan_directory('.')

    if not files:
        print("✔ No Chinese characters found.")
    else:
        print("❗ Found Chinese characters in the following files:")
        for f in files:
            print(" -", f)
