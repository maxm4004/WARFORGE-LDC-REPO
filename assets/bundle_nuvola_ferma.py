# Variante "nuvola ferma": la nube si forma davanti a chi spara e resta
# lì (niente dissolvenza, niente nuove sbuffate), senza audio.
import sys, copy, UnityPy
src, dst = sys.argv[1], sys.argv[2]
L = 100000.0        # vita delle particelle (s): in pratica per sempre
FORMA = 5.0         # secondi in cui la nube si forma (come l'originale)
env = UnityPy.load(src)
bf = list(env.files.values())[0]
for obj in env.objects:
    t = obj.type.name
    if t == "AudioSource":
        tt = obj.read_typetree()
        tt["m_Enabled"] = 0
        tt["m_PlayOnAwake"] = False
        obj.save_typetree(tt)
    elif t == "AudioClip":
        tt = obj.read_typetree()
        tt["m_PreloadAudioData"] = False
        tt["m_Resource"]["m_Offset"] = 0
        tt["m_Resource"]["m_Size"] = 0       # niente audio nel file
        obj.save_typetree(tt)
    elif t == "ParticleSystem":
        tt = obj.read_typetree()
        vecchia = tt["InitialModule"]["startLifetime"]["scalar"]
        k = vecchia / L
        tt["looping"] = False
        tt["prewarm"] = False
        tt["InitialModule"]["startLifetime"]["scalar"] = L
        tt["InitialModule"]["startLifetime"]["minScalar"] = L
        for b in tt["EmissionModule"]["m_Bursts"]:
            b["time"] = 0.0
        # crescita: stessi secondi di prima
        for key in tt["SizeModule"]["curve"]["maxCurve"]["m_Curve"]:
            if key["time"] > 0: key["time"] = key["time"] * k
        # trasparenza costante (niente dissolvenza)
        g = tt["ColorModule"]["gradient"]
        for nome in ("maxGradient", "minGradient"):
            mg = g.get(nome)
            if mg and mg.get("m_NumAlphaKeys", 0) >= 2:
                a0 = mg["key0"]["a"]
                for i in range(1, mg["m_NumAlphaKeys"]):
                    mg[f"key{i}"]["a"] = a0
        # velocità: si apre per FORMA secondi e poi si ferma
        cv = tt["ClampVelocityModule"]
        mag = cv["magnitude"]
        base = mag["scalar"]
        chiave = copy.deepcopy(tt["SizeModule"]["curve"]["maxCurve"]["m_Curve"][0])
        def kf(tm, v):
            c = copy.deepcopy(chiave); c["time"] = tm; c["value"] = v
            c["inSlope"] = 0.0; c["outSlope"] = 0.0
            return c
        mag["minMaxState"] = 1
        mag["scalar"] = base
        mag["maxCurve"]["m_Curve"] = [kf(0.0, 1.0), kf(FORMA * 0.6 / L, 0.3), kf(FORMA / L, 0.0), kf(1.0, 0.0)]
        obj.save_typetree(tt)
        print("particelle: vita", L, "crescita entro", FORMA, "s, poi ferme")
from UnityPy.streams import EndianBinaryReader
for k in list(bf.files):
    if k.endswith(".resource"):
        r = EndianBinaryReader(b""); r.flags = bf.files[k].flags
        bf.files[k] = r
open(dst, "wb").write(bf.save(packer="lz4"))
print("salvato", dst)
