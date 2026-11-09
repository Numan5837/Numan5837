"""Build script-free animated SVG artwork for the GitHub profile.

Run python scripts/render_profile_v2.py. SVGs use SMIL/CSS and no remote fonts,
scripts, foreignObject elements, or third-party rendering services.
"""
from pathlib import Path
from html import escape
import math
import re

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets'
BG='#080b16'; PANEL='#101525'; BORDER='#27324b'
WHITE='#f1f5ff'; MUTED='#9faec9'; CYAN='#62edee'; PURPLE='#a98aff'; LIME='#c5f784'

DEFS='''<defs>
<linearGradient id="ink"><stop stop-color="#fbfcff"/><stop offset=".52" stop-color="#bbc5ff"/><stop offset="1" stop-color="#79edee"/></linearGradient>
<linearGradient id="neon" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#6aeef3"/><stop offset=".48" stop-color="#8b8dff"/><stop offset="1" stop-color="#d999ff"/></linearGradient>
<radialGradient id="aura"><stop stop-color="#6044ce" stop-opacity=".38"/><stop offset="1" stop-color="#6044ce" stop-opacity="0"/></radialGradient>
<radialGradient id="cyanAura"><stop stop-color="#137f97" stop-opacity=".28"/><stop offset="1" stop-color="#137f97" stop-opacity="0"/></radialGradient>
<linearGradient id="surface" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#171e35"/><stop offset="1" stop-color="#0d1221"/></linearGradient>
<filter id="glow" x="-70%" y="-70%" width="240%" height="240%"><feGaussianBlur stdDeviation="5"/></filter>
<pattern id="dots" width="30" height="30" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="#99a9f0" opacity=".11"/></pattern>
</defs>
<style>
text{font-family:'Segoe UI',Arial,sans-serif;fill:#f1f5ff}
.mono{font-family:Consolas,'DejaVu Sans Mono',monospace}
.muted{fill:#9faec9}.cyan{fill:#62edee}.purple{fill:#a98aff}.lime{fill:#c5f784}
.dash{stroke-dasharray:5 10;animation:dash 24s linear infinite}
.breathe{animation:breathe 4s ease-in-out infinite}
@keyframes dash{to{stroke-dashoffset:-180}}
@keyframes breathe{50%{opacity:.38}}
@media(prefers-reduced-motion:reduce){*{animation:none!important}}
</style>'''

def tx(x,y,s,size=20,cls='',**attrs):
    extra=' '.join(f'{k.replace("_","-")}="{v}"' for k,v in attrs.items())
    return f'<text x="{x}" y="{y}" font-size="{size}" class="{cls}" {extra}>{escape(s)}</text>'

def rect(x,y,w,h,fill=PANEL,stroke=BORDER,r=18,**kw):
    extra=' '.join(f'{k.replace("_","-")}="{v}"' for k,v in kw.items())
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" {extra}/>'

def dot(x,y,c=CYAN,r=4):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}"/>'

def terminal_mark(cx,cy):
    """A clean terminal glyph, with no text label inside the hero artwork."""
    return rect(cx-37,cy-33,74,66,'#10172c','#51618d',14)+f'<path d="M{cx-17} {cy-11}l11 11-11 11M{cx+1} {cy+12}h17" fill="none" stroke="{CYAN}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'

def packet(path,color=CYAN,dur=6,begin=0,r=4):
    return f'<circle r="{r}" fill="{color}"><animateMotion path="{path}" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/></circle>'

def svg(name,w,h,body,title):
    result=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img"><title>{escape(title)}</title>{DEFS}{body}</svg>'
    OUT.mkdir(exist_ok=True)
    (OUT/f'{name}.svg').write_text(result,encoding='utf-8')
    # Separate static SVG for reduced motion. SMIL is removed, not just CSS.
    still=re.sub(r'<circle\b[^>]*><animateMotion\b[^>]*/></circle>','',result)
    still=re.sub(r'<animate(?:Motion|Transform)?\b[^>]*/>','',still)
    still=re.sub(r'<animate(?:Motion|Transform)?\b.*?</animate(?:Motion|Transform)?>','',still,flags=re.S)
    still=still.replace('</style>','*{animation:none!important}</style>')
    (OUT/f'{name}-static.svg').write_text(still,encoding='utf-8')
    print(name,len(result.encode()),'bytes')

