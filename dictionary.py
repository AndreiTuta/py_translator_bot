from asyncio.log import logger
import logging

from pathlib import Path
from emoji import UNICODE_EMOJI


logger = logging.getLogger(__name__)

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

    def is_emoji(self, word):
        return word in UNICODE_EMOJI

    def get_word(self, word):
        try:
            return self.words[word]
        except KeyError:
            logging.info(f"Dictionary doesn't contain word {word}")
            return None

    def add_word(self, word, translation):
        self.words[word]=translation
        self.words["updated"] = True
