"""校验这个仓库还符合 WorkBuddy 技能的契约。

契约只有四条，坏任何一条，别人 clone 下来技能都不会加载，而且不会报错：

1. SKILL.md 在仓库根（因为安装是一行 clone 到 ~/.workbuddy/skills/agent-team）
2. frontmatter 里有 name 和 description，都不为空
3. README 里出现当前仓库地址，安装说明跟着仓库名走
4. README 里的安装路径是 ~/.workbuddy/skills，不是别的工具的目录
"""

import os
import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = pathlib.Path(__file__).resolve().parent.parent
errors: list[str] = []

# 1 + 2：技能本体
skill = ROOT / "SKILL.md"
if not skill.is_file():
    errors.append("SKILL.md 不在仓库根，克隆下来技能不会加载")
else:
    text = skill.read_text(encoding="utf-8")
    front = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not front:
        errors.append("SKILL.md 开头没有 YAML frontmatter")
    else:
        for field in ("name", "description"):
            found = re.search(rf"^{field}:\s*(.+)$", front.group(1), re.M)
            if not found or not found.group(1).strip():
                errors.append(f"frontmatter 里的 {field} 缺失或为空")

# 3 + 4：安装说明
readme = ROOT / "README.md"
if not readme.is_file():
    errors.append("README.md 不存在")
else:
    body = readme.read_text(encoding="utf-8")

    repo = os.environ.get("GITHUB_REPOSITORY", "")
    if not repo:
        try:
            url = subprocess.check_output(
                ["git", "remote", "get-url", "origin"], cwd=ROOT, text=True
            ).strip()
            repo = re.sub(r"\.git$", "", url)
            repo = re.sub(r"^.*github\.com[:/]", "", repo)
        except Exception:
            repo = ""
    if repo and repo not in body:
        errors.append(f"README 里没出现仓库地址 {repo}，安装说明可能没跟着改名")

    if "~/.workbuddy/skills" not in body:
        errors.append("README 里没有 ~/.workbuddy/skills，安装路径可能写错")

if errors:
    print("校验失败：")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print("校验通过：SKILL.md 在根、frontmatter 完整、安装说明指向 WorkBuddy")
