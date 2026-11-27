# Potato Pai homepage pixel art v3: animated white title, sakura trees, clouds, blue-screen icons.
import json, sys, math, random

G = {
 'P': ["######.","#######","##...##","##...##","#######","######.","##.....","##.....","##....."],
 'O': [".#####.","#######","##...##","##...##","##...##","##...##","##...##","#######",".#####."],
 'T': ["######","######","..##..","..##..","..##..","..##..","..##..","..##..","..##.."],
 'A': [".#####.","#######","##...##","##...##","#######","#######","##...##","##...##","##...##"],
 'I': ["######","######","..##..","..##..","..##..","..##..","..##..","######","######"],
}
GAP, SPACE, LH = 2, 4, 14
BAYER = [[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]]

def runs(cells):
    rows = {}
    for (x, y) in cells: rows.setdefault(y, []).append(x)
    out = []
    for y, xs in sorted(rows.items()):
        xs.sort(); s = p = xs[0]
        for x in xs[1:] + [None]:
            if x is not None and x == p + 1: p = x; continue
            out.append((s, y, p - s + 1))
            if x is not None: s = p = x
    return out

def rects(cells, color, extra=""):
    r = runs(cells)
    if not r: return ''
    return f'<g fill="{color}"{extra}>' + ''.join(f'<rect x="{x}" y="{y}" width="{w}" height="1"/>' for x, y, w in r) + '</g>'

def title_svg(lines, cls):
    # place letters
    letters, widths = [], []
    for w in lines:
        n = [c for c in w if c != ' ']
        widths.append(sum(len(G[c][0]) for c in n) + GAP*(len(n)-1) + SPACE*w.count(' '))
    W = max(widths)
    M = 2
    for li, w in enumerate(lines):
        x = (W - widths[li]) // 2
        for c in w:
            if c == ' ': x += SPACE - GAP; continue
            cells = {(x+cx+M, li*LH + r + M): r for r, row in enumerate(G[c]) for cx, ch in enumerate(row) if ch == '#'}
            letters.append(cells)
            x += len(G[c][0]) + GAP
    w, h = W + 2*M + 3, (len(lines)-1)*LH + 9 + 2*M + 4
    out = []
    for i, cells in enumerate(letters):
        base = set(cells)
        far = {(x+2, y+3) for (x, y) in base}
        near = {(x+1, y+1) for (x, y) in base}
        body = [rects(far, "#000000", ' opacity=".45"'), rects(near - base, "#0e1a0d", ' opacity=".9"')]
        top = {p for p, r in cells.items() if r == 0}
        low = {p for p, r in cells.items() if r >= 7}
        mid = base - top - low
        body += [rects(mid, "#ffffff"), rects(low, "#eef3dc"), rects(top, "#ffffff")]
        # tiny pink rim light on the left edge, bottom half
        rim = {(x, y) for (x, y) in base if (x-1, y) not in base and cells[(x, y)] >= 4}
        body.append(rects(rim, "#f6f1de"))
        out.append(f'<g class="lt" style="--i:{i}">' + ''.join(body) + '</g>')
    return (f'<svg class="{cls}" viewBox="0 0 {w} {h}" shape-rendering="crispEdges" aria-hidden="true" style="--w:{w};--h:{h}">'
            + ''.join(out) + '</svg>')

def blob_scene(W, H, blobs, palette, seed, trunk=None, ground=None):
    rnd = random.Random(seed)
    noise = {(x, y): rnd.uniform(-1.2, 1.2) for x in range(W) for y in range(H)}
    layers = {k: set() for k in palette}
    canopy = {}
    for (cx, cy, r) in blobs:
        for y in range(int(cy-r-2), int(cy+r+3)):
            for x in range(int(cx-r-2), int(cx+r+3)):
                if not (0 <= x < W and 0 <= y < H): continue
                d = math.hypot(x-cx, (y-cy)*1.1)
                if d < r + noise[(x, y)]:
                    l = ((cx - x) * .7 + (cy - y)) / r          # light from top-left
                    l += (BAYER[y % 4][x % 4] - 7.5) / 16 * .45
                    canopy[(x, y)] = max(canopy.get((x, y), -9), l)
    if trunk:
        for (x, y), k in trunk.items():
            if (x, y) not in canopy or k == 'force': layers['bark' if (x+y) % 7 else 'barkL'].add((x, y))
    for p, l in canopy.items():
        k = 'hi' if l > .75 else 'lt' if l > .2 else 'base' if l > -.45 else 'sh'
        layers[k].add(p)
    edge = {p for p in canopy if (p[0], p[1]+1) not in canopy}
    layers['sh'] |= edge
    if ground:
        for p in ground: layers['petal'].add(p)
    return layers

def thick_line(a, b, w0, w1):
    (x0, y0), (x1, y1) = a, b
    n = max(abs(x1-x0), abs(y1-y0)) * 2 + 1
    cells = set()
    for i in range(n + 1):
        t = i / n
        x, y = x0 + (x1-x0)*t, y0 + (y1-y0)*t
        ww = w0 + (w1-w0)*t
        for dx in range(-int(ww), int(ww)+1):
            if abs(dx) <= ww/2: cells.add((round(x+dx), round(y)))
    return cells

