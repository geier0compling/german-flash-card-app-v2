import csv
import nltk
import spacy
import requests
from googletrans import Translator
from bs4 import BeautifulSoup
from nltk.tag import StanfordPOSTagger
from nltk.tokenize import word_tokenize

nltk.download('averaged_perceptron_tagger')
nltk.download('universal_tagset')

german_pos_model = '/Users/matthewgeier/Downloads/stanford-postagger-full-2020-11-17/models/german-ud.tagger'  # replace with your actual path
stanford_dir = '/Users/matthewgeier/Downloads/stanford-postagger-full-2020-11-17/stanford-postagger.jar'
german_pos_tagger = StanfordPOSTagger(german_pos_model, stanford_dir, encoding='utf8')

text = """Jetzt aber, in den Gassen Montpelliers, spürte und sah Grenouille deutlich - und jedesmal, wenn er es wieder sah, durchrieselte ihn ein heftiges Gefühl von Stolz -, dass er eine Wirkung auf die Menschen ausübte."""
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

# create translator object
translator = Translator()

# define a function that will translate a list of words from german to english
def translate_text(text, source_lang="de", target_lang="en"):
    translator = Translator()
    translation = translator.translate(text, src=source_lang, dest=target_lang)
    return translation.text

def translate_words(words, source_lang="de", target_lang="en"):
    translation_dict = {}
    for word in words:
        translated_word = translate_text(word, source_lang, target_lang)
        translation_dict[word] = translated_word
    return translation_dict

# translate nouns
nouns = lemmatized_words_dict["NOUN"]
translated_nouns = translate_words(nouns)
print("Translated Nouns:", translated_nouns)

# translate verbs
verbs = lemmatized_words_dict["VERB"]
translated_verbs = translate_words(verbs)
print("Translated Verbs:", translated_verbs)

# translate adj
adj = lemmatized_words_dict["ADJ"]
translated_adj = translate_words(adj)
print("Translated Adjectives:", translated_adj)

# Empty list to collect the rows
rows = []

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
        return None # returning None when the span is not found

for german_noun, english_noun in translated_nouns.items():
    try:
        noun_span = print_word_info(german_noun, 'dwdswb-ft-blocktext')
        if noun_span:
            parts = noun_span.get_text().split("·")
            gender_singular = parts[0].strip().split()[1].replace('(', '').replace(')', '').strip(',')
            try:
                german_phrase = f"{gender_dict[gender_singular]} {german_noun}"  # Singular form with gender
                if len(parts) >= 3:
                    plural_parts = parts[2].strip().split(":")
                    if len(plural_parts) >= 2:
                        plural_form = plural_parts[1].strip()  # Take the word after the colon
                        german_phrase += f" | die {plural_form}"  # Add the plural form
                rows.append({
                    'German': german_phrase,
                    'English': f"the {english_noun}"
                })
            except KeyError:
                # Handle the case when the gender is unknown
                rows.append({
                    'German': german_noun,
                    'English': f"the {english_noun} - Unknown gender."
                })
        else:
            print(f"{german_noun} - issue finding german noun")
    except Exception as e:
        print(f"Issue with {german_noun}: {str(e)}")

for german_verb, english_verb in translated_verbs.items():
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
        rows.append({
            'German': f"{german_verb} ({' , '.join(conjugations)})",
            'English': english_verb
        })
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
                    rows.append({
                        'German': f"{preposition} {base_verb} ({' , '.join(conjugations)})",
                        'English': english_verb
                    })

for german_adj, english_adj in translated_adj.items():
    adj_span = print_word_info(german_adj, 'dwdswb-ft-blocktext')
    if adj_span:
        text = adj_span.get_text()
        komparativ, superlativ = None, None
        parts = text.split("·")

        for part in parts:
            stripped_part = part.strip()

            if "Komparativ:" in stripped_part:
                komparativ = stripped_part.split(":")[1].strip()
            elif "Superlativ:" in stripped_part:
                superlativ = stripped_part.split(":")[1].strip()

        german_string = german_adj
        if komparativ and superlativ: # Both forms are available
            german_string += f", {komparativ}, {superlativ}"
        elif komparativ: # Only the comparative form is available
            german_string += f", {komparativ}"
        elif superlativ: # Only the superlative form is available
            german_string += f", {superlativ}"

        rows.append({
            'German': german_string,
            'English': english_adj
        })
    else:
        rows.append({
            'German': german_adj,
            'English': english_adj
        })

# Write the rows to a CSV file
with open('translations.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['German', 'English']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for row in rows:
        writer.writerow(row)
