import sys, UnityPy
from UnityPy.enums import TextureFormat
from UnityPy.streams import EndianBinaryReader
src, dst, tex_max = sys.argv[1], sys.argv[2], int(sys.argv[3])
# nuvola: fattore sulla grandezza delle particelle e sul loro numero
k_size = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
k_num  = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0
env = UnityPy.load(src)
bf = list(env.files.values())[0]
cab = [k for k in bf.files if not k.endswith(('.resS', '.resource'))][0]
# 1) texture ridotte e messe dentro il file (non più in .resS)
for obj in env.objects:
    if obj.type.name == "Texture2D":
        d = obj.read()
        img = d.image
        lato = 64 if d.m_Name == "BlackMask" else tex_max
        if img.width > lato:
            img = img.resize((lato, lato))
        d.set_image(img, target_format=d.m_TextureFormat, mipmap_count=1)
        d.save()
        print("texture", d.m_Name, d.m_Width, d.m_Height, TextureFormat(d.m_TextureFormat).name)
# 1b) nuvola più grande: particelle più grandi e un po' più numerose
for obj in env.objects:
    if obj.type.name == "ParticleSystem" and (k_size != 1 or k_num != 1):
        tt = obj.read_typetree()
        ss = tt["InitialModule"]["startSize"]
        ss["scalar"] *= k_size
        ss["minScalar"] *= k_size
        for b in tt["EmissionModule"]["m_Bursts"]:
            b["countCurve"]["scalar"] = float(round(b["countCurve"]["scalar"] * k_num))
            b["countCurve"]["minScalar"] = float(round(b["countCurve"].get("minScalar", 0) * k_num))
        obj.save_typetree(tt)
        print("particelle", ss["minScalar"], ss["scalar"], [b["countCurve"]["scalar"] for b in tt["EmissionModule"]["m_Bursts"]])
# 2) audio: le tre varianti usano la prima (il .resource tiene solo quella)
# si tiene il suono più leggero
primo = None
for obj in env.objects:
    if obj.type.name == "AudioClip":
        r = obj.read_typetree()["m_Resource"]
        if primo is None or r["m_Size"] < primo["m_Size"]:
            primo = dict(r)
for obj in env.objects:
    if obj.type.name == "AudioClip":
        tt = obj.read_typetree()
        print("clip", tt["m_Name"], tt["m_Resource"]["m_Offset"], tt["m_Resource"]["m_Size"], "->", 0, primo["m_Size"])
        tt["m_Resource"]["m_Offset"] = 0     # il .resource nuovo contiene solo quel suono
        tt["m_Resource"]["m_Size"] = primo["m_Size"]
        tt["m_PreloadAudioData"] = True      # suono pronto al caricamento del bundle
        obj.save_typetree(tt)
    if obj.type.name == "AudioSource":
        tt = obj.read_typetree()
        tt["Loop"] = False           # una volta sola, non in continuo
        obj.save_typetree(tt)
res_key = cab + ".resource"
old = bf.files[res_key]
raw = bytes(old.bytes) if hasattr(old, "bytes") else old.read_bytes(old.Length)
r = EndianBinaryReader(raw[primo["m_Offset"]:primo["m_Offset"] + primo["m_Size"]]); r.flags = old.flags
bf.files[res_key] = r
# 3) .resS vuoto: le texture ora stanno nel file
r = EndianBinaryReader(b""); r.flags = bf.files[cab + ".resS"].flags
bf.files[cab + ".resS"] = r
bf.mark_changed() if hasattr(bf, "mark_changed") else None
for f in bf.files.values():
    if hasattr(f, "mark_changed"): pass
open(dst, "wb").write(bf.save(packer="lz4"))
print("salvato", dst)
