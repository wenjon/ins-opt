"""
清理所有"真假/矿痕/辨别/放大镜/假货"等残留
=============================================
保留"我们不这样做"的反模式说明也清理掉，让内容完全统一
"""

from pathlib import Path

ROOT = Path("D:/github/ins-opt")

# 文件 1: 04-content-drafts/00-launch-week.html Day 2 替换
file1 = ROOT / "04-content-drafts" / "00-launch-week.html"
content = file1.read_text(encoding="utf-8")

old_day2 = """<h2>Day 2（周二）｜我买的第一条水晶是假的</h2>

<h3>形式</h3>
<p>Feed 单图 + 长文案</p>

<h3>英文文案</h3>
<pre>
I have a confession.

My first "crystal bracelet" was fake.

It was perfect. Too perfect. Every bead looked the same. Glassy. Smooth.
I wore it for 6 months feeling special, until someone pointed out:
"Real crystal has inclusions. Yours doesn'\''t."

I was so embarrassed.

That day I started learning. I read about mineral formations.
I bought a 10x loupe. I started examining every stone.

Now I know: the "flaws" in natural crystal are the proof.
And I will never buy a bead that looks too perfect again.

水晶｜我买的第一条是假的
玻璃太完美，反而是红旗
"瑕疵" 才是真品的印记
现在我买每颗珠子都要用放大镜看
（希望你别像我一样交了 6 个月的 "学费"）

#CrystalConfession #RealCrystal #MyJourney
</pre>

<h3>图片描述</h3>
<ul>
<li>主体：1 条手链特写（可以是 "假" 的示范，用 1 颗玻璃 + 1 颗天然水晶对比）</li>
<li>背景：浅木桌 + 1 个放大镜</li>
<li>光线：自然光</li>
</ul>

<h3>最佳发布时间</h3>
<p><strong>晚上 20:00-21:00</strong></p>"""

new_day2 = """<h2>Day 2（周二）｜朋友们都以为我是行家</h2>

<h3>形式</h3>
<p>Feed 单图 + 长文案</p>

<h3>英文文案</h3>
<pre>
A funny thing happened when I started wearing crystal daily.

Friends kept asking:
"Where did you get that?"
"How do you pick them?"
"Are you a crystal expert now?"

I'\''m not.
I just wear one every day. That'\''s it.

But I noticed: wearing the same thing daily, people assume you know more than you do.

So I started answering honestly:
"I don'\''t know much. I just like how this one feels."

Funny how that works.

一件有趣的事发生在我开始天天戴水晶之后。

朋友们老问：
"你哪儿买的？"
"你怎么挑的？"
"你是水晶行家吗？"

我不是。
我就是天天戴。就这些。

但我发现：天天戴一样东西，别人会以为你懂很多。

所以我开始诚实回答：
"我不懂什么。我就是喜欢这颗戴起来的感觉。"

好笑的是，这就够了。

#MyCrystalDiary #NotAnExpert #JustWear
</pre>

<h3>图片描述</h3>
<ul>
<li>主体：作者手腕戴水晶的特写</li>
<li>背景：日常生活场景（咖啡店 / 办公桌 / 家里）</li>
<li>光线：自然光</li>
</ul>

<h3>最佳发布时间</h3>
<p><strong>晚上 20:00-21:00</strong></p>"""

if old_day2 in content:
    content = content.replace(old_day2, new_day2)
    file1.write_text(content, encoding="utf-8")
    print("✓ 00-launch-week.html Day 2 替换")
else:
    print("- Day 2 模式未找到")


# 文件 2 & 3: 清理"我不用放大镜/矿痕/真假"等反模式说明
replacements = [
    # series-02-natural.html
    (
        ROOT / "04-content-drafts" / "series-02-natural.html",
        "不做真假辨别，不教人识别矿痕，只分享我和水晶之间的故事",
        "只分享我的佩戴日常和感受"
    ),
    (
        ROOT / "04-content-drafts" / "series-02-natural.html",
        "I'\''m not an expert. I don'\''t use a loupe. I don'\''t memorize mineral charts.",
        "I'\''m not an expert. I just wear it and see how I feel."
    ),
    (
        ROOT / "04-content-drafts" / "series-02-natural.html",
        "我不是专家。不用放大镜，不背矿物图。",
        "我不是专家。戴着看感觉就好。"
    ),
    (
        ROOT / "04-content-drafts" / "series-02-natural.html",
        "就这样。没专业知识。没用过放大镜。",
        "就这样。没什么专业知识。"
    ),
    # 03-copy-templates/02-natural.html
    (
        ROOT / "03-copy-templates" / "02-natural.html",
        "不做真假辨别，不教人识别矿痕，只分享我和水晶之间的故事",
        "只分享旅程和感受"
    ),
    (
        ROOT / "03-copy-templates" / "02-natural.html",
        "I don'\''t use a loupe",
        ""
    ),
    (
        ROOT / "03-copy-templates" / "02-natural.html",
        "不用放大镜",
        ""
    ),
    (
        ROOT / "03-copy-templates" / "02-natural.html",
        "没用过放大镜",
        ""
    ),
    # 03-copy-templates/index.html
    (
        ROOT / "03-copy-templates" / "index.html",
        "我的假货故事、真实体验",
        "我的水晶旅程、佩戴日常"
    ),
    # 04-content-drafts/index.html
    (
        ROOT / "04-content-drafts" / "index.html",
        "我的真假对比实验",
        "我的水晶日常记录"
    ),
    # 04-content-drafts/series-04-luck.html
    (
        ROOT / "04-content-drafts" / "series-04-luck.html",
        "under loupe",
        "up close"
    ),
    (
        ROOT / "04-content-drafts" / "series-04-luck.html",
        "放大镜下",
        "近距离看"
    ),
    (
        ROOT / "04-content-drafts" / "series-04-luck.html",
        "I'\''ll send photos of each stone (under loupe)",
        "I'\''ll send photos of each stone up close"
    ),
    (
        ROOT / "04-content-drafts" / "series-04-luck.html",
        "想看每颗石头放大镜下的照片",
        "想看每颗石头近距离的照片"
    ),
    (
        ROOT / "04-content-drafts" / "series-04-luck.html",
        "想看放大镜下的真品长什么样",
        "想看近距离的真品长什么样"
    ),
    (
        ROOT / "04-content-drafts" / "series-04-luck.html",
        "想看放大镜下的细节",
        "想看近距离的细节"
    ),
]

for path, old, new in replacements:
    if not path.exists():
        print(f"- 文件不存在: {path.name}")
        continue
    content = path.read_text(encoding="utf-8")
    if old in content:
        content = content.replace(old, new)
        path.write_text(content, encoding="utf-8")
        print(f"✓ {path.name}: '{old[:30]}...' → '{new[:30] if new else '(empty)'}...'")
    else:
        print(f"- 未找到: {path.name} '{old[:30]}...'")


# 清理任何残留的"fake" 单词在 launch week 中
launch = ROOT / "04-content-drafts" / "00-launch-week.html"
content = launch.read_text(encoding="utf-8")
launch_replacements = [
    ('"fake crystal confession"', '"first time wearing daily"'),
    ('"My fake crystal confession"', '"My first time wearing daily"'),
    ('"fake crystal confession" and', '"first time wearing" and'),
    ('"I wore a fake one for 6 months"', '"I wore my first one for 6 months"'),
]
for old, new in launch_replacements:
    if old in content:
        content = content.replace(old, new)
        launch.write_text(content, encoding="utf-8")
        print(f"✓ 00-launch-week.html: '{old[:30]}...' → '{new[:30]}...'")

print("\n✅ 全部清理完成")
