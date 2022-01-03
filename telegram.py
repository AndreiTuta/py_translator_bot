import telebot

from datetime import datetime
import requests
from pathlib import Path

class Dictionary():
    def __init__(self, lang):
        self.language = lang
        self.dict_loc = f'dictionary/{self.language}.txt'
        self.words = self.load_words()

    def load_words(self):
        words = {}
        try:
            with open(self.dict_loc) as fp:
                while True:
                    line = fp.readline()        
                    if not line:
                        break
                    content = line.split(":")
                    word = content[0]
                    translation = content[1].replace('\n', '')
                    print(f"{word}: {translation}")
                    words[word] = translation
                    words["updated"] = False
                fp.close()
        except FileNotFoundError:
            print(f'Dictionary for language {self.language} doesn\'t exist. It will be initialised as empty')
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
            print("Not updating word file.")

    def get_word(self, word):
        try:
            return self.words[word]
        except KeyError:
            print(f"Dictionary doesn't contain word {word}")
            return None

    def add_word(self, word, translation):
        self.words[word]=translation
        self.words["updated"] = True

class Translator():
    def __init__(self, dict: Dictionary, key):
        self.key = key
        self.dict = dict

    def translate_message(self, message, lang):
        translated_message = []
        for word in message.split(' '):
            translation = self.translate_word(word, lang)
            if translation is None:
                raise Exception("Translation language not found in dictionary")
            print(f'Processing translation for {translation}')
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
                self.dict.add_word(new_word, translation)
                print(f"Adding a new word to dictionary")
            self.dict.save_words()
            return translation
        else:
            print("Language not found.")
            return None

    def translate_deepl(self, word):
        url = f"https://api-free.deepl.com/v2/translate?auth_key={self.key}&text={word}&target_lang=EN"
        response = requests.request("GET", url, headers={}, data={})
        if(response.status_code == 200):
            text = response.json()
            translations = text['translations']
            translation = translations[0]['text']
            print(f"Processed translation for {word} using DeepL: {translation}")
            return translation
        else:
            return "Error translating"

d = Dictionary('ru')
t = Translator(d, input("Enter API key: "))
# bot = telebot.TeleBot(telegram_key, threaded=False)

# @bot.message_handler(commands=['identify'])
# def identify(message):
#   cid = message.chat.id

# bot.polling(none_stop=True, interval=3, timeout=10)