def tree_svg(cls, seed, scale_blobs=1.0):
    W, H = 76, 66
    trunk = {}
    for seg in [((38, 65), (37, 40), 6, 4), ((37, 44), (22, 30), 3, 2), ((37, 42), (54, 28), 3, 2), ((37, 40), (36, 22), 3, 2),
                ((24, 32), (12, 34), 2, 1), ((52, 30), (64, 33), 2, 1)]:
        for p in thick_line(seg[0], seg[1], seg[2], seg[3]): trunk[p] = 1
    blobs = [(20, 24, 11), (36, 16, 12), (53, 22, 12), (28, 31, 9), (46, 31, 9), (11, 32, 7), (64, 31, 7), (36, 27, 8)]
    pal = {'sh': "#2c3b24", 'base': "#4d6a3b", 'lt': "#6f9152", 'hi': "#a6c97c", 'bark': "#3d3021", 'barkL': "#5a4630", 'petal': "#6f9152"}
    rnd = random.Random(seed + 7)
    ground = {(rnd.randint(14, 62), rnd.randint(62, 65)) for _ in range(10)}
    L = blob_scene(W, H, blobs, pal, seed, trunk, ground)
    body = ''.join(rects(L[k], pal[k]) for k in ['bark', 'barkL', 'sh', 'base', 'lt', 'hi', 'petal'])
    return f'<svg class="{cls}" viewBox="0 0 {W} {H}" shape-rendering="crispEdges" aria-hidden="true" style="--w:{W};--h:{H}">{body}</svg>'

def cloud_svg(cls, seed):
    W, H = 60, 22
    blobs = [(14, 13, 8), (26, 9, 9), (39, 11, 8), (50, 14, 6), (31, 15, 7)]
    pal = {'sh': "#4f4680", 'base': "#6e62a6", 'lt': "#9284c6", 'hi': "#b9abe3", 'bark': "#000", 'barkL': "#000", 'petal': "#000"}
    L = blob_scene(W, H, blobs, pal, seed)
    body = ''.join(rects(L[k], pal[k]) for k in ['sh', 'base', 'lt', 'hi'])
    return f'<svg class="{cls}" viewBox="0 0 {W} {H}" shape-rendering="crispEdges" aria-hidden="true" style="--w:{W};--h:{H}">{body}</svg>'

PAL = {'K':"#1d1b22",'b':"#4a4f5e",'d':"#2e323d",'l':"#6d7486",'S':"#a9dcf5",'s':"#74b6dc",'H':"#e8f8ff",
       'G':"#9aa3b5",'A':"#2b2620",'P':"#8a5a2b",'p':"#c4893f",'g':"#6fbf5a"}
ICONS = {
 'phone': ["................",".....KKKKKK.....","....KlbbbbdK....","....KlbGGbdK....","....KKKKKKKK....","....KSHSSSsK....",
           "....KHSSSSsK....","....KSSSSSsK....","....KSSppSsK....","....KSpPPpsK....","....KggggggK....","....KKKKKKKK....",
           "....KlbGGbdK....","....KlbbbbdK....",".....KKKKKK.....","................"],
 'pc':    ["................",".KKKKKKKKKKKKKK.","KlbbbbbbbbbbbbdK","KlKKKKKKKKKKKKdK","KlKSHSSSSSSSsKdK","KlKHSSSSSSSSsKdK",
           "KlKSSSSSppSSsKdK","KlKSSSSpPPpSsKdK","KlKggggggggggKdK","KlKKKKKKKKKKKKdK","KlbbbbbbGGbbbbdK",".KKKKKKKKKKKKKK.",
           "......KbdK......","....KKKKKKKK....","...KlbbbbbbdK...","...KKKKKKKKKK..."],
 'tall':  ["................","....KKKKKK......","...KlbbbbdK..A..","...KKKKKKKK.AAA.","...KSHSSSsK..A..","...KHSSSSsK..A..",
           "...KSSSSSsK..A..","...KSSSSSsK..A..","...KSSppSsK..A..","...KSpPPpsK..A..","...KggggggK..A..","...KKKKKKKK.AAA.",
           "...KlbGGbdK..A..","....KKKKKK......","................","................"],
 'wide':  ["................","................","..KKKKKKKKKKKK..",".KlKSHSSSSSSKdK.","KlbKHSSSSSSsKbdK","KlGKSSSSppSsKbdK",
           "KlGKSSSpPPpsKbdK","KlbKgggggggKKbdK",".KlKKKKKKKKKKdK.","..KKKKKKKKKKKK..","................","..A..........A..",
           ".AAAAAAAAAAAAAA.","..A..........A..","................","................"],
}
def icon_svg(name):
    rows = ICONS[name]
    assert all(len(r) == 16 for r in rows) and len(rows) == 16, (name, [len(r) for r in rows])
    by = {}
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch != '.': by.setdefault(ch, set()).add((x, y))
    return ('<svg class="ic" viewBox="0 0 16 16" shape-rendering="crispEdges" aria-hidden="true">'
            + ''.join(rects(c, PAL[k]) for k, c in by.items()) + '</svg>')

out = {'wide': title_svg(["POTATO PAI"], "t-wide"), 'stack': title_svg(["POTATO", "PAI"], "t-stack"),
       'tree': tree_svg("tree", 11), 'tree2': tree_svg("tree", 23), 'cloud': cloud_svg("cloud", 5),
       'icons': {k: icon_svg(k) for k in ICONS}}
json.dump(out, open(sys.argv[1], 'w'))
import re
for k in ('wide', 'stack', 'tree', 'cloud'): print(k, re.search(r'viewBox="([^"]+)"', out[k]).group(1), len(out[k]))
