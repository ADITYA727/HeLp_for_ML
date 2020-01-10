import nltk
s='Aakash works in India.'
nltk.ne_chunk(nltk.tag.pos_tag(s.split()), binary=True)