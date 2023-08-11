import nltk
import spacy
import requests
import streamlit
from bs4 import BeautifulSoup
from nltk.tag import StanfordPOSTagger
from nltk.tokenize import word_tokenize
from googletrans import Translator

import streamlit as st
import pandas as pd

def generate_flash_cards(text):
    # Load Spacy's German model
    nlp = spacy.load('de_core_news_md')
    doc = nlp(text)

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
    for token in doc:
        if token.pos_ in tagged_words_dict:
            tagged_words_dict[token.pos_].append(token.text)

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

    # Set up the Google Cloud Translation API client
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

    output_str = ""

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
            return None  # returning None when the span is not found

    for german_noun, english_noun in translated_nouns.items():
        try:
            noun_span = print_word_info(german_noun, 'dwdswb-ft-blocktext')
            if noun_span:
                parts = noun_span.get_text().split("·")
                gender_singular = parts[0].strip().split()[1].replace('(', '').replace(')', '').strip(',')
                try:
                    output_str += f"{gender_dict[gender_singular]} {german_noun}"  # Print the singular form with gender
                    if len(parts) >= 3:
                        plural_parts = parts[2].strip().split(":")
                        if len(plural_parts) >= 2:
                            plural_form = plural_parts[1].strip()  # Take the word after the colon
                            output_str += f" | die {plural_form} - the {english_noun}\n\n"  # Print the plural form and translation
                        else:
                            output_str += f" - No plural form found - the {english_noun}\n\n"
                    else:
                        output_str += f" - No plural form found - the {english_noun}\n\n"
                except KeyError:
                    output_str += f"{german_noun} - Unknown gender - the {english_noun} \n\n"
            else:
                output_str += f"{german_noun} - issue finding german noun\n\n"
        except Exception as e:
            output_str += f"Issue with {german_noun}: {str(e)}\n\n"

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
                conjugations[index:index + 2] = [' '.join(conjugations[index:index + 2])]
            output_str += f"{german_verb} - {english_verb}\n({' , '.join(conjugations)})\n\n"
        else:
            # Handle separable verbs
            prepositions = ['nach', 'vor', 'über', 'unter', 'auf', 'ab', 'an', 'aus', 'ein', 'mit',
                            'zu']  # Add more prepositions as needed
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
                            index = conjugations.index(
                                f"ist {preposition}") if f"ist {preposition}" in conjugations else conjugations.index(
                                f"hat {preposition}")
                            conjugations[index:index + 2] = [' '.join(conjugations[index:index + 2])]
                        output_str += f"{preposition} | {base_verb} - {english_verb}\n({' , '.join(conjugations)})\n\n"
                    break

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

            if komparativ and superlativ:  # Both forms are available
                output_str += f"{german_adj}, {komparativ}, {superlativ} - {english_adj}\n\n"
            elif komparativ:  # Only the comparative form is available
                output_str += f"{german_adj}, {komparativ} - {english_adj}\n\n"
            elif superlativ:  # Only the superlative form is available
                output_str += f"{german_adj}, {superlativ} - {english_adj}\n\n"
            else:  # Neither form is available
                output_str += f"{german_adj} - {english_adj}\n\n"
        else:
            output_str += f"{german_adj} - {english_adj}\n\n"

    return output_str
    return lemmatized_words_dict