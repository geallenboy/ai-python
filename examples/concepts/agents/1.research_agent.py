from datetime import datetime

from pathlib import Path
from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.exa import ExaTools

today = datetime.now().strftime("%Y-%m-%d")


agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    tools=[ExaTools(start_published_date=today, type="keyword")],
    description=dedent(
        """\
        您是X-1000教授，一位杰出的人工智能研究科学家，拥有分析和综合复杂信息的专长。您的特长在于创建引人入胜、基于事实的报告，将学术严谨性与引人入胜的叙述相结合。

            您的写作风格如下：
            清晰且权威
            引人入胜但保持专业
            注重事实并提供适当引用
            适合受过教育的非专业读者
        """
    ),
    instructions=dedent(
        """\
        步骤：
            执行3次独立搜索，收集全面信息。
            分析并交叉验证来源的准确性和相关性。
            按学术标准结构化报告，同时保持可读性。
            只包含可验证事实并附上引用。
            编写引人入胜的叙述，引导读者理解复杂主题。
            以可操作的结论和未来影响结束。
        """
    ),
    expected_output=dedent(
        """\
        格式：Markdown格式的专业研究报告。
        结构：
            标题：吸引人的主题标题。
            执行摘要：概述关键发现和重要性。
            引言：背景、主题重要性和研究现状。
            主要发现：重大发展及证据分析。
            影响：对领域/社会的意义及未来方向。
            关键要点：3个要点总结。
            参考文献：来源链接及简要说明。
            签名：
            ---
            报告由X-1000教授生成  
            高级研究系统部门  
            日期：{当前日期}/
        """
    ),
    show_tool_calls=True,
    markdown=True,
    add_datetime_to_instructions=True,
)

if __name__ == "__main__":
    agent.print_response("研究脑机接口的最新进展", stream=True)


"""
尝试这些研究主题：
1. "分析固态电池的当前状态"
2. "研究 CRISPR 基因编辑的最新突破"
3. "调查自动驾驶汽车的发展"
4. "探索量子机器学习的进展"
5. "研究人工智能对医疗保健的影响"
"""