# Hun-appointment-chatbot

A simple Hungarian chatbot for booking an appointment using the Rasa framework.

## Setup

-   Install dependencies
-   Rasa will try to use NLP models linked to 'hu' in Spacy
    -   Link Hungarian models to Spacy:  `python3 -m spacy link hu_core_ud_lg hu`
-   `rasa train`  should work now

## Usage

Before using the bot,  you'll have to specify a list of dates that the bot'll accept or suggest as free dates.  You can do this by adding new roes to the test_data.json file.  Each row should correspond to an interval,  like this:

```json
[
  {"start_date":  "2021-01-18T12:00", "end_date": "2021-01-18T18:00"},
  {"start_date":  "2021-01-20T12:00", "end_date": "2021-01-20T18:00"}
]

```

The chatbot will ignore all past intervals or the past part of any relevant intervals.  

You can test the chatbot on CLI running  `rasa run actions  &  rasa shell`,  where the first command starts the action server in the background,  and the second will start the conversation in the terminal.  The program might take a few seconds to load,  after which you can initiate a conversation with the chatbot.

The following is an example conversation,  that shows the chatbot's capabilities.

```
USER:   szia                                                                                                                                                                                                                     
BOT:    Szia! Miben segíthetek?
USER:   időpontot szertenék foglalni                                                                                                                                                                                             
BOT:    Okés. Mikor lenne jó?
USER:   holnap esetleg?                                                                                                                                                                                                          
BOT:    Ráérek holnap. Mikor lenne jó aznap?
USER:   ráérsz délután?                                                                                                                                                                                                          
BOT:    12 óra és délután 6 óra között ráérek. Mikor legyen pontosan?
USER:   legyen 14:30-kor                                                                                                                                                                                                         
BOT:    Rendben, akkor holnap délután fél 3-kor találkozunk.
USER:   köszi, viszlát!                                                                                                                                                                                                          
BOT:    Viszlát!

```
## Evaluation
You can test the bot with these pipelines:

`rasa test nlu --config config1.yml --cross-validation --runs 1 --folds 6`

`rasa test nlu --config config2.yml --cross-validation --runs 1 --folds 6`

Explanation:

**`--config`**:  Switch between the config files, that you currently want to test. 

**`--cross-validation`**: To test your model more extensively, use cross-validation, which automatically creates multiple train/test splits.  (~80% train/~20% test split)

**`--runs`**: Change the number of runs. 

**`--folds`**: Number of test in a run.


Here, we compare scores for intent classification, side by side.

|config| precision|accuracy|f1-score|
|:---:|:---:|:---:|:---:|
|config_1.yml (Bert)|0.675 |0.709|0.669|
|config_2.yml (Spacy)|0.823 |0.794|0.787|


## License

This project is licensed under  [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0)  license.  Feel free to use it in your own projects.

## Contribute

Any help or feedback in further developing the library is welcome!