def knot(theta):
    points=[]
    for j in range(161):
        t=j/160*math.tau
        x=(2+.63*math.cos(3*t))*math.cos(2*t)
        y=(2+.63*math.cos(3*t))*math.sin(2*t)
        z=.9*math.sin(3*t)
        rx=x*math.cos(theta)+z*math.sin(theta)
        rz=-x*math.sin(theta)+z*math.cos(theta)
        ry=y*.84-rz*.48
        px=926+(rx*.94-ry*.24)*73
        py=241+(rx*.24+ry*.94)*73
        points.append(f'{px:.1f},{py:.1f}')
    return 'M'+' L'.join(points)+' Z'

def hero():
    b=rect(1,1,1198,658,BG,'#252e47',24)
    b+='<rect x="1" y="1" width="1198" height="658" rx="24" fill="url(#dots)"/>'
    b+='<ellipse cx="970" cy="230" rx="365" ry="290" fill="url(#aura)" class="breathe"/>'
    b+='<ellipse cx="110" cy="585" rx="500" ry="210" fill="url(#cyanAura)"/>'
    b+=tx(42,44,'N / 5837',19,'mono',font_weight=700)
    b+=tx(189,44,'ENGINEERING × EVALUATION',14,'mono muted',letter_spacing=2)
    b+=dot(1017,38,LIME,3)+tx(1030,44,'HUMAN ENGINEER',12,'mono lime')
    b+='<path d="M42 66H1158" stroke="#28334c"/>'
    b+=tx(44,112,'NUMAN S.  /  REAL SYSTEMS. REAL CHALLENGES.',15,'mono cyan',letter_spacing=1.2)
    b+=tx(35,256,'NUMAN',152,'',font_weight=900,letter_spacing=-9,style='fill:url(#ink)')
    b+=tx(44,314,'I build the tests',39,'',font_weight=600)
    b+=tx(44,363,'that test AI.',39,'',font_weight=600)
    b+=tx(44,404,'Hard benchmarks. Exact verifiers. Reproducible systems.',20,'muted')
    # A rotating projected torus knot, rather than a flat rotating icon.
    values=';'.join(knot(j/24*math.tau) for j in range(25))
    animate=f'<animate attributeName="d" values="{values}" dur="18s" repeatCount="indefinite"/>'
    b+=f'<path d="{knot(0)}" fill="none" stroke="url(#neon)" stroke-width="21" opacity=".3" filter="url(#glow)">{animate}</path>'
    b+=f'<path d="{knot(0)}" fill="none" stroke="url(#neon)" stroke-width="4.5" stroke-linejoin="round">{animate}</path>'
    b+='<ellipse cx="926" cy="241" rx="219" ry="69" fill="none" stroke="#5273a2" stroke-width="1" class="dash" transform="rotate(-24 926 241)"/>'
    b+=packet('M707 241 C707 107 1145 107 1145 241 C1145 375 707 375 707 241',LIME,12,r=5)
    b+=terminal_mark(926,241)
    b+=tx(834,430,'RESEARCH → RUNTIME',16,'mono muted',letter_spacing=1.4)
    # Role ribbon.
    labels=[('MERCOR','Real World Engineer',CYAN),('TERMINAL-BENCH','Domain Expert',PURPLE),('CORE FOCUS','Agent evaluation',LIME)]
    for j,(label,sub,c) in enumerate(labels):
        x=44+j*375
        b+='<path d="M%d 452H%d" stroke="%s" stroke-opacity=".5"/>'%(x,x+345,c)
        b+=tx(x,479,label,13,'mono',style=f'fill:{c}',letter_spacing=1.4)
        b+=tx(x,506,sub,22,'',font_weight=600)
    # Always-visible terminal: animated log rows are clipped to their pane.
    b+=rect(28,536,1144,104,'#0b1120','#2b3752',12)
    b+='<defs><clipPath id="logs"><rect x="47" y="553" width="1100" height="68"/></clipPath></defs>'
    b+=tx(48,561,'~/numan',12,'mono purple')
    b+='<g clip-path="url(#logs)"><g><animateTransform attributeName="transform" type="translate" values="0 0;0 0;0 -70;0 -70;0 -140;0 -140;0 -210;0 -210;0 -280" keyTimes="0;.19;.24;.43;.48;.67;.72;.91;1" dur="16s" repeatCount="indefinite"/>'
    logs=[('$ benchmark --domain mathematics','task.spec loaded → container ready → verifier attached'),('$ engineer --target real-world-systems','inspect → implement → reproduce → validate'),('$ evaluate --agent terminal --trace','tool calls → execution traces → independent checks'),('$ verifier --audit --adversarial','oracle + no-op + mutations → evidence report'),('$ benchmark --domain mathematics','task.spec loaded → container ready → verifier attached')]
    for j,(cmd,output) in enumerate(logs):
        y=586+j*70
        b+=tx(48,y,cmd,19,'mono')+tx(48,y+25,output,15,'mono muted')
    b+='</g></g>'
    b+=rect(1041,554,108,24,'#152938','none',6)+tx(1055,571,'WORKFLOW',11,'mono cyan')
    b='<defs><clipPath id="canvas"><rect width="1200" height="660" rx="24"/></clipPath></defs><g clip-path="url(#canvas)">'+b+'</g>'
    svg('hero-v2',1200,660,b,'Numan S. | Mercor Real World Engineer | Terminal-Bench Domain Expert | Agent evaluation and verifier engineering')

