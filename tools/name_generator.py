import random
import string

ADJECTIVES = [
    "Brave", "Happy", "Lucky", "Swift", "Cool", 
    "Fast", "Fun", "Epic", "Pro", "Star", 
    "Mega", "Super", "Wild", "Crazy", "Sly"
]

NOUNS = [
    "Cookie", "Runner", "Fox", "Wolf", "Bear",
    "Panda", "Tiger", "Lion", "Hawk", "Eagle",
    "Hero", "King", "Queen", "Boss", "Ninja"
]

def generate_random_name(min_length=3, max_length=10):
    """
    Generate a random readable name like 'FunCookie42'.
    Length will be constrained to min_length and max_length.
    """
    while True:
        adj = random.choice(ADJECTIVES)
        noun = random.choice(NOUNS)
        num = str(random.randint(1, 99))
        
        name = f"{adj}{noun}{num}"
        
        if min_length <= len(name) <= max_length:
            return name
            
        # If it's too long, just return a random string
        if len(name) > max_length:
            return ''.join(random.choices(string.ascii_letters + string.digits, k=max_length))
