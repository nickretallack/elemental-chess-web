#!/usr/bin/env python

"""Produces a random anonymous name.

This is a port of the make_anonymous function in the Wakaba imageboard software
and uses the same names.

You can either import this as a module, or simply run it to print a single name
to stdout.
"""

import random
from time import time

def random_name(seed=None):
    """Returns a random name.

    The only parameter is an optional seed to use.
    """

    if not seed:
        seed = time()
    random.seed(seed)

    name = "%s %s" % (_rand_first_name(), _rand_surname())

    # Be polite and reseed if this should be used as a module
    random.seed()

    return name

def _rand_first_name():
    return random.choice( [
        'Albert', 'Alice', 'Angus', 'Archie', 'Augustus', 'Barnaby', 'Basil',
        'Beatrice', 'Betsy', 'Caroline', 'Cedric', 'Charles', 'Charlotte',
        'Clara', 'Cornelius', 'Cyril', 'David', 'Doris', 'Ebenezer',
        'Edward', 'Edwin', 'Eliza', 'Emma', 'Ernest', 'Esther', 'Eugene',
        'Fanny', 'Frederick', 'George', 'Graham', 'Hamilton', 'Hannah',
        'Hedda', 'Henry', 'Hugh', 'Ian', 'Isabella', 'Jack', 'James',
        'Jarvis', 'Jenny', 'John', 'Lillian', 'Lydia', 'Martha', 'Martin',
        'Matilda', 'Molly', 'Nathaniel', 'Nell', 'Nicholas', 'Nigel',
        'Oliver', 'Phineas', 'Phoebe', 'Phyllis', 'Polly', 'Priscilla',
        'Rebecca', 'Reuben', 'Samuel', 'Sidney', 'Simon', 'Sophie',
        'Thomas', 'Walter', 'Wesley', 'William',
    ] )

def _rand_surname():
    simple = [
        _rand_surname_prefix, _rand_surname_suffix
        ]
    complex_prefix = [
        _rand_surname_start, _rand_surname_vowel, _rand_surname_prefix_end,
        _rand_surname_suffix,
        ]
    complex_both = [
        _rand_surname_start, _rand_surname_vowel, _rand_surname_prefix_end,
        _rand_surname_consonant, _rand_surname_vowel, _rand_surname_suffix_end,
        ]

    functions = random.choice( [
        simple, simple,
        complex_prefix, complex_prefix, complex_prefix, 
        complex_both, complex_both, complex_both, 
    ] )

    return ''.join([ func() for func in functions ])

def _rand_surname_prefix():
    return random.choice( [
        'Small', 'Snod', 'Bard', 'Billing', 'Black', 'Shake', 'Tilling',
        'Good', 'Worthing', 'Blythe', 'Green', 'Duck', 'Pitt', 'Grand',
        'Brook', 'Blather', 'Bun', 'Buzz', 'Clay', 'Fan', 'Dart', 'Grim',
        'Honey', 'Light', 'Murd', 'Nickle', 'Pick', 'Pock', 'Trot', 'Toot',
        'Turvey',
    ] )

def _rand_surname_suffix():
    return random.choice( [
        'shaw', 'man', 'stone', 'son', 'ham', 'gold', 'banks', 'foot', 'worth',
        'way', 'hall', 'dock', 'ford', 'well', 'bury', 'stock', 'field',
        'lock', 'dale', 'water', 'hood', 'ridge', 'ville', 'spear', 'forth',
        'will'
    ] )

def _rand_surname_vowel():
    return random.choice( ['a', 'e', 'i', 'o', 'u'] )

def _rand_surname_start():
    return random.choice( [
        'B', 'B', 'C', 'D', 'D', 'F', 'F', 'G', 'G', 'H', 'H', 'M', 'N', 'P',
        'P', 'S', 'S', 'W', 'Ch', 'Br', 'Cr', 'Dr', 'Bl', 'Cl', 'S',
    ] )

def _rand_surname_consonant():
    return random.choice( [
        'b', 'd', 'f', 'h', 'k', 'l', 'm', 'n', 'p', 's', 't', 'w', 'ch', 'st',
    ] )

def _rand_surname_prefix_end():
    return random.choice( [
        'ving', 'zzle', 'ndle', 'ddle', 'ller', 'rring', 'tting', 'nning',
        'ssle', 'mmer', 'bber', 'bble', 'nger', 'nner', 'sh', 'ffing', 'nder',
        'pper', 'mmle', 'lly', 'bling', 'nkin', 'dge', 'ckle', 'ggle', 'mble',
        'ckle', 'rry',
    ] )

def _rand_surname_suffix_end():
    return random.choice( [
        't', 'ck', 'tch', 'd', 'g', 'n', 't', 't', 'ck', 'tch', 'dge', 're',
        'rk', 'dge', 're', 'ne', 'dging', 
    ] )


if __name__ == '__main__':
    print random_name()
