# -*- coding: utf-8 -*-
import re

# === hypothesis_tree 갱신 ===
with open(r'C:\lab\vsurf_capital\common\hypothesis_tree.md', encoding='utf-8') as f:
    ht = f.read()

ht = ht.replace(
    '| H-V3 | VVP pool \ud544\ud130\ub294 RS\uc640 \ub3c5\ub9bd\uc801\uc73c\ub85c \ubbf8\ub798 \uc218\uc775\uc744 \uc608\uce21\ud558\ub294\uac00 | \u2705 \uc870\uac74\ubd80 \u2014 \uac80\uc99d \uc9c4\ud589 \uc911 | RS \ud1b5\uc81c \ud6c4 \uc7ac\ud655\uc778 = VVP \uc5f0\uad6c \ub9c8\uc9c0\ub9c9 \ubcf4\ub8e8. #L1-010 v2 \ubc1c\ud589 (2026-05-04). \uae30\uc874 \uc9c4\uc220 "\ud480 \ud544\ud130 \uc758\ubbf8" \u2192 \uac15\ud654 |',
    '| H-V3 | VVP pool \ud544\ud130\ub294 RS\uc640 \ub3c5\ub9bd\uc801\uc73c\ub85c \ubbf8\ub798 \uc218\uc775\uc744 \uc608\uce21\ud558\ub294\uac00 | \u2705 YES (VVP_50 \ud55c\uc815) | PSM lift 3.99\xd7, \ud68c\uadc0 p<0.001. RS\xb7\uc2dc\ucd1d\xb7\uc139\ud130\xb7\uac70\ub798\ub7c9 \ud1b5\uc81c \ud6c4 VVP_50 \ub3c5\ub9bd \uc608\uce21\ub825 \ud655\uc778. VVP_8 \ub2e8\ub3c5 \ubb34\ud6a8. #L1-010 \uc885\uacb0 (2026-05-06) |'
)

ht = ht.replace(
    '| H-VVD3 | d+5~15 \uc870\uae30 \uc2dd\ubcc4 Forward \uac80\uc99d | \u23f3 \ubbf8\ubc1c\uc8fc | H-V3 \uacb0\uacfc \ud6c4 \ubc29\ud5a5 \uacb0\uc815 |',
    '| H-VVD3 | d+5~15 \uc870\uae30 \uc2dd\ubcc4 Forward \uac80\uc99d | \u23f3 \ubc1c\uc8fc \uac00\ub2a5 | H-V3 \u2705 YES \u2192 H-VVD3 forward \uac80\uc99d \ud6c4\ubcf4 (\uc6b0\uc120\uc21c\uc704 \u2605\u2605) |'
)

ht = ht.replace(
    '**\uac80\uc99d \uc21c\uc11c** (04-29 \ud3c9\uac00 \ud6c4 \uac31\uc2e0): H-V1 \u26a0\ufe0f + H-V2 \ud83d\udd34 \u2192 **H-V3 \uc9c4\ud589 \uc911 (#L1-010, RS \ud1b5\uc81c \uac80\uc99d)** \u2192 \uacb0\uacfc\uc5d0 \ub530\ub77c H-VVD3 / H-V5 \ubd84\uae30 \uacb0\uc815. H-VVD2 \u2705 YES \ubcc4\ub3c4 \ud2b8\ub799 (Cl.2 RS \uac15\ud654\ud615 \ud6c4\uc18d \uac00\uc124 \ud6c4\ubcf4).',
    '**\uac80\uc99d \uc21c\uc11c** (05-06 \uac31\uc2e0): H-V1 \u26a0\ufe0f + H-V2 \ud83d\udd34 \u2192 **H-V3 \u2705 YES (VVP_50 \ud55c\uc815, #L1-010 \uc885\uacb0)** \u2192 H-VVD3 forward \uac80\uc99d (\u2605\u2605) / I-013 (Druck, VVP_50 \ud55c\uc815) \ubc1c\uc8fc \uac00\ub2a5. H-VVD2 \u2705 YES \ubcc4\ub3c4 \ud2b8\ub799.'
)

ht = ht.replace(
    '| **#L1-010 v2** | **H-V3** | **\ud65c\uc131\xb7\uc9c4\ud589 \uc911** (Step 1 \ubc1c\ud589, Step 1.5 \ub300\uae30) | **2026-05-04** |',
    '| **#L1-010 v3** | **H-V3** | **\u2705 \uc885\uacb0** (VVP_50 \ud55c\uc815 YES) | **2026-05-06** |'
)

old_history = '| 2026-05-04 | H-V3 \uc9c4\uc220 \uac15\ud654 ("\ud480 \ud544\ud130 \uc758\ubbf8" \u2192 "RS \uc640 \ub3c5\ub9bd\uc801\uc73c\ub85c \ubbf8\ub798 \uc218\uc775 \uc608\uce21"). #L1-010 v2 \ubc1c\ud589 (RS \ud1b5\uc81c \uac80\uc99d, COO \uad8c\uace0 4\uac74 \ubc18\uc601: HV5 \uc2dc\uc7a5 \uc0ac\uc774\ud074 / \uac00\uc124 \uc9c4\uc220 \uac31\uc2e0 / Cl.2 \ubd84\ub9ac / Step 1.5 6 \uc139\uc158). #Exe-008 v1 \ubc1c\ud589 (VVP \ub9e4\uc218 \uc2e0\ud638 \uccb4\uacb0 \uc2e4\ud328 \uc9c4\ub2e8, \ubcc4\uac74). |'
new_history = old_history + '\n| 2026-05-06 | H-V3 \u2705 YES (VVP_50 \ud55c\uc815) \ud655\uc815. PSM lift 3.99\xd7, p<0.001. #L1-010 v3 \uc885\uacb0. H-VVD3 \ubc1c\uc8fc \uac00\ub2a5 \ub2e8\uacc4 \uc9c4\uc785. Idea Inbox 3\uac74 \ub4f1\uc7ac: H-VVD-Universe (\u2605\u2605\u2605) / H-VVD-RS (\u2605\u2605) / H-VVP-NoVVD (\u2605). |'
ht = ht.replace(old_history, new_history)

