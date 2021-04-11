from julia import Main
from PIL import Image
import numpy as np
Ju = Main
Ju.using("WordCloud")

Ju.eval("Colors=WordCloud.Colors") 
Ju.eval("torgba(c) = (c=Colors.RGBA{Colors.N0f8}(c); \
    rgba=(Colors.red(c),Colors.green(c),Colors.blue(c),Colors.alpha(c)); \
        reinterpret.(UInt8, rgba))")
Ju.eval("torgba(img::AbstractArray) = torgba.(img)")
Ju.eval('suspendedfuncfactory(fun, args...; kargs...) = (c::Channel)->fun(()->put!(c, "wait"), args...; kargs...)')

def paint(wc, *args, **kargs):
    mat = Ju.torgba(Ju.paint(wc.jwc, *args, **kargs))
    mat = np.array(mat).astype('uint8')
    img = Image.fromarray(mat)
    return img

class SVG:
    def __init__(self, svgstring):
        self.content = svgstring
    def _repr_svg_(self):
        return self.content

def paintsvg(wc, *args, **kargs):
    svg = Ju.paintsvg(wc.jwc, *args, **kargs);
    return SVG(Ju.svgstring(svg))

class WC:
    def __init__(self, wc):
        self.jwc = wc
    def __repr__(self):
        return f"wordcloud({self.jwc.words}) #{len(self.jwc.words)} words"
    def _repr_png_(self):
        return paint(self)._repr_png_()

def wordcloud(*args, **kargs):
    wc = Ju.wordcloud(*args, **kargs)
    return WC(wc)

def wcfuncfactory(name):
    def fun(*args, **kargs):
        pwc, *oths = args
        jwc = Ju.eval(name)(pwc.jwc, *oths, **kargs)
        return pwc
    return fun
def funcfactory(name):
    def fun(*args, **kargs):
        pwc, *oths = args
        r = Ju.eval(name)(pwc.jwc, *oths, **kargs)
        return r
    return fun

def __getattr__(name):
    if name in ["generate", "placement", "rescale","initimages"]:
        return wcfuncfactory(name + "!")
    if name.startswith("get"):
        return funcfactory(name)
    if name.startswith("set"):
        return funcfactory(name + "!")

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

def getcolors(wc, *args, **kargs):
    return Ju.torgba(Ju.getcolors(wc.jwc, *args, **kargs))

class suspendedfun:
    def __init__(self, fun, wc, *args, **kargs):
        self.wc = wc
        self.args = args
        self.kargs = kargs
        self.fun = fun
    def __enter__(self):
        f = Ju.suspendedfuncfactory(self.fun, self.wc.jwc, *self.args, **self.kargs)
        self.taskref = Ju.eval("Ref{Task}()")
        self.chn = Ju.Channel(f, taskref=self.taskref)
        return self.wc
    def __exit__(self, exc_type, exc_val, exc_tb):
        Ju.eval("take!")(self.chn)
        Ju.wait(Ju.getindex(self.taskref))
        assert Ju.istaskdone(Ju.getindex(self.taskref))
        return exc_type is None
    
class keep(suspendedfun):
    def __init__(self, wc, *args, **kargs):
        super().__init__(Ju.keep, wc, *args, **kargs)
class ignore(suspendedfun):
    def __init__(self, wc, *args, **kargs):
        super().__init__(Ju.ignore, wc, *args, **kargs)
class pin(suspendedfun):
    def __init__(self, wc, *args, **kargs):
        super().__init__(Ju.pin, wc, *args, **kargs)