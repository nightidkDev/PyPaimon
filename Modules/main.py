import string
import pymorphy2
import re

morph = pymorphy2.MorphAnalyzer()

class WordsFilter(object):
    def __init__(self):
        self.deny_words = []
    
    def set_words(self, arr_words):
        if type(arr_words) != type([]):
            raise ValueError("Type of words to set aren't <class 'list'>")
        else:
            self.deny_words = arr_words

    def words(self):
        return self.deny_words

    def filter(self, phrase):
        return WordsFilter.gen(self, phrase)

    def gen(self, text):
        founds = []
        for word in text.split():
            for wrd in self.deny_words:
                if wrd in word:
                    if len(word) >= len(wrd) and len(wrd) / len(word) * 100 >= 72:
                        founds.append(True)
                        break
                    else:
                        founds.append(False)
                        break
                elif wrd in text:
                    if len(wrd.split(" ")) >= 2 and wrd in text:    
                        founds.append(True)
                        break
                    else:
                        founds.append(False)
                        break
                else:
                    continue
        return True if len(list(filter(lambda x: x is True, founds))) != 0 else False
