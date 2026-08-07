# -*- coding: utf-8 -*-
content = open(r'C:\lab\vsurf_capital\common\CT_handover_v10_src.md', encoding='utf-8').read()
with open(r'C:\lab\vsurf_capital\common\CT_handover_20260507_v10.md', 'w', encoding='utf-8') as f:
    f.write(content)
print("OK")
