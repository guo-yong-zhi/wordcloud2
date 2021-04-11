from julia import Main
from PIL import Image
import numpy as np

Main.using("WordCloud")

Main.eval("Colors=WordCloud.Colors") 
Main.eval("torgba(img) = (c->(reinterpret(UInt8, Colors.red(c)), \
    reinterpret(UInt8, Colors.green(c)), \
        reinterpret(UInt8, Colors.blue(c)), \
            reinterpret(UInt8, Colors.alpha(c)))).(Colors.RGBA{Colors.N0f8}.(img))")

wc = Main.wordcloud(["1"], [1]);

def paint(wc, *args, **kargs):
    mat = Main.torgba(Main.paint(wc.WC, *args, **kargs))
    mat = np.array(mat).astype('uint8')
    img = Image.fromarray(mat)
    return img

class SVG:
    def __init__(self, svgstring):
        self.content = svgstring
    def _repr_svg_(self):
        return self.content

def paintsvg(wc, *args, **kargs):
    svg = Main.paintsvg(wc.WC, *args, **kargs);
    return SVG(Main.svgstring(svg))

class WC:
    def __init__(self, wc):
        self.WC = wc
    def __repr__(self):
        return f"wordcloud({self.WC.words}) #{len(self.WC.words)} words"
    def _repr_png_(self):
        return paint(self)._repr_png_()

def wordcloud(*args, **kargs):
    wc = Main.wordcloud(*args, **kargs)
    return WC(wc)