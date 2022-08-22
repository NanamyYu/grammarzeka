from collections import defaultdict


# Функция сложности слова
exec(open('scripts/word_difficulty.py').read())


# Датасеты
fullname = save_zip_csv(url='https://github.com/Koziev/NLP_Datasets/raw/master/Stress/all_accents.zip',
                        dirname='datasets/stress',
                        new_filename='all_accents.tsv')
stress_df = pd.read_csv(fullname, sep='\t', names=['Lemma', 'stress'])
stress_df = stress_df.drop_duplicates(subset=['Lemma'])
stress_df = stress_df.set_index('Lemma')

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
letter_df = letter_df.div(letter_df.max(axis=1), axis=0)


# Вспомогательные функции
def get_morphs_list(lemma: str) -> List[str]:
    if lemma not in morph_df.index:
        return []
    return list(morph_df.loc[lemma]['analysis'].split('/'))

def get_word_probability(word: str) -> int:
    probability = 0
    amount = 0
    for i in range(len(word) - 1):
        c = word[i]
        next_c = word[i + 1]
        if c in letters and next_c in letters:
            probability += letter_df.loc[c][next_c]
            amount += 1
    return probability / amount if amount else 0

def get_n_best_words(words, max_amount: int=1) -> List[str]:
    if max_amount < len(words):
        return sorted(list(words), key=lambda word: get_word_probability(word), reverse=True)[:max_amount]
    return list(words)

stress_vowels_dict = {'о':'а', 'а':'о', 'е':'и', 'и':'е', 'я':'е'}

def stress_vowels_distortion(word: str, stress_word: str, morphs_list: List[str]=[], max_amount: int=1) -> List[str]:  
    def do_distortion(word_: str, stress_word: str) -> None:
        if 0 <= stress_word.find('^') < len(stress_word) - 2:
            i = stress_word.find('^')
            stress_word = stress_word[:i] + stress_word[i + 1].upper() + stress_word[i + 2:]
        else:
            return []
        for i in range(1, len(word_) - 3):
            if i < len(stress_word) and stress_word[i] in stress_vowels_dict and stress_word[i] == word_[i]:
                distortion = word_[:i] + stress_vowels_dict[word_[i]] + word_[i + 1:]
                if distortion not in distortions and distortion != word:
                    distortions.add(distortion)
                    do_distortion(distortion, stress_word)
        
    distortions = set()
    do_distortion(word, stress_word)
    return get_n_best_words(distortions, max_amount)

deaf_consonants = set('пфктшсхцчщ')
consonants_pairs = {
    'б':'п', 
    'г':'к', 
    'д':'т', 
    'ж':'ш', 
    'з':'с', 
}

def consonants_distortion(word: str, morphs_list: List[str]=[], max_amount: int=1) -> List[str]:  
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
    return get_n_best_words(distortions, max_amount)

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
    
def roots_distortion(word: str, morphs_list: List[str]=[], max_amount: int=1) -> List[str]:
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
    return get_n_best_words(distortions, max_amount)

prefix_pairs = {'пре':'при', 'при':'пре',
                'без':'бес', 'бес':'без',
                'воз':'вос', 'вос':'воз',
                'вз':'вс', 'вс':'вз',
                'из':'ис', 'ис':'из',
                'низ':'нис', 'нис':'низ',
                'раз':'рас', 'рас':'раз',
                'роз':'рос', 'рос':'роз',
                'чрез':'чрес', 'чрес':'чрез'}

def prefixs_distortion(word: str, morphs_list: List[str]=[], max_amount: int=1) -> List[str]:
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
    return get_n_best_words(distortions, max_amount)

vowels_after_prefixs_pairs = {'и':'ы', 'ы':'и'}

def vowels_after_prefixs_distortion(word: str, morphs_list: List[str]=[], max_amount: int=1) -> List[str]:
    if 0 < max_amount and morphs_list:
        morph = morphs_list[0].replace('\'', '')
        if len(morph) < len(word) and word[len(morph)] in vowels_after_prefixs_pairs:
            distortion = word[:len(morph)] +\
                        vowels_after_prefixs_pairs[word[len(morph)]] +\
                        word[len(morph) + 1:]
            if distortion != word:
                return [distortion]
    return []

postfix_pairs = {'тся':'ться', 'ться':'тся'}

def postfixs_distortion(word: str, morphs_list: List[str]=[], max_amount: int=1) -> List[str]:
    if 0 < max_amount:
        for postfix in postfix_pairs:
            if word[-len(postfix):] == postfix:
                return [word[:-len(postfix)] + postfix_pairs[postfix]]
    return []

vowels = set('аяоёуюыиэе')

def two_in_row_distortion(word: str, morphs_list: List[str]=[], max_amount: int=1) -> List[str]:
    def do_distortion(word_: str) -> None:
        for i in range(len(word_)):
            if i > 0 and word_[i - 1] == word_[i] and word_[i] not in vowels:
                distortion = word_[:i] + word_[i + 1:]
                if distortion not in distortions and distortion != word:
                    distortions.add(distortion)
                    do_distortion(distortion)
            
    distortions = set()
    do_distortion(word)
    return get_n_best_words(distortions, max_amount)

single_suffixs = set(['ан', 'ян', 'ын', 'ин'])

def duplicate_distortion(word: str, morphs_list: List[str], max_amount: int=1) -> List[str]:
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
    return get_n_best_words(distortions, max_amount)

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

def silent_consonants_distortion(word: str, morphs_list: List[str]=[], max_amount: int=1) -> List[str]:
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
    return get_n_best_words(distortions, max_amount)

def hard_sign_distortion(word: str, morphs_list: List[str]=[], max_amount: int=1) -> List[str]:
    if 0 < max_amount and 'ъ' in set(word):
        return [word.replace('ъ', 'ь', 1)]
    return []

def hyphen_distortion(word: str, morphs_list: List[str]=[], max_amount: int=1) -> List[str]:
    if 1 < max_amount and '-' in set(word):
        return [word.replace('-', ' '), word.replace('-', '')]
    if 0 < max_amount and '-' in set(word):
        return [word.replace('-', '')]
    return []


# Основная функция сложности слова
def create_distortions(word: str, lemma: str, max_amount: int=6) -> List[str]:
    morphs_list=get_morphs_list(lemma)    
    distortions = set([word])
    
    def do_function(func, stress: bool=False) -> None:
        result = set()
        amount = (max_amount // len(distortions)) - 1
        for distortion in distortions:
            if stress:
                if word in stress_df.index:
                    stress_word = stress_df.loc[word]['stress']
                    result.update(func(distortion, stress_word, morphs_list, amount))
            else:
                result.update(func(distortion, morphs_list, amount))
        distortions.update(result)     

    do_function(roots_distortion)
    do_function(prefixs_distortion)
    do_function(vowels_after_prefixs_distortion)
    do_function(postfixs_distortion)
    do_function(two_in_row_distortion)
    do_function(duplicate_distortion)
    do_function(silent_consonants_distortion)
    do_function(hard_sign_distortion)
    do_function(hyphen_distortion)
    do_function(consonants_distortion)
    do_function(stress_vowels_distortion, True)
    
    distortions.remove(word)
    return list(distortions)

# Функции анализа искажений .txt
def countplot_distortions_df(distortions_df: pd.DataFrame) -> None:
    print('Всего слов: {}'.format(len(distortions_df)))
    print('Слов без искажений: {}'.format(len(distortions_df[distortions_df['distortions_amount'] == 0])))
    print('Слов с искажениями: {}'.format(len(distortions_df[distortions_df['distortions_amount'] != 0])))
    
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