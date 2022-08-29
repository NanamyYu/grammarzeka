import os
import shutil
import io
import zipfile
import requests
import string
import pandas as pd
import numpy as np
from typing import Optional, List
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
import re
from bs4 import BeautifulSoup
import warnings

warnings.filterwarnings('ignore')

# Константы
import pymorphy2
morph = pymorphy2.MorphAnalyzer()

MIN_PHONEME = 0
MAX_PHONEME = 5

MIN_LENGTH = 4
MAX_LENGTH = 14

MIN_FREQ_LOG = 1
MAX_FREQ_LOG = 4

simple_POS = {'NUMR', 'ADVB', 'NPRO', 'PRED', 'PREP', 'CONJ', 'PRCL', 'INTJ'}
medium_POS = {'NOUN', 'ADJF', 'ADJS', 'COMP', 'VERB', 'INFN'}
difficult_POS = {'PRTF', 'PRTS', 'GRND'}

MIN_MORPH = 1
MAX_MORPH = 7


# Датасеты
def save_zip_csv(url: str, dirname: str, new_filename: str) -> None:
    fullname = os.path.join(dirname, new_filename)
    
    if not os.path.exists(fullname):
        r = requests.get(url)
        with r, zipfile.ZipFile(io.BytesIO(r.content)) as archive:
            archive.extractall(dirname)
    return fullname

def save_zip_txt(url: str, dirname: str, new_filename: str) -> None:
    fullname = os.path.join(dirname, new_filename)
    
    if not os.path.exists(fullname):
        shutil.rmtree(dirname, ignore_errors=True)

        r = requests.get(url)
        with r, zipfile.ZipFile(io.BytesIO(r.content)) as archive:
            archive.extractall(dirname)

        for filename in os.listdir(dirname):
            if filename.endswith('.txt'):
                with open(os.path.join(dirname, filename), 'rb') as f:
                    text = f.read().decode('cp1251')
                    with open(fullname, 'wb') as ru:
                        ru.write(text.encode('utf-8'))
    return fullname

def save_words(level:str):
    dirname = 'datasets/word_levels'
    fullname = os.path.join(dirname, str(level) + '.txt')
    
    if not os.path.exists(fullname):
        html = requests.get(os.path.join('http://www.tolstyslovar.com/ru', level)).content
        soup = BeautifulSoup(html, 'html.parser')

        word_list = []
        for word in soup.findAll(attrs={'class': 'word'}):
            word_list.append(word.text)

        os.makedirs(dirname, exist_ok=True)
        with open(fullname, 'wb') as ru:
            ru.write(' '.join(word_list).encode('utf-8'))
    return fullname

a1_level_path = save_words(level='a1')
c1_level_path = save_words(level='c1')

fullname = save_zip_csv(url='http://dict.ruslang.ru/Freq2011.zip',
                        dirname='datasets/freq',
                        new_filename='freqrnc2011.csv')
freq_df = pd.read_csv(fullname, sep='\t')[['Lemma', 'Freq(ipm)']]
freq_df['Lemma'] = freq_df['Lemma'].str.lower()
freq_df['length'] = freq_df['Lemma'].str.len()
freq_df = freq_df.drop_duplicates(subset=['Lemma'])
freq_df = freq_df.set_index('Lemma')

fullname = save_zip_txt(url='http://www.speakrus.ru/dict2/tikhonov.zip',
                        dirname='datasets/tikhonov',
                        new_filename='tikhonov.txt')        
morph_df = pd.read_csv(fullname, sep='|', names=['Lemma', 'analysis'])
morph_df['Lemma'] = morph_df['Lemma'].str.replace('\d+', '').str.split().str[0].str.lower()
morph_df['analysis'] = morph_df['analysis'].str.replace('\d+', '').str.split(pat=',', n=1).str[0].str.split().str[0]
morph_df['count_morph'] = morph_df['analysis'].str.count(pat='/') + 1
morph_df = morph_df.drop_duplicates(subset=['Lemma'])
morph_df = morph_df.set_index('Lemma')

a1_level_path = save_words(level='a1')
c1_level_path = save_words(level='c1')


