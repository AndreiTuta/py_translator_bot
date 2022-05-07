from asyncio.log import logger
import logging

from pathlib import Path
import emoji

logger = logging.getLogger(__name__)

BAD_CHARS = [';', ':', '!', "*", '\\n' , '-', ',', '.', '?']

class Dictionary():
    def __init__(self, lang):
        self.language = lang
        self.dict_loc = f'dictionary/{self.language}.txt'
        self.words = self.load_words()

    def load_words(self):
        words = {}
        try:
            with open(self.dict_loc) as fp:
                logger.info(f'Processing dictionary at {self.dict_loc}')
                while True:
                    line = fp.readline()        
                    if not line:
                        break
                    content = line.split(":")
                    word = content[0]
                    translation = content[1].replace('\n', '')
                    logger.info(f"{word}: {translation}")
                    words[word] = translation
                    words["updated"] = False
                fp.close()
        except FileNotFoundError:
            logger.info(f'Dictionary for language {self.language} doesn\'t exist. It will be initialised as empty')
            Path(self.dict_loc).touch(exist_ok=True)
        return words

    def save_words(self):
        if(self.words["updated"]):
            file1 = open(self.dict_loc, "w", encoding="utf-8")
            for word, translation in self.words.items():
                if word != '' and translation != '':
                    line = f"{word}:{translation}"
                    logger.info(f"{line}")
                    if ":" in line and word != 'updated':
                        file1.write(line)
                        file1.write("\n")
            file1.close()
        else:
            logger.info("Not updating word file.")

    def is_emoji(self, word):
        return emoji.demojize(word) != word
    
    def clean(self, word):
        if word != '':
            for i in BAD_CHARS :
                word = word.replace(i, '')
            return word
    
    def is_clean(self, word):
        w = self.clean(word)
        return  w is not None and w != ''

    def get_word(self, word):
        try:
            return self.words[word]
        except KeyError:
            logger.info(f"Dictionary doesn't contain word {word}")
            return None

    def add_word(self, word, translation):
        self.words[word]=translation
        self.words["updated"] = True
