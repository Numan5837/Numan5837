"""Animate the real public contribution calendar as a Pac-Man arcade.

The generated SVG is an animation, not a playable game. Uses only Python's
standard library. GITHUB_TOKEN is optional for a saved --calendar-json input.
"""
import argparse
import json
import os
from pathlib import Path
from urllib.request import Request,urlopen

QUERY='''query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}'''

def get_calendar(username):
    token=os.environ.get('GITHUB_TOKEN')
    if not token: raise RuntimeError('GITHUB_TOKEN required to refresh the public contribution calendar')
    request=Request('https://api.github.com/graphql',data=json.dumps({'query':QUERY,'variables':{'login':username}}).encode(),headers={'Authorization':f'Bearer {token}','Content-Type':'application/json','User-Agent':'Numan5837-profile-arcade'})
    with urlopen(request,timeout=30) as response: payload=json.load(response)
    if payload.get('errors'): raise RuntimeError('GitHub did not return a complete contribution calendar')
    return payload['data']['user']['contributionsCollection']['contributionCalendar']

def render(calendar):
    weeks=calendar['weeks']; n=len(weeks)
    if not weeks or n>54: raise ValueError('Unexpected contribution calendar size')
    b=['''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="338" viewBox="0 0 1200 338" role="img"><title>Pac-Man arcade animation of Numan5837's actual GitHub contribution calendar</title>
<defs><linearGradient id="edge"><stop stop-color="#62edee"/><stop offset="1" stop-color="#a98aff"/></linearGradient></defs>
<style>text{font-family:Consolas,monospace;fill:#f1f5ff}.wall{stroke:#384276;fill:none;stroke-width:2}@media(prefers-reduced-motion:reduce){.players{display:none}}</style>
<rect x="1" y="1" width="1198" height="336" rx="20" fill="#080b16" stroke="#29334b"/>
<text x="30" y="39" fill="#a98aff" font-size="14" letter-spacing="2">PAC-MAN / CONTRIBUTION RUN</text>
<text x="30" y="72" font-size="20">A year of building. One pixel at a time.</text>
<path d="M24 99H1176V286H24Z" class="wall"/><path d="M29 104H1171V281H29Z" class="wall" opacity=".35"/>
''']
    spacing=1104/(n-1); sx=48; sy=125; dy=23
    data={}
    for x,week in enumerate(weeks):
        for day in week['contributionDays']:
            # ISO weekday -> GitHub's Sunday-first rows.
            from datetime import date
            y=(date.fromisoformat(day['date']).weekday()+1)%7
            data[x,y]=day['contributionCount']
    order=[(x,y) for y in range(7) for x in (range(n) if y%2==0 else reversed(range(n))) if (x,y) in data]
    indexes={pos:i for i,pos in enumerate(order)}
    max_count=max(data.values(),default=1) or 1
    for (x,y),count in data.items():
        px=sx+x*spacing;py=sy+y*dy
        color='#1c2641' if count==0 else ['#347f90','#62c5c9','#a98aff','#e1cbff'][min(3,int(count/max_count*4))]
        b.append(f'<rect x="{px-6:.1f}" y="{py-6:.1f}" width="12" height="12" rx="3" fill="{color}"/>')
        if count:
            t=indexes[x,y]/len(order)*.9
            b.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="2.4" fill="#d6f6f9"><animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;{t:.5f};{t+.002:.5f};.96;1" dur="40s" repeatCount="indefinite"/></circle>')
    route='M'+' L'.join(f'{sx+x*spacing:.1f},{sy+y*dy}' for x,y in order)
    # Complete the loop along the outer maze rail.
    endx,endy=order[-1]
    route+=f' L1170,{sy+endy*dy} L1170,111 L48,111 L48,125'
    b.append('<g class="players">')
    b.append(f'<g><animateMotion path="{route}" dur="40s" rotate="auto" repeatCount="indefinite"/><path d="M0 0L10 -8A13 13 0 1 0 10 8Z" fill="#f8d86b"><animate attributeName="d" values="M0 0L10 -8A13 13 0 1 0 10 8Z;M0 0L13 -1A13 13 0 1 0 13 1Z;M0 0L10 -8A13 13 0 1 0 10 8Z" dur=".3s" repeatCount="indefinite"/></path></g>')
    for i,color in enumerate(['#a98aff','#62edee','#ff91b8']):
        b.append(f'<g><animateMotion path="{route}" dur="40s" begin="-{1.3+i*.85}s" repeatCount="indefinite"/><path d="M-10 10V0A10 10 0 0 1 10 0V10L5 6 0 10-5 6Z" fill="{color}"/><ellipse cx="-4" cy="-1" rx="3" ry="4" fill="#fff"/><ellipse cx="4" cy="-1" rx="3" ry="4" fill="#fff"/><circle cx="-3" cy="-1" r="1.5" fill="#121934"/><circle cx="5" cy="-1" r="1.5" fill="#121934"/></g>')
    b.append('</g>')
    total=calendar['totalContributions']; active=sum(c>0 for c in data.values())
    b.append(f'<text x="30" y="316" font-size="13" fill="#9faec9">{total} CONTRIBUTIONS / {active} ACTIVE DAYS / ACTUAL GITHUB CALENDAR</text><text x="974" y="316" font-size="12" fill="#9faec9">ANIMATED REPLAY</text></svg>')
    return ''.join(b)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--username',default='Numan5837')
    p.add_argument('--calendar-json',type=Path)
    p.add_argument('--output',type=Path,default=Path('assets/contribution-pacman.svg'))
    args=p.parse_args()
    data=json.loads(args.calendar_json.read_text(encoding='utf-8-sig')) if args.calendar_json else get_calendar(args.username)
    output=render(data);args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(output,encoding='utf-8')
    # Use a static calendar for reduced-motion preferences.
    # Remove animated players and dot visibility changes for the static view.
    import xml.etree.ElementTree as ET
    tree=ET.fromstring(output)
    for child in list(tree):
        if child.attrib.get('class')=='players':tree.remove(child)
    for element in tree.iter():
        for child in list(element):
            if child.tag.rsplit('}',1)[-1]=='animate':element.remove(child)
    ET.register_namespace('','http://www.w3.org/2000/svg')
    args.output.with_name(args.output.stem+'-static.svg').write_text(ET.tostring(tree,encoding='unicode'),encoding='utf-8')
    print(f'Arcade refreshed from {data["totalContributions"]} contributions across {len(data["weeks"])} weeks')

if __name__=='__main__': main()
