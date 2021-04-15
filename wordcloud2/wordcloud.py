import sys
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
Ju.eval('suspendedfuncfactory(fun, args...; kargs...) = (c::Channel)->fun(()->(put!(c,"waiting");take!(c)), args...; kargs...)')
this = sys.modules[__name__]

Symbol = lambda s: Ju.eval("PyCall.pyjlwrap_new(:%s)"%s.lstrip(":"))
def torgba(*args, **kargs):
    return Ju.torgba(*args, **kargs)

def paint(wc, *args, **kargs):
    if args and isinstance(args[0], str) and args[0].lower().endswith(".svg"):
        return paintsvg(wc, *args, **kargs)
    mat = torgba(Ju.paint(wc.jwc, *args, **kargs))
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
    def __getattr__(self, name):
        try:
            if hasattr(this, name):
                return lambda *args,**kargs:getattr(this, name)(self, *args,**kargs)
            else:
                jf = Ju.eval("WordCloud.%s"%name)
                return lambda *args,**kargs:jf(self, *args,**kargs)
        except:
            raise AttributeError(r"'WC' object has no attribute '%s'"%name)

def wordcloud(*args, **kargs):
    if "colors" in kargs and isinstance(kargs["colors"],str) and kargs["colors"].startswith(":"):
        kargs["colors"] = Symbol(kargs["colors"])
    wc = Ju.wordcloud(*args, **kargs)
    return WC(wc)

# def getcolors(wc, *args, **kargs):
#     return torgba(Ju.getcolors(wc.jwc, *args, **kargs))
def setstate(wc, state):
    Ju.setstate_b(wc.jwc, Symbol(state))
    return state
def gif_generate(*args, **kargs):
    return Ju.eval("WordCloud.generate")(*args, **kargs)

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
        Ju.take_b(self.chn)
        return self.wc
    def __exit__(self, exc_type, exc_val, exc_tb):
        Ju.put_b(self.chn, "go")
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

def wcfuncfactorywc(name):
    def fun(*args, **kargs):
        pwc, *oths = args
        jwc = Ju.eval(name)(pwc.jwc, *oths, **kargs)
        return pwc
    return fun
def wcfuncfactory(name):
    def fun(*args, **kargs):
        pwc, *oths = args
        r = Ju.eval(name)(pwc.jwc, *oths, **kargs)
        return r
    return fun
def funcfactory(name):
    return lambda *args,**kargs:Ju.eval(name)(*args, **kargs)

for pyfun in ["generate", "generate_animation", "placement", "rescale", "initimages", "record"]:
    setattr(this, pyfun, wcfuncfactorywc(pyfun + "!"))
for pyfun in ["record"]:
    setattr(this, pyfun, wcfuncfactorywc(pyfun))
for fun in set(Ju.eval("names(WordCloud)")) - {'WordCloud'}:
    pyfun = fun.rstrip("!")
    if not hasattr(this, pyfun):
        if (pyfun.startswith("get") or pyfun.startswith("set")) and "shift" not in pyfun:
            setattr(this, pyfun, wcfuncfactory(fun))
        else:
            setattr(this, pyfun, funcfactory(fun))

def __getattr__(name):
    try:
        return Ju.eval("WordCloud.%s"%name)
    except:
        pass
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
