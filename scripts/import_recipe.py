#!/usr/bin/env python3
import os
import sys
import re
import json
import subprocess
import urllib.request
import textwrap

# Ensure required libraries are installed
try:
    import requests
    from bs4 import BeautifulSoup
    from recipe_scrapers import scrape_me
except ImportError:
    print("Missing required scraping libraries (requests, beautifulsoup4, recipe-scrapers).")
    choice = input("Would you like to install them automatically using pip? [Y/n]: ").strip().lower()
    if choice in ('', 'y', 'yes'):
        try:
            print("Installing dependencies...")
            subprocess.run([sys.executable, "-m", "pip", "install", "requests", "beautifulsoup4", "recipe-scrapers"], check=True)
            print("Dependencies installed successfully!\n")
            # Import again after installation
            import requests
            from bs4 import BeautifulSoup
            from recipe_scrapers import scrape_me
        except subprocess.CalledProcessError as e:
            print(f"Error installing dependencies: {e}")
            sys.exit(1)
    else:
        print("Please manually install the dependencies: pip install requests beautifulsoup4 recipe-scrapers")
        sys.exit(1)

# List of all categories with their keywords for scoring
CATEGORY_KEYWORDS = {
    'Recipes/Breakfast': ['breakfast', 'waffle', 'egg', 'pancake', 'granola', 'crepe', 'toast', 'oatmeal'],
    'Recipes/Baking/Breads': ['bread', 'bun', 'loaf', 'yeast', 'roll', 'sourdough', 'focaccia', 'brioche', 'flatbread', 'naan', 'cornbread'],
    'Recipes/Baking/Cookies': ['cookie', 'biscuit', 'pecan bar', 'lemon bar', 'brownie'],
    'Recipes/Desserts': ['dessert', 'cake', 'pie', 'cheesecake', 'marshmallow', 'chocolate', 'sweet', 'crisp', 'tart', 'pudding'],
    'Recipes/Entrees/Poultry': ['chicken', 'turkey', 'poultry', 'duck', 'chicken wing', 'wings'],
    'Recipes/Entrees/Beef': ['beef', 'steak', 'brisket', 'prime rib', 'short rib', 'ribeye', 'meatball', 'hamburger', 'burger'],
    'Recipes/Entrees/Pork': ['pork', 'ham', 'bacon', 'tenderloin', 'pork chop', 'ribs', 'sausage'],
    'Recipes/Entrees/Seafood': ['shrimp', 'fish', 'salmon', 'tuna', 'seafood', 'prawn', 'cod', 'lobster', 'crab', 'halibut', 'seafood'],
    'Recipes/Entrees/Pasta': ['pasta', 'spaghetti', 'lasagna', 'penne', 'macaroni', 'noodle', 'gnocchi', 'orzo', 'linguine', 'ziti'],
    'Recipes/Entrees/Lamb': ['lamb', 'mutton', 'lamb chop', 'gyros'],
    'Recipes/Entrees/Veg': ['vegetarian', 'vegan', 'tofu', 'eggplant', 'paneer', 'falafel'],
    'Recipes/Entrees/Misc': ['entree', 'dinner', 'taco', 'quesadilla', 'stromboli', 'pepper', 'curry'],
    'Recipes/Sauces': ['sauce', 'pesto', 'gravy', 'dressing', 'marinade', 'mayo', 'tzatziki', 'aioli', 'chimichurri', 'teriyaki', 'buffalo'],
    'Recipes/Dips-Salsa-Chutneys': ['dip', 'salsa', 'chutney', 'guacamole', 'hummus', 'queso', 'spinach dip'],
    'Recipes/SoupsAndStews': ['soup', 'stew', 'chowder', 'chili', 'gumbo', 'bouillabaisse', 'ramen', 'broth'],
    'Recipes/Salads': ['salad', 'coleslaw', 'caesar salad'],
    'Recipes/Sides': ['side', 'potato', 'vegetable', 'rice', 'beans', 'asparagus', 'corn', 'zucchini', 'brussels sprouts', 'fiddleheads', 'spaetzle', 'garlic knot'],
    'Recipes/PicklesAndPreserves': ['pickle', 'preserve', 'jam', 'jelly', 'kimchi', 'sauerkraut'],
    'Recipes/Barbecue/Sauces': ['bbq sauce', 'barbecue sauce'],
    'Recipes/Barbecue/SpiceRubs': ['rub', 'spice mix', 'seasoning'],
    'Recipes/AirFryer': ['air fryer', 'airfryer'],
    'Recipes/InstantPot': ['instant pot', 'ip', 'pressure cooker'],
    'Recipes/Sous-Vide': ['sous vide', 'sousvide'],
    'Recipes/SmokedAndCured': ['smoked', 'cured', 'jerky', 'bacon curing'],
    'Recipes/Canapes-Tapas': ['canape', 'tapas', 'skewer', 'crostini', 'bruschetta', 'appetizer', 'jalapeno poppers', 'potato skins'],
}

