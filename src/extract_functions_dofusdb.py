from requests import get
from functools import cache
from utilities import threaded_execution, stop_thread, get_print_lock
from typing import List, Dict, Any

class APIError(Exception):
    """Exception raised for errors in the API response."""
    pass

class JobNotFound(Exception):
    """Exception raised when a job is not found."""
    pass


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
    response = get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        raise APIError(f"Error fetching data from API: {response.status_code}")


@cache
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
    response = get(url)
    if response.status_code == 200:
        data = response.json()
        return data["description"]["fr"]
    else:
        raise APIError(f"Error fetching data from API: {response.status_code}")


def effects_management(item: Dict[str, Any]) -> None:
    """Gère les effets d'un item.
    
    Args:
        item (Dict[str, Any]): Les données de l'item à traiter.
    """
    effects = item['effects']
    for effect in effects:
        effect_val1, effect_val2 = effect['from'], effect['to']
        if effect_val1 < 0:
            continue
        if effect_val2 == 0:
            effect_val2 = effect_val1
        effect_name = get_effect_name(effect['effectId'])
        if effect_name == "Arme de chasse":
            effect_val1, effect_val2 = 1, 1
        if effect_val1 == 0:
            print(effect_name, effect_val1, effect_val2, item['name']['fr'], item["isDestructible"], effect['effectId'])


def item_management(item: Dict[str, Any], category_data: Dict[str, Any]) -> None:
    """Gère un item individuel."""
    if (item['hasRecipe'] and  item['isDestructible']):
        #effects = effects_management(item)
        object_data = {
            'name': item['name']['fr'],
            'level': item['level'],
            'effects': []
        }
        category_data['items'].append(object_data)


def items_management(data, category_data):
    """Gère les items d'une catégorie."""
    for item in data['data']:
        item_management(item, category_data)


def category_management(category_id, level_min, level_max, category_data):
    """Gère les catégories d'items."""
    data = get_items_data(category_id, level_min, level_max, 0)
    total = data['total']
    items_management(data, category_data)
    for i in range(10, total+1, 10):
        data = get_items_data(category_id, level_min, level_max, i)
        items_management(data, category_data)

        
def job_management(job_name, level_min, level_max, jobs, results):
    """Gère les métiers et leurs catégories."""
    job = get_job_with_name(job_name, jobs)
    if job is None:
        raise JobNotFound(f"Job '{job_name}' not found.")
    
    category_data = {
        'name': job_name,
        'items': []
    }
    category_id = job['category_id']

    with get_print_lock():
        print(f"Processing job: {job_name}")
        [print(f"\tProcessing category ID: {cat_id}") for cat_id in category_id]

    threads = []
    for cat_id in category_id:
        thread = threaded_execution(category_management, cat_id, level_min, level_max, category_data)
        threads.append(thread)
    for thread in threads:
        stop_thread(thread)
    category_data['items'] = flatten_items(sort_group_by_level(sort_grouped_items_by_name(group_items_by_level(category_data))))
    results.append(category_data)


def try_all_jobs(jobs: List[Dict[str, Any]], results: List[Dict[str, Any]]) -> None:
    """Essaie tous les métiers définis dans le fichier jobs.json."""
    threads = []
    for job in jobs:
        thread = threaded_execution(job_management, job["name"], 0, 200, jobs, results)
        threads.append(thread)
    for thread in threads:
        stop_thread(thread)
