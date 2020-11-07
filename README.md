# HUN-BOT

A simple Hungarian chatbot for booking an appointment.
Date parsing is partially based on https://github.com/sedthh/lara-hungarian-nlp.

## SETUP

* Set up Hungarian NLP models for Spacy
    * Repo: https://github.com/oroszgy/spacy-hungarian-models
* Rasa will try to use NLP models linked to 'hu' in Spacy
    * Link Hungarian models to Spacy: <code>python3 -m spacy link hu_core_ud_lg hu</code>
 * <code>rasa train</code> should work now
