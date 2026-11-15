# Sparo dal bundle ORIGINALE del cannone di TTS, in una sola lettura e
# un solo salvataggio (Max 15/11: rilavorare un bundle gia' salvato da
# UnityPy ne rompe l'importazione in TTS).
#   tipo = cannone | moschetto | muto
import UnityPy, sys
from PIL import Image
from UnityPy.streams import EndianBinaryReader
src, dst, tipo = sys.argv[1], sys.argv[2], sys.argv[3]
suono = sys.argv[4] if len(sys.argv) > 4 else None
env = UnityPy.load(src)
byid = {o.path_id: o for o in env.objects}
def goname(tt):
    return byid[tt['m_GameObject']['m_PathID']].read_typetree()['m_Name']
clip = data = None
if tipo == "moschetto":
    es = UnityPy.load(suono)
    for o in es.objects:
        if o.type.name == "AudioClip" and o.read_typetree()["m_Name"] == "VolleyFire5s":
            clip = o.read_typetree()
    r = clip["m_Resource"]
    data = bytes(es.file.files[r["m_Source"].split("/")[-1]].bytes)[r["m_Offset"]:r["m_Offset"] + r["m_Size"]]
for o in env.objects:
    t = o.type.name
    if t in ("MeshRenderer", "SkinnedMeshRenderer", "MeshCollider"):
        tt = o.read_typetree(); tt['m_Enabled'] = 0; o.save_typetree(tt)
    elif t == "ParticleSystem":
        tt = o.read_typetree(); tt['scalingMode'] = 0; o.save_typetree(tt)
    elif t == "MonoBehaviour":
        tt = o.read_typetree()
        if "TriggerEffects" in tt:
            for e in tt["TriggerEffects"]:
                e["Sound"]["Positional3D"] = 0
                if tipo == "muto": e["Sound"]["Audio"]["m_PathID"] = 0
            o.save_typetree(tt)
    elif t == "Texture2D":
        d = o.read()
        if d.m_Name.startswith("DiceRoller_Cannon"):
            d.image = Image.new("RGBA", (4, 4), (0, 0, 0, 0)); d.save()
    elif t == "AudioClip" and tipo == "moschetto":
        tt = o.read_typetree()
        rname = tt["m_Resource"]["m_Source"].split("/")[-1]
        vecchio = env.file.files[rname]
        nuovo = EndianBinaryReader(data)
        for a in ("flags", "name"):
            if hasattr(vecchio, a): setattr(nuovo, a, getattr(vecchio, a))
        env.file.files[rname] = nuovo
        for k in ("m_Channels", "m_Frequency", "m_BitsPerSample", "m_Length", "m_CompressionFormat", "m_LoadType"):
            tt[k] = clip[k]
        tt["m_Resource"]["m_Offset"] = 0
        tt["m_Resource"]["m_Size"] = len(data)
        o.save_typetree(tt)
open(dst, "wb").write(env.file.save(packer="lz4"))
print(tipo, "ok")
