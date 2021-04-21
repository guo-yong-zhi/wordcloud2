from wordcloud2 import wordcloud as W
import string
import random

background = W.loadmask(W.pkgdir(W.WordCloud)+"/res/butterfly.png")
istrans = lambda c:max(c[:3])*(c[3]/255)<128
mask = W.backgroundmask(background, istrans)
W.showmask(background, mask)
#md# `showmask` might be helpful to find a proper `istrans` function
samples = string.ascii_uppercase.lower()+string.ascii_uppercase+string.digits
words = [random.choice(samples) for _ in range(600)]
weights = [random.expovariate(1) + 1 for _ in range(600)]

wc = W.wordcloud(
    words, weights,
    mask = background,
    colors = "LimeGreen",
    angles = -30,
    density = 0.45,
    transparentcolor = istrans,
    border = 1,
).generate()
#md# ## average style
wc.recolor(style="average")
avgimg = wc.paint("average.png", background=False)
#md# ## clipping style
wc.recolor(style="clipping")
clipimg = wc.paint("clipping.png", background=False)
#md# ## blending style
wc.recolor(style="reset")
wc.recolor(style="blending")
blendimg = wc.paint("blending.png", background=False)
#md# ## mix style
#md# styles can also be mixed
# setcolors!(wc, :, "LimeGreen")
wc.recolor(style="reset")
wc.recolor(range(1,len(words)+1,3), style="average") #vector index is ok
wc.recolor(range(2,len(words)+1,3), style="clipping")
wc.recolor(range(3,len(words)+1,3), style="blending")
wc.setcolors(range(200,251), "black")
wc.recolor(range(200,251), style="reset")
wc.setcolors(1, "black")
wc.recolor(1, style="reset") #single index is ok
mixstyleimg = wc.paint("mixstyle.png", background=False)