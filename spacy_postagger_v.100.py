import spacy

nlp = spacy.load('de_core_news_sm')

doc = nlp("Das ist ein Satz.")
for token in doc:
    print(token.text, token.pos_)
