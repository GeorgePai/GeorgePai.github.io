# Potato Pai homepage pixel art v2: layered arcade title + multi-tone device icons.
import json, sys

G = {
 'P': ["######.","#######","##...##","##...##","#######","######.","##.....","##.....","##....."],
 'O': [".#####.","#######","##...##","##...##","##...##","##...##","##...##","#######",".#####."],
 'T': ["######","######","..##..","..##..","..##..","..##..","..##..","..##..","..##.."],
 'A': [".#####.","#######","##...##","##...##","#######","#######","##...##","##...##","##...##"],
 'I': ["######","######","..##..","..##..","..##..","..##..","..##..","######","######"],
}
GAP, SPACE, LH = 2, 4, 16          # letter gap, word space, line pitch (rows)
BANDS = ["#fff8d2","#ffeb8a","#ffd650","#ffc63c","#fbab33","#f3932b","#e47a23","#d0641d","#b9521a"]
HI, SHADE = "#ffffff", None        # bevel highlight / right-edge shade handled per band
EXT = ["#c25a1b", "#9a4314", "#70300e"]   # extrusion depth 1..3
INK, RIM = "#120a04", "#fff1cf"
HALO = "#f2a93b"
BAYER = [[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]]

def darker(hexc, f):
    r, g, b = (int(hexc[i:i+2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % (int(r*f), int(g*f), int(b*f))

def layout(lines):
    px, widths = {}, []
    for w in lines:
        n = [c for c in w if c != ' ']
        widths.append(sum(len(G[c][0]) for c in n) + GAP*(len(n)-1) + (SPACE-GAP)*w.count(' ') + GAP*w.count(' '))
    W = max(widths)
    for li, w in enumerate(lines):
        x = (W - widths[li]) // 2
        for c in w:
            if c == ' ': x += SPACE; continue
            for r, row in enumerate(G[c]):
                for cx, ch in enumerate(row):
                    if ch == '#': px[(x+cx, li*LH + r)] = r
            x += len(G[c][0]) + GAP
    return px, W, (len(lines)-1)*LH + 9

N8 = [(dx, dy) for dx in (-1,0,1) for dy in (-1,0,1)]
def dil(s, k=1):
    for _ in range(k): s = s | {(x+dx, y+dy) for (x, y) in s for dx, dy in N8}
    return s

def rects(cells, color, extra=""):
    rows = {}
    for (x, y) in cells: rows.setdefault(y, []).append(x)
    out = []
    for y, xs in sorted(rows.items()):
        xs.sort(); s = p = xs[0]
        for x in xs[1:] + [None]:
            if x is not None and x == p + 1: p = x; continue
            out.append(f'<rect x="{s}" y="{y}" width="{p-s+1}" height="1"/>')
            if x is not None: s = p = x
    return f'<g fill="{color}"{extra}>' + ''.join(out) + '</g>' if out else ''

def title_svg(lines, cls, uid):
    fill, W, H = layout(lines)
    M = 9
    F = {(x+M, y+M): r for (x, y), r in fill.items()}
    base = set(F)
    X = {}
    for k in (1, 2, 3):                             # 3D extrusion attached to the letters
        for (x, y) in base:
            q = (x, y+k)
            if q not in base and q not in X: X[q] = k
    solid = base | set(X)
    ink = dil(solid) - solid                        # one ink outline around letter+extrusion
    body = solid | ink
    rim = dil(body) - body                          # cream outer rim
    outer = body | rim
    w, h = W + 2*M, H + 2*M + 3
    # dithered halo behind title (ordered Bayer, fades with distance)
    halo = set()
    # cheap distance: chebyshev rings
    ring, seen = set(outer), set(outer)
    for d in range(1, 5):
        ring = dil(ring) - seen; seen |= ring
        thr = 16 * (1 - d/5) ** 1.3
        for (x, y) in ring:
            if 0 <= x < w and 0 <= y < h and BAYER[y % 4][x % 4] < thr: halo.add((x, y))
    parts = [rects(halo, HALO, ' opacity=".22"'), rects(rim, RIM), rects(ink, INK)]
    for k, col in enumerate(EXT, 1):
        parts.append(rects({p for p, kk in X.items() if kk == k}, col))
    # letter fill with bevel: left/top edge lighter, right edge darker
    for r, col in enumerate(BANDS):
        cells = {p for p, rr in F.items() if rr == r}
        right = {(x, y) for (x, y) in cells if (x+1, y) not in base}
        parts.append(rects(cells - right, col))
        parts.append(rects(right, darker(col, .82)))
    left = {(x, y) for (x, y) in base if (x-1, y) not in base and F[(x, y)] <= 4}
    parts.append(rects(left, "#fffbe8", ' opacity=".55"'))
    top = {(x, y) for (x, y) in base if (x, y-1) not in base and (x-1, y) not in base and F[(x, y)] <= 1}
    parts.append(rects(top, HI))
    # moving glint, clipped to the letter fill
    clip = ''.join(f'<rect x="{x}" y="{y}" width="1" height="1"/>' for (x, y) in sorted(base))
    glint = (f'<defs><clipPath id="g{uid}">{clip}</clipPath></defs>'
             f'<g clip-path="url(#g{uid})"><g class="glint" fill="#ffffff" opacity=".85">'
             + ''.join(f'<rect x="{-y-4}" y="{y}" width="2" height="1"/><rect x="{-y-1}" y="{y}" width="1" height="1"/>' for y in range(h))
             + '</g></g>')
    return (f'<svg class="{cls}" viewBox="0 0 {w} {h}" shape-rendering="crispEdges" aria-hidden="true" style="--w:{w};--h:{h};--L:{w+h+4}px">'
            + ''.join(parts) + glint + '</svg>')

PAL = {'K':"#0b0a09",'b':"#4b4339",'d':"#2d2822",'l':"#6c6255",'S':"#f2c35b",'s':"#c98f2c",'H':"#fff3c4",
       'G':"#8f877a",'A':"#e8d6a6",'P':"#7a4a1f",'p':"#b07236",'g':"#5b8f3a"}
ICONS = {
 'phone': [
  "................",
  ".....KKKKKK.....",
  "....KlbbbbdK....",
  "....KlbGGbdK....",
  "....KKKKKKKK....",
  "....KSHSSSsK....",
  "....KHSSSSsK....",
  "....KSSSSSsK....",
  "....KSSppSsK....",
  "....KSpPPpsK....",
  "....KggggggK....",
  "....KKKKKKKK....",
  "....KlbGGbdK....",
  "....KlbbbbdK....",
  ".....KKKKKK.....",
  "................"],
 'pc': [
  "................",
  ".KKKKKKKKKKKKKK.",
  "KlbbbbbbbbbbbbdK",
  "KlKKKKKKKKKKKKdK",
  "KlKSHSSSSSSSsKdK",
  "KlKHSSSSSSSSsKdK",
  "KlKSSSSSppSSsKdK",
  "KlKSSSSpPPpSsKdK",
  "KlKggggggggggKdK",
  "KlKKKKKKKKKKKKdK",
  "KlbbbbbbGGbbbbdK",
  ".KKKKKKKKKKKKKK.",
  "......KbdK......",
  "....KKKKKKKK....",
  "...KlbbbbbbdK...",
  "...KKKKKKKKKK..."],
 'tall': [
  "................",
  "....KKKKKK......",
  "...KlbbbbdK..A..",
  "...KKKKKKKK.AAA.",
  "...KSHSSSsK..A..",
  "...KHSSSSsK..A..",
  "...KSSSSSsK..A..",
  "...KSSSSSsK..A..",
  "...KSSSSSsK..A..",
  "...KSSSSSsK..A..",
  "...KssssssK..A..",
  "...KKKKKKKK.AAA.",
  "...KlbGGbdK..A..",
  "....KKKKKK......",
  "................",
  "................"],
 'wide': [
  "................",
  "................",
  "..KKKKKKKKKKKK..",
  ".KlKSHSSSSSSKdK.",
  "KlbKHSSSSSSsKbdK",
  "KlGKSSSSSSSsKbdK",
  "KlGKSSSSSSSsKbdK",
  "KlbKsssssssKKbdK",
  ".KlKKKKKKKKKKdK.",
  "..KKKKKKKKKKKK..",
  "................",
  "..A..........A..",
  ".AAAAAAAAAAAAAA.",
  "..A..........A..",
  "................",
  "................"],
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

out = {'wide': title_svg(["POTATO PAI"], "t-wide", "w"), 'stack': title_svg(["POTATO", "PAI"], "t-stack", "s"),
       'icons': {k: icon_svg(k) for k in ICONS}}
json.dump(out, open(sys.argv[1], 'w'))
import re
for k in ('wide', 'stack'): print(k, re.search(r'viewBox="([^"]+)"', out[k]).group(1), len(out[k]))
