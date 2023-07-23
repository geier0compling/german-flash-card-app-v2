import nltk
import spacy
import requests
from bs4 import BeautifulSoup
from nltk.tag import StanfordPOSTagger
from nltk.tokenize import word_tokenize

nltk.download('averaged_perceptron_tagger')
nltk.download('universal_tagset')

german_pos_model = '/Users/matthewgeier/Downloads/stanford-postagger-full-2020-11-17/models/german-ud.tagger'  # replace with your actual path
stanford_dir = '/Users/matthewgeier/Downloads/stanford-postagger-full-2020-11-17/stanford-postagger.jar'
german_pos_tagger = StanfordPOSTagger(german_pos_model, stanford_dir, encoding='utf8')

text = "Nur die schöne Eingeborene Momosan, an solche wilden Seefahrten nicht gewöhnt, war in ein Rettungsboot geklettert."
tokenized_text = word_tokenize(text)  # Use word_tokenize instead of text.split()
tagged_text = german_pos_tagger.tag(tokenized_text)

# Initialize the dictionary of lists
tagged_words_dict = {
    "NOUN": [],
    "VERB": [],
    "ADJ": [],
    "PRON": [],
    "PUNCT": [],
    "ADV": [],
    "AUX": [],
    "ADP": [],
    "DET": []
}

# Add the words to the correct list based on their POS tag
for word, tag in tagged_text:
    if tag in tagged_words_dict:
        tagged_words_dict[tag].append(word)

print("Nouns:", tagged_words_dict["NOUN"])
print("Verbs:", tagged_words_dict["VERB"])
print("Adjectives:", tagged_words_dict["ADJ"])
print("Pronouns:", tagged_words_dict["PRON"])
print("Punctuation:", tagged_words_dict["PUNCT"])
print("Adverbs:", tagged_words_dict["ADV"])
print("Auxiliary:", tagged_words_dict["AUX"])
print("Adpositions:", tagged_words_dict["ADP"])
print("Determiners:", tagged_words_dict["DET"])

# Load Spacy's German model
nlp = spacy.load('de_core_news_md')

# Initialize a new dictionary of lists for the lemmas
lemmatized_words_dict = {
    "NOUN": [],
    "VERB": [],
    "ADJ": [],
    "PRON": [],
    "PUNCT": [],
    "ADV": [],
    "AUX": [],
    "ADP": [],
    "DET": []
}

# Iterate over each category and each word in each category
for tag in tagged_words_dict:
    for word in tagged_words_dict[tag]:
        # Lemmatize the word
        lemma = nlp(word)[0].lemma_
        # Add the lemma to the correct list
        lemmatized_words_dict[tag].append(lemma)

print("Nouns:", lemmatized_words_dict["NOUN"])
print("Verbs:", lemmatized_words_dict["VERB"])
print("Adjectives:", lemmatized_words_dict["ADJ"])
print("Pronouns:", lemmatized_words_dict["PRON"])
print("Punctuation:", lemmatized_words_dict["PUNCT"])
print("Adverbs:", lemmatized_words_dict["ADV"])
print("Auxiliary:", lemmatized_words_dict["AUX"])
print("Adpositions:", lemmatized_words_dict["ADP"])
print("Determiners:", lemmatized_words_dict["DET"])

gender_dict = {'Femininum': 'die', 'Maskulinum': 'der', 'Neutrum': 'das'}

def print_word_info(word, span_class):
    url = f"https://www.dwds.de/wb/{word}"
    response = requests.get(url)
    content = response.text
    soup = BeautifulSoup(content, 'html.parser')
    span = soup.find('span', attrs={'class': span_class})

    if span:
        return span
    else:
        print(f"Couldn't find the span for {word}")

for german_noun in lemmatized_words_dict["NOUN"]:
    noun_span = print_word_info(german_noun, 'dwdswb-ft-blocktext')
    if noun_span:
        parts = noun_span.get_text().split("·")
        gender_singular = parts[0].strip().split()[1].replace('(', '').replace(')', '') # Only take the word inside the brackets
        plural_form = parts[2].strip().split(":")[1].strip() # Take the word after the colon
        print(f"{gender_dict[gender_singular]} {german_noun} | die {plural_form}\n")

for german_verb in lemmatized_words_dict["VERB"]:
    url1 = f"https://www.dwds.de/wb/{german_verb}"
    response = requests.get(url1)
    content = response.text

    soup = BeautifulSoup(content, 'html.parser')

    verb_span = soup.find('span', attrs={'class': 'dwdswb-flexionen'})

    if verb_span:
        parts = verb_span.find_all('span', attrs={'class': 'dwdswb-flexion-hl'})
        conjugations = [b.text for b in parts]
        if "ist" in conjugations or "hat" in conjugations:
            index = conjugations.index("ist") if "ist" in conjugations else conjugations.index("hat")
            conjugations[index:index+2] = [' '.join(conjugations[index:index+2])]
        print(f"{german_verb}\n({' , '.join(conjugations)})\n")
    else:
        # Handle separable verbs
        prepositions = ['nach', 'vor', 'über', 'unter', 'auf', 'ab', 'an', 'aus', 'ein', 'mit', 'zu'] # Add more prepositions as needed
        for preposition in prepositions:
            if german_verb.startswith(preposition):
                base_verb = german_verb[len(preposition):]
                url1 = f"https://www.dwds.de/wb/{base_verb}"
                response = requests.get(url1)
                content = response.text

                soup = BeautifulSoup(content, 'html.parser')

                verb_span = soup.find('span', attrs={'class': 'dwdswb-flexionen'})
                if verb_span:
                    parts = verb_span.find_all('span', attrs={'class': 'dwdswb-flexion-hl'})
                    conjugations = [f"{b.text} {preposition}" for b in parts]
                    if f"ist {preposition}" in conjugations or f"hat {preposition}" in conjugations:
                        index = conjugations.index(f"ist {preposition}") if f"ist {preposition}" in conjugations else conjugations.index(f"hat {preposition}")
                        conjugations[index:index+2] = [' '.join(conjugations[index:index+2])]
                    print(f"{preposition} | {base_verb}\n({' , '.join(conjugations)})\n")
                break

for german_adj in lemmatized_words_dict["ADJ"]:
    adj_span = print_word_info(german_adj, 'dwdswb-ft-blocktext')
    if adj_span:
        parts = adj_span.get_text().split("·")
        if len(parts) >= 3: # Only if there are both comparative and superlative forms
            komparativ = parts[1].strip().split(":")[1].strip() # Take the word after the colon
            superlativ = parts[2].strip().split(":")[1].strip() # Take the word after the colon
            print(f"{german_adj}, {komparativ}, {superlativ}\n")
        else:
            print(f"{german_adj}\n")
