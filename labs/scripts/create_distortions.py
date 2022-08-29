from collections import defaultdict
from typing import Set


# Функция сложности слова
exec(open('scripts/word_difficulty.py').read())

def transform_word(word: str) -> tuple:
    delete_symbols = set(string.punctuation) - set('-') | set('«»…')
    word = ''.join([w for w in word.replace(' ', '') if w not in delete_symbols])
    word = re.sub('[a-zA-Z]|\d', '', word)
    is_capitalized = word[0].isupper() if word else False
    return word.lower(), is_capitalized


# Датасеты
letters_dict = dict()
letters = set('абвгдежзийклмнопрстуфхцчшщъыьэюя')
for word in morph_df.index:
    for i in range(len(word) - 1):
        c = word[i]
        next_c = word[i + 1]
        if c in letters and next_c in letters:
            if c not in letters_dict:
                letters_dict[c] = defaultdict(int)
            letters_dict[c][next_c] += 1
letter_df = pd.DataFrame.from_dict(letters_dict, orient='index').fillna(0)
letter_df = letter_df.div(letter_df.sum(axis=1), axis=0)

fullname = save_zip_csv(url='https://github.com/Koziev/NLP_Datasets/raw/master/Stress/all_accents.zip',
                        dirname='datasets/stress',
                        new_filename='all_accents.tsv')
stress_df = pd.read_csv(fullname, sep='\t', names=['Lemma', 'stress'])
stress_df = stress_df.drop_duplicates(subset=['Lemma'])
stress_df = stress_df.set_index('Lemma')


# Вспомогательные функции
def get_word_probability(word: str) -> int:
    probability = 1
    for i in range(len(word) - 1):
        c = word[i]
        next_c = word[i + 1]
        if c in letters and next_c in letters:
            probability *= letter_df.loc[c][next_c]
    return probability

def get_n_best_words(words, max_amount: int=1) -> List[str]:
    if max_amount < len(words):
        return sorted(list(words), key=lambda word: get_word_probability(word), reverse=True)[:max_amount]
    return list(words)

def get_morphs_list(lemma: str) -> List[str]:
    if lemma not in morph_df.index:
        return []
    return list(morph_df.loc[lemma]['analysis'].split('/'))

stress_vowels_dict = {'о':'а', 'а':'о', 'е':'и', 'и':'е', 'я':'е'}

def stress_vowels_distortion(word: str, stress_word: str, morphs_list: List[str]=[]) -> Set[str]:  
    def do_distortion(word_: str, stress_word: str) -> None:
        check_word = ''
        if 0 <= stress_word.find('^') < len(stress_word) - 2:
            i = stress_word.find('^')
            check_word = stress_word[:i] + stress_word[i + 1].upper() + stress_word[i + 2:]
        else:
            return set()
        
        i = j = 2
        while (i < len(word) - 3) and (j < len(check_word) - 3):
            if word[i] != check_word[j].lower():
                if word[i] == check_word[j + 1].lower():
                    j += 1
                elif word[i + 1] == check_word[j].lower():
                    i += 1
            if check_word[j] in stress_vowels_dict and word[i] == check_word[j]:
                distortion = word_[:i] + stress_vowels_dict[word_[i]] + word_[i + 1:]
                if distortion not in distortions and distortion != word:
                    distortions.add(distortion)
                    do_distortion(distortion, stress_word)
            i += 1
            j += 1
        
    distortions = set()
    do_distortion(word, stress_word)
    return distortions

deaf_consonants = set('пфктшсхцчщ')
consonants_pairs = {
    'б':'п', 
    'г':'к', 
    'д':'т', 
    'ж':'ш', 
    'з':'с', 
}

def consonants_distortion(word: str, morphs_list: List[str]=[]) -> Set[str]:  
    def do_distortion(word_: str) -> None:
        for i in range(len(word_)):
            distortion = None
            c = word_[i] 
            after_c = word_[i + 1] if i < len(word_) - 1 else None
            if c in consonants_pairs and (i == len(word_) - 1 or after_c in deaf_consonants):
                distortion = word_[:i] + consonants_pairs[c] + word_[i + 1:]
                if distortion not in distortions and distortion != word:
                    distortions.add(distortion)
                    do_distortion(distortion)
        
    distortions = set()
    do_distortion(word)
    return distortions

root_pairs = {'раст':'рост', 'ращ':'рощ', 'рос':'рас',
               'лаг':'лог', 'лож':'лаж',
               'скак':'скок', 'скоч':'скач',
               'гар':'гор', 'гор':'гар', 
               'твар':'твор','твор':'твар', 
               'клан':'клон', 'клон':'клан',
               'зар':'зор', 'зор':'зар',
               'плав':'плов', 'плов':'плав',
               'мак':'мок', 'моч':'мач',
               'равн':'ровн', 'ровн':'равн',
               'бер':'бир', 'бир':'бер',
               'дер':'дир', 'дир':'дер',
               'пер':'пир', 'пир':'пер',
               'тер':'тир', 'тир':'тер',
               'мер':'мир', 'мир':'мер',
               'жег':'жиг', 'жиг':'жег',
               'стел':'стил', 'стил':'стел',
               'блест':'блист', 'блист':'блест',
               'чет':'чит', 'чит':'чет',
               'кас':'кос', 'кос':'кас'}
    
