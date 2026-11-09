"""Render the profile's self-hosted terminal artwork. Requires Pillow >= 10.

Usage: python scripts/render_console.py
Uses system fonts on Windows and DejaVu fonts on Linux. No network requests.
"""
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
W, H = 1200, 568
BG = '#090f14'
PANEL = '#101b23'
LINE = '#263946'
TEXT = '#edf4f2'
MUTED = '#a2b6bd'
GREEN = '#b8f593'
CYAN = '#75dce7'

def font(size, bold=False, mono=False):
    names = [('consolab.ttf' if bold else 'consola.ttf') if mono else
             ('segoeuib.ttf' if bold else 'segoeui.ttf')]
    names += [('DejaVuSansMono-Bold.ttf' if bold else 'DejaVuSansMono.ttf') if mono
              else ('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf')]
    for name in names:
        for folder in [Path('C:/Windows/Fonts'), Path('/usr/share/fonts/truetype/dejavu')]:
            if (folder / name).exists():
                return ImageFont.truetype(str(folder / name), size)
    raise RuntimeError('Install Segoe UI / Consolas or DejaVu fonts to render assets')

def text(d, xy, value, size=20, fill=TEXT, bold=False, mono=False):
    d.text(xy, value, font=font(size, bold, mono), fill=fill)

def pill(d, x, y, value, color=GREEN):
    f = font(18, mono=True)
    width = math.ceil(d.textlength(value, font=f)) + 28
    d.rounded_rectangle((x, y, x + width, y + 35), radius=7, fill=PANEL, outline=LINE)
    d.text((x + 14, y + 6), value, font=f, fill=color)
    return x + width + 10

def hero_base():
    im = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((1, 1, W-2, H-2), radius=22, outline=LINE, width=2)
    for x in range(34, 1200, 28):
        for y in range(86, 420, 28):
            if x > 790:
                d.point((x,y), fill='#1b2b34')
    for i,c in enumerate(['#ef827c','#edc579',GREEN]):
        d.ellipse((32+i*23,25,43+i*23,36),fill=c)
    text(d,(120,20),'numan5837 / engineering console',17,MUTED,mono=True)
    text(d,(955,20),'BUILD / EVALUATE',17,GREEN,mono=True)
    d.line((26,58,1174,58),fill=LINE)
    text(d,(42,88),'AI EVALUATION  /  BENCHMARK ENGINEERING',18,GREEN,mono=True)
    text(d,(36,122),'Numan S.',83,bold=True)
    text(d,(42,234),'Hard tasks.',44,bold=True)
    text(d,(42,288),'Checkable results.',44,bold=True)
    text(d,(44,359),'Real-world engineering. Research-grounded evaluation.',22,MUTED)
    x=pill(d,44,407,'MERCOR / REAL WORLD ENGINEER')
    pill(d,x,407,'TERMINAL-BENCH / DOMAIN EXPERT',CYAN)
    # A compact evaluation circuit: task -> agent -> verifier -> evidence.
    cx,cy=980,244
    for r in [112,84]:
        d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=LINE,width=1)
    d.line((868,244,980,160,1092,244,980,328,868,244),fill='#41606a',width=2)
    for x,y,label in [(980,132,'TASK'),(1092,244,'AGENT'),(980,356,'VERIFY'),(868,244,'RUN')]:
        d.ellipse((x-5,y-5,x+5,y+5),fill=CYAN)
        tw=d.textlength(label,font=font(14,mono=True))
        text(d,(x-tw/2,y+13),label,14,MUTED,mono=True)
    d.rounded_rectangle((926,211,1034,276),radius=12,fill=PANEL,outline=LINE)
    text(d,(941,222),'>_',35,GREEN,bold=True,mono=True)
    d.line((28,468,1172,468),fill=LINE)
    text(d,(44,492),'~ $',23,GREEN,bold=True,mono=True)
    text(d,(44,538),'PYTHON  /  LINUX  /  DOCKER  /  EXACT VERIFIERS',13,MUTED,mono=True)
    text(d,(949,538),'REPRODUCIBLE BY DESIGN',13,MUTED,mono=True)
    return im

COMMANDS = ['evaluate --domain mathematics', 'build --target real-world-systems',
            'verify --mode independently-checkable', 'inspect --agent-trajectories']

def hero_frame(base,i):
    im=base.copy(); d=ImageDraw.Draw(im)
    # Start on a completed command, then continue the same seamless cycle.
    phase=(i+36)%192
    step=phase//48; tick=phase%48
    command=COMMANDS[step%len(COMMANDS)]
    count=min(len(command),max(0,int((tick-2)*1.55)))
    shown=command[:count]
    text(d,(111,492),shown,23,TEXT,mono=True)
    if tick<32 or tick%12<6:
        x=111+d.textlength(shown,font=font(23,mono=True))+4
        d.rectangle((x,496,x+10,519),fill=GREEN)
    angle=(i/192*math.tau*2)-math.pi/2
    x=980+112*math.cos(angle); y=244+112*math.sin(angle)
    d.ellipse((x-7,y-7,x+7,y+7),fill=GREEN)
    return im

def save_gif(frames,path,duration):
    # One shared palette avoids flicker and lets GIF store small changed regions.
    palette=frames[0].quantize(colors=128,method=Image.Quantize.MEDIANCUT)
    indexed=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
    indexed[0].save(path,save_all=True,append_images=indexed[1:],duration=duration,
                    loop=0,optimize=True,disposal=1)
    print(f'{path.name}: {path.stat().st_size/1024:.0f} KiB')

def pipeline_frame(i):
    im=Image.new('RGB',(1200,248),BG); d=ImageDraw.Draw(im)
    d.rounded_rectangle((1,1,1198,246),radius=18,outline=LINE,width=2)
    text(d,(28,20),'~ $ run evaluation_pipeline',18,GREEN,mono=True)
    stages=[('01','DESIGN','domain problem'),('02','REPRODUCE','isolated runtime'),
            ('03','CALIBRATE','oracle + controls'),('04','EVALUATE','agent trajectories'),
            ('05','VERIFY','checkable evidence')]
    active=(i//16)%5
    for j,(n,title,desc) in enumerate(stages):
        x=28+j*234
        if j<4:
            d.line((x+210,134,x+232,134),fill=LINE,width=2)
            pos=(i%16)/15
            px=x+210+int(22*pos)
            if j==active: d.ellipse((px-3,131,px+3,137),fill=GREEN)
        d.rounded_rectangle((x,78,x+208,184),radius=10,fill=PANEL,outline=GREEN if j==active else LINE,width=2)
        text(d,(x+14,88),n,15,GREEN,mono=True)
        text(d,(x+14,115),title,18,TEXT,bold=True,mono=True)
        text(d,(x+14,149),desc,15,MUTED,mono=True)
    text(d,(28,208),'FAILURE ANALYSIS -> IMPROVE THE TASK, VERIFIER, OR ENVIRONMENT -> REPEAT',16,MUTED,mono=True)
    return im

def main():
    ASSETS.mkdir(exist_ok=True)
    base=hero_base()
    save_gif([hero_frame(base,i) for i in range(192)],ASSETS/'terminal-console.gif',80)
    hero_frame(base,0).save(ASSETS/'terminal-console-static.png')
    save_gif([pipeline_frame(i) for i in range(80)],ASSETS/'evaluation-loop.gif',100)
    pipeline_frame(0).save(ASSETS/'evaluation-loop-static.png')

if __name__=='__main__': main()
