from wordcloud2 import wordcloud as W
import random

words = "天地玄黄宇宙洪荒日月盈昃辰宿列张寒来暑往秋收冬藏闰余成岁律吕调阳云腾致雨露结为霜金生丽水玉出昆冈剑号巨阙珠称夜光果珍李柰菜重芥姜海咸河淡鳞潜羽翔龙师火帝鸟官人皇始制文字乃服衣裳推位让国有虞陶唐吊民伐罪周发殷汤坐朝问道垂拱平章"
words = list(words)
weights = [random.random()**2 * 100 + 30 for i in range(len(words))]
wc = W.wordcloud(words, weights)
wc.generate()
W.paint(wc, "qianziwen.svg")