from PIL import Image

W, H = 350, 420
bg = Image.new("RGBA", (W, H), (255, 255, 255, 255))

ghost = Image.open("monstera.png").convert("RGBA")

# Each ghost: (scale, opacity, x_center_fraction, y_center_fraction)
# Smaller + more transparent = farther away (top), larger + more opaque = closer (bottom)
ghosts = [
    # Far away / top
    (0.10, 40,  0.15, 0.08),
    (0.08, 30,  0.75, 0.05),
    (0.12, 50,  0.50, 0.12),
    (0.09, 35,  0.88, 0.18),
    # Mid distance
    (0.18, 70,  0.20, 0.30),
    (0.15, 60,  0.65, 0.38),
    (0.20, 75,  0.82, 0.50),
    (0.16, 65,  0.35, 0.55),
    # Close / bottom
    (0.28, 110, 0.10, 0.72),
    # (0.32, 120, 0.70, 0.78),
    # (0.25, 100, 0.45, 0.88),
    (0.38, 140, 0.88, 0.95),
]

for scale, opacity, fx, fy in ghosts:
    new_w = max(1, int(ghost.width * scale))
    new_h = max(1, int(ghost.height * scale))
    g = ghost.resize((new_w, new_h), Image.LANCZOS)

    r, gr, b, a = g.split()
    a = a.point(lambda p: int(p * opacity / 255))
    g = Image.merge("RGBA", (r, gr, b, a))

    x = int(fx * W - new_w / 2)
    y = int(fy * H - new_h / 2)

    bg.paste(g, (x, y), g)

bg = bg.convert("RGB")
bg.save("bg.png")
print("Saved bg.png")