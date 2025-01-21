import distributed.comm.ucx

init_once_original = distributed.comm.ucx.init_once

def init_once_patched():
    print("PATCHED!", flush=True)
    init_once_original()

print("Patching...", flush=True)
distributed.comm.ucx.init_once = init_once_patched