def to_pascal_case(title):
    # Remove special characters, keep alphanumeric and spaces
    clean = re.sub(r'[^a-zA-Z0-9\s-]', '', title)
    words = re.split(r'[\s-]+', clean)
    return "".join(w.capitalize() for w in words if w)

def to_title_case(title):
    # Clean spacing and capitalize each word
    words = title.strip().split()
    return " ".join(w.capitalize() for w in words if w)

def clean_html(text):
    if not text:
        return ""
    # Strip HTML tags
    clean = re.sub(r'<[^>]*>', '', text)
    # Unescape HTML entities
    import html
    clean = html.unescape(clean)
    return clean.strip()

def scrape_schema_json_ld(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        json_ld_schemas = soup.find_all('script', type='application/ld+json')
        recipe_data = None
        for schema in json_ld_schemas:
            try:
                # Clean contents
                content = schema.string
                if not content:
                    continue
                data = json.loads(content)
                
                # Check for Recipe in list, dict, or @graph
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and item.get('@type') == 'Recipe':
                            recipe_data = item
                            break
                elif isinstance(data, dict):
                    if data.get('@type') == 'Recipe':
                        recipe_data = data
                    elif '@graph' in data:
                        for item in data['@graph']:
                            if isinstance(item, dict) and item.get('@type') == 'Recipe':
                                recipe_data = item
                                break
                if recipe_data:
                    break
            except Exception:
                continue
                
        if recipe_data:
            title = recipe_data.get('name', '')
            ingredients = [clean_html(ing) for ing in recipe_data.get('recipeIngredient', []) if ing]
            
            raw_instructions = recipe_data.get('recipeInstructions', [])
            instructions = []
            if isinstance(raw_instructions, list):
                for step in raw_instructions:
                    if isinstance(step, dict):
                        if step.get('@type') == 'HowToStep':
                            instructions.append(clean_html(step.get('text', '')))
                        elif step.get('@type') == 'HowToSection':
                            for substep in step.get('itemListElement', []):
                                if isinstance(substep, dict):
                                    instructions.append(clean_html(substep.get('text', '')))
                    elif isinstance(step, str):
                        instructions.append(clean_html(step))
            elif isinstance(raw_instructions, str):
                instructions = [clean_html(raw_instructions)]
                
            yields = recipe_data.get('recipeYield', '')
            if isinstance(yields, list):
                yields = yields[0] if yields else ''
            yields = clean_html(str(yields))
                
            prep_time = recipe_data.get('prepTime', '')
            cook_time = recipe_data.get('cookTime', '')
            total_time = recipe_data.get('totalTime', '')
            
            def parse_duration(d):
                if not d or not isinstance(d, str): return ''
                m = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?', d)
                if not m: return d
                hours, minutes = m.groups()
                res = []
                if hours: res.append(f"{hours} minute" if int(hours) == 0 else f"{hours} hour" + ("s" if int(hours)>1 else ""))
                if minutes: res.append(f"{minutes} minute" + ("s" if int(minutes)>1 else ""))
                return ' '.join(res) if res else d
                
            return {
                'title': title,
                'ingredients': ingredients,
                'instructions': instructions,
                'yields': parse_duration(yields) if isinstance(yields, str) and yields.startswith('PT') else yields,
                'prep_time': parse_duration(prep_time),
                'cook_time': parse_duration(cook_time),
                'total_time': parse_duration(total_time)
            }
    except Exception as e:
        print(f"DEBUG: Schema extractor failed: {e}")
    return None

def fetch_recipe(url):
    print(f"Scraping {url}...")
    
    # Method 1: recipe-scrapers (with wild mode)
    try:
        scraper = scrape_me(url, wild_mode=True)
        title = scraper.title()
        ingredients = [clean_html(ing) for ing in scraper.ingredients() if ing]
        instructions = [clean_html(step) for step in scraper.instructions_list() if step]
        
        # Safe yields fetch
        yields = ""
        try: yields = scraper.yields()
        except Exception: pass
        
        total_time = ""
        try: total_time = f"{scraper.total_time()} minutes" if isinstance(scraper.total_time(), int) else str(scraper.total_time())
        except Exception: pass
        
        prep_time = ""
        try: prep_time = f"{scraper.prep_time()} minutes" if isinstance(scraper.prep_time(), int) else str(scraper.prep_time())
        except Exception: pass
        
        cook_time = ""
        try: cook_time = f"{scraper.cook_time()} minutes" if isinstance(scraper.cook_time(), int) else str(scraper.cook_time())
        except Exception: pass
        
        # Check if we got valid ingredients/instructions, otherwise fall back
        if len(ingredients) > 0 and len(instructions) > 0:
            return {
                'title': title,
                'ingredients': ingredients,
                'instructions': instructions,
                'yields': yields,
                'prep_time': prep_time,
                'cook_time': cook_time,
                'total_time': total_time
            }
    except Exception as e:
        print(f"Warning: Primary scraper failed ({e}). Trying fallback schema extractor...")

    # Method 2: Schema.org JSON-LD extractor
    schema_data = scrape_schema_json_ld(url)
    if schema_data and len(schema_data['ingredients']) > 0:
        return schema_data
        
    print("Error: Could not extract recipe from the URL. Please verify the URL or try another recipe site.")
    sys.exit(1)

def guess_category(recipe, repo_path):
    title = recipe['title']
    ingredients = recipe['ingredients']
    text = (title + ' ' + ' '.join(ingredients)).lower()
    
    scores = {cat: 0 for cat in CATEGORY_KEYWORDS}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        # Verify that category path actually exists in repo
        cat_path = os.path.join(repo_path, cat)
        if not os.path.exists(cat_path):
            continue
            
        for kw in keywords:
            if kw in text:
                scores[cat] += 3 if kw in title.lower() else 1
                
    # Sort categories by score
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    if sorted_scores[0][1] > 0:
        return sorted_scores[0][0]
    return None

def choose_category_manually(repo_path):
    print("\nAvailable Categories:")
    # Find all categories under Recipes that actually have index files
    categories = []
    for root, dirs, files in os.walk(os.path.join(repo_path, 'Recipes')):
        if 'Recipes.rst' in files:
            rel_path = os.path.relpath(root, repo_path)
            categories.append(rel_path)
            
    categories.sort()
    for idx, cat in enumerate(categories, 1):
        print(f"{idx:2d}. {cat}")
        
    while True:
        try:
            choice = input(f"\nSelect a category number [1-{len(categories)}]: ").strip()
            num = int(choice)
            if 1 <= num <= len(categories):
                return categories[num - 1]
        except ValueError:
            pass
        print(f"Invalid choice. Please enter a number between 1 and {len(categories)}.")

def get_overlap_score(title1, title2):
    stop_words = {'with', 'and', 'in', 'of', 'the', 'a', 'an', 'on', 'for', 'to', 'at', 'by', 'from', 'style', 'easy', 'quick', 'best', 'simple', 'perfect'}
    words1 = set(re.sub(r'[^a-z0-9\s]', '', title1.lower()).split()) - stop_words
    words2 = set(re.sub(r'[^a-z0-9\s]', '', title2.lower()).split()) - stop_words
    return len(words1.intersection(words2))

def pascal_case_to_title(filename):
    # Convert 'DavesCajunSpiceMix.rst' to 'Daves Cajun Spice Mix'
    name = filename[:-4] if filename.endswith('.rst') else filename
    # Insert space before capital letters
    spaced = re.sub(r'(?<!^)(?=[A-Z])', ' ', name)
    return spaced

def parse_existing_includes(recipes_rst_path):
    if not os.path.exists(recipes_rst_path):
        return []
        
    with open(recipes_rst_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Find all includes, ignoring page breaks
    include_pattern = re.compile(r'^\.\.\s+include::\s+([^./\s][^/\s]*\.rst)\s*$', re.MULTILINE)
    matches = include_pattern.findall(content)
    
    recipes = []
    for m in matches:
        if 'recipePageBreak.rst' not in m:
            recipes.append({
                'filename': m,
                'title': pascal_case_to_title(m)
            })
    return recipes

def determine_insertion_point(new_title, existing_recipes):
    if not existing_recipes:
        return None, "empty"
        
    max_score = 0
    best_idx = -1
    
    # Calculate word overlap scores
    for idx, rec in enumerate(existing_recipes):
        score = get_overlap_score(new_title, rec['title'])
        if score > max_score:
            max_score = score
            best_idx = idx
        elif score == max_score and max_score > 0:
            # If tied, place it at the end of the matching group
            best_idx = idx
            
    if max_score > 0:
        recommended_after = existing_recipes[best_idx]
        return recommended_after['filename'], "recommended"
        
    # No matches found: place at end by default
    return existing_recipes[-1]['filename'], "default_end"

def generate_recipe_rst(recipe, url):
    title = to_title_case(recipe['title'])
    underline = "=" * len(title)
    
    # Table grid
    prep = recipe['prep_time']
    total = recipe['total_time']
    cook = recipe['cook_time']
    yields = recipe['yields']
    
    # Determine the best cook/total representation
    total_representation = total if total else (cook if cook else "")
    
    parts = []
    if prep: parts.append(f"Prep: {prep}")
    if total_representation: parts.append(f"Total: {total_representation}")
    if yields: parts.append(f"Yield: {yields}")
    
    grid_table = ""
    if parts:
        col_lengths = [len(p) + 2 for p in parts]
        top_line = "+" + "+".join("-" * l for l in col_lengths) + "+"
        content_line = "|" + "|".join(f" {p} ".ljust(l) for p, l in zip(parts, col_lengths)) + "|"
        grid_table = f"{top_line}\n{content_line}\n{top_line}\n\n"
        
    # Source line
    source_line = f"Source: `{clean_html(title)} <{url}>`__\n\n"
    
    # Ingredients formatting
    ingredients_str = "Ingredients\n-----------\n\n"
    for ing in recipe['ingredients']:
        # Format as reStructuredText bullet
        clean_ing = clean_html(ing)
        # Strip existing leading bullets if scraped
        clean_ing = re.sub(r'^[\s\-\*\•\d\.]+', '', clean_ing).strip()
        ingredients_str += f"- {clean_ing}\n"
    ingredients_str += "\n"
    
    # Directions formatting
    directions_str = ""
    if recipe['instructions']:
        directions_str = "Directions\n----------\n\n"
        for idx, step in enumerate(recipe['instructions'], 1):
            clean_step = clean_html(step)
            # Remove leading numbers if scraped
            clean_step = re.sub(r'^\d+[\.\s]+', '', clean_step).strip()
            
            # Format and wrap the step, keeping 3 spaces indent for subsequent lines
            wrapped = textwrap.wrap(clean_step, width=80)
            if wrapped:
                directions_str += f"{idx}. {wrapped[0]}\n"
                for line in wrapped[1:]:
                    directions_str += f"   {line}\n"
        directions_str += "\n"
        
    # Assemble complete document
    rst = f"{title}\n{underline}\n\n"
    rst += grid_table
    rst += source_line
    rst += ingredients_str
    rst += directions_str
    
    return rst

def update_recipes_index_file(recipes_rst_path, new_filename, relative_page_break_path, insert_after_filename=None, insert_at_beginning=False, insert_at_end=False):
    with open(recipes_rst_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    include_pattern = re.compile(r'^\.\.\s+include::\s+([^./\s][^/\s]*\.rst)\s*$', re.MULTILINE)
    page_break_pattern = re.compile(r'recipePageBreak\.rst')
    
    recipe_includes = []
    for idx, line in enumerate(lines):
        m = include_pattern.match(line)
        if m and not page_break_pattern.search(line):
            recipe_includes.append({
                'filename': m.group(1),
                'line_num': idx,
                'line_content': line
            })
            
    new_include_str = f".. include:: {new_filename}\n"
    page_break_str = f".. include:: {relative_page_break_path}\n"
    
    if not recipe_includes:
        # Index is empty, just append to index
        lines.append("\n" + new_include_str + "\n")
    else:
        if insert_at_beginning:
            # Place at index 0 (very first include)
            first_include_idx = recipe_includes[0]['line_num']
            insertion = [
                new_include_str,
                "\n",
                page_break_str,
                "\n"
            ]
            lines[first_include_idx:first_include_idx] = insertion
        elif insert_at_end:
            # Place after the last include
            last_include_idx = recipe_includes[-1]['line_num']
            # Search for page break line following the last include
            has_page_break = False
            for idx in range(last_include_idx + 1, len(lines)):
                if page_break_pattern.search(lines[idx]):
                    has_page_break = True
                    last_include_idx = idx
                    break
                    
            insertion = []
            if not has_page_break:
                insertion.append("\n")
                insertion.append(page_break_str)
            insertion.append("\n")
            insertion.append(new_include_str)
            lines[last_include_idx + 1:last_include_idx + 1] = insertion
        else:
            # Find the specific include line to place after
            target_idx = None
            for idx, rec in enumerate(recipe_includes):
                if rec['filename'] == insert_after_filename:
                    target_idx = idx
                    break
                    
            if target_idx is None:
                # Fallback to end if target not found
                return update_recipes_index_file(recipes_rst_path, new_filename, relative_page_break_path, insert_at_end=True)
                
            target_line_num = recipe_includes[target_idx]['line_num']
            
            # Find next include line number
            next_include_line_num = len(lines)
            if target_idx + 1 < len(recipe_includes):
                next_include_line_num = recipe_includes[target_idx + 1]['line_num']
                
            # Check for page break line in between
            page_break_line_num = None
            for idx in range(target_line_num + 1, next_include_line_num):
                if page_break_pattern.search(lines[idx]):
                    page_break_line_num = idx
                    break
                    
            if page_break_line_num is not None:
                # Place after the existing page break
                insertion = [
                    "\n",
                    new_include_str,
                    "\n",
                    page_break_str
                ]
                lines[page_break_line_num + 1:page_break_line_num + 1] = insertion
            else:
                # No page break found, insert one along with the include
                insertion = [
                    "\n",
                    page_break_str,
                    "\n",
                    new_include_str
                ]
                lines[target_line_num + 1:target_line_num + 1] = insertion
                
    # Write updated index back
    with open(recipes_rst_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

def main():
    print("=" * 60)
    print("          Cookbook Recipe Importer (Web-to-RST)")
    print("=" * 60)
    
    # 1. Ask for Recipe URL
    url = input("Enter the Recipe URL: ").strip()
    if not url:
        print("Error: URL cannot be empty.")
        sys.exit(1)
        
    # Get repo root path
    # Assume the scripts/ folders is located in the repo root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_path = os.path.abspath(os.path.join(script_dir, ".."))
    
    # 2. Fetch and parse recipe
    recipe = fetch_recipe(url)
    print(f"\nSuccessfully extracted: \"{recipe['title']}\"")
    
    # 3. Guess Category
    guessed_cat = guess_category(recipe, repo_path)
    category = None
    
    if guessed_cat:
        print(f"\nI guessed this recipe fits best in: {guessed_cat}")
        ans = input("Is this correct? [Y/n]: ").strip().lower()
        if ans in ('', 'y', 'yes'):
            category = guessed_cat
            
    if not category:
        print("\nCould not determine category automatically or suggestion was rejected.")
        category = choose_category_manually(repo_path)
        
    print(f"\nTarget Category Folder: {category}")
    
    # Calculate file paths
    category_dir = os.path.join(repo_path, category)
    pascal_name = to_pascal_case(recipe['title'])
    recipe_filename = f"{pascal_name}.rst"
    recipe_file_path = os.path.join(category_dir, recipe_filename)
    recipes_rst_path = os.path.join(category_dir, "Recipes.rst")
    
    # Make sure we don't overwrite an existing file without confirmation
    if os.path.exists(recipe_file_path):
        ans = input(f"\nWarning: File '{recipe_filename}' already exists. Overwrite? [y/N]: ").strip().lower()
        if ans not in ('y', 'yes'):
            print("Import cancelled.")
            sys.exit(0)
            
    # 4. Determine insertion point in Recipes.rst
    existing_recipes = parse_existing_includes(recipes_rst_path)
    insert_after_filename, insert_type = determine_insertion_point(recipe['title'], existing_recipes)
    
    insert_action = "end"
    if insert_type == "recommended" and insert_after_filename:
        # We have a recommendation
        recommended_title = pascal_case_to_title(insert_after_filename)
        print(f"\nRecommended Placement: Place after \"{recommended_title}\"")
        print("  (Matches similar recipes to group them logically together)")
        print("\nWhere would you like to place it?")
        print(f"1. Accept recommendation (after \"{recommended_title}\") [Default]")
        print("2. Place at the very beginning of the section")
        print("3. Place at the very end of the section")
        print("4. Manually choose which recipe to place after")
        
        choice = input("Select option [1-4]: ").strip()
        if choice in ('', '1'):
            insert_action = "recommended"
        elif choice == '2':
            insert_action = "beginning"
        elif choice == '3':
            insert_action = "end"
        elif choice == '4':
            insert_action = "manual"
    else:
        # No recommendation available
        print("\nCould not automatically find a similar recipe group.")
        print("\nWhere would you like to place it?")
        print("1. Place at the very end of the section [Default]")
        print("2. Place at the very beginning of the section")
        print("3. Manually choose which recipe to place after")
        
        choice = input("Select option [1-3]: ").strip()
        if choice in ('', '1'):
            insert_action = "end"
        elif choice == '2':
            insert_action = "beginning"
        elif choice == '3':
            insert_action = "manual"
            
    # Handle manual selection
    if insert_action == "manual":
        print("\nRecipes in this section:")
        print(" 0. [Place at the very beginning]")
        for idx, rec in enumerate(existing_recipes, 1):
            print(f"{idx:2d}. {rec['title']}")
            
        while True:
            try:
                choice = input(f"Place after recipe number [0-{len(existing_recipes)}]: ").strip()
                num = int(choice)
                if num == 0:
                    insert_action = "beginning"
                    break
                elif 1 <= num <= len(existing_recipes):
                    insert_after_filename = existing_recipes[num - 1]['filename']
                    insert_action = "recommended"
                    break
            except ValueError:
                pass
            print(f"Invalid entry. Enter a number between 0 and {len(existing_recipes)}.")

    # 5. Generate and write the recipe RST content
    rst_content = generate_recipe_rst(recipe, url)
    with open(recipe_file_path, 'w', encoding='utf-8') as f:
        f.write(rst_content)
    print(f"\nWritten recipe file: {os.path.relpath(recipe_file_path, repo_path)}")
    
    # 6. Calculate relative page break path
    # Depth calculation relative to 'Recipes/' folder
    # e.g., 'Recipes/Breakfast' depth is 2 elements relative to repo root, relative to Breakfast is '../..'
    parts = category.split(os.sep)
    # depth counts how many levels we need to go up to reach repo root
    # e.g. Recipes/Breakfast -> parts=['Recipes', 'Breakfast'] (length 2)
    # Relative path is '../../includes/recipePageBreak.rst'
    depth = len(parts)
    up_path = "/".join(".." for _ in range(depth))
    relative_page_break_path = f"{up_path}/includes/recipePageBreak.rst"
    
    # 7. Update index Recipes.rst
    if insert_action == "beginning":
        update_recipes_index_file(recipes_rst_path, recipe_filename, relative_page_break_path, insert_at_beginning=True)
    elif insert_action == "end":
        update_recipes_index_file(recipes_rst_path, recipe_filename, relative_page_break_path, insert_at_end=True)
    else:
        update_recipes_index_file(recipes_rst_path, recipe_filename, relative_page_break_path, insert_after_filename=insert_after_filename)
        
    print(f"Updated index file: {os.path.relpath(recipes_rst_path, repo_path)}")
    print("\nImport complete! The recipe is ready to be built in the Cookbook.")

if __name__ == "__main__":
    main()
