"""Animate a real public contribution calendar, then reveal its activity stats.

Pac-Man clears the calendar squares in a timed replay. The website supplies the
separate playable game. Uses only the Python standard library. GITHUB_TOKEN is
required for a fresh calendar; --calendar-json supports offline regeneration.
Writes contribution-data.json beside the SVG from the same public snapshot,
so the playable website and profile animation share contribution data.
"""
import argparse
from datetime import date, datetime, timezone
from html import escape
import json
import math
import os
from pathlib import Path
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

QUERY = '''query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}'''
DURATION = 40
CLEAR_AT = .86
REVEAL_AT = .89
RESET_AT = .975


def nonnegative(value, name):
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f'{name} must be a nonnegative integer')
    return value


def public_json(url):
    request = Request(url, headers={
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'Numan5837-profile-arcade',
        'X-GitHub-Api-Version': '2022-11-28',
    })
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def get_calendar(username):
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        raise RuntimeError('GITHUB_TOKEN required to refresh the public contribution calendar')
    request = Request('https://api.github.com/graphql',
        data=json.dumps({'query': QUERY, 'variables': {'login': username}}).encode(),
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json',
                 'User-Agent': 'Numan5837-profile-arcade'})
    with urlopen(request, timeout=30) as response:
        payload = json.load(response)
    if payload.get('errors'):
        raise RuntimeError('GitHub did not return a complete contribution calendar')
    calendar = payload['data']['user']['contributionsCollection']['contributionCalendar']
    # A repository-scoped Actions token can filter search to its installation.
    # Read PR and repository counts without authentication to count public work.
    search = public_json('https://api.github.com/search/issues?' + urlencode({
        'q': f'is:pr author:{username}', 'per_page': 1,
    }))
    if search.get('incomplete_results'):
        raise RuntimeError('GitHub returned incomplete public PR search results')
    profile = public_json('https://api.github.com/users/' + quote(username, safe=''))
    calendar['publicPullRequests'] = nonnegative(search['total_count'], 'publicPullRequests')
    calendar['publicRepositories'] = nonnegative(profile['public_repos'], 'publicRepositories')
    return calendar


def reveal_counter(x, label, total, index, width):
    """Roll through real count increments; the static default is the final value."""
    steps = min(12, max(1, total))
    values = [round(total * step / steps) for step in range(steps + 1)]
    final_offset = steps * 54
    start = REVEAL_AT + index * .003
    end = .94 + index * .003
    times = [0, start] + [start + (end-start)*j/steps for j in range(1,steps+1)] + [1]
    offsets = [0,0] + [-j*54 for j in range(1,steps+1)] + [-final_offset]
    rows = ''.join(f'<text x="{x+width/2:.1f}" y="{226+j*54}" text-anchor="middle" font-size="44" font-weight="700">{value:,}</text>' for j,value in enumerate(values))
    return (
        f'<rect x="{x}" y="145" width="{width}" height="111" rx="12" fill="#121c33" stroke="#3b5178"/>'
        f'<text x="{x+width/2:.1f}" y="171" text-anchor="middle" font-size="12" letter-spacing="1" class="counter-label">{escape(label)}</text>'
        f'<defs><clipPath id="counter-{index}"><rect x="{x+8}" y="181" width="{width-16}" height="58"/></clipPath></defs>'
        f'<g clip-path="url(#counter-{index})"><g transform="translate(0 {-final_offset})">'
        f'<animateTransform attributeName="transform" type="translate" calcMode="discrete" values="{";".join(f"0 {v}" for v in offsets)}" keyTimes="{";".join(f"{t:.5f}" for t in times)}" dur="{DURATION}s" repeatCount="indefinite"/>'
        f'{rows}</g></g>'
    )


