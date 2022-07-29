from typing import List
import random

def create_distortions(word: str) -> List[str]:
    distortions = []
    for i in range(random.randint(1, 3)):
        distortions.append(word + str(i))
    return distortions