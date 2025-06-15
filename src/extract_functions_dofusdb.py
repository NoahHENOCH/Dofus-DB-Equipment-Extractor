from requests import get as requests_get
from functools import cache as functools_cache
from re import sub as re_sub
from typing import List, Dict, Any
from utilities import threaded_execution, stop_thread, get_print_lock, json_reader, json_writer, file_exists

effects_name = json_reader("data/json/effectsName.json")


class APIError(Exception):
    """Exception raised for errors in the API response."""
    pass

class JobNotFound(Exception):
    """Exception raised when a job is not found."""
    pass

class IngredientNotFound(Exception):
    """Exception raised when an ingredient is not found in the recipe."""
    pass

class EndOfExecution(Exception):
    """Exception raised to indicate the end of execution."""
    def __init__(self):
        super().__init__("Execution terminated by user.")

def group_items_by_level(category_data: Dict[str, Any]) -> Dict[int, List[Dict[str, Any]]]:
    """Groupe les items par niveau dans une catégorie.
    
    Args:
        category_data (Dict[str, Any]): Les données de la catégorie contenant les items.
    Returns:
        Dict[int, List[Dict[str, Any]]]: Un dictionnaire où les clés sont les niveaux et les valeurs sont des listes d'items.
    """
    grouped_items = {}
    for item in category_data['items']:
        level = item['level']
        if level not in grouped_items:
            grouped_items[level] = []
        grouped_items[level].append(item)
    return grouped_items