def navigation():
    entries=[('work','01','SELECTED WORK','M8 8h8v8H8z M12 3v5 M3 12h5 M16 12h5 M12 16v5'),('systems','02','VERIFIER LAB','M4 12l5 5L20 5'),('domains','03','DOMAIN MAP','M3 6h18M3 12h18M3 18h18'),('arcade','04','CONTRIBUTION ARCADE','M7 8h10l4 11-5-3H8l-5 3z M6 12h6 M9 9v6 M16 12h1')]
    for name,n,label,path in entries:
        b=rect(1,1,287,62,'url(#surface)',BORDER,10)
        b+=f'<g transform="translate(17 19)" fill="none" stroke="{CYAN}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="{path}"/></g>'
        b+=tx(55,26,n,10,'mono muted')+tx(55,46,label,13,'mono',letter_spacing=.5)
        b+=tx(263,38,'↗',16,'cyan')
        svg('nav-'+name,288,64,b,label)
        short={'work':'WORK','systems':'LAB','domains':'DOMAINS','arcade':'ARCADE'}[name]
        compact=rect(1,1,287,82,'url(#surface)',BORDER,12)+tx(24,54,short,30,'mono',font_weight=700)+tx(244,52,'↗',26,'cyan')
        svg('nav-'+name+'-mobile',288,84,compact,label)

def mobile_hero():
    b=rect(1,1,718,938,BG,BORDER,24)
    b+='<rect width="720" height="940" fill="url(#dots)"/>'
    b+=tx(32,43,'N / 5837',18,'mono',font_weight=700)+tx(441,43,'HUMAN ENGINEER',14,'mono lime')
    b+='<path d="M32 67H688" stroke="#29334b"/>'
    b+=tx(32,110,'NUMAN S. / ENGINEERING × EVALUATION',16,'mono cyan')
    b+=tx(23,233,'NUMAN',139,'',font_weight=900,letter_spacing=-7,style='fill:url(#ink)')
    b+=tx(32,286,'I build the tests that test AI.',37,'',font_weight=600)
    b+='<ellipse cx="360" cy="489" rx="340" ry="235" fill="url(#aura)" class="breathe"/>'
    values=';'.join(knot(j/24*math.tau) for j in range(25))
    animate=f'<animate attributeName="d" values="{values}" dur="18s" repeatCount="indefinite"/>'
    b+='<g transform="translate(-566 239)">'
    b+=f'<path d="{knot(0)}" fill="none" stroke="url(#neon)" stroke-width="22" opacity=".35" filter="url(#glow)">{animate}</path>'
    b+=f'<path d="{knot(0)}" fill="none" stroke="url(#neon)" stroke-width="5">{animate}</path>'
    b+='<ellipse cx="926" cy="241" rx="232" ry="77" fill="none" stroke="#657ba7" class="dash" transform="rotate(-24 926 241)"/>'
    b+=packet('M707 241 C707 107 1145 107 1145 241 C1145 375 707 375 707 241',LIME,12,r=6)
    b+=terminal_mark(926,241)+'</g>'
    for x,label,role,c in [(32,'MERCOR','Real World Engineer',CYAN),(380,'TERMINAL-BENCH','Domain Expert',PURPLE)]:
        b+=f'<path d="M{x} 697h306" stroke="{c}" stroke-opacity=".5"/>'
        b+=tx(x,728,label,15,'mono',style=f'fill:{c}',letter_spacing=1)+tx(x,766,role,26,'',font_weight=650)
    b+=rect(24,805,672,109,'#0b1120',BORDER,14)+tx(43,840,'~ $ verify --mode independently-checkable',19,'mono cyan')
    b+=tx(43,878,'reference → controls → traces → evidence',18,'mono muted')
    b+='<rect x="656" y="822" width="10" height="20" fill="#a98aff"><animate attributeName="opacity" values="1;0;1" dur="1.2s" repeatCount="indefinite"/></rect>'
    svg('hero-v2-mobile',720,940,b,'Numan S. — Mercor Real World Engineer, Terminal-Bench Domain Expert. I build the tests that test AI.')

def experience():
    b=''
    entries=[('01 / REAL-WORLD SYSTEMS','Mercor','Real World Engineer',['Engineering real workflows.','Building executable solutions.','Checking outcomes against reality.'],CYAN),('02 / TERMINAL-BENCH','Handshake AI','Dynamo · Insight',['Terminal-Bench 2 & 3.','Operations, mathematics, ML','research & data engineering.'],PURPLE),('03 / SCIENTIFIC REASONING','Turing','Domain Expert',['Scientific & mathematical tasks','for Meta. Reference solutions.','Independently checkable results.'],LIME)]
    for j,(label,name,role,lines,c) in enumerate(entries):
        x=j*402+1
        b+=rect(x,1,394,280,'url(#surface)',BORDER,16)
        b+=f'<path d="M{x+24} 1H{x+190}" stroke="{c}" stroke-width="2"/>'
        b+=tx(x+24,39,label,12,'mono',style=f'fill:{c}',letter_spacing=.5)
        b+=tx(x+24,99,name,37,'',font_weight=700)
        b+=tx(x+24,133,role,21,'muted')
        for k,line in enumerate(lines): b+=tx(x+24,188+k*28,line,17,'muted')
        b+=f'<circle cx="{x+352}" cy="37" r="4" fill="{c}"><animate attributeName="opacity" values="1;.25;1" dur="4s" begin="{j}s" repeatCount="indefinite"/></circle>'
    svg('experience-v2',1200,282,b,'Mercor Real World Engineer; Handshake AI Terminal-Bench 2 and 3; Turing scientific and mathematical task development')
    b=''
    for j,(label,name,role,lines,c) in enumerate(entries):
        y=j*220+1
        b+=rect(1,y,718,208,'url(#surface)',BORDER,16)
        b+=tx(25,y+32,label,16,'mono',style=f'fill:{c}')
        b+=tx(25,y+89,name,41,'',font_weight=700)+tx(25,y+127,role,25,'muted')
        # Keep text readable without shrinking three desktop columns.
        for k,line in enumerate(lines):b+=tx(350,y+80+k*35,line,19,'muted')
    svg('experience-v2-mobile',720,650,b,'Mercor Real World Engineer; Handshake AI Terminal-Bench 2 and 3; Turing scientific task development')

