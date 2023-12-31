import streamlit as st
import pandas as pd
from german_flash_card_def_function import generate_flash_cards
import spacy

# Download and install the German language model for spaCy if not already installed
try:
    nlp = spacy.load('de_core_news_md')
except OSError:
    import subprocess
    subprocess.run(['python', '-m', 'spacy', 'download', 'de_core_news_md'])
    nlp = spacy.load('de_core_news_md')

def main():
    st.title('Get Flash Cards')
    user_input = st.text_input('Enter your text here:')
    if user_input:
        output = generate_flash_cards(user_input) # Call the function here
        output = output.replace('\n', '<br/>')
        st.markdown(output, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

