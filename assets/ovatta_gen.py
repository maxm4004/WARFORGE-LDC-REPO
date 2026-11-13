import math, random
random.seed(7)
# fiocco di ovatta: grappolo di sfere schiacciate e "bitorzolute"
# unità TTS, base sul piano y=0, centro in (0,0). Fronte lungo X.
lumps = [  # cx, cz, rx, ry, rz
    (-0.85, 0.05, 0.55, 0.42, 0.50),
    (-0.30, -0.10, 0.62, 0.55, 0.55),
    ( 0.30, 0.08, 0.65, 0.60, 0.58),
    ( 0.88, -0.05, 0.52, 0.45, 0.48),
    (-0.05, 0.30, 0.50, 0.40, 0.42),
    ( 0.10, -0.32, 0.48, 0.38, 0.40),
    (-0.55, 0.00, 0.40, 0.70, 0.40),
    ( 0.55, 0.00, 0.38, 0.62, 0.38),
]
NU, NV = 14, 9
V, N, F = [], [], []
for (cx, cz, rx, ry, rz) in lumps:
    base = len(V)
    seed = random.random() * 10
    for j in range(NV + 1):
        th = math.pi * j / NV            # 0 = cima, pi = fondo
        for i in range(NU):
            ph = 2 * math.pi * i / NU
            nx, ny, nz = math.sin(th) * math.cos(ph), math.cos(th), math.sin(th) * math.sin(ph)
            bump = 1 + 0.10 * math.sin(3 * ph + seed) * math.sin(2 * th + seed) + 0.06 * math.sin(5 * ph + 2 * th + seed)
            x, y, z = cx + nx * rx * bump, ry * 0.85 + ny * ry * bump, cz + nz * rz * bump
            y = max(y, 0.0)              # piatto sotto, appoggiato al tavolo
            V.append((x, y, z)); N.append((nx, ny, nz))
    for j in range(NV):
        for i in range(NU):
            a = base + j * NU + i
            b = base + j * NU + (i + 1) % NU
            c = base + (j + 1) * NU + (i + 1) % NU
            d = base + (j + 1) * NU + i
            F.append((a, b, c)); F.append((a, c, d))
with open("ovatta.obj", "w") as f:
    f.write("# WARFORGE LDC - fumo del tiro come ovatta (fiocco statico)\n")
    for v in V: f.write("v %.4f %.4f %.4f\n" % v)
    for n in N: f.write("vn %.4f %.4f %.4f\n" % n)
    for (a, b, c) in F:
        f.write("f %d//%d %d//%d %d//%d\n" % (a + 1, a + 1, b + 1, b + 1, c + 1, c + 1))
xs=[v[0] for v in V]; ys=[v[1] for v in V]; zs=[v[2] for v in V]
print(len(V), "vertici", len(F), "triangoli", "X %.2f..%.2f Y %.2f..%.2f Z %.2f..%.2f" % (min(xs),max(xs),min(ys),max(ys),min(zs),max(zs)))
