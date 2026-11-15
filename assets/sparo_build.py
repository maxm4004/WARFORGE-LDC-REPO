# Sparo dal bundle ORIGINALE del cannone di TTS, in una sola lettura e
# un solo salvataggio per oggetto (rileggere un typetree gia' salvato
# perde le modifiche).
#   tipo = cannone | moschetto | muto
# Ogni bundle ha nome e CAB suoi: Unity non carica due bundle con lo
# stesso nome interno (Max 15/11: i moschetti accanto allo sparo del
# cannone davano la scheda di importazione).
import UnityPy, sys, hashlib
from PIL import Image
from UnityPy.streams import EndianBinaryReader
src, dst, tipo = sys.argv[1], sys.argv[2], sys.argv[3]
suono = sys.argv[4] if len(sys.argv) > 4 else None
NOMI = {"cannone": None, "moschetto": "ldc_musket_sparo", "muto": "ldc_musket_sparo_muto"}
nuovo_nome = NOMI[tipo]
env = UnityPy.load(src)
vecchio_cab = [k for k in env.file.files if not k.endswith((".resource", ".resS"))][0]
nuovo_cab = ("CAB-" + hashlib.md5(nuovo_nome.encode()).hexdigest()) if nuovo_nome else vecchio_cab
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
    elif t == "AssetBundle" and nuovo_nome:
        tt = o.read_typetree()
        tt["m_Name"] = tt["m_AssetBundleName"] = nuovo_nome
        o.save_typetree(tt)
    elif t == "AudioClip":
        tt = o.read_typetree()
        if tipo == "moschetto":
            for k in ("m_Channels", "m_Frequency", "m_BitsPerSample", "m_Length", "m_CompressionFormat", "m_LoadType"):
                tt[k] = clip[k]
            tt["m_Resource"]["m_Offset"] = 0
            tt["m_Resource"]["m_Size"] = len(data)
            tt["m_Name"] = "VolleyFire5s"
        tt["m_Resource"]["m_Source"] = tt["m_Resource"]["m_Source"].replace(vecchio_cab, nuovo_cab)
        o.save_typetree(tt)
files = env.file.files
nuovi = {}
for k, v in files.items():
    nk = k.replace(vecchio_cab, nuovo_cab)
    if k.endswith(".resource") and data is not None:
        nv = EndianBinaryReader(data)
        for a in ("flags", "name"):
            if hasattr(v, a): setattr(nv, a, getattr(v, a))
        v = nv
    if hasattr(v, "name"):
        try: v.name = nk
        except Exception: pass
    nuovi[nk] = v
files.clear(); files.update(nuovi)
open(dst, "wb").write(env.file.save(packer="lz4"))
print(tipo, nuovo_nome or "(nome originale)", nuovo_cab)
