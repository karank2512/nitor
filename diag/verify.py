"""Controlled render check: which font did Chrome actually use, and do the
cases differ at the same pixel position?

For each case: one page with exactly ONE @font-face (data URI of a named
font file, sha256 recorded), integer line-height (no fractional offsets),
a fresh Chrome profile per invocation, then
  1) --dump-dom: FontFace.status, document.fonts.check, canvas widths
     (HHHH at 100px must be 240px for a 600-unit mono; a sentinel 'x',
     absent from the font, must fall back and measure differently),
  2) --screenshot at the same layout; diffs vs the Clean case.
Usage: python3.11 diag/verify.py <fontdir> <outdir>
"""
import base64
import hashlib
import json
import os
import re
import subprocess
import sys
from PIL import Image, ImageChops, ImageOps

CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
LANE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fontdir, outdir = (os.path.abspath(a) for a in sys.argv[1:3])
os.makedirs(outdir, exist_ok=True)
PROFILES = os.path.join(LANE, '.chrome-diag-profiles', os.path.basename(outdir))

TEXT = ['nnonnoon  nnannsnngnn  HHnnHHoo',
        'il1  0o0  {lion}  {sign}  1001 0110',
        'a lagoon slang lion song gloss signs',
        'Hossain {aloss} snail1 log0 {nisga}',
        '{ sign{ son1 } 010 } iiillll1111']

CASES = [  # (id, file, font-variation-settings or None)
    ('clean', 'ProofClean.ttf', None),
    ('ctrlvar0', 'ProofCtrlVar.ttf', "'TRCE' 0"),
    ('z0_trce0', 'ProofTRCE-z0.ttf', "'TRCE' 0"),
    ('z0_novar', 'ProofTRCE-z0.ttf', None),
    ('h2_trce0', 'ProofTRCE-h2.ttf', "'TRCE' 0"),
    ('z0_trce100', 'ProofTRCE-z0.ttf', "'TRCE' 100"),
    ('ghost', 'ProofGhost.ttf', None),
]
SMOOTH = {'default': '', 'aa': '-webkit-font-smoothing:antialiased;'}


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def page(case, smooth):
    cid, file, fvs = case
    b64 = base64.b64encode(open(os.path.join(fontdir, file), 'rb').read()).decode()
    var = f'font-variation-settings:{fvs};' if fvs else ''
    js = """
    document.fonts.ready.then(async () => {
      const faces = []; document.fonts.forEach(f => faces.push({family: f.family, status: f.status}));
      const c = document.createElement('canvas').getContext('2d');
      const w = (fam, s) => { c.font = '100px ' + fam; return c.measureText(s).width; };
      const r = {faces, check: document.fonts.check("13px 'Probe'"),
        HHHH_probe: w("'Probe'", 'HHHH'), HHHH_fallback_monospace: w('monospace', 'HHHH'),
        sentinel_x_probe: w("'Probe', 'Courier New'", 'x'), sentinel_x_courier: w("'Courier New'", 'x'),
        text_el_computed: getComputedStyle(document.getElementById('t')).fontFamily,
        text_el_fvs: getComputedStyle(document.getElementById('t')).fontVariationSettings,
        text_width_px: document.getElementById('probe').getBoundingClientRect().width};
      document.getElementById('diag').textContent = 'DIAG' + JSON.stringify(r) + 'END';
    });"""
    html = f"""<!doctype html><meta charset=utf-8><style>
@font-face{{font-family:'Probe';src:url(data:font/ttf;base64,{b64}) format('truetype');font-display:block}}
html,body{{margin:0;background:#f4f1ea;color:#16171a}}
#t{{position:absolute;left:20px;top:20px;font-family:'Probe';{var}{SMOOTH[smooth]}
   font-size:13px;line-height:18px;white-space:pre}}
#probe{{position:absolute;left:0;top:300px;font-family:'Probe';font-size:100px;white-space:pre;visibility:hidden}}
#diag{{position:absolute;top:400px;font:10px monospace}}
</style><div id=t>{chr(10).join(TEXT)}</div><span id=probe>HHHH</span><div id=diag></div>
<script>{js}</script>"""
    p = os.path.join(outdir, f'{cid}-{smooth}.html')
    open(p, 'w').write(html)
    return p


def chrome(args, profile):
    base = [CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars',
            '--no-first-run', '--no-default-browser-check', '--use-mock-keychain',
            '--password-store=basic', '--disable-extensions',
            '--disk-cache-size=1', '--force-device-scale-factor=1',
            f'--user-data-dir={profile}', '--virtual-time-budget=4000']
    return subprocess.run(base + args, check=True, capture_output=True, timeout=120, text=True)


if __name__ == '__main__':
    report = {'fonts': {}, 'cases': {}}
    for _, f, _ in CASES:
        report['fonts'][f] = sha(os.path.join(fontdir, f))
    for smooth in SMOOTH:
        imgs = {}
        for case in CASES:
            cid = case[0]
            h = page(case, smooth)
            dom = chrome(['--dump-dom', 'file://' + h],
                         os.path.join(PROFILES, f'{cid}-{smooth}-dom')).stdout
            m = re.search(r'DIAG(.*?)END', dom)
            diag = json.loads(m.group(1).replace('&quot;', '"')) if m else 'NO DIAG'
            png = os.path.join(outdir, f'{cid}-{smooth}.png')
            chrome([f'--window-size=420,130', f'--screenshot={png}', 'file://' + h],
                   os.path.join(PROFILES, f'{cid}-{smooth}-shot'))
            imgs[cid] = Image.open(png).convert('L')
            report['cases'][f'{cid}-{smooth}'] = {
                'font_file': case[1], 'font_sha256': report['fonts'][case[1]],
                'font_variation_settings': case[2], 'png': png, 'png_sha256': sha(png),
                'diag': diag}
        for cid, im in imgs.items():
            d = ImageChops.difference(imgs['clean'], im)
            hist = d.histogram()
            r = report['cases'][f'{cid}-{smooth}']
            r['vs_clean'] = {'max': d.getextrema()[1], 'changed': sum(hist[1:]),
                             'gt15': sum(hist[16:]), 'bbox': d.getbbox()}
            if d.getbbox():
                dp = os.path.join(outdir, f'diff-{cid}-{smooth}.png')
                ImageOps.invert(ImageOps.autocontrast(d)).resize(
                    (d.width * 3, d.height * 3), Image.NEAREST).save(dp)
                r['diff_png'], r['diff_sha256'] = dp, sha(dp)
    json.dump(report, open(os.path.join(outdir, 'report.json'), 'w'), indent=1)
    for k, v in report['cases'].items():
        dg = v['diag'] if isinstance(v['diag'], dict) else {}
        print(f"{k:22s} {v['font_file']:18s} fvs={str(v['font_variation_settings']):12s} "
              f"status={[f['status'] for f in dg.get('faces', [])]} "
              f"HHHH={dg.get('HHHH_probe')} mono={dg.get('HHHH_fallback_monospace')} "
              f"x={dg.get('sentinel_x_probe')}/{dg.get('sentinel_x_courier')} "
              f"fvs_css={dg.get('text_el_fvs')} | vs clean: changed {v['vs_clean']['changed']}, "
              f">15 {v['vs_clean']['gt15']}")
