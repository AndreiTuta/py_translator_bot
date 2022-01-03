import telebot
import requests
import logging
import os

from datetime import datetime
from pathlib import Path

# logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

class Dictionary():
    def __init__(self, lang):
        self.language = lang
        self.dict_loc = f'dictionary/{self.language}.txt'
        self.words = self.load_words()

    def load_words(self):
        words = {}
        try:
            with open(self.dict_loc) as fp:
                logging.info(f'Processing dictionary at {self.dict_loc}')
                while True:
                    line = fp.readline()        
                    if not line:
                        break
                    content = line.split(":")
                    word = content[0]
                    translation = content[1].replace('\n', '')
                    logging.info(f"{word}: {translation}")
                    words[word] = translation
                    words["updated"] = False
                fp.close()
        except FileNotFoundError:
            logging.info(f'Dictionary for language {self.language} doesn\'t exist. It will be initialised as empty')
            Path(self.dict_loc).touch(exist_ok=True)
        return words

    def save_words(self):
        if(self.words["updated"]):
            file1 = open(self.dict_loc, "w")
            for word, translation in self.words.items():
                if word != 'updated':
                    file1.write(f"{word}:{translation}")
                    file1.write("\n")
            file1.close()
        else:
            logging.info("Not updating word file.")

    def get_word(self, word):
        try:
            return self.words[word]
        except KeyError:
            logging.info(f"Dictionary doesn't contain word {word}")
            return None

    def add_word(self, word, translation):
        self.words[word]=translation
        self.words["updated"] = True

class Translator():
    def __init__(self, dict: Dictionary, key):
        self.key = key
        self.dict = dict

    def translate_message(self, message, lang):
        if message is not None:
            translated_message = []
            for word in message.split(' '):
                translation = self.translate_word(word, lang)
                if translation is None:
                    raise Exception("Translation language not found in dictionary")
                logging.info(f'Processing translation for {translation}')
                translated_message.append(translation)
            return ' '.join(translated_message)

    def translate_word(self, message_word, lang):
        if (self.dict.language == lang):
            word = self.dict.get_word(message_word)
            if(word is not None):
                return word
            else: 
                new_word = message_word
                translation = self.translate_deepl(message_word)
                if translation is not None:
                    self.dict.add_word(new_word, translation)
                    logging.info(f"Adding a new word to dictionary")
                    self.dict.save_words()
                    return translation
                else:
                    return None
        else:
            logging.info("Language not found.")
            return None

    def translate_deepl(self, word):
        url = f"https://api-free.deepl.com/v2/translate?auth_key={self.key}&text={word}&source_lang={self.dict.language}&target_lang=EN"
        response = requests.request("GET", url, headers={}, data={})
        if(response.status_code == 200):
            text = response.json()
            translations = text['translations']
            translation = translations[0]['text']
            logging.info(f"Processed translation for {word} using DeepL: {translation}")
            return translation
        else:
            logging.info(f"Error translating {word}")
            return None

class TranslatorBot():
    def __init__(self, api_key) -> None:
        self.bot = telebot.TeleBot(api_key, threaded=False)
        logging.info('Initialised telebot')

    # method used to parse arguments passed after the command
    def extract_arg(self, arg):
        logging.info(f'processing args: {arg}')
        return arg.split()[1:]

tBot = TranslatorBot(os.environ["TELEGRAM_KEY"])
bot = tBot.bot
chat_translators = {}

@bot.message_handler(commands=['help', 'start', 'info'])
def get_help(message):
    help_info =  f"""/help /start /info - displays the menu \n /identify [iso lang code]- adds the current chat into a list of translators by creating a translator from [iso lang code] to EN \n /translate [message] - returns the translation of the message to english"""
   
    bot.reply_to(message, help_info)

@bot.message_handler(commands=['identify'])
def identify(message):
    cid = message.chat.id
    args = tBot.extract_arg(message.text)
    if(len(args) == 1):
        arg = str(args[0])
        t = Translator(Dictionary(arg), os.environ["DEEPL_KEY"])
        chat_translators[cid] = t
        bot.reply_to(message, f"Created translator for {cid} and language {arg}")
    else:
        bot.reply_to(message, "Please pass a second param to initialise the translator")

@bot.message_handler(commands=['translate'])
def translate_message(message):
    cid = message.chat.id
    try:
        t = chat_translators[cid]
        message_text = message.text.replace('/translate','')
        bot.reply_to(message, t.translate_message(message_text, t.dict.language))
    except KeyError:
        pass

bot.polling(none_stop=True, interval=3, timeout=10)

