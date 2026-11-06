"""EAN-13 (the barcode printed on the back of every modern book, carrying its ISBN-13)
drawn as an SVG image. No extra library needed."""

_L = ["0001101", "0011001", "0010011", "0111101", "0100011",
      "0110001", "0101111", "0111011", "0110111", "0001011"]
_R = ["".join("1" if b == "0" else "0" for b in c) for c in _L]   # right-hand digits
_G = [c[::-1] for c in _R]                                           # left-hand "even" digits
_PARITY = ["LLLLLL", "LLGLGG", "LLGGLG", "LLGGGL", "LGLLGG",
           "LGGLLG", "LGGGLL", "LGLGLG", "LGLGGL", "LGGLGL"]


def ean13_bits(code):
    if len(code) != 13 or not code.isdigit():
        raise ValueError("EAN-13 needs exactly 13 digits")
    pattern = _PARITY[int(code[0])]
    bits = "101"
    for i, d in enumerate(code[1:7]):
        bits += (_L if pattern[i] == "L" else _G)[int(d)]
    bits += "01010"
    for d in code[7:]:
        bits += _R[int(d)]
    return bits + "101"


def ean13_svg(code, bar_height=60, label=True):
    """Returns an SVG string. Quiet zones (white margins) are included, which scanners need."""
    bits = ean13_bits(code)
    quiet_l, quiet_r = 11, 9
    width = quiet_l + 95 + quiet_r
    text_h = 12 if label else 2
    height = bar_height + text_h
    guard = {*range(0, 3), *range(45, 50), *range(92, 95)}      # start, centre and end bars run longer
    rects, i = [], 0
    while i < 95:
        if bits[i] == "1":
            j = i
            while j < 95 and bits[j] == "1":
                j += 1
            h = bar_height if any(k in guard for k in range(i, j)) else bar_height - 6
            rects.append(f'<rect x="{quiet_l + i}" y="0" width="{j - i}" height="{h}"/>')
            i = j
        else:
            i += 1
    text = ""
    if label:
        y = bar_height + 8
        text = (f'<text x="{quiet_l - 4}" y="{y}" text-anchor="end">{code[0]}</text>'
                f'<text x="{quiet_l + 3 + 21}" y="{y}" text-anchor="middle" textLength="39">{code[1:7]}</text>'
                f'<text x="{quiet_l + 50 + 21}" y="{y}" text-anchor="middle" textLength="39">{code[7:]}</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" '
            f'aria-label="Barcode for ISBN {code}" style="width:100%;height:auto;display:block">'
            f'<rect width="{width}" height="{height}" fill="#fff"/>'
            f'<g fill="#000">{"".join(rects)}</g>'
            f'<g fill="#000" font-family="Arial,Helvetica,sans-serif" font-size="9">{text}</g></svg>')
