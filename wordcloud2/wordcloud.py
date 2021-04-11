from julia import Main
from PIL import Image
import numpy as np

Main.using("WordCloud")

Main.eval("Colors=WordCloud.Colors") 
Main.eval("torgba(c) = (c=Colors.RGBA{Colors.N0f8}(c); \
    rgba=(Colors.red(c),Colors.green(c),Colors.blue(c),Colors.alpha(c)); \
        reinterpret.(UInt8, rgba))")
Main.eval("torgba(img::AbstractMatrix) = torgba.(img)")
Main.eval('suspendedfuncfactory(fun, args...; kargs...) = (c::Channel)->fun(()->put!(c, "wait"), args...; kargs...)')
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

def wcfuncfactory(name):
    def fun(*args, **kargs):
        pwc, *oths = args
        jwc = Main.eval(name)(pwc.WC, *oths, **kargs)
        return pwc
    return fun
def funcfactory(name):
    def fun(*args, **kargs):
        pwc, *oths = args
        r = Main.eval(name)(pwc.WC, *oths, **kargs)
        return r
    return fun

def __getattr__(name):
    if name == "getcolor":
        return
    if name in ["generate", "placement", "rescale","initimages"]:
        return wcfuncfactory(name + "!")
    if name.startswith("get"):
        return funcfactory(name)
    if name.startswith("set"):
        return funcfactory(name + "!")

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
    
class suspendedfun:
    def __init__(self, fun, wc, *args, **kargs):
        self.wc = wc
        self.args = args
        self.kargs = kargs
        self.fun = fun
    def __enter__(self):
        f = Main.suspendedfuncfactory(self.fun, self.wc.WC, *self.args, **self.kargs)
        self.taskref = Main.eval("Ref{Task}()")
        self.chn = Main.Channel(f, taskref=self.taskref)
        return self.wc
    def __exit__(self, exc_type, exc_val, exc_tb):
        Main.eval("take!")(self.chn)
        Main.wait(Main.getindex(self.taskref))
        assert Main.istaskdone(Main.getindex(self.taskref))
        return exc_type is None
    
class keep(suspendedfun):
    def __init__(self, wc, *args, **kargs):
        super().__init__(Main.keep, wc, *args, **kargs)
class ignore(suspendedfun):
    def __init__(self, wc, *args, **kargs):
        super().__init__(Main.ignore, wc, *args, **kargs)
class pin(suspendedfun):
    def __init__(self, wc, *args, **kargs):
        super().__init__(Main.pin, wc, *args, **kargs)