from wordcloud2 import wordcloud as W

import csv
with open(W.pkgdir(W.WordCloud)+"/res/guxiang_frequency.txt", encoding='utf-8') as f:
    df = list(csv.reader(f, delimiter="\t"))
words = [i[1] for i in df]
weights = [int(i[2]) for i in df]
wc = W.wordcloud(words, weights, density=0.65)
gifdirectory = "guxiang_animation"
wc.generate_animation(100, outputdir=gifdirectory)