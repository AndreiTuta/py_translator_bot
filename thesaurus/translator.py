
import logging 
import requests 

from .dictionary import Dictionary

logger = logging.getLogger(__name__)

class Translator():
    def __init__(self, dict: Dictionary, key):
        self.key = key
        self.dict = dict

    def translate_message(self, message, lang):
        if message is not None:
            translated_message = []
            for word in message.split(' '):
                if not self.dict.is_emoji(word) and self.dict.is_clean(word):
                    translation = self.translate_word(word, lang)
                    if translation is None or translation == '':
                        translation = f"[{word} couldn't be translated]"
                    logger.info(f'Processing translation for {translation}')
                    translated_message.append(translation)
                else: 
                    logger.info(f'Word {word} is an character/emoji, so not translating')
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
                    logger.info(f"Adding a new word to dictionary")
                    self.dict.save_words()
                    return translation
                else:
                    return None
        else:
            logger.info("Language not found.")
            return None

    def translate_deepl(self, word):
        url = f"https://api-free.deepl.com/v2/translate?auth_key={self.key}&text={word}&source_lang={self.dict.language}&target_lang=EN"
        response = requests.request("GET", url, headers={}, data={})
        if(response.status_code == 200):
            text = response.json()
            translations = text['translations']
            translation = translations[0]['text']
            logger.info(f"Processed translation for {word} using DeepL: {translation}")
            return translation
        else:
            logger.info(f"Error translating {word}")
            return None