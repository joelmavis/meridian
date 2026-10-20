import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_radar.py"


def message(index: int, priority: str = "P2", is_x_post: bool = False) -> str:
    x_fields = (
        '<p><strong>来源类型：</strong>X 原帖</p><p><strong>作者／机构：</strong>测试机构</p>'
        '<p><strong>原帖语言：</strong>英文</p>'
    ) if is_x_post else ""
    source = f"https://x.com/example/status/{index}" if is_x_post else f"https://example.org/{index}"
    return f"""<article>
  <h3>{index}. 测试消息</h3>
  <p>重要性：中</p>
  <p>优先级：{priority}</p>
  <p>发生了什么：一项可验证的变化。</p>
  <p>为什么值得关注：它可能影响全球 AI 治理。</p>
  <p>适合做什么类型内容：快评文章</p>
  {x_fields}
  <p>来源：<a href=\"{source}\">原始来源</a></p>
</article>"""


def report(messages: str) -> str:
    return f"""<!doctype html>
<html lang=\"zh-CN\"><body>
<h1>Meridian｜全球 AI 治理晨报</h1>
<h2>今日 10 条消息</h2>
{messages}
<h2>本日判断</h2><h3>可确认事实</h3><p>事实。</p>
<h3>基于现有事实的推论</h3><p>推论。</p>
<h2>今日建议</h2><p>下一步。</p>
<h2>来源与方法说明</h2><p>说明。</p>
</body></html>"""


class RadarValidationTests(unittest.TestCase):
    def validate(self, text: str) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "daily.html"
            path.write_text(text, encoding="utf-8")
            return subprocess.run([sys.executable, str(VALIDATOR), str(path)], capture_output=True, text=True)

    def test_accepts_exactly_ten_messages(self):
        messages = "\n".join(message(index, is_x_post=index <= 3) for index in range(1, 11))
        self.assertEqual(self.validate(report(messages)).returncode, 0)

    def test_rejects_fewer_than_ten_messages(self):
        messages = "\n".join(message(index, is_x_post=index <= 3) for index in range(1, 10))
        self.assertNotEqual(self.validate(report(messages)).returncode, 0)

    def test_rejects_message_without_source_link(self):
        messages = "\n".join(message(index, is_x_post=index <= 3) for index in range(1, 11))
        self.assertNotEqual(self.validate(report(messages.replace('href=\"https://example.org/4\"', ''))).returncode, 0)

    def test_accepts_p3_background_signal(self):
        messages = "\n".join(message(index, "P3" if index == 10 else "P2", index <= 3) for index in range(1, 11))
        self.assertEqual(self.validate(report(messages)).returncode, 0)

    def test_rejects_fewer_than_three_x_posts(self):
        messages = "\n".join(message(index, is_x_post=index <= 2) for index in range(1, 11))
        self.assertNotEqual(self.validate(report(messages)).returncode, 0)
