# Sparo dei moschetti dal bundle del cannone (cannon_sparo): stesso
# fumo e vampa, suono della salva di fucileria (VolleyFire5s di
# musket_suono). muto = senza suono (per le basi dopo la prima).
import UnityPy, sys
from UnityPy.streams import EndianBinaryReader
src, suono, dst, muto = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] == "muto"
env = UnityPy.load(src)
if not muto:
    es = UnityPy.load(suono)
    clip = None
    for o in es.objects:
        if o.type.name == "AudioClip" and o.read_typetree()["m_Name"] == "VolleyFire5s":
            clip = o.read_typetree()
    res = clip["m_Resource"]
    rname = res["m_Source"].split("/")[-1]
    data = bytes(es.file.files[rname].bytes)[res["m_Offset"]:res["m_Offset"] + res["m_Size"]]
    print("salva", len(data), "byte")
for o in env.objects:
    if o.type.name == "AudioClip":
        tt = o.read_typetree()
        if not muto:
            rname = tt["m_Resource"]["m_Source"].split("/")[-1]
            vecchio = env.file.files[rname]
            nuovo = EndianBinaryReader(data)
            for attr in ("flags", "name"):
                if hasattr(vecchio, attr): setattr(nuovo, attr, getattr(vecchio, attr))
            env.file.files[rname] = nuovo
            for k in ("m_Channels", "m_Frequency", "m_BitsPerSample", "m_Length", "m_CompressionFormat", "m_LoadType"):
                tt[k] = clip[k]
            tt["m_Resource"]["m_Offset"] = 0
            tt["m_Resource"]["m_Size"] = len(data)
            tt["m_Name"] = "VolleyFire5s"
            o.save_typetree(tt)
    if o.type.name == "MonoBehaviour":
        tt = o.read_typetree()
        if "TriggerEffects" in tt and muto:
            for e in tt["TriggerEffects"]:
                e["Sound"]["Audio"]["m_PathID"] = 0
            o.save_typetree(tt)
open(dst, "wb").write(env.file.save(packer="lz4"))
