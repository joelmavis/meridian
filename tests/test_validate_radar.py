import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_radar.py"


def signal(title: str, priority: str = "P1") -> str:
    return f"""### 1. {title}

优先级：{priority}
发生了什么：一项可验证的变化。
为什么重要：它可能改变治理或依赖关系。
所属研究方向：欧洲科技政治
与欧洲 AI 治理的关系：该变化直接影响欧盟 AI 治理的实施或外部影响。
来源：https://example.org/primary
建议动作：快速研究
"""


class RadarValidationTests(unittest.TestCase):
    def validate(self, text: str) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "daily.md"
            path.write_text("# 每日情报雷达\n\n## 今日 3 个信号\n\n" + text, encoding="utf-8")
            return subprocess.run([sys.executable, str(VALIDATOR), str(path)], capture_output=True, text=True)

    def test_accepts_exactly_three_signals(self):
        text = "\n".join(signal(f"信号{i}").replace("### 1.", f"### {i}.") for i in range(1, 4))
        self.assertEqual(self.validate(text).returncode, 0)

    def test_rejects_more_than_three_signals(self):
        text = "\n".join(signal(f"信号{i}").replace("### 1.", f"### {i}.") for i in range(1, 5))
        self.assertNotEqual(self.validate(text).returncode, 0)

    def test_rejects_fewer_than_three_signals(self):
        self.assertNotEqual(self.validate(signal("官方政策变化")).returncode, 0)

    def test_accepts_a_counter_signal(self):
        text = "\n".join(
            signal(title, priority).replace("### 1.", f"### {index}.")
            for index, (title, priority) in enumerate(
                [
                    ("成员国公开反对共同云主权框架", "P2"),
                    ("官方政策变化", "P1"),
                    ("基础设施建设进展", "P3"),
                ],
                start=1,
            )
        )
        self.assertEqual(self.validate(text).returncode, 0)

    def test_accepts_global_ai_geopolitics_track(self):
        text = "\n".join(
            signal(title, priority)
            .replace("### 1.", f"### {index}.")
            .replace("所属研究方向：欧洲科技政治", "所属研究方向：全球AI地缘政治与多边治理")
            for index, (title, priority) in enumerate(
                [
                    ("多边 AI 标准进展", "P1"),
                    ("全球南方基础设施项目", "P2"),
                    ("区域政策动态", "P3"),
                ],
                start=1,
            )
        )
        self.assertEqual(self.validate(text).returncode, 0)