def roots_distortion(word: str, morphs_list: List[str]=[]) -> Set[str]:
    def do_distortion(word_: str) -> None:
        index = 0
        for morph in morphs_list:
            if morph in root_pairs and morph == word_[index:index + len(morph)]:
                distortion = word_[:index] + root_pairs[morph] + word_[index + len(morph):]
                if distortion not in distortions and distortion != word:
                    distortions.add(distortion)
                    do_distortion(distortion)
            index += len(morph.replace('\'', ''))

    distortions = set()
    do_distortion(word)
    return distortions

prefix_pairs = {'пре':'при', 'при':'пре',
                'без':'бес', 'бес':'без',
                'воз':'вос', 'вос':'воз',
                'вз':'вс', 'вс':'вз',
                'из':'ис', 'ис':'из',
                'низ':'нис', 'нис':'низ',
                'раз':'рас', 'рас':'раз',
                'роз':'рос', 'рос':'роз',
                'чрез':'чрес', 'чрес':'чрез'}

def prefixs_distortion(word: str, morphs_list: List[str]=[]) -> Set[str]:
    def do_distortion(word_: str) -> None:
        index = 0
        for morph in morphs_list:
            if morph in prefix_pairs and morph == word_[index:index + len(morph)]:
                distortion = word_[:index] + prefix_pairs[morph] + word_[index + len(morph):]
                if distortion not in distortions and distortion != word:
                    distortions.add(distortion)
                    do_distortion(distortion)
            index += len(morph.replace('\'', ''))
            
    distortions = set()
    do_distortion(word)
    return distortions

vowels_after_prefixs_pairs = {'и':'ы', 'ы':'и'}

all_prefixs = {'без', 'бес', 'в', 'во', 'вз', 'взо', 'вс', 'вне', 'внутри', 'воз', 'возо', 'вос', 'все', 'вы', 'до', 'за',
               'из', 'изо', 'ис', 'испод', 'к', 'кое', 'кой', 'меж', 'междо', 'между', 'на', 'над', 'надо', 'наи', 'не',
               'небез', 'небес', 'недо', 'ни', 'низ', 'низо', 'нис', 'о', 'об', 'обо', 'обез', 'обес', 'около', 'от', 'ото', 
               'па', 'пере', 'по', 'под', 'подo', 'поза', 'после', 'пра', 'пре', 'пред', 'предо', 'преди', 'при', 'про', 
               'противо', 'раз', 'разо', 'рас', 'роз', 'рос', 'с', 'со', 'сверх', 'среди', 'су', 'сыз', 'тре', 'у', 'чрез', 
               'через', 'черес', 'а', 'анти', 'архи', 'би', 'вице', 'гипер', 'де', 'дез', 'дис', 'им', 'интер', 'ир', 'квази',
               'контр', 'макро', 'кросс', 'мега', 'микро', 'мини', 'обер', 'пан', 'пост', 'пре', 'прото', 'псевдо', 'ре', 
               'суб', 'супер', 'сюр', 'транс', 'ультра', 'уни', 'экзо', 'экс', 'экстра'}

def vowels_after_prefixs_distortion(word: str, morphs_list: List[str]=[]) -> Set[str]:
    if morphs_list:
        morph = morphs_list[0].replace('\'', '')
        if len(morph) < len(word) and morph in all_prefixs and word[len(morph)] in vowels_after_prefixs_pairs:
            distortion = word[:len(morph)] +\
                        vowels_after_prefixs_pairs[word[len(morph)]] +\
                        word[len(morph) + 1:]
            if distortion != word:
                return {distortion}
    return set()

postfix_pairs = {'тся':'ться', 'ться':'тся'}

def postfixs_distortion(word: str, morphs_list: List[str]=[]) -> Set[str]:
    for postfix in postfix_pairs:
        if word[-len(postfix):] == postfix:
            return {word[:-len(postfix)] + postfix_pairs[postfix]}
    return set()

vowels = set('аяоёуюыиэе')

def two_in_row_distortion(word: str, morphs_list: List[str]=[]) -> Set[str]:
    def do_distortion(word_: str) -> None:
        for i in range(len(word_)):
            if i > 0 and word_[i - 1] == word_[i] and word_[i] not in vowels:
                distortion = word_[:i] + word_[i + 1:]
                if distortion not in distortions and distortion != word:
                    distortions.add(distortion)
                    do_distortion(distortion)
            
    distortions = set()
    do_distortion(word)
    return distortions

single_suffixs = set(['ан', 'ян', 'ын', 'ин'])

