# Hun-appointment-chatbot

A simple Hungarian chatbot for booking an appointment using the Rasa framework.

This repository contains the bot, backend and frontend for a site that can be deployed and used for hosting discussions with the bot.

### Structure of the repository

The repository contains four separate submodules, as well as a few scripts for various smaller tasks.
```
hun-appointment-chatbot/
├─ action_server/
├─ rasa_server/
├─ nodejs/
├─ flask_tts/
```

- **action_server**: Action server module for the bot, the brain of the chatbot. All code that determines how the bot reacts and handles user interactions are implemented here.
- **rasa_server**: Rasa server module. The bot structure (NLU and Core parts) is implemented here.
- **nodejs**: Backend for the site where the bot is deployed.
- **flask_tts**: Frontend for the bot's website.

### Local development and usage

The easiest way to interact with the bot locally is through rasa CLI. This process describes how to set up the environment, train your custom NLU and Core models for the bot, and how to have discussions with the bot in the terminal.

If you're not looking for deploying the whole site, but only the development of the chatbot the relevant submodules  for this are the action server and the Rasa server.

### Setup
* Install dependencies with <code>pip install -r requirements.txt</code>. Please note, that the two modules (rasa_server and action_server) have separate dependencies, you'll need to install both. (Two separate virtual environments for the two submodules are perfectly fine as well.)
* Rasa will try to use NLP models linked to 'hu' in Spacy
    * Link Hungarian models to Spacy: <code>python3 -m spacy link hu_core_ud_lg hu</code>
 * You can now train models with <code>rasa train</code>, but the steps above are also required for having a conversation with the bot locally

### Usage
Before using the bot, you'll have to specify a list of dates that the bot'll accept or suggest as free dates.
You can do this by adding new rows to the `action_server/test_data.json` file. Each row should correspond to an interval, like this:
```json
[
  {"start_date":  "2021-01-18T12:00", "end_date": "2021-01-18T18:00"},
  {"start_date":  "2021-01-20T12:00", "end_date": "2021-01-20T18:00"}
]
```
The chatbot will ignore all past intervals or the past part of any relevant intervals.<br>

A much simpler way for testing purposes to use the script in the project root to generate random intervals for the bot. To achieve this, simply run `python data_generator.py`. This will overwrite data in `action_server/test_data.json`.

To be able to interact with the bot, you'll need to get both the action and rasa servers running.

For the action server, run `rasa run actions` in the `action_server` submodule. This will start a local server that receives data from the quasi frontend of the bot (the rasa server).

Now, run `rasa shell` in the `rasa_server` directory. 

The program might take a few seconds to load, after which you can initiate a conversation with the chatbot.

The following is an example conversation, that shows the chatbot's capabilities.
```
USER:   Szia                                                                                                                                                                                                                     
BOT:    Szia! Miben segíthetek?
USER:   időpontot szertenék foglalni                                                                                                                                                                                             
BOT:    Okés. Mikor lenne jó?
        Esetleg holnap délután 2 óra és délután 4 óra között jó valamikor?
USER:   esetleg jövő héten inkább?                                                                                                                                                           
BOT:    A kért időszakban több alkalom is megfelel, például jövő hét hétfőn, jövő hét csütörtökön és jövő hét pénteken. Megfelel esetleg valamikor ezek közül?
USER:   legyen a csütörtök                                                                                                                                                                                                        
BOT:    A kért időszakban több alkalom is megfelel, például jövő hét csütörtökön reggel 9 óra-tól 12 óra-ig és jövő hét csütörtökön délután 2 óra-tól délután 5 óra-ig. Megfelel esetleg valamikor ezek közül?
USER:   délelőtt                                                                                                                                                                                                       
BOT:    Szuper, reggel 9 óra és délelőtt 11 óra között jól hangzik. Ezen belül ráérsz?
USER:   legyen 9                                                                                                                                                                                                     
BOT:    Rendben, Főnök úr számára tökéletes időpont reggel 9 óra. Köszönöm!
```

## License
This project is licensed under [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0) license. Feel free to use it in your own projects.

## Contribute
Any help or feedback in further developing the library is welcome!
