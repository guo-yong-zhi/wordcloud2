from wordcloud2 import wordcloud as W

words, weights = W.processtext(open(W.pkgdir(W.WordCloud)+"/res/alice.txt").read(), 
              stopwords=set(W.stopwords_en).union({"said"}))
wc = W.wordcloud(
    words, weights,
    mask = W.loadmask(W.pkgdir(W.WordCloud)+"/res/alice_mask.png", color="#faeef8"),
    colors = ":Set1_5",
    angles = (0, 90),
    density = 0.55).generate()
new_background = W.outline(wc.getmask(), color="purple", linewidth=1)
wc.paint("alice.png", ratio=0.5, background=new_background)
#md# ![alice](alice.png)  