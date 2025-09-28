import random

def generate_random_pokemon_id():
    """
    Generates a random National Pokédex ID.

    The range is currently set from 1 to 1025, covering all
    official Pokémon up to the end of Generation IX (Scarlet/Violet).

    Returns:
        int: A random integer representing a Pokémon's National Pokédex ID.
    """
    # The current official range of Pokémon IDs is 1 to 1025 (Gen I to Gen IX)
    min_id = 1
    max_id = 1025

    # Use random.randint() for an inclusive range
    random_id = random.randint(min_id, max_id)

    return random_id

random_pokemon = generate_random_pokemon_id()
print(f"Random Pokémon ID: {random_pokemon}")