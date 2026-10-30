# -*- coding: utf-8 -*-
"""Generate title cards and lower-third overlays for the car video draft."""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(OUT, exist_ok=True)

FONT_B = r"C:\Windows\Fonts\msyhbd.ttc"
FONT_R = r"C:\Windows\Fonts\msyh.ttc"
INK = (24, 26, 30)
GRAY = (105, 112, 122)
LIGHT = (246, 245, 241)
RED = (176, 58, 46)
BLUE = (31, 78, 121)


def font(path, size):
    return ImageFont.truetype(path, size, index=0)


def text_w(draw, s, f):
    box = draw.textbbox((0, 0), s, font=f)
    return box[2] - box[0], box[3] - box[1]


def center_text(draw, y, s, f, fill=INK, spacing=10):
    w, h = text_w(draw, s, f)
    draw.multiline_text(((W - w) / 2, y), s, font=f, fill=fill,
                        align="center", spacing=spacing)


def base_card():
    im = Image.new("RGB", (W, H), LIGHT)
    d = ImageDraw.Draw(im)
    # Very light paper texture: fine horizontal rules
    for y in range(0, H, 8):
        d.line([(0, y), (W, y)], fill=(242, 241, 237), width=1)
    # thin top bar
    d.rectangle([0, 0, W, 10], fill=RED)
    return im, d


def top_line(d, s="2026 全国大学生嵌入式芯片与系统设计竞赛 · FPGA 创新设计赛道"):
    f = font(FONT_R, 26)
    d.text((92, 64), s, font=f, fill=GRAY)
    d.line([(92, 112), (92 + 72, 112)], fill=RED, width=4)


def bottom_note(d, s=None):
    d.text((W - 340, H - 66), "Zynq-7020 + VIM3", font=font(FONT_B, 24), fill=BLUE)


def title_card():
    im, d = base_card()
    top_line(d)
    center_text(d, 250, "基于 AMD Zynq-7020 与 Khadas VIM3 的", font(FONT_R, 46), GRAY)
    center_text(d, 330, "异构智能小车", font(FONT_B, 118), INK)
    center_text(d, 498, "实时控制平台", font(FONT_B, 96), RED)
    d.line([(W / 2 - 120, 660), (W / 2 + 120, 660)], fill=INK, width=5)
    center_text(d, 700, "Zynq-7020 PL 确定性实时控制  ×  Khadas VIM3 策略调度", font(FONT_R, 32), INK)
    bottom_note(d)
    im.save(os.path.join(OUT, "01_title.png"))


def section_card(name, number, headline, sub):
    im, d = base_card()
    top_line(d)
    # huge pale number on the right
    d.text((W - 520, 210), number, font=font(FONT_B, 330), fill=(232, 230, 224))
    f_small = font(FONT_B, 34)
    d.text((92, 260), f"{number} / {name}", font=f_small, fill=RED)
    d.line([(92, 315), (92 + 90, 315)], fill=RED, width=5)
    # headline can be two lines
    f = font(FONT_B, 78)
    draw_lines(d, 390, headline, f, INK, 22)
    d.text((96, 690), sub, font=font(FONT_R, 30), fill=GRAY)
    bottom_note(d)
    im.save(os.path.join(OUT, f"{number}_{name}.png"))


def draw_lines(d, y, text, f, fill, spacing=18):
    lines = text.split("\n")
    for line in lines:
        d.text((92, y), line, font=f, fill=fill)
        y += f.size + spacing


def box(d, rect, title, sub, fill, line, title_color=INK, sub_color=GRAY, title_size=32, sub_size=22):
    d.rounded_rectangle(rect, radius=10, fill=fill, outline=line, width=2)
    x1, y1, x2, y2 = rect
    d.text((x1 + 18, y1 + 14), title, font=font(FONT_B, title_size), fill=title_color)
    if sub:
        d.text((x1 + 18, y1 + 58), sub, font=font(FONT_R, sub_size), fill=sub_color)


