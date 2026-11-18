"""RC1 vs RC2 ampersand, Chrome-rendered, wght 100..900 (9 steps), dark + light.
Writes drift1/out/qa-render-rc2/amp-rc1-vs-rc2-<ground>.png. Fresh profile per render."""
import base64, hashlib, json, os, re, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); LANE = os.path.dirname(HERE)
OUT = os.path.join(HERE, 'out', 'qa-render-rc2')
CH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
F = {'R1': os.path.join(HERE, 'out', 'rc1', 'DriftD1-RC1-VF.ttf'), 'R2': os.path.join(HERE, 'out', 'rc2', 'DriftD1-RC2-VF.ttf')}
faces = ''.join(f"@font-face{{font-family:'{k}';src:url(data:font/ttf;base64,{base64.b64encode(open(v,'rb').read()).decode()}) format('truetype');font-weight:100 900}}" for k, v in F.items())
res = {}
for g, (bg, fg) in {'dark': ('#050607', '#e9ecef'), 'light': ('#f2efe9', '#111214')}.items():
    rows = ''.join(f"<div style='display:flex;gap:28px;align-items:baseline'><span class=l>{w}</span>"
                   f"<span class=t style=\"font-family:R1;font-variation-settings:'wght' {w}\">&amp;</span>"
                   f"<span class=t style=\"font-family:R2;font-variation-settings:'wght' {w}\">&amp;</span></div>"
                   for w in range(100, 901, 100))
    html = (f"<!doctype html><meta charset=utf-8><style>{faces}html,body{{margin:0;background:{bg};color:{fg}}}"
            f"body{{padding:20px 30px;column-count:3}}.t{{font-size:190px;line-height:1}}.l{{font:12px Helvetica;color:#888;width:40px}}"
            f"#d{{display:none}}</style><div style='font:13px Helvetica;color:#888'>left = RC1, right = RC2 (per weight)</div>{rows}"
            "<div id=d></div><script>document.fonts.ready.then(()=>{const s=[];document.fonts.forEach(f=>s.push(f.family+':'+f.status));"
            "document.getElementById('d').textContent='DIAG'+JSON.stringify(s)+'END'})</script>")
    p = os.path.join(OUT, f'amp-rc1-vs-rc2-{g}.html'); open(p, 'w').write(html)
    prof = os.path.join(LANE, '.chrome-diag-profiles', 'drift1-ampcmp', g)
    base = [CH, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--no-first-run', '--use-mock-keychain',
            '--password-store=basic', '--disk-cache-size=1', '--force-device-scale-factor=1', '--virtual-time-budget=4000']
    dom = subprocess.run(base + [f'--user-data-dir={prof}-dom', '--dump-dom', 'file://' + p], capture_output=True, text=True, timeout=120).stdout
    png = os.path.join(OUT, f'amp-rc1-vs-rc2-{g}.png')
    subprocess.run(base + [f'--user-data-dir={prof}-shot', '--window-size=1500,820', f'--screenshot={png}', 'file://' + p], capture_output=True, text=True, timeout=120, check=True)
    m = re.search(r'DIAG(.*?)END', dom)
    res[g] = [os.path.relpath(png, LANE), hashlib.sha256(open(png, 'rb').read()).hexdigest(), m.group(1).replace('&quot;', '"') if m else None]
print(json.dumps(res, indent=1))
