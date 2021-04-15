#md# Big words will be placed closer to the center
from wordcloud2 import wordcloud as W

wc = W.wordcloud(
    W.processtext(open(W.pkgdir(W.WordCloud)+"/res/alice.txt").read(), 
              stopwords=set(W.stopwords_en).union({"said"})),
    angles = 0,
    density = 0.6,
    run = W.Ju.initimages_b)
wc.placement(style=W.Symbol("gathering"), level=5)
wc.generate(patient=-1)
print("results are saved to gathering.svg")
wc.paint("gathering.svg")
wc
#eval# runexample(:gathering)
#md# ![](gathering.svg)