# Вспомогательные функции
def transform_word(word: str) -> tuple:
    delete_symbols = set(string.punctuation) - set('-') | set('«»…')
    word = ''.join([w for w in word.replace(' ', '') if w not in delete_symbols])
    word = re.sub('[a-zA-Z]|\d', '', word)
    is_capitalized = word[0].isupper() if word else False
    return word.lower(), is_capitalized

def get_word_info(word: str) -> tuple: 
    morph_parse = morph.parse(word)[0]
    return word, morph_parse.normal_form, morph_parse.tag.POS 

vowels = set('аяоёуюыиэе')
consonants = set('бвгджзйклмнпрстфхцчшщ')
marks = set('ъь')

deaf_consonants = set('пфктшсхцчщ')
voices_consonants = set('лмнрйбвгджз')

ioted_vowels = { 
    'я' : {'one': 'а', 'two': 'йа'},
    'ё' : {'one': 'о', 'two': 'йо'},
    'ю' : {'one': 'у', 'two': 'йу'},
    'е' : {'one': 'э', 'two': 'йэ'},
}

stress_vowels = {
    'о': {'stress': 'о', 'not_stress': 'a'},
    'е': {'stress': 'э', 'not_stress': 'и'},
    'я': {'stress': 'а', 'not_stress': 'и'},
}

deaf_pairs = {
    'б': 'п',
    'в': 'ф',
    'г': 'к',
    'д': 'т',
    'ж': 'ш',
    'з': 'с'
}

simple_groups = { #abc -> ac
    'с' : {'т': set('нл')}, # стн, стл 
    'н' : {'д': set('шц'), 'т': 'г'}, # ндш, ндц, нтг
    'з' : {'д': set('нц')}, # здн, здц
    'р' : {'д': set('цч')} # рдц, рдч 
}

sh_groups = { # ab -> шb
    'ч' : set('нт') # чн, чт
}

sch_groups = { # ab -> щ
    'с' : 'ч', # сч
    'з' : 'ч', # зч
    'ж' : 'ч', # жч
}

def get_transcription(word: str) -> tuple:
    diff = [0] * len(word)
    transcription = ['!'] * len(word)
    for i in range(len(word)):
        c = word[i]
        before_c = word[i - 1] if i > 0 else None
        after_c = word[i + 1] if i < len(word) - 1 else None
        after_after_c = word[i + 2] if i < len(word) - 2 else None
        if c in vowels:
            transcription[i] = c
            diff[i] = 0
            if c in ioted_vowels:
                if i == 0 or before_c in vowels or before_c in marks:
                    transcription[i] = ioted_vowels[c]['two']
                    diff[i] = 2
                else:
                    transcription[i] = ioted_vowels[c]['one']
                    diff[i] = 1
            elif c == 'и':
                if before_c == 'ь':
                    transcription[i] = 'йи'
                    diff[i] = 2
                elif before_c in set('жшц'):
                    transcription[i] = 'ы'
                    diff[i] = 1
                else:
                    transcription[i] = 'и'
                    diff[i] = 0
            elif c in stress_vowels:
                transcription[i] = stress_vowels[c]['not_stress']
                diff[i] = 1
        elif c in consonants:
            transcription[i] = c
            diff[i] = 0
            if c in deaf_pairs:
                if i == len(word) - 1 or after_c in deaf_consonants:
                    transcription[i] = deaf_pairs[c]
                    diff[i] = 1
            if before_c and after_c and\
                before_c in simple_groups and\
                c in simple_groups[before_c] and\
                after_c in simple_groups[before_c][c]:
                transcription[i] = ''
                diff[i] = 1
            if before_c in sh_groups and c in sh_groups[before_c]:
                transcription[i - 1] = 'ш'
                diff[i - 1] = 1
            if before_c in sch_groups and c in sch_groups[before_c]:
                transcription[i - 1] = 'щ'
                diff[i - 1] = 1
                transcription[i] = ''
                diff[i] = 1
            if before_c == 'л' and c == 'н' and after_c == 'ц':
                transcription[i - 1] = ''
                diff[i - 1] = 1
            if before_c == 'в' and c == 'с' and after_c == 'т' and after_after_c == 'в':
                transcription[i - 1] = ''
                diff[i - 1] = 1
            if i == 0 and c == 'с' and after_c in voices_consonants:
                transcription[i] = 'з'
                diff[i] = 1
            if c == 'г' and after_c in deaf_consonants:
                transcription[i] = 'x'
                diff[i] = 1
            if before_c == c:
                transcription[i] = ''
                diff[i] = 1
        else:
            transcription[i] = ''
            diff[i] = 1
    if word.endswith(('ого', 'его')):
        transcription[-2] = 'в'
        diff[-2] = 1
    if word.endswith('тся'):
        transcription[-3] = 'ц'
        diff[-3] = 1
        transcription[-2] = ''
        diff[-2] = 1
    if word.endswith('ться'):
        transcription[-4] = 'ц'
        diff[-4] = 1
        transcription[-3] = ''
        diff[-3] = 1
        transcription[-2] = ''
        diff[-2] = 1
    return sum(diff), diff, transcription

