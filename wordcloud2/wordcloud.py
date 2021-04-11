from julia import Main
from PIL import Image
import numpy as np

Main.using("WordCloud")

Main.eval("Colors=WordCloud.Colors") 
Main.eval("torgba(img) = (c->(reinterpret(UInt8, Colors.red(c)), \
    reinterpret(UInt8, Colors.green(c)), \
        reinterpret(UInt8, Colors.blue(c)), \
            reinterpret(UInt8, Colors.alpha(c)))).\
                (Colors.RGBA{Colors.N0f8}.(img))")

wc = Main.wordcloud(["1"], [1]);
mat = Main.torgba(Main.paint(wc))
mat = np.array(mat).astype('uint8')
img = Image.fromarray(mat)

class SVG:
    def __init__(self, svgstring):
        self.content = svgstring
    def _repr_svg_(self):
        return self.content
        
svg = Main.paintsvg(wc);
SVG(Main.svgstring(svg))