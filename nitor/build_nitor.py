# Copyright (c) 2026, Karan Kapur, with Reserved Font Name "Nitor".
# This file is part of the Nitor Font Software, licensed under the
# SIL Open Font License, Version 1.1 (see OFL.txt).
"""Nitor final font files: the accepted RC2 font with the Nitor family names,
copyright notice, SIL Open Font License 1.1 records and installable embedding
set. NAME/METADATA ONLY - outlines, variations, metrics, cmap and kerning are
copied byte-for-byte from RC2 and verified below.

Inputs : RC2 variable font (default drift1/out/rc2/DriftD1-RC2-VF.ttf, or $NITOR_SRC)
Outputs: $NITOR_OUT (default nitor/out/fonts):
         Nitor-VF.ttf, Nitor-Thin.ttf, Nitor-Regular.ttf, Nitor-Black.ttf, validation.json
Usage  : python3.11 nitor/build_nitor.py
"""
import hashlib
import json
import os

from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

HERE = os.path.dirname(os.path.abspath(__file__))
LANE = os.path.dirname(HERE)
SRC = os.environ.get('NITOR_SRC', os.path.join(LANE, 'drift1', 'out', 'rc2', 'DriftD1-RC2-VF.ttf'))
OUT = os.environ.get('NITOR_OUT', os.path.join(HERE, 'out', 'fonts'))
FAMILY, VERSION = 'Nitor', 'Version 1.001'
DESCRIPTION = 'Nitor - reverse-contrast variable display face (wght 100-900).'
COPYRIGHT = 'Copyright (c) 2026, Karan Kapur, with Reserved Font Name "Nitor".'
LICENSE_DESC = ('This Font Software is licensed under the SIL Open Font License, Version 1.1. '
                'This license is available with a FAQ at: https://openfontlicense.org')
LICENSE_URL = 'https://openfontlicense.org'
FS_TYPE = 0   # installable embedding, as the OFL permits
OLD_TOKENS = ('Drift', 'D1', 'RC1', 'RC2', 'PrivateProof', 'PRIVATE PROOF', 'variable proof', 'exploratory',
              'TBD', 'No license granted', 'not a public release')
GEOMETRY_TABLES = ('glyf', 'loca', 'gvar', 'hmtx', 'hhea', 'maxp', 'cmap', 'GPOS', 'post')
STATICS = ((100, 'Thin'), (400, 'Regular'), (900, 'Black'))


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def set_name(font, nid, text):
    font['name'].setName(text, nid, 3, 1, 0x409)
    font['name'].setName(text, nid, 1, 0, 0)


def table_bytes(font, tag):
    return font.getTableData(tag) if tag in font else None


def names_of(font):
    return {r.nameID: r.toUnicode() for r in font['name'].names if r.platformID == 3}


def name_variable(f):
    for nid, text in ((1, f'{FAMILY} Thin'), (2, 'Regular'), (3, f'{FAMILY}-Thin; {VERSION}'),
                      (4, f'{FAMILY} Thin'), (5, VERSION), (6, f'{FAMILY}-Thin'),
                      (10, DESCRIPTION), (16, FAMILY), (17, 'Thin'), (25, FAMILY),
                      (0, COPYRIGHT), (13, LICENSE_DESC), (14, LICENSE_URL)):
        set_name(f, nid, text)
    f['OS/2'].fsType = FS_TYPE
    # fvar instance labels: 100 Thin, 400 Regular, 900 Black (900 is "Black" in
    # the CSS/OpenType weight scale; RC2 called it "Bold")
    thin_id = f['name'].addMultilingualName({'en': 'Thin'}, f, minNameID=256)
    black_id = f['name'].addMultilingualName({'en': 'Black'}, f, minNameID=256)
    for inst in f['fvar'].instances:
        w = inst.coordinates['wght']
        if w == 100:
            inst.subfamilyNameID = thin_id
        elif w == 900:
            inst.subfamilyNameID = black_id
    used = {a.axisNameID for a in f['fvar'].axes} | {i.subfamilyNameID for i in f['fvar'].instances}
    f['name'].names = [r for r in f['name'].names if r.nameID < 256 or r.nameID in used]
    f['head'].fontRevision = 1.001