def architecture_card():
    im, d = base_card()
    top_line(d)
    d.text((92, 145), "02 / 系统分块", font=font(FONT_B, 34), fill=RED)
    d.line([(92, 200), (92 + 90, 200)], fill=RED, width=5)
    d.text((92, 228), "Zynq-7020 PL 负责“必须准时”，Khadas VIM3 负责“怎么走”", font=font(FONT_B, 44), fill=INK)

    # Sensors
    d.text((96, 300), "感知", font=font(FONT_B, 30), fill=BLUE)
    sensor_names = ["五路循迹", "红外避障", "超声测距", "正交编码器"]
    xs = [230, 600, 970, 1340]
    for x, name in zip(xs, sensor_names):
        box(d, [x, 288, x + 300, 378], name, "", (255, 255, 255), (207, 210, 214), title_size=28)

    # FPGA and MCU panels
    fpga = [90, 430, 880, 760]
    mcu = [1000, 430, 1830, 760]
    d.rounded_rectangle(fpga, radius=12, fill=(231, 241, 250), outline=(70, 120, 170), width=3)
    d.rounded_rectangle(mcu, radius=12, fill=(248, 238, 235), outline=(176, 90, 76), width=3)
    d.text((fpga[0] + 24, fpga[1] + 18), "Zynq-7020 PL 实时层", font=font(FONT_B, 36), fill=BLUE)
    d.text((mcu[0] + 24, mcu[1] + 18), "Khadas VIM3 策略层", font=font(FONT_B, 36), fill=RED)

    fpga_items = [("20 kHz PWM", "四路 · 相位对齐"), ("正交解码", "4 倍频 · 周期测量"),
                  ("超声计时", "μs 级 · 不阻塞"), ("硬件急停", "阈值判决 · 旁路 MCU")]
    mcu_items = [("状态机", "INIT/IDLE/LINE/AVOID"), ("速度闭环", "左右轮独立 PI"),
                 ("串口命令", "A/B/C/D/I/L/O/R"), ("故障处理", "超时/CRC/急停")]
    for i, (a, b) in enumerate(fpga_items):
        x = fpga[0] + 20 + (i % 2) * 385
        y = fpga[1] + 78 + (i // 2) * 122
        box(d, [x, y, x + 365, y + 112], a, b, (255, 255, 255), (160, 190, 215), title_size=29, sub_size=22)
    for i, (a, b) in enumerate(mcu_items):
        x = mcu[0] + 20 + (i % 2) * 405
        y = mcu[1] + 78 + (i // 2) * 122
        box(d, [x, y, x + 385, y + 112], a, b, (255, 255, 255), (220, 180, 170), title_size=29, sub_size=22)

    # SPI link
    d.line([(880, 590), (1000, 590)], fill=INK, width=4)
    d.polygon([(1000, 590), (984, 581), (984, 599)], fill=INK)
    d.text((890, 540), "SPI 9 MHz", font=font(FONT_B, 20), fill=INK)
    d.text((890, 610), "快照/命令", font=font(FONT_R, 19), fill=GRAY)

    # Actuators
    d.text((96, 806), "执行", font=font(FONT_B, 30), fill=BLUE)
    box(d, [230, 792, 750, 882], "四驱电机", "PWM + DIR ×4", (255, 255, 255), (207, 210, 214), title_size=32, sub_size=24)
    box(d, [800, 792, 1120, 882], "舵机", "500–2500 μs", (255, 255, 255), (207, 210, 214), title_size=32, sub_size=24)

    # Safety bypass note
    d.rounded_rectangle([1160, 790, 1824, 892], radius=8, fill=(253, 236, 233), outline=(176, 58, 46), width=2)
    d.text((1180, 802), "硬急停旁路", font=font(FONT_B, 32), fill=RED)
    d.text((1180, 842), "红外/超声阈值 → 立即撤驱，不经过主控", font=font(FONT_R, 24), fill=INK)

    bottom_note(d)
    im.save(os.path.join(OUT, "03_architecture.png"))


PHOTO_FULL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "board_new_full.jpg")
PHOTO_TOP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "board_new_full.jpg")


def photo_panel(im, d, path, box, crop=None):
    src = Image.open(path).convert("RGB")
    if crop:
        src = src.crop(crop)
    x1, y1, x2, y2 = box
    scale = min((x2 - x1) / src.width, (y2 - y1) / src.height)
    w, h = int(src.width * scale), int(src.height * scale)
    src = src.resize((w, h), Image.LANCZOS)
    x = x1 + (x2 - x1 - w) // 2
    y = y1 + (y2 - y1 - h) // 2
    d.rectangle([x - 14, y - 14, x + w + 14, y + h + 14], fill=(255, 255, 255), outline=(215, 212, 205), width=2)
    im.paste(src, (x, y))


def hardware_full():
    im, d = base_card()
    top_line(d)
    d.text((92, 145), "03 / 硬件实物", font=font(FONT_B, 34), fill=RED)
    d.line([(92, 200), (92 + 90, 200)], fill=RED, width=5)
    d.text((92, 228), "Zynq-7020 + Khadas VIM3 实拍", font=font(FONT_B, 54), fill=INK)
    photo_panel(im, d, PHOTO_FULL, [90, 320, 610, 970])
    blocks = [
        ("Zynq-7020", "PL 实时层：PWM / 编码器 / 急停 / 时间戳", (231, 241, 250), (70, 120, 170)),
        ("Khadas VIM3", "Amlogic A311D · 5 TOPS NPU · 策略层", (248, 238, 235), (176, 90, 76)),
        ("板间互连", "SPI 9 MHz · 电源 · 共地", (243, 242, 236), (150, 145, 135)),
    ]
    y = 330
    for title, desc, fill, line in blocks:
        d.rounded_rectangle([660, y, 1830, y + 180], radius=10, fill=fill, outline=line, width=2)
        d.text((684, y + 22), title, font=font(FONT_B, 40), fill=line)
        d.text((684, y + 92), desc, font=font(FONT_R, 30), fill=INK)
        y += 205
    bottom_note(d)
    im.save(os.path.join(OUT, "03_hw_full.png"))


def hardware_vim3():
    im, d = base_card()
    top_line(d)
    d.text((92, 145), "03 / 硬件实物", font=font(FONT_B, 34), fill=RED)
    d.line([(92, 200), (92 + 90, 200)], fill=RED, width=5)
    d.text((92, 228), "Khadas VIM3：策略与 AI", font=font(FONT_B, 54), fill=INK)
    photo_panel(im, d, PHOTO_TOP, [90, 320, 1110, 950], crop=(140, 30, 860, 580))
    items = [("A311D", "4×A73 + 2×A53"), ("5 TOPS", "NPU · 本地推理"),
             ("状态机", "INIT / IDLE / LINE / AVOID"), ("串口", "A/B/C/D/I/L/O/R")]
    y = 330
    for a, b in items:
        d.rounded_rectangle([1160, y, 1830, y + 132], radius=8, fill=(255, 255, 255), outline=(220, 180, 170), width=2)
        d.text((1180, y + 14), a, font=font(FONT_B, 30), fill=RED)
        d.text((1180, y + 62), b, font=font(FONT_R, 23), fill=GRAY)
        y += 152
    bottom_note(d)
    im.save(os.path.join(OUT, "03_hw_vim3.png"))


def hardware_zynq():
    im, d = base_card()
    top_line(d)
    d.text((92, 145), "03 / 硬件实物", font=font(FONT_B, 34), fill=RED)
    d.line([(92, 200), (92 + 90, 200)], fill=RED, width=5)
    d.text((92, 228), "Zynq-7020：PL 实时层", font=font(FONT_B, 54), fill=INK)
    photo_panel(im, d, PHOTO_FULL, [90, 335, 820, 995], crop=(140, 460, 860, 1160))
    items = [("20 kHz PWM", "四路 · 周期边界双缓冲"), ("正交解码", "4 倍频 · 边沿时间戳"),
             ("超声计时", "μs 级 · 不阻塞"), ("硬件急停", "阈值判决 · 旁路 MCU")]
    y = 320
    for a, b in items:
        d.rounded_rectangle([860, y, 1830, y + 128], radius=8, fill=(255, 255, 255), outline=(160, 190, 215), width=2)
        d.text((882, y + 14), a, font=font(FONT_B, 30), fill=BLUE)
        d.text((882, y + 62), b, font=font(FONT_R, 23), fill=GRAY)
        y += 148
    bottom_note(d)
    im.save(os.path.join(OUT, "03_hw_zynq.png"))


def summary_card():
    im, d = base_card()
    top_line(d)
    d.text((92, 150), "05 / 设计要点", font=font(FONT_B, 34), fill=RED)
    d.line([(92, 205), (92 + 90, 205)], fill=RED, width=5)
    d.text((92, 250), "这辆车的关键，不是“用了 Zynq”", font=font(FONT_B, 58), fill=INK)
    d.text((92, 330), "而是把“必须准时”的部分从软件里拿出来", font=font(FONT_B, 58), fill=INK)
    items = [
        ("20 kHz", "硬件 PWM，四路相位对齐，周期抖动纳秒级"),
        ("正交解码", "编码器四倍频计数，速度闭环不再靠软件轮询"),
        ("硬件急停", "红外/超声阈值在 PL 内判决，紧急撤驱不经过 MCU"),
    ]
    y = 470
    for label, desc in items:
        d.rectangle([92, y, 116, y + 86], fill=RED)
        d.text((142, y - 6), label, font=font(FONT_B, 40), fill=BLUE)
        d.text((142, y + 46), desc, font=font(FONT_R, 30), fill=INK)
        y += 132
    bottom_note(d)
    im.save(os.path.join(OUT, "05_summary.png"))


def end_card():
    im, d = base_card()
    top_line(d)
    center_text(d, 300, "END", font(FONT_B, 160), INK)
    d.line([(W / 2 - 100, 520), (W / 2 + 100, 520)], fill=RED, width=6)
    center_text(d, 570, "Zynq-7020 + Khadas VIM3 异构智能小车", font(FONT_B, 50), fill=BLUE)
    bottom_note(d)
    im.save(os.path.join(OUT, "06_end.png"))


def _badge(d):
    return


def overlay_top(label, sub):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([78, 74, 700, 244], radius=12, fill=(0, 0, 0, 150))
    d.rectangle([78, 74, 86, 244], fill=RED)
    d.text((112, 94), label, font=font(FONT_B, 48), fill=(255, 255, 255, 255))
    d.text((114, 164), sub, font=font(FONT_R, 23), fill=(226, 226, 226, 255))
    _badge(d)
    im.save(os.path.join(OUT, f"ovtop_{label}.png"))


def overlay_side(label, sub):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([78, 330, 570, 540], radius=12, fill=(0, 0, 0, 150))
    d.rectangle([78, 330, 86, 540], fill=RED)
    d.text((112, 352), label, font=font(FONT_B, 46), fill=(255, 255, 255, 255))
    y = 420
    for line in sub.split("\n"):
        d.text((114, y), line, font=font(FONT_R, 21), fill=(226, 226, 226, 255))
        y += 34
    _badge(d)
    im.save(os.path.join(OUT, f"ovside_{label}.png"))


def bg_vertical():
    im = Image.new("RGB", (W, H), (246, 245, 240))
    d = ImageDraw.Draw(im)
    for y in range(0, H, 8):
        d.line([(0, y), (W, y)], fill=(242, 240, 234), width=1)
    d.rectangle([0, 0, W, 10], fill=RED)
    # Frame for 705x940 source.
    d.rounded_rectangle([588, 42, 1332, 1038], radius=10, fill=(226, 223, 214))
    d.rounded_rectangle([598, 52, 1322, 1028], radius=8, fill=(255, 255, 255))
    d.text((110, 130), "ORIGINAL", font=font(FONT_B, 26), fill=(195, 190, 180))
    d.text((110, 168), "FOOTAGE", font=font(FONT_B, 26), fill=(195, 190, 180))
    d.text((110, 240), "原始实拍", font=font(FONT_B, 34), fill=(140, 136, 128))
    d.text((1410, 810), "Zynq-7020", font=font(FONT_B, 48), fill=(210, 206, 196))
    d.text((1410, 875), "+ VIM3", font=font(FONT_B, 38), fill=(210, 206, 196))
    im.save(os.path.join(OUT, "bg_vertical.png"))


def demo_background():
    # Static card behind the portrait source; keeps the encode fast and the frame stable.
    im = Image.new("RGB", (W, H), (246, 245, 240))
    d = ImageDraw.Draw(im)
    for y in range(0, H, 8):
        d.line([(0, y), (W, y)], fill=(242, 240, 234), width=1)
    d.rectangle([0, 0, W, 10], fill=RED)
    # Frame for the 556x940 portrait source.
    d.rounded_rectangle([654, 44, 1266, 1036], radius=10, fill=(225, 222, 213))
    d.rounded_rectangle([664, 54, 1256, 1026], radius=8, fill=(255, 255, 255))
    # Side captions in the empty margins.
    d.text((110, 150), "ORIGINAL", font=font(FONT_B, 28), fill=(190, 186, 176))
    d.text((110, 190), "FOOTAGE", font=font(FONT_B, 28), fill=(190, 186, 176))
    d.text((110, 260), "原始实拍", font=font(FONT_B, 36), fill=(140, 136, 128))
    d.text((110, 310), "竖屏素材 · 横屏适配", font=font(FONT_R, 22), fill=(165, 160, 150))
    d.text((1410, 810), "Zynq-7020", font=font(FONT_B, 48), fill=(210, 206, 196))
    d.text((1410, 875), "+ VIM3", font=font(FONT_B, 38), fill=(210, 206, 196))
    im.save(os.path.join(OUT, "bg_demo.png"))


if __name__ == "__main__":
    title_card()
    section_card("作品介绍", "01", "把“必须准时”的任务\n从软件里拿出来", "策略、调度与交互留在 Khadas VIM3")
    architecture_card()
    hardware_full()
    hardware_vim3()
    hardware_zynq()
    section_card("视频展示", "04", "原始实拍素材\n横屏适配", "实拍片段 · 分段说明")
    summary_card()
    end_card()
    overlay_side("红外避障", "原始实拍 · 障碍物进入\n→ 停车/转向")
    overlay_top("超声波跟随", "原始实拍 · 手靠近 → 跟随/停止")
    bg_vertical()
    demo_background()
    print("assets written", OUT)
