"""Render final/preview.mp4: the TB-500 cover image, voice-final.wav and one caption per line, for listening on a phone."""
import json, os, subprocess, textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
FIN = os.path.join(HERE, "final")
COVER = os.path.join(HERE, "..", "..", "img", "reels", "series30", "tb-500-cover.jpg")
FONT = "C\\:/Windows/Fonts/arialbd.ttf"


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                                capture_output=True, text=True).stdout)


lines = json.load(open(os.path.join(HERE, "lines.json")))
cap = os.path.join(FIN, "captions"); os.makedirs(cap, exist_ok=True)
t, filt = 0.0, ["scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"]
for L in lines:
    d = dur(os.path.join(FIN, f"{L['id']}.wav")) + 0.18
    tf = os.path.join(cap, f"{L['id']}.txt")
    open(tf, "w", encoding="utf-8").write("\n".join(textwrap.wrap(L["text"], 24)))
    rel = os.path.relpath(tf, FIN).replace("\\", "/")
    filt.append(f"drawtext=fontfile='{FONT}':textfile='{rel}':fontcolor=white:fontsize=64:line_spacing=14:"
                f"box=1:boxcolor=black@0.65:boxborderw=28:x=(w-tw)/2:y=h*0.62:enable='between(t,{t:.2f},{t + d:.2f})'")
    t += d
subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", "30", "-i", COVER,
                "-i", "voice-final.wav", "-vf", ",".join(filt), "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-preset", "veryfast", "-crf", "23", "-c:a", "aac", "-b:a", "160k", "-shortest",
                "-movflags", "+faststart", "preview.mp4"], cwd=FIN, check=True)
print("ok", round(t, 2))