def duplicate_distortion(word: str, morphs_list: List[str]) -> Set[str]:
    def do_distortion(word_: str) -> None:
        index = 0
        for morph in morphs_list:
            morph = morph.replace('\'', '')
            if morph in single_suffixs and morph == word_[index:index + len(morph)] and\
                index + len(morph) < len(word) and word_[index + len(morph) - 1] != word_[index + len(morph)]:
                    distortion = word_[:index] + morph + 'н' + word_[index + len(morph):]
                    if distortion not in distortions and distortion != word:
                        distortions.add(distortion)
                        do_distortion(distortion)
            index += len(morph)
            
    distortions = set()
    do_distortion(word)
    return distortions

silent_consonants_dict = {'стн':'сн',
                          'стл':'сл',
                          'ндш':'нш',
                          'ндц':'нц',
                          'нтг':'нг',
                          'здн':'зн',
                          'здц':'зц',
                          'рдц':'рц',
                          'рдч':'рч',
                          'лнц':'нц',
                          'вств':'ств'}

def silent_consonants_distortion(word: str, morphs_list: List[str]=[]) -> Set[str]:
    def do_distortion(word_: str) -> None:
        for key, value in silent_consonants_dict.items():
            distortion = word_.replace(key, value, 1)
            if distortion not in distortions and distortion != word:
                distortions.add(distortion)
                do_distortion(distortion)
        if len(distortions) == 0:
            for key, value in silent_consonants_dict.items():
                distortion = word_.replace(value, key, 1)
                if distortion not in distortions and distortion != word:
                    distortions.add(distortion)
                    do_distortion(distortion)
    
    distortions = set()
    do_distortion(word)
    return distortions

def hard_sign_distortion(word: str, morphs_list: List[str]=[]) -> Set[str]:
    if 'ъ' in set(word):
        return {word.replace('ъ', 'ь', 1)}
    return set()

def hyphen_distortion(word: str, morphs_list: List[str]=[]) -> Set[str]:
    if '-' in set(word):
        return {word.replace('-', ' '), word.replace('-', '')}
    return set()


# Основная функция сложности слова
def create_distortions(word: str, lemma: str, min_amount: int=3, max_amount: int=6) -> List[str]:
    morphs_list=get_morphs_list(lemma)    
    distortions = set([word])
    
    def do_function(func, stress: bool=False) -> None:
        result = set()
        amount = (max_amount // len(distortions)) - 1
        for distortion in distortions:
            created_distortions = set()
            if stress:
                if word in stress_df.index:
                    stress_word = stress_df.loc[word]['stress']
                    created_distortions = func(distortion, stress_word, morphs_list)
            else:
                created_distortions = func(distortion, morphs_list)
            new_distortions = created_distortions - distortions - result
            result.update(get_n_best_words(new_distortions, max_amount=amount))
        distortions.update(result)     

    do_function(roots_distortion)
    do_function(prefixs_distortion)
    do_function(vowels_after_prefixs_distortion)
    do_function(postfixs_distortion)
    do_function(consonants_distortion)
    do_function(hard_sign_distortion)
    do_function(two_in_row_distortion)
    do_function(duplicate_distortion)
    do_function(silent_consonants_distortion)
    do_function(hyphen_distortion)
    do_function(stress_vowels_distortion, True)
    
    if len(distortions) < min_amount:
        return []
    distortions.remove(word)
    return list(distortions)


# Функции анализа искажений .txt
def countplot_distortions_df(distortions_df: pd.DataFrame) -> None:
    print('Всего слов: {}'.format(len(distortions_df)))
    print('Слов без искажений: {}'.format(len(distortions_df[distortions_df['distortions_amount'] == 0])))
    print('Слов с искажениями: {}'.format(len(distortions_df[distortions_df['distortions_amount'] != 0])))
    
    plt.rc('font', size=13)
    
    fig, ax = plt.subplots(figsize=(8, 4))
    
    sns.countplot(x=distortions_df[distortions_df['distortions_amount'] != 0]['distortions_amount'])
    ax.set_title('Количество слов с определенном количеством искажений')
    ax.set_ylabel('Количество слов')
    ax.set_xlabel('Количество искажений')
    
    plt.show()
    
def analyze_distortions(filepath: str, stop=None, show_plot=True) -> pd.DataFrame:
    distortions_df = pd.DataFrame(columns=['distortions', 'distortions_amount'])
    with open(filepath, 'rb') as f:
        for i, word in enumerate(tqdm(f.read().decode('utf-8').split())):
            word = transform_word(word)[0]
            if word and word not in distortions_df.index and word.find('-') < 0:
                difficulty = word_difficulty(word)
                if 0.5 <= difficulty['difficulty']:
                    distortions = create_distortions(word, difficulty['lemma'])
                    info = {'distortions': distortions,
                            'distortions_amount': len(distortions),
                            'difficulty': difficulty['difficulty']}
                    row = pd.Series(info, name=word)
                    distortions_df = distortions_df.append(row)
            if stop and stop <= i:
                break
    if show_plot:
        countplot_distortions_df(distortions_df)
    return distortions_df