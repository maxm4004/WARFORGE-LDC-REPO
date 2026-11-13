import sys, UnityPy, collections
env = UnityPy.load(sys.argv[1])
for f in env.files.values():
    print("file", type(f).__name__, getattr(f, 'version', ''), getattr(f,'name',''))
    for k, sub in getattr(f, 'files', {}).items():
        print("  sub", k, type(sub).__name__, getattr(sub,'unity_version',''))
tot = collections.Counter(); cnt = collections.Counter()
rows=[]
for obj in env.objects:
    t = obj.type.name
    size = obj.byte_size
    name = ""
    try:
        d = obj.read()
        name = getattr(d, 'm_Name', '') or getattr(d,'name','')
        extra=""
        if t == "Texture2D":
            extra = f"{d.m_Width}x{d.m_Height} fmt={d.m_TextureFormat} mips={getattr(d,'m_MipCount','?')}"
            # stream data
            sd = getattr(d,'m_StreamData',None)
            if sd and sd.size: extra += f" stream={sd.size}"
        if t == "AudioClip":
            extra = f"fmt={getattr(d,'m_CompressionFormat','?')} ch={getattr(d,'m_Channels','?')} freq={getattr(d,'m_Frequency','?')} len={getattr(d,'m_Length','?')} res={getattr(d,'m_Resource',None) and d.m_Resource.m_Size}"
        if t == "Mesh":
            extra = f"verts={getattr(d,'m_VertexData',None) and d.m_VertexData.m_VertexCount}"
    except Exception as e:
        extra = "ERR " + str(e)[:60]
    tot[t] += size; cnt[t] += 1
    rows.append((size, t, name, extra))
print()
for t, s in tot.most_common(): print(f"{t:20s} n={cnt[t]:3d} {s:9d} bytes")
print()
for r in sorted(rows, reverse=True)[:25]: print(r)
