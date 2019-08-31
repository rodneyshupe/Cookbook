
import json

import os
import io
#import chardet
import codecs

filename = 'recipe_data.json'
bytecount = min(32, os.path.getsize(filename))
raw = open(filename, 'rb').read(bytecount)

if raw.startswith(codecs.BOM_UTF8):
    encoding = 'utf-8-sig'
else:
    #result = chardet.detect(raw)
    #encoding = result['encoding']
    encoding = 'utf-8'

infile = io.open(filename, 'r', encoding='utf-8-sig')
data = infile.read()
infile.close()

json_data = json.loads(data)

recipes = json_data['recipeml']['recipe']
print (len(recipes))

def print_ingredient(ingredient):
    str = "- "
    if 'amt' in ingredient:
        if 'qty' in ingredient['amt']:
            str += ingredient['amt']['qty'] + " "
        if 'unit' in ingredient['amt']:
            str += ingredient['amt']['unit'] + " "
    if 'item' in ingredient:
        str += ingredient['item']
    if 'prep' in ingredient:
        str += ", " + ingredient['prep']
    str += "\n"
    return str

def print_ingredient_list(ingredients):
    str = ""
    if isinstance(ingredients, list):
        i = 0
        while i < len(ingredients):
            str += print_ingredient(ingredients[i])
            i += 1
    else:
        str += print_ingredient(ingredients)
    return str

def print_ingredient_group(ingredient_group):
    str = ingredient_group['title'] + "\n"
    str += "^"*len(ingredient_group['title']) + "\n\n"
    if 'ing' in ingredient_group:
        str += print_ingredient_list(ingredient_group['ing']) + "\n\n"
    return str


def print_directions(directions):
    str = ""
    if isinstance(directions, list):
        d = 0
        while d < len(directions):
            str += "# " + directions[d] + "\n"
            d += 1
    else:
        str += directions + "\n"
    return str

def print_directions_group(directions_group):
    str = directions_group['title'] + "\n"
    str += "^"*len(directions_group['title']) + "\n\n"
    if 'step' in directions_group:
        str += print_directions(directions_group['step']) + "\n\n"
    return str

def print_recipe(recipe):
    str = "\n.. raw:: pdf\n\n   OddPageBreak recipePage\n\n"

    str += recipe['head']['title'] + "\n"
    str += "="*len(recipe['head']['title']) + "\n\n"
    if 'description' in recipe:
        str += recipe['description'] + "\n\n"
    if 'yield' in recipe['head'] and 'qty' in recipe['head']['yield']:
        str += "Yield:" + recipe['head']['yield']['qty'] + "\n\n"

    if 'ingredients' in recipe:
        str += "Ingredients\n-----------\n\n"
        if 'ing' in recipe['ingredients']:
            str += print_ingredient_list(recipe['ingredients']['ing']) + "\n\n"
        if 'ing-div' in recipe['ingredients']:
            if isinstance(recipe['ingredients']['ing-div'], list):
                ig = 0
                while ig < len(recipe['ingredients']['ing-div']):
                    str += print_ingredient_group(recipe['ingredients']['ing-div'][ig])
                    ig += 1
            else:
                str += print_ingredient_group(recipe['ingredients']['ing-div'])

    if 'directions' in recipe:
        str += "Directions\n----------\n\n"
        if 'step' in recipe['directions']:
            str += print_directions(recipe['directions']['step']) + "\n\n"
        if 'dir-div' in recipe['directions']:
            if isinstance(recipe['directions']['dir-div'], list):
                dg = 0
                while dg < len(recipe['directions']['dir-div']):
                    str += print_directions_group(recipe['directions']['dir-div'][dg])
                    dg += 1
            else:
                str += print_directions_group(recipe['directions']['dir-div'])


    if 'note' in recipe:
        str += "Note\n----\n" + recipe['note'] + "\n\n"

    return str

cat_list = ['Appetizer', 'Barbecue Rub', 'Barbecue Sauce', 'Cocktail', 'Dessert', 'Entree', 'Salads', 'Sauce', 'Soups']


cat_list = ['Sauce']

c = 0
while c < len(cat_list):
    r = 0
    while r < len(recipes):
        cat = ""
        if 'categories' in recipes[r]['head']:
            if isinstance(recipes[r]['head']['categories']['cat'], list):
                if recipes[r]['head']['categories']['cat'][0] == 'Entree':
                    cat = recipes[r]['head']['categories']['cat'][0]
                else:
                    cat = recipes[r]['head']['categories']['cat'][0] + " " + recipes[r]['head']['categories']['cat'][1]
            else:
                cat = recipes[r]['head']['categories']['cat']
        if cat == cat_list[c]:
            print(print_recipe(recipes[r]).encode('utf-8'))
        r += 1
    c += 1
