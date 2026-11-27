# Assemble index.html v3 from head + style/body + script and pixgen3 output.
import json, random, sys
d = json.load(open('/home/claude/tools/pix3.json'))
head = open('/home/claude/tools/v3_head.html').read().replace('content="#0b0a09"', 'content="#0a0a0a"')
body = open('/home/claude/tools/v3_style_body.html').read()
script = open('/home/claude/tools/v3_script.html').read()
s = head + body + script
def cls(svg, c, extra=''):
    return svg.replace('class="tree"', f'class="tree {c}"').replace('class="cloud"', f'class="cloud {c}"', 1)
rnd = random.Random(3)
petals = ''.join(
    f'<i style="--x:{rnd.randint(2,98)}%;--d:{rnd.uniform(7,13):.1f}s;--dl:{-rnd.uniform(0,13):.1f}s;--dx:{rnd.choice([-1,1])*rnd.randint(30,90)}px;'
    f'--c:{rnd.choice(["#29713c","#6fbf5a","#a6c97c","#c9eed3"])}"></i>' for _ in range(12)) + ''.join(
    f'<b style="--x:{rnd.randint(4,96)}%;--d:{rnd.uniform(9,15):.1f}s;--dl:{-rnd.uniform(0,15):.1f}s;--dx:{rnd.choice([-1,1])*rnd.randint(10,50)}px"></b>' for _ in range(8))
rep = {
    '@@WIDE@@': d['wide'], '@@STACK@@': d['stack'],
    '@@treeL@@': cls(d['tree'], 'l'), '@@treeR@@': cls(d['tree2'], 'r'),
    '@@treeBL@@': cls(d['tree2'], 'back l'), '@@treeBR@@': cls(d['tree'], 'back r'),
    '@@petals@@': petals,
    '@@phone@@': d['icons']['phone'], '@@pc@@': d['icons']['pc'], '@@tall@@': d['icons']['tall'], '@@wide_ic@@': d['icons']['wide'],
}
for k, v in rep.items():
    assert k in s, k
    s = s.replace(k, v)
assert '@@' not in s
open(sys.argv[1], 'w').write(s)
print('ok', len(s))