def name_static(f, w, style):
    fam1 = FAMILY if style == 'Regular' else f'{FAMILY} {style}'
    for nid, text in ((1, fam1), (2, 'Regular'), (3, f'{FAMILY}-{style}; {VERSION}'),
                      (4, f'{FAMILY} {style}'), (5, VERSION), (6, f'{FAMILY}-{style}'),
                      (10, DESCRIPTION), (16, FAMILY), (17, style),
                      (0, COPYRIGHT), (13, LICENSE_DESC), (14, LICENSE_URL)):
        set_name(f, nid, text)
    f['OS/2'].fsType = FS_TYPE
    f['name'].names = [r for r in f['name'].names if r.nameID < 256 and r.nameID != 25]
    f['OS/2'].usWeightClass = w
    f['OS/2'].fsSelection = (f['OS/2'].fsSelection & ~0b100001) | 0b1000000   # REGULAR, not bold/italic
    f['head'].macStyle = 0
    f['head'].fontRevision = 1.001


def main():
    os.makedirs(OUT, exist_ok=True)
    rc2 = TTFont(SRC)
    vf = TTFont(SRC)
    name_variable(vf)
    vf_path = os.path.join(OUT, f'{FAMILY}-VF.ttf')
    vf.save(vf_path)
    report = {'source_rc2': {'path': os.path.relpath(SRC, LANE), 'sha256': sha(SRC)}, 'files': {}}
    vfr = TTFont(vf_path)
    report['files']['Nitor-VF.ttf'] = {
        'sha256': sha(vf_path), 'names': names_of(vfr),
        'fvar_axes': [(a.axisTag, a.minValue, a.defaultValue, a.maxValue) for a in vfr['fvar'].axes],
        'fvar_instances': [(names_of(vfr)[i.subfamilyNameID], i.coordinates['wght']) for i in vfr['fvar'].instances],
        'tables_identical_to_rc2': {t: table_bytes(vfr, t) == table_bytes(rc2, t) for t in GEOMETRY_TABLES + ('OS/2',)},
        'fvar_axes_identical_to_rc2': [(a.axisTag, a.minValue, a.defaultValue, a.maxValue) for a in vfr['fvar'].axes]
        == [(a.axisTag, a.minValue, a.defaultValue, a.maxValue) for a in rc2['fvar'].axes]}
    for w, style in STATICS:
        st = instancer.instantiateVariableFont(TTFont(vf_path), {'wght': w})
        ref = instancer.instantiateVariableFont(TTFont(SRC), {'wght': w})   # RC2 cut the same way
        name_static(st, w, style)
        p = os.path.join(OUT, f'{FAMILY}-{style}.ttf')
        st.save(p)
        str_ = TTFont(p)
        report['files'][f'{FAMILY}-{style}.ttf'] = {
            'sha256': sha(p), 'names': names_of(str_), 'usWeightClass': str_['OS/2'].usWeightClass,
            'tables_identical_to_rc2_instance': {t: table_bytes(str_, t) == table_bytes(ref, t)
                                                 for t in GEOMETRY_TABLES if t in str_ or t in ref}}
    # metadata validation
    problems = []
    for fn, info in report['files'].items():
        for nid, text in info['names'].items():
            if any(tok in text for tok in OLD_TOKENS):
                problems.append((fn, nid, text))
        for t, same in {**info.get('tables_identical_to_rc2', {}), **info.get('tables_identical_to_rc2_instance', {})}.items():
            if t != 'OS/2' and not same:
                problems.append((fn, 'table differs', t))
        f = TTFont(os.path.join(OUT, fn))
        ps = info['names'][6]
        if not (ps.replace('-', '').isalnum() and len(ps) <= 63 and fn.startswith(ps.split('-')[0])):
            problems.append((fn, 'postscript name', ps))
        if len(f.getBestCmap()) != 77 or f['maxp'].numGlyphs != 78:
            problems.append((fn, 'coverage', len(f.getBestCmap()), f['maxp'].numGlyphs))
        for nid, want in ((0, COPYRIGHT), (13, LICENSE_DESC), (14, LICENSE_URL), (5, VERSION)):
            if info['names'].get(nid) != want:
                problems.append((fn, 'name', nid, info['names'].get(nid)))
        if f['OS/2'].fsType != FS_TYPE:
            problems.append((fn, 'fsType', f['OS/2'].fsType))
    report['old_title_geometry_or_metadata_problems'] = problems
    json.dump(report, open(os.path.join(OUT, 'validation.json'), 'w'), indent=1, ensure_ascii=False)
    print(json.dumps(report, indent=1, ensure_ascii=False))


if __name__ == '__main__':
    main()
