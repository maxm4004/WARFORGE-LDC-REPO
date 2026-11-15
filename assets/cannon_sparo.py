# Bundle del cannone di TTS -> solo lo sparo (fumo, vampa, boato)
# Spegne i renderer e il collider del cannone, rimpicciolisce le sue texture.
import UnityPy, sys
from PIL import Image
src, dst = sys.argv[1], sys.argv[2]
env = UnityPy.load(src)
byid = {o.path_id: o for o in env.objects}
def goname(tt):
    return byid[tt['m_GameObject']['m_PathID']].read_typetree()['m_Name']
for o in env.objects:
    t = o.type.name
    if t in ("MeshRenderer", "SkinnedMeshRenderer", "MeshCollider"):
        tt = o.read_typetree()
        print("spengo", t, goname(tt))
        tt['m_Enabled'] = 0
        o.save_typetree(tt)
    elif t == "ParticleSystem":
        # Hierarchy: le particelle seguono la scala dell'oggetto in TTS
        tt = o.read_typetree()
        print("particelle", goname(tt), "scalingMode", tt['scalingMode'], "-> 0")
        tt['scalingMode'] = 0
        o.save_typetree(tt)
    elif t == "MonoBehaviour":
        # suono dello sparo 2D: si sente ovunque sia la camera (Max
        # 15/11: col 3D, da lontano o sul vassoio dei dadi, non si sentiva)
        tt = o.read_typetree()
        if "TriggerEffects" in tt:
            for e in tt["TriggerEffects"]:
                print("trigger", e["Name"], "Positional3D", e["Sound"]["Positional3D"], "-> 0")
                e["Sound"]["Positional3D"] = 0
            o.save_typetree(tt)
    elif t == "Texture2D":
        d = o.read()
        if d.m_Name.startswith("DiceRoller_Cannon"):
            print("texture", d.m_Name, d.m_Width, d.m_Height, "-> 4x4")
            d.image = Image.new("RGBA", (4, 4), (0, 0, 0, 0))
            d.save()
open(dst, "wb").write(env.file.save(packer="lz4"))
