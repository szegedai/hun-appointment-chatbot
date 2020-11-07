# HUN-BOT

## SETUP

* Set up Hungarian NLP models for Spacy
    * Repo: https://github.com/oroszgy/spacy-hungarian-models
* Rasa will try to use NLP models linked to 'hu' in Spacy
    * Link Hungarian models to Spacy: <code>python3 -m spacy link hu_core_ud_lg hu</code>
 * <code>rasa train</code> should work now