with open(r'C:\lab\vsurf_capital\common\hypothesis_tree.md', 'w', encoding='utf-8') as f:
    f.write(ht)
print("hypothesis_tree OK")

# === idea_inbox 3건 등재 ===
with open(r'C:\lab\vsurf_capital\common\idea_inbox.md', encoding='utf-8') as f:
    ib = f.read()

# 목록 테이블에 3건 추가
ib = ib.replace(
    '| I-013 | 1min VVP \uae30\ubc18 \uc790\ub3d9\ub9e4\ub9e4 \ub9e4\uc218 \uc758\ubbf8 \uac80\uc99d (Druck) | \uba54\uc778\ud2b8\ub799 \ud6c4\ubcf4 | H-V3 \uacb0\uacfc \ud6c4 / H-S \uc790\uc2dd \ud6c4\ubcf4 | 2026-05-03 | \uc2e0\uaddc \u2014 H-V3 \uacb0\uacfc \ub300\uae30 |',
    '| I-013 | 1min VVP \uae30\ubc18 \uc790\ub3d9\ub9e4\ub9e4 \ub9e4\uc218 \uc758\ubbf8 \uac80\uc99d (Druck) | \uba54\uc778\ud2b8\ub799 \ud6c4\ubcf4 | H-V3 \uacb0\uacfc \ud6c4 / H-S \uc790\uc2dd \ud6c4\ubcf4 | 2026-05-03 | H-V3 \u2705 \u2192 VVP_50 \ud55c\uc815 \ubc1c\uc8fc \uac00\ub2a5 |\n| I-014 | H-VVD-Universe (\u2605\u2605\u2605) universe A/B/C/D \ube44\uad50 | \uba54\uc778\ud2b8\ub799 \ud6c4\ubcf4 | H-VVD3 \uc790\uc2dd \ud6c4\ubcf4 | 2026-05-06 | \uc2e0\uaddc \u2014 \uc2ec\uc0ac \ub300\uae30 |\n| I-015 | H-VVD-RS (\u2605\u2605) VVD pool RS \ub3c5\ub9bd\uc131 \uac80\uc99d | \uba54\uc778\ud2b8\ub799 \ud6c4\ubcf4 | H-V3 \uc790\uc2dd \ud6c4\ubcf4 | 2026-05-06 | \uc2e0\uaddc \u2014 \uc2ec\uc0ac \ub300\uae30 |\n| I-016 | H-VVP-NoVVD (\u2605) VVD \ubb34\uad00 \uc885\ubaa9\uc5d0\uc11c VVP \uc720\ud6a8\uc131 | \uba54\uc778\ud2b8\ub799 \ud6c4\ubcf4 | H-VVP \uc790\uc2dd \ud6c4\ubcf4 | 2026-05-06 | \uc2e0\uaddc \u2014 \uc2ec\uc0ac \ub300\uae30 |'
)

# I-013 상태 갱신
ib = ib.replace(
    '\uc2e0\uaddc \u2014 H-V3 (#L1-010) \uacb0\uacfc \ub300\uae30. Druck (Exe BU) \ucc98\ub9ac.',
    'H-V3 \u2705 YES \u2192 VVP_50 \ud55c\uc815 \ubc1c\uc8fc \uac00\ub2a5. Druck (Exe BU) \ucc98\ub9ac.'
)

# 갱신 이력
new_entries = '\n| 2026-05-06 | I-013 \uc0c1\ud0dc \uac31\uc2e0 (H-V3 YES \u2192 VVP_50 \ud55c\uc815 \ubc1c\uc8fc \uac00\ub2a5) |\n| 2026-05-06 | I-014 H-VVD-Universe \uc2e0\uaddc \ub4f1\uc7ac (\u2605\u2605\u2605) |\n| 2026-05-06 | I-015 H-VVD-RS \uc2e0\uaddc \ub4f1\uc7ac (\u2605\u2605) |\n| 2026-05-06 | I-016 H-VVP-NoVVD \uc2e0\uaddc \ub4f1\uc7ac (\u2605) |'

ib = ib.replace(
    '| 2026-05-03 | I-013 \ub4f1\uc7ac (1min VVP \uc790\ub3d9\ub9e4\ub9e4 \ub9e4\uc218 \uc758\ubbf8 \uac80\uc99d, Druck \uc601\uc5ed, H-V3 \uacb0\uacfc \ub300\uae30) + I-011 \uc5f0\uacb0 \ucd94\uac00 |',
    '| 2026-05-03 | I-013 \ub4f1\uc7ac (1min VVP \uc790\ub3d9\ub9e4\ub9e4 \ub9e4\uc218 \uc758\ubbf8 \uac80\uc99d, Druck \uc601\uc5ed, H-V3 \uacb0\uacfc \ub300\uae30) + I-011 \uc5f0\uacb0 \ucd94\uac00 |' + new_entries
)

with open(r'C:\lab\vsurf_capital\common\idea_inbox.md', 'w', encoding='utf-8') as f:
    f.write(ib)
print("idea_inbox OK")
