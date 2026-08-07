import shutil, os
pairs = [
    ('C:/mnt/user-data/outputs/COO_entry_wrapper_v8.1.md', 'C:/lab/vsurf_capital/common/COO_entry_wrapper_v8.1.md'),
    ('C:/mnt/user-data/outputs/GM_entry_wrapper_Howard_v4.1.md', 'C:/lab/vsurf_capital/common/GM_entry_wrapper_Howard_v4.1.md'),
    ('C:/mnt/user-data/outputs/GM_entry_wrapper_Druck_v4.1.md', 'C:/lab/vsurf_capital/common/GM_entry_wrapper_Druck_v4.1.md'),
    ('C:/mnt/user-data/outputs/GM_entry_wrapper_Ellis_v4.1.md', 'C:/lab/vsurf_capital/common/GM_entry_wrapper_Ellis_v4.1.md'),
]
for src, dst in pairs:
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print('OK', dst)
    else:
        print('NOT FOUND', src)