def sort_items_by_name(tab: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Trie les items par nom.
    
    Args:
        tab (List[Dict[str, Any]]): La liste des items à trier.
    Returns:
        List[Dict[str, Any]]: La liste des items triée par nom.
    """
    return sorted(tab, key=lambda x: x['name'].lower())


def sort_grouped_items_by_name(grouped_items: Dict[int, List[Dict[str, Any]]]) -> Dict[int, List[Dict[str, Any]]]:
    """Trie les items groupés par nom.
    
    Args:
        grouped_items (Dict[int, List[Dict[str, Any]]]): Les items groupés par niveau.
    Returns:
        Dict[int, List[Dict[str, Any]]]: Les items groupés par niveau, triés par nom.
    """
    sorted_grouped_items = {}
    for level, items in grouped_items.items():
        sorted_grouped_items[level] = sort_items_by_name(items)
    return sorted_grouped_items


def sort_group_by_level(grouped_items: Dict[int, List[Dict[str, Any]]]) -> Dict[int, List[Dict[str, Any]]]:
    """Trie les groupes d'items par niveau (ordre décroissant).
    
    Args:
        grouped_items (Dict[int, List[Dict[str, Any]]]): Les items groupés par niveau.
        Returns:
        Dict[int, List[Dict[str, Any]]]: Les items groupés par niveau, triés par niveau décroissant.
    """
    return dict(sorted(grouped_items.items(), key=lambda item: item[0], reverse=True))


def flatten_items(grouped_items: Dict[int, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """Aplati les listes d'items groupés par niveau en une seule liste.
    
    Args:
        grouped_items (Dict[int, List[Dict[str, Any]]]): Les items groupés par niveau.
    Returns:
        List[Dict[str, Any]]: Une liste aplatie de tous les items triés par niveau et nom.
    """
    flat_items = []
    for items in grouped_items.values():
        flat_items.extend(items)
    return flat_items


def get_job_with_name(job_name: str, jobs: List[Dict[str, Any]]) -> Dict[str, Any]|None:
    """Retourne les informations d'un métier grâce à son nom.
    
    Args:
        job_name (str): Le nom du métier à rechercher.
        jobs (List[Dict[str, Any]]): La liste des métiers disponibles.
    Returns:
        Dict[str, Any]: Les informations du métier correspondant au nom, ou None si non trouvé.
    """
    for job in jobs:
        if job['name'] == job_name:
            return job
    return None


def get_items_data(category_id: int, level_min: int, level_max: int, skip: int) -> Dict[str, Any]:
    """Récupère les données des items d'une catégorie depuis l'API.
    
    Args:
        category_id (int): L'ID de la catégorie d'items.
        level_min (int): Le niveau minimum des items à récupérer.
        level_max (int): Le niveau maximum des items à récupérer.
        skip (int): Le nombre d'items à ignorer pour la pagination.
    Returns:
        Dict[str, Any]: Les données des items récupérées depuis l'API.
    Raises:
        APIError: Si une erreur se produit lors de la récupération des données depuis l'API.
    """
    url = "https://api.dofusdb.fr/items"
    params = {
        'typeId[$ne]': 203,  # Exclure les items de type 203
        'typeId[$in][]': category_id,
        'level[$gte]': level_min,
        'level[$lte]': level_max,
        '$sort': '-level',  # Tri par niveau décroissant
        '$skip': skip,      # Pagination
        'lang': 'fr'        # Langue de la réponse
    }
    response = requests_get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        raise APIError(f"Error fetching data from API: {response.status_code}")


@functools_cache
def clean_effect_name(baseeffect_name: str) -> str:
    """Supprime les # suivis d'un chiffre (1, 2 ou 3) et le contenu entre accolades {} dans le nom d'effet.

    Args:
        effect_name (str): Le nom d'effet à nettoyer.
    Returns:
        str: Le nom d'effet nettoyé.
    """
    # Supprimer les # suivis de 1, 2 ou 3
    effect_name = re_sub(r'#([1-3])', '', baseeffect_name)
    # Supprimer le contenu entre accolades {}
    effect_name = re_sub(r'\{[^\}]*\}', '', effect_name)
    # Supprimer le contenu entre des <> (par exemple, <sprite name="feu">)
    effect_name = re_sub(r'<.*> ', '', effect_name)
    # Supprimer les accolades restantes
    effect_name = str.replace(effect_name, '}', '')
    effect_name = re_sub(r'Dommages?', 'Dommages', effect_name)
    # Nettoyer les espaces superflus    
    return effect_name.strip()


@functools_cache
def get_effect_name(effect_id: int) -> str:
    """Récupère les informations d'un effet par son ID.
    
    Args:
        effect_id (int): L'ID de l'effet à récupérer.
    Returns:
        str: Le nom de l'effet en français.
    Raises:
        APIError: Si une erreur se produit lors de la récupération des données depuis l'API.
    """
    url = "https://api.dofusdb.fr/effects/"+str(effect_id)
    response = requests_get(url)
    if response.status_code == 200:
        data = response.json()
        return data["description"]["fr"]
    else:
        raise APIError(f"Error fetching data from API: {response.status_code}")



def effects_management(item: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Gère les effets d'un item.
    
    Args:
        item (Dict[str, Any]): Les données de l'item à traiter.
    Returns:
        List[Dict[str, Any]]: Une liste de dictionnaires contenant les effets nettoyés de l'item.
    """
    effects = item['effects']
    res = []
    global effects_name

    for effect in effects:
        effect_val1, effect_val2 = effect['from'], effect['to']
        effect_name = clean_effect_name(get_effect_name(effect['effectId']))
        if effect_name == "Arme de chasse":
            effect_val1, effect_val2 = 1, 1
        if effect_val1 < 0 or (effect_val1 == 0 and effect_val2 == 0) or (effect_name not in effects_name):
            continue
        if effect_val2 == 0:
            effect_val2 = effect_val1
        res.append({'name': effect_name, 'value1': effect_val1, 'value2': effect_val2})
    return res


@functools_cache
def get_recipe_data(item_id: int) -> Dict[str, Any]:
    """Récupère les données de la recette d'un item par son ID depuis l'API.
    
    Args:
        item_id (int): L'ID de l'item pour lequel récupérer la recette.
    Returns:
        Dict[str, Any]: Les données de la recette de l'item.
    Raises:
        APIError: Si une erreur se produit lors de la récupération des données depuis l'API.
    """
    url = f"https://api.dofusdb.fr/recipes/{item_id}"
    response = requests_get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise APIError(f"Error fetching recipe data from API: {response.status_code}")


def get_ingredient_with_id(ingredient_id: int, ingredients: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Retourne les données d'un ingrédient dans la recette par son ID.
    
    Args:
        ingredient_id (int): L'ID de l'ingrédient à rechercher.
        recipe_data (Dict[str, Any]): Les données de la recette de l'item.
    Returns:
        Dict[str, Any]: Les données de l'ingrédient correspondant à l'ID.
    Raises:
        IngredientNotFound: Si l'ingrédient n'est pas trouvé dans la recette.
    """
    for ingredient in ingredients:
        if ingredient['id'] == ingredient_id:
            return ingredient
    raise IngredientNotFound(f"Ingredient with ID {ingredient_id} not found in recipe.")


@functools_cache
def recipe_management(item_id: int) -> List[Dict[str, Any]]:
    """Récupère la recette d'un item par son ID.

    Args:
        item_id (int): L'ID de l'item pour lequel récupérer la recette.
    Returns:
        List[Dict[str, Any]]: Une liste de dictionnaires contenant les ingrédients de la recette.
    Raises:
        APIError: Si une erreur se produit lors de la récupération des données depuis l'API.
    """
    recipe_data = get_recipe_data(item_id)
    res = {"job": recipe_data['job']['name']['fr'], "ingredients": []}
    for i in range(len(recipe_data['ingredientIds'])):
        quantity = recipe_data['quantities'][i]
        ingredient_id = recipe_data['ingredientIds'][i]
        ingredient_data = get_ingredient_with_id(ingredient_id, recipe_data['ingredients'])
        ingredient_recipe = None
        ingredient_has_recipe = ingredient_data['hasRecipe']
        ingredient_secret_recipe = ingredient_data['secretRecipe']
        ingredient_name = ingredient_data['name']['fr']
        if ingredient_has_recipe:
            ingredient_recipe = recipe_management(ingredient_id)
        res['ingredients'].append({
            'name': ingredient_name,
            'quantity': quantity,
            'hasRecipe': ingredient_has_recipe,
            'secretRecipe': ingredient_secret_recipe,
            'recipe' : ingredient_recipe
        })
    return res


def item_management(item: Dict[str, Any], jobs_data: Dict[str, Any]) -> None:
    """Gère un item individuel.
    
    Args:
        item (Dict[str, Any]): Les données de l'item à traiter.
        jobs_data (Dict[str, Any]): Listes des items récupérés avec les données nécessaires d'un job.
    """
    if (item['hasRecipe']) and  (item['isDestructible']) and (not item['secretRecipe']):
        effects = effects_management(item)
        if (len(effects) == 0):
            return
        recipes = recipe_management(item['id'])
        item_data = {'name': item['name']['fr'], 'level': item['level'], 'effects': effects, 'img': item['img'], "recipes": recipes}
        jobs_data['items'].append(item_data)


def items_management(data : Dict[str, Any], jobs_data: Dict[str, Any]) -> None:
    """Gère les items d'une catégorie.

    Args:
        data (Dict[str, Any]): Les données des items récupérées depuis l'API.
        jobs_data (Dict[str, Any]): Listes des items récupérés avec les données nécessaires d'un job.
    """
    for item in data['data']:
        item_management(item, jobs_data)


def category_management(category_id: int, level_min: int, level_max: int, jobs_data: Dict[str, Any]) -> None:
    """Gère la catégorie d'items avec l'ID donné.
    
    Args:
        category_id (int): L'ID de la catégorie d'items à traiter.
        level_min (int): Le niveau minimum des items à récupérer.
        level_max (int): Le niveau maximum des items à récupérer.
        jobs_data (Dict[str, Any]): Listes des items récupérés avec les données nécessaires d'un job.
    """
    data = get_items_data(category_id, level_min, level_max, 0)
    total = data['total']
    items_management(data, jobs_data)
    for i in range(10, total+1, 10):
        data = get_items_data(category_id, level_min, level_max, i)
        items_management(data, jobs_data)

        
def job_management(job_name: str, level_min: int, level_max: int, jobs: List[Dict[str, Any]], results: List[Dict[str, Any]]) -> None:
    """Gère un métier spécifique récupéré avec son nom et traite les catégories associées.
    
    Args:
        job_name (str): Le nom du métier à traiter.
        level_min (int): Le niveau minimum des items à récupérer.
        level_max (int): Le niveau maximum des items à récupérer.
        jobs (List[Dict[str, Any]]): La liste des métiers disponibles avec une liste de catégories.
        results (List[Dict[str, Any]]): La liste des résultats à remplir avec les données des métiers.
    Raises:
        JobNotFound: Si le métier avec le nom donné n'est pas trouvé dans la liste des métiers.
    """
    job = get_job_with_name(job_name, jobs)
    if job is None:
        raise JobNotFound(f"Job '{job_name}' not found.")
    
    jobs_data = {
        'name': job_name,
        'items': []
    }
    category_id = job['category_id']

    with get_print_lock():
        print(f"Processing job: {job_name}")
        [print(f"\tProcessing category ID: {cat_id}") for cat_id in category_id]

    threads = []
    for cat_id in category_id:
        thread = threaded_execution(category_management, cat_id, level_min, level_max, jobs_data)
        threads.append(thread)
    for thread in threads:
        stop_thread(thread)
    jobs_data['items'] = flatten_items(sort_group_by_level(sort_grouped_items_by_name(group_items_by_level(jobs_data))))
    results.append(jobs_data)


def try_all_jobs(level_min: int, level_max: int, jobs: List[Dict[str, Any]], results: List[Dict[str, Any]]) -> None:
    """Essaye de traiter tous les métiers disponibles.

    Args:
        level_min (int): Le niveau minimum des items à récupérer.
        level_max (int): Le niveau maximum des items à récupérer.
        jobs (List[Dict[str, Any]]): La liste des métiers disponibles avec une liste de catégories.
        results (List[Dict[str, Any]]): La liste des résultats à remplir avec les données des métiers.
    """
    threads = []
    for job in jobs:
        thread = threaded_execution(job_management, job["name"], level_min, level_max, jobs, results)
        threads.append(thread)
    for thread in threads:
        stop_thread(thread)


def prompt_overwrite_results(result_file: str) -> bool:
    """Prompt user if they want to overwrite results.json.
    
    Returns:
        bool: True if the user wants to overwrite, False otherwise.
    Raises:
        EndOfExecution: If the user decides to quit the extraction process.
    """
    if file_exists(result_file):
        while True:
            ans = input("results.json file already exists. Do you want to extract new datas? (y/n/q): ").lower()
            if ans == "q":
                raise EndOfExecution()
            if ans in ["y", "n"]:
                return ans == "y"
    return True


def prompt_job_selection(jobs: List[Dict[str, Any]]) -> str:
    """Prompt user to select a job or all jobs.
    
    Args:
        jobs (List[Dict[str, Any]]): List of jobs to choose from.
    Returns:
        str: The selected job index or 'a' for all jobs.
    Raises:
        EndOfExecution: If the user decides to quit the extraction process.
    """
    possible_jobs = ["a"]
    msg_jobs = "q. Quit\na. All jobs\n"
    for index, job in enumerate(jobs):
        msg_jobs += f"{index}. {job['name']}\n"
        possible_jobs.append(str(index))
    msg = f"Available jobs:\n{msg_jobs}Select a job to extract data : "
    while True:
        ansj = input(msg).lower()
        if ansj == "q":
            raise EndOfExecution()
        if ansj in possible_jobs:
            return ansj


def prompt_level(prompt_text: str, min_value: int, max_value: int) -> int:
    """Prompt user for a level input within a range.
    
    Args:
        prompt_text (str): The text to display in the prompt.
        min_value (int): The minimum acceptable value.
        max_value (int): The maximum acceptable value.
    Returns:
        int: The validated level input from the user.
    Raises:
        EndOfExecution: If the user decides to quit the extraction process.
    """
    while True:
        try:
            ans = input(prompt_text)
            if ans == "q":
                raise EndOfExecution()
            ans_int = int(ans)
            if min_value <= ans_int <= max_value:
                return ans_int
            else:
                print(f"Invalid input. Please enter a number between {min_value} and {max_value}.")
        except ValueError:
            print(f"Invalid input. Please enter a number between {min_value} and {max_value}.")


def extract_management(result_file: str) -> List[Dict[str, Any]]:
    """Gestion de l'extraction des données

    Args:
        result_file (str): Le chemin du fichier de résultats où les données extraites seront stockées.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing the extracted data.
    Raises:
        EndOfExecution: If the user decides to quit the extraction process.
    """
    print("Starting extraction management...")
    results = []

    if not prompt_overwrite_results(result_file):
        results = json_reader(result_file)
        return results

    jobs = json_reader("data/json/jobs.json")
    ansj = prompt_job_selection(jobs)
    ans_lvl_min = prompt_level("Enter the minimum level (0-200, q to quit): ", 0, 200)
    ans_lvl_max = prompt_level(f"Enter the maximum level ({ans_lvl_min}-200, q to quit): ", ans_lvl_min, 200)

    if ansj == "a":
        print("Extracting all jobs...")
        try_all_jobs(ans_lvl_min, ans_lvl_max, jobs, results)
    else:
        print(f"Extracting job {jobs[int(ansj)]['name']}...")
        job_management(jobs[int(ansj)]['name'], ans_lvl_min, ans_lvl_max, jobs, results)
    json_writer(result_file, results)
    return results