def word_phoneme_param(word: str) -> float:
    diff, _, _= get_transcription(word)
    normalize_phoneme = (diff - MIN_PHONEME) / (MAX_PHONEME - MIN_PHONEME)
    return max(0, min(normalize_phoneme, 1))

def word_length_param(word: str) -> float:
    normalize_length = (len(word) - MIN_LENGTH) / (MAX_LENGTH - MIN_LENGTH)
    return max(0, min(normalize_length, 1))

def word_freq_param(lemma: str) -> Optional[float]:
    if lemma not in freq_df.index:
        return None
    found_lemma = freq_df.loc[lemma]
    freq = np.log1p(found_lemma['Freq(ipm)'].item())
    normalize_freq = (freq - MIN_FREQ_LOG) / (MAX_FREQ_LOG - MIN_FREQ_LOG)
    return 1 - max(0, min(normalize_freq, 1))

def word_POS_param(POS: str) -> Optional[float]:
    if POS in simple_POS:
        return 0
    if POS in medium_POS:
        return 0.5
    if POS in difficult_POS:
        return 1
    return None

def word_morph_param(lemma: str) -> Optional[float]:
    if lemma not in morph_df.index:
        return None
    found_lemma = morph_df.loc[lemma]
    count_morph = found_lemma['count_morph'].item()
    normalize_morph = (count_morph - MIN_MORPH) / (MAX_MORPH - MIN_MORPH)
    return max(0, min(normalize_morph, 1))


# Основная функция сложности слова
def word_difficulty(word: str) -> dict:
    word, lemma, POS = get_word_info(word)
    params = {'word_phoneme_param': word_phoneme_param(word),
              'word_length_param': word_length_param(word),
              'word_freq_param': word_freq_param(lemma),
              #'word_POS_param': word_POS_param(POS),
              'word_morph_param': word_morph_param(lemma)}
    difficulty = np.mean([param for param in params.values() if param is not None])
    return {'lemma': lemma, 'difficulty': difficulty, 'params': params}


# Функции анализа .txt
def distplot_text_df(text_dfs: List[pd.DataFrame], labels: List[str]=[], FROM: int=0, TO: int=1) -> None:
    plt.rc('font', size=13)
    
    fig, ax = plt.subplots(figsize=(8, 4))
    for text_df in text_dfs:
        sns.distplot(x=text_df['difficulty'], label='1')

    ax.set_title('Сложность слова от ' + str(FROM) + ' до ' + str(TO))
    ax.set_ylabel('Плотность распределения')
    ax.set_xlabel('Сложность слова')

    plt.xlim(FROM, TO)
    plt.legend(labels=labels)
    plt.show()

def analyze_text(filepath: str, stop=None, unique=True, show_plot=True) -> pd.DataFrame:
    text_df = pd.DataFrame(columns=['lemma', 'difficulty'])
    with open(filepath, 'rb') as f:
        for i, word in enumerate(tqdm(f.read().decode('utf-8').split())):
            word = transform_word(word)[0]
            if word and (not unique or word not in text_df.index):
                difficulty = word_difficulty(word)
                info = {'lemma': difficulty['lemma'],
                        'difficulty': difficulty['difficulty']}
                info.update(difficulty['params'])
                row = pd.Series(info, name=word)
                text_df = text_df.append(row)
            if stop and stop <= i:
                break
    if show_plot:
        distplot_text_df([text_df], labels=[os.path.basename(filepath)])
    return text_df