def render(calendar):
    weeks = calendar['weeks']
    n = len(weeks)
    if not weeks or n > 54:
        raise ValueError('Unexpected contribution calendar size')
    total = nonnegative(calendar['totalContributions'], 'totalContributions')
    data = {}
    for x, week in enumerate(weeks):
        for day in week['contributionDays']:
            y = (date.fromisoformat(day['date']).weekday()+1) % 7
            data[x,y] = nonnegative(day['contributionCount'], 'contributionCount')
    if not data:
        raise ValueError('The contribution calendar contains no days')
    active = sum(c > 0 for c in data.values())
    metrics = [('CONTRIBUTIONS', total), ('ACTIVE DAYS', active)]
    for key, label in [('publicPullRequests','PUBLIC PULL REQUESTS'), ('publicRepositories','PUBLIC REPOSITORIES')]:
        if key in calendar:
            metrics.append((label, nonnegative(calendar[key], key)))

    b = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="338" viewBox="0 0 1200 338" role="img"><title>Pac-Man clears Numan5837's real contribution calendar and reveals public activity statistics</title>
<defs><linearGradient id="edge"><stop stop-color="#62edee"/><stop offset="1" stop-color="#a98aff"/></linearGradient></defs>
<style>text{{font-family:Consolas,monospace;fill:#f1f5ff}}.wall{{stroke:#384276;fill:none;stroke-width:2}}.counter-label{{fill:#92c5d5}}@media(prefers-reduced-motion:reduce){{.players{{display:none}}}}</style>
<rect id="background" x="1" y="1" width="1198" height="336" rx="20" fill="#080b16" stroke="#29334b"/>
<text x="30" y="39" font-size="14" letter-spacing="2">PAC-MAN / CONTRIBUTION RUN</text>
<text x="30" y="72" font-size="20">Eat the calendar. Reveal the work.</text>
<path d="M24 99H1176V286H24Z" class="wall"/><path d="M29 104H1171V281H29Z" class="wall" opacity=".35"/>
''']
    spacing = 1104 / max(1,n-1)
    sx, sy, dy = 48, 125, 23
    order = [(x,y) for y in range(7) for x in (range(n) if y%2==0 else reversed(range(n))) if (x,y) in data]
    points = [(sx+x*spacing, sy+y*dy) for x,y in order]
    distances = [0.0]
    for a,z in zip(points, points[1:]):
        distances.append(distances[-1] + math.dist(a,z))
    grid_distance = distances[-1] or 1.0
    consume_times = {pos: CLEAR_AT*distance/grid_distance for pos,distance in zip(order,distances)}
    max_count = max(data.values(),default=1) or 1
    b.append('<g class="calendar-cells">')
    for (x,y), count in data.items():
        px,py = sx+x*spacing, sy+y*dy
        color = '#1c2641' if count == 0 else ['#347f90','#62c5c9','#a98aff','#e1cbff'][min(3,int(count/max_count*4))]
        t = consume_times[x,y]
        if t == 0:
            values, times = '1;.04;.04;1', f'0;.001;{RESET_AT};1'
        else:
            values, times = '1;1;.04;.04;1', f'0;{max(.0001,t-.001):.5f};{t+.001:.5f};{RESET_AT};1'
        b.append(f'<rect class="contribution-cell" data-count="{count}" x="{px-6:.1f}" y="{py-6:.1f}" width="12" height="12" rx="3" fill="{color}"><animate attributeName="opacity" values="{values}" keyTimes="{times}" dur="{DURATION}s" repeatCount="indefinite"/></rect>')
    b.append('</g>')
    route = 'M'+' L'.join(f'{x:.1f},{y:.1f}' for x,y in points)
    # The calendar occupies the first 86% of the loop. The return rail leaves
    # room for the counter reveal, and all cells reset before the next round.
    return_points = [(1170,points[-1][1]),(1170,111),(48,111),points[0]]
    full_points = points + return_points
    full_distance = sum(math.dist(a,z) for a,z in zip(full_points,full_points[1:])) or 1
    route += ''.join(f' L{x:.1f},{y:.1f}' for x,y in return_points)
    split = grid_distance/full_distance
    motion = f'path="{route}" dur="{DURATION}s" calcMode="linear" keyPoints="0;{split:.7f};1" keyTimes="0;{CLEAR_AT};1" repeatCount="indefinite"'
    b.append('<g class="players">')
    b.append(f'<g><animateMotion {motion} rotate="auto"/><path d="M0 0L10 -8A13 13 0 1 0 10 8Z" fill="#f8d86b"><animate attributeName="d" values="M0 0L10 -8A13 13 0 1 0 10 8Z;M0 0L13 -1A13 13 0 1 0 13 1Z;M0 0L10 -8A13 13 0 1 0 10 8Z" dur=".3s" repeatCount="indefinite"/></path></g>')
    for i,color in enumerate(['#a98aff','#62edee','#ff91b8']):
        b.append(f'<g><animateMotion {motion} begin="-{1.3+i*.85}s"/><path d="M-10 10V0A10 10 0 0 1 10 0V10L5 6 0 10-5 6Z" fill="{color}"/><ellipse cx="-4" cy="-1" rx="3" ry="4" fill="#fff"/><ellipse cx="4" cy="-1" rx="3" ry="4" fill="#fff"/><circle cx="-3" cy="-1" r="1.5" fill="#121934"/><circle cx="5" cy="-1" r="1.5" fill="#121934"/></g>')
    b.append('</g>')
    b.append(f'<g class="activity-counters" opacity="0"><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;.88;.89;.965;.985;1" dur="{DURATION}s" repeatCount="indefinite"/>')
    gap = 16
    width = (1080-gap*(len(metrics)-1))/len(metrics)
    for i,(label,value) in enumerate(metrics):
        b.append(reveal_counter(60+i*(width+gap),label,value,i,width))
    b.append('</g>')
    b.append(f'<text class="footer" x="30" y="316" font-size="13">{total} CONTRIBUTIONS / {active} ACTIVE DAYS / ACTUAL PUBLIC GITHUB DATA</text><text class="footer" x="974" y="316" font-size="12">ANIMATED REPLAY</text></svg>')
    return ''.join(b)


def static_svg(output):
    tree = ET.fromstring(output)
    tree.set('height','538')
    tree.set('viewBox','0 0 1200 538')
    for child in list(tree):
        if child.attrib.get('class') == 'players':
            tree.remove(child)
        elif child.attrib.get('class') == 'activity-counters':
            child.set('opacity','1')
            child.set('transform','translate(0 188)')
        elif child.attrib.get('class') == 'footer':
            child.set('y','510')
        elif child.attrib.get('id') == 'background':
            child.set('height','536')
    for element in tree.iter():
        for child in list(element):
            if child.tag.rsplit('}',1)[-1].startswith('animate'):
                element.remove(child)
    ET.register_namespace('','http://www.w3.org/2000/svg')
    return ET.tostring(tree,encoding='unicode')


def contribution_snapshot(calendar, username):
    """Expose only public calendar/stat fields; never include request headers."""
    days = sorted(({
        'date': day['date'],
        'contributionCount': nonnegative(day['contributionCount'], 'contributionCount'),
    } for week in calendar['weeks'] for day in week['contributionDays']),
        key=lambda day: day['date'])
    snapshot = {
        'username': username,
        'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'totalContributions': nonnegative(calendar['totalContributions'], 'totalContributions'),
        'activeDays': sum(day['contributionCount'] > 0 for day in days),
        # Legacy offline calendars may lack these fields. Null means unknown,
        # rather than inventing a zero count or making unexpected network calls.
        'pullRequests': None,
        'publicRepositories': None,
        'days': days,
    }
    for source, target in [('publicPullRequests', 'pullRequests'),
                           ('publicRepositories', 'publicRepositories')]:
        if source in calendar:
            snapshot[target] = nonnegative(calendar[source], source)
    return snapshot


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--username',default='Numan5837')
    p.add_argument('--calendar-json',type=Path)
    p.add_argument('--output',type=Path,default=Path('assets/contribution-pacman.svg'))
    args = p.parse_args()
    data = json.loads(args.calendar_json.read_text(encoding='utf-8-sig')) if args.calendar_json else get_calendar(args.username)
    output = render(data)
    static = static_svg(output)
    snapshot = contribution_snapshot(data, args.username)
    # Validate both documents before modifying the published output files.
    ET.fromstring(output)
    ET.fromstring(static)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(output,encoding='utf-8')
    args.output.with_name(args.output.stem+'-static.svg').write_text(static,encoding='utf-8')
    args.output.with_name('contribution-data.json').write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Arcade refreshed from {data["totalContributions"]} contributions across {len(data["weeks"])} weeks; actual squares clear before the public counters appear')


if __name__ == '__main__':
    main()