def domains():
    entries=[('01','Mathematics','Proofs. Numerical reasoning.','Exact, checkable certificates.',CYAN),('02','ML research','Reproducible experiments.','Model and trajectory analysis.',PURPLE),('03','Operations','Planning under constraints.','Backlogs, staffing, allocation.',LIME),('04','Data engineering','Reliable data and databases.','Consistency & reconciliation.',CYAN),('05','Agent systems','Terminal execution & tooling.','Isolation and container runtimes.',PURPLE),('06','Verifier engineering','Oracle, no-op, mutation checks.','Defensible scores and evidence.',LIME)]
    b=''
    for j,(n,title,l1,l2,c) in enumerate(entries):
        x=(j%3)*402+1; y=(j//3)*171+1
        b+=rect(x,y,394,160,'url(#surface)',BORDER,14)
        b+=tx(x+22,y+31,n,13,'mono',style=f'fill:{c}')
        b+=tx(x+22,y+71,title,27,'',font_weight=650)
        b+=tx(x+22,y+105,l1,17,'muted')+tx(x+22,y+131,l2,17,'muted')
        b+=f'<path d="M{x+340} {y+24}h24m-12 -12v24" stroke="{c}" stroke-opacity=".6"/>'
    svg('domains-v2',1200,333,b,'Expertise: mathematics, ML research, operations, data engineering, agent systems, verifier engineering')
    b=''
    for j,(n,title,l1,l2,c) in enumerate(entries):
        x=(j%2)*364+1;y=(j//2)*171+1
        b+=rect(x,y,354,160,'url(#surface)',BORDER,14)
        b+=tx(x+20,y+31,n,14,'mono',style=f'fill:{c}')+tx(x+20,y+72,title,26,'',font_weight=650)
        b+=tx(x+20,y+107,l1,17,'muted')+tx(x+20,y+133,l2,17,'muted')
    svg('domains-v2-mobile',720,504,b,'Mathematics, ML research, operations, data engineering, agent systems, and verifier engineering')

def node(x,y,w,h,title,sub,c=CYAN,title_size=17,sub_size=14):
    return rect(x,y,w,h,'url(#surface)',BORDER,12)+dot(x+17,y+24,c,3)+tx(x+30,y+30,title,title_size,'mono',font_weight=700)+tx(x+17,y+58,sub,sub_size,'muted')

def verifier():
    b=rect(1,1,1198,550,BG,BORDER,20)
    b+='<ellipse cx="590" cy="250" rx="560" ry="230" fill="url(#aura)" opacity=".6"/>'
    b+=tx(32,39,'VERIFIER LAB / EXECUTION GRAPH',14,'mono cyan',letter_spacing=1)
    b+=tx(32,83,'A score is only as good as its verifier.',34,'',font_weight=650)
    b+=tx(32,113,'An animated view of the checks behind a trustworthy evaluation.',18,'muted')
    paths=['M230 263H284','M490 263H544','M750 263C786 263 773 186 807 186','M750 263H807','M750 263C786 263 773 340 807 340','M1011 186C1052 186 1050 263 1080 263','M1011 263H1080','M1011 340C1052 340 1050 263 1080 263']
    for j,p in enumerate(paths):
        c=[CYAN,CYAN,CYAN,PURPLE,LIME,CYAN,PURPLE,LIME][j]
        b+=f'<path d="{p}" fill="none" stroke="{c}" stroke-opacity=".35" stroke-width="2"/>'
        b+=packet(p,c,3.2,j*.37,4)
    b+=node(28,221,202,84,'TASK PACKAGE','spec + fixtures + oracle')
    b+=node(284,221,206,84,'SANDBOX','Docker / isolated state')
    b+=node(544,221,206,84,'AGENT RUN','commands + artifacts')
    b+=node(807,150,204,72,'EXACT CHECK','verifier-owned truth',CYAN)
    b+=node(807,227,204,72,'RUBRIC JUDGE','criterion + evidence',PURPLE)
    b+=node(807,304,204,72,'ADVERSARIAL','no-op + mutation',LIME)
    b+=rect(1081,218,87,91,'#132b32','#3c7982',12)+tx(1092,250,'✓',26,'cyan')+tx(1092,278,'REPORT',12,'mono cyan')
    b+='<path d="M644 306V405H128V306" fill="none" stroke="#65729e" stroke-dasharray="5 7" class="dash"/>'
    b+=tx(238,399,'FAILURE ANALYSIS → REFINE → RE-RUN',13,'mono muted')
    b+=rect(28,440,1140,83,'#0d1425',BORDER,10)
    labels=[('ORACLE','must pass',CYAN),('NO-OP','must fail',PURPLE),('MUTATIONS','probe shortcuts',LIME),('INFRA ERRORS','separate from model failures',MUTED)]
    for j,(title,sub,c) in enumerate(labels):
        x=48+j*276
        b+=tx(x,469,title,12,'mono',style=f'fill:{c}',letter_spacing=.8)+tx(x,495,sub,16,'')
    b+=tx(985,39,'WORKFLOW DEMO',12,'mono muted')
    svg('verifier-lab',1200,552,b,'Animated verifier graph: task package, isolated sandbox, agent execution, exact checks, rubric judge, adversarial controls, evidence report, and failure analysis loop. Illustrative workflow.')
    b=rect(1,1,718,1088,BG,BORDER,20)
    b+=tx(28,42,'VERIFIER LAB / WORKFLOW DEMO',16,'mono cyan')
    b+=tx(28,100,'A score is only as good',35,'',font_weight=650)+tx(28,146,'as its verifier.',35,'',font_weight=650)
    for j,(title,sub) in enumerate([('TASK PACKAGE','spec + fixtures + oracle'),('ISOLATED SANDBOX','Docker / verifier-owned state'),('AGENT EXECUTION','commands + artifacts + trajectory')]):
        y=190+j*148
        b+=node(132,y,456,96,title,sub,CYAN,24,20)
        p=f'M360 {y+96}V{y+148}'
        if j<2:b+=f'<path d="{p}" stroke="#416c86" stroke-width="2"/>'+packet(p,CYAN,2,j*.3,5)
    for j,(title,sub,c) in enumerate([('EXACT CHECK','ground truth',CYAN),('RUBRIC JUDGE','criteria',PURPLE),('ADVERSARIAL','controls',LIME)]):
        x=24+j*230
        p=f'M360 582C360 620 {x+105} 600 {x+105} 650'
        b+=f'<path d="{p}" fill="none" stroke="{c}" stroke-opacity=".45" stroke-width="2"/>'+packet(p,c,3,j*.3,5)
        b+=node(x,650,212,85,title,sub,c,20,18)
        p=f'M{x+105} 735C{x+105} 795 360 770 360 814'
        b+=f'<path d="{p}" fill="none" stroke="{c}" stroke-opacity=".45" stroke-width="2"/>'+packet(p,c,3,j*.3,5)
    b+=node(132,815,456,96,'EVIDENCE REPORT','checkable scores + failure analysis',LIME,24,20)
    b+='<path d="M132 862H68V238H132" fill="none" stroke="#58678e" class="dash"/>'
    b+=tx(28,979,'ORACLE PASSES / NO-OP FAILS',20,'mono cyan')+tx(28,1018,'MODEL FAILURE ≠ INFRASTRUCTURE FAILURE',18,'mono muted')
    svg('verifier-lab-mobile',720,1090,b,'Vertical animated verifier graph: task package, sandbox, agent run, parallel exact checks, rubric judging, adversarial controls, and an evidence report with feedback.')

def section(name,n,title,subtitle):
    b=tx(1,24,n,13,'mono cyan',letter_spacing=2)+tx(1,72,title,38,'',font_weight=700)+tx(1,104,subtitle,17,'muted')
    b+='<path d="M0 124H1200" stroke="#29334b"/>'
    b+='<path d="M0 124H120" stroke="url(#neon)" stroke-width="2"><animate attributeName="d" values="M0 124H120;M1080 124H1200;M0 124H120" dur="14s" repeatCount="indefinite"/></path>'
    svg('section-'+name,1200,127,b,title)
    lines={'work':['Engineering,','with receipts.'],'systems':['From terminal','to trustworthy.'],'domains':['Different domains.','The same rigor.'],'arcade':['Serious work.','Playful pixels.']}[name]
    sub={'work':'Public tasks. Private systems. Open-source work.','systems':'Execution is the beginning. Verification is the work.','domains':'Research-grounded. Independently checkable.','arcade':'My contribution history, reimagined as an arcade.'}[name]
    b=tx(1,25,n,17,'mono cyan',letter_spacing=1)+tx(1,88,lines[0],52,'',font_weight=700)+tx(1,146,lines[1],52,'',font_weight=700)+tx(1,194,sub,21,'muted')
    b+='<path d="M0 222H720" stroke="#29334b"/><path d="M0 222H120" stroke="url(#neon)" stroke-width="2"/>'
    svg('section-'+name+'-mobile',720,225,b,title)

def main():
    hero();mobile_hero();navigation();experience();domains();verifier()
    for args in [('work','01 / THE WORK','Engineering, with receipts.','Public task contributions, private evaluation systems, and open-source patches.'),('systems','02 / UNDER THE HOOD','From terminal to trustworthy.','Execution is the beginning. Verification is the work.'),('domains','03 / EXPERTISE','Different domains. The same rigor.','Research-grounded challenges. Explicit constraints. Independently checkable outcomes.'),('arcade','04 / OFF THE CLOCK','Serious work. Playful pixels.','My contribution history, reimagined as an arcade.')]:section(*args)

if __name__=='__main__':main()
