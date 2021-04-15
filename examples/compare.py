from wordcloud2 import wordcloud as W

import os
from PIL import Image

stwords = {"us", "will"}
print("==Obama's==")
cs = W.randomscheme() #:Set1_8
as_ = W.randomangles() #(0,90,45,-45)
dens = 0.5 #not too high
wca = W.wordcloud(
    W.processtext(open(W.pkgdir(W.WordCloud)+"/res/Barack Obama's First Inaugural Address.txt").read(), 
                stopwords=set(W.stopwords_en).union(stwords)), 
    colors = cs,
    angles = as_,
    density = dens)
wca.generate()
#md# ### Then generate the wordcloud on the right      
print("==Trump's==")
wcb = W.wordcloud(
    W.processtext(open(W.pkgdir(W.WordCloud)+"/res/Donald Trump's Inaugural Address.txt").read(), 
                  stopwords=set(W.stopwords_en).union(stwords)),
    mask = wca.getsvgmask(),
    colors = cs,
    angles = as_,
    density = dens,
    run = W.identity, #turn off the useless initimage! and placement! in advance
)
#md# Follow these steps to generate a wordcloud: initimage! -> placement! -> generate!
samewords = list(set(wca.getwords()).intersection(wcb.getwords()))
print(len(samewords), "same words")

for w in samewords:
    wcb.setcolors(w, wca.getcolors(w))
    wcb.setangles(w, wca.getangles(w))
wcb.initimages()
wcb.setstate(":placement!")

print("=ignore defferent words=")
with wcb.keep(samewords) as wcb:
    assert set(wcb.getwords()) == set(samewords)
    centers = wca.getpositions(samewords, type=W.Ju.getcenter)
    wcb.setpositions(samewords, centers, type=W.Ju.setcenter_b) #manually initialize the position,
    wcb.setstate(":placement!") #and set the state flag
    wcb.generate(1000, patient=-1, retry=1) #patient=-1 means no teleport; retry=1 means no rescale

print("=pin same words=")
with wcb.pin(samewords):
    wcb.placement()
    wcb.generate(1000, retry=1) #allow teleport but don‘t allow rescale

if wcb.getstate() != ":generate!":
    print("=overall tuning=")
    wcb.generate(1000, patient=-1, retry=2) #allow rescale but don‘t allow teleport

ma = wca.paint()
mb = wcb.paint()
sp = ma.width//20
cmp = Image.new('RGBA', (ma.width*2+sp, ma.height))
cmp.paste(ma, (0, 0, ma.width, ma.height))
cmp.paste(mb, (ma.width+sp, 0, ma.width*2+sp, ma.height))
os.makedirs('address_compare', exist_ok=True)
print("results are saved in address_compare")
cmp.save("address_compare/compare.png")
gif = W.GIF("address_compare")
wca.record("Obama", gif)
wcb.record("Trump", gif)
W.gif_generate(gif, framerate=1)
#md# ![](address_compare/compare.png)  
#md# ![](address_compare/result.gif)  