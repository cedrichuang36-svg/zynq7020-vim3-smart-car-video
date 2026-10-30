# -*- coding: utf-8 -*-
"""Assemble a 16:9 draft from the existing vertical phone footage.

All non-source visuals are title/architecture cards or clearly labelled
design illustrations. No fabricated live-action hardware shot is inserted.
"""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
SEG = os.path.join(HERE, "segments")
os.makedirs(SEG, exist_ok=True)

FFMPEG = os.environ.get("FFMPEG", "ffmpeg")
SRC = os.environ.get("SOURCE_VIDEO", os.path.join(HERE, "source", "实验视频.mp4"))
W, H, FPS = 1920, 1080, 30


def run(args, tag):
    print("===", tag)
    p = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if p.returncode != 0:
        print(p.stdout.decode("utf-8", "ignore")[-4000:])
        raise SystemExit("ffmpeg failed: " + tag)
    print("ok")


def card(src, dur, out):
    args = [
        FFMPEG, "-y",
        "-loop", "1", "-i", os.path.join(ASSETS, src),
        "-f", "lavfi", "-t", str(dur), "-i", "anullsrc=r=44100:cl=stereo",
        "-t", str(dur),
        "-vf", f"scale={W}:{H},format=yuv420p,fade=t=in:st=0:d=0.25,fade=t=out:st={max(0,dur-0.25):.2f}:d=0.25",
        "-r", str(FPS),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-ac", "2",
        "-shortest", "-movflags", "+faststart",
        out,
    ]
    run(args, "card " + src)


def demo_vertical(start, dur, overlay, out):
    # IR segment is a 720x960 vertical picture inside a 720x1264 phone canvas.
    vf = (
        "[0:v]crop=720:960:0:153,scale=-2:940,"
        "unsharp=5:5:0.8:3:3:0.3[fgs];"
        "[1:v][fgs]overlay=(W-w)/2:(H-h)/2[base];"
        "[base][2:v]overlay=0:0,format=yuv420p,"
        f"fade=t=in:st=0:d=0.25,fade=t=out:st={max(0,dur-0.25):.2f}:d=0.25[v];"
        f"[0:a]volume=0.85,afade=t=in:st=0:d=0.3,"
        f"afade=t=out:st={max(0,dur-0.3):.2f}:d=0.3[a]"
    )
    args = [
        FFMPEG, "-y",
        "-ss", str(start), "-t", str(dur), "-i", SRC,
        "-loop", "1", "-i", os.path.join(ASSETS, "bg_vertical.png"),
        "-loop", "1", "-i", os.path.join(ASSETS, overlay),
        "-filter_complex", vf,
        "-map", "[v]", "-map", "[a]",
        "-t", str(dur), "-r", str(FPS),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-ac", "2",
        "-movflags", "+faststart", out,
    ]
    run(args, f"vertical {start}-{start+dur}")


def demo_horizontal(start, dur, overlay, out):
    # Ultrasonic segment is already 720x406 (16:9) inside the phone canvas.
    vf = (
        "[0:v]crop=720:406:0:430,scale=1920:1080,"
        "unsharp=5:5:0.9:3:3:0.4,eq=contrast=1.04:saturation=1.04[base];"
        "[base][1:v]overlay=0:0,format=yuv420p,"
        f"fade=t=in:st=0:d=0.25,fade=t=out:st={max(0,dur-0.25):.2f}:d=0.25[v];"
        f"[0:a]volume=0.85,afade=t=in:st=0:d=0.3,"
        f"afade=t=out:st={max(0,dur-0.3):.2f}:d=0.3[a]"
    )
    args = [
        FFMPEG, "-y",
        "-ss", str(start), "-t", str(dur), "-i", SRC,
        "-loop", "1", "-i", os.path.join(ASSETS, overlay),
        "-filter_complex", vf,
        "-map", "[v]", "-map", "[a]",
        "-t", str(dur), "-r", str(FPS),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-ac", "2",
        "-movflags", "+faststart", out,
    ]
    run(args, f"horizontal {start}-{start+dur}")


def main():
    segs = []
    specs = [
        ("01_title.png", 6.0, "00_title.mp4"),
        ("01_作品介绍.png", 3.0, "01_intro.mp4"),
        ("03_architecture.png", 10.0, "02_arch.mp4"),
        ("03_hw_full.png", 2.0, "02a_hw_full.mp4"),
        ("03_hw_vim3.png", 2.0, "02b_hw_vim3.mp4"),
        ("03_hw_zynq.png", 2.0, "02c_hw_zynq.mp4"),
        ("04_视频展示.png", 3.0, "03_show.mp4"),
    ]
    for png, dur, name in specs:
        out = os.path.join(SEG, name)
        card(png, dur, out)
        segs.append(out)

    ir = os.path.join(SEG, "04_ir.mp4")
    demo_vertical(0.0, 16.2, "ovside_红外避障.png", ir)
    segs.append(ir)

    us = os.path.join(SEG, "05_us.mp4")
    demo_horizontal(20.4, 12.8, "ovtop_超声波跟随.png", us)
    segs.append(us)

    for png, dur, name in [
        ("05_summary.png", 8.0, "06_summary.mp4"),
        ("06_end.png", 6.0, "07_end.mp4"),
    ]:
        out = os.path.join(SEG, name)
        card(png, dur, out)
        segs.append(out)

    listfile = os.path.join(SEG, "concat.txt")
    with open(listfile, "w", encoding="utf-8") as f:
        for p in segs:
            f.write("file '" + p.replace("\\", "/") + "'\n")

    out = os.path.join(HERE, "比赛视频_Zynq_VIM3版_1080p.mp4")
    args = [
        FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", listfile,
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
        "-r", str(FPS), "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-ac", "2",
        "-movflags", "+faststart", out,
    ]
    run(args, "concat")
    print("FINAL", out)


if __name__ == "__main__":
    main()
