from utilities import json_reader, json_writer, copy_text, file_exists
from typing import List, Dict, Any, Tuple

#Dictionnaire equipement = {metier : {nom_equipement : {prix : int, taux_de_brisage : int, quantity : int, img: str}}}
#Dictionnaire ingredients = {nom_ingredient : {price : int, quantity : int, img:str}}
#Dictionnaire recettes = {nom_recette : {price, int, job:str, quantity : int, is_equipment : bool, img:str}}

def ingredient_in_equipments(ingredient_name: str, job: str, equipments: Dict[str, Dict[str, Dict[str, Any]]]) -> bool:
    """Check if an ingredient is present in the equipments for a specific job.

    Args:
        ingredient_name (str): The name of the ingredient to check.
        job (str): The job to check against.
        equipments (Dict[str, Dict[str, Dict[str, Any]]]): The equipments dictionary.

    Returns:
        bool: True if the ingredient is found in the equipments for the specified job, False otherwise.
    """
    return job in equipments and ingredient_name in equipments[job]


def handle_ingredient_with_recipe(ingredient: Dict[str, Any], ingredients: Dict[str, Dict[str, int]], recipes: Dict[str, Dict[str, Any]], equipments: Dict[str, Dict[str, Dict[str, Any]]]) -> None:
    """Handle an ingredient that has a recipe.
    
    Args:
        ingredient (Dict[str, Any]): The ingredient to process.
        ingredients (Dict[str, Dict[str, int]]): The dictionary of ingredients.
        recipes (Dict[str, Dict[str, Any]]): The dictionary of recipes.
        equipments (Dict[str, Dict[str, Dict[str, Any]]]): The dictionary of equipments.
    """
    ingredient_name = ingredient["name"]
    job = ingredient["recipe"]["job"]
    quantity = ingredient["quantity"]
    img = ingredient["img"]
    process_recipe_ingredients(ingredient["recipe"]["ingredients"], ingredients, recipes, equipments)
    is_equipment = ingredient_in_equipments(ingredient_name, job, equipments)
    if is_equipment:
        equipments[job][ingredient_name]["quantity"] += quantity
    if ingredient_name not in recipes:
        recipes[ingredient_name] = {
            "price": -1,
            "job": job,
            "quantity": quantity + 1 if is_equipment else quantity,
            "is_equipment": is_equipment,
            "img": img
        }
    else:
        recipes[ingredient_name]["quantity"] += quantity


def handle_ingredient_without_recipe(ingredient: Dict[str, Any], ingredients: Dict[str, Dict[str, int]]) -> None:
    """Handle an ingredient that does not have a recipe.
    
    Args:
        ingredient (Dict[str, Any]): The ingredient to process.
        ingredients (Dict[str, Dict[str, int]]): The dictionary of ingredients.
    """
    ingredient_name = ingredient["name"]
    quantity = ingredient["quantity"]
    img = ingredient["img"]
    if ingredient_name not in ingredients:
        ingredients[ingredient_name] = {"price": -1, "quantity": quantity, "img": img}
    else:
        ingredients[ingredient_name]["quantity"] += quantity


def process_recipe_ingredients(recipe: List[Dict[str, Any]], ingredients: Dict[str, Dict[str, int]], recipes: Dict[str, Dict[str, Any]], equipments: Dict[str, Dict[str, Dict[str, Any]]]) -> None:
    """Recursively find and process ingredients in a recipe.

    Args:
        recipe (List[Dict[str, Any]]): The recipe to process.
        ingredients (Dict[str, Dict[str, int]]): The dictionary of ingredients.
        recipes (Dict[str, Dict[str, Any]]): The dictionary of recipes.
        equipments (Dict[str, Dict[str, Dict[str, Any]]]): The dictionary of equipments.
    """
    for ingredient in recipe:
        if ingredient["hasRecipe"]:
            handle_ingredient_with_recipe(ingredient, ingredients, recipes, equipments)
        else:
            handle_ingredient_without_recipe(ingredient, ingredients)


def generate_empty_list_of_prices(equipments_file: str, ingredients_price_file: str, recipes_price_file: str, result: List[Dict[str, Any]]) -> Tuple[Dict[str, Dict[str, Dict[str, int]]], Dict[str, Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    """Generate or load empty lists of prices for equipments, ingredients, and recipes.

    Args:
        equipments_file (str): Path to the equipments JSON file.
        ingredients_price_file (str): Path to the ingredients price JSON file.
        recipes_price_file (str): Path to the recipes price JSON file.
        result (List[Dict[str, Any]]):  A list of dictionaries containing extracted data from api dofus db.

    Returns:
        Tuple[Dict[str, Dict[str, Dict[str, int]]], Dict[str, int], Dict[str, int] A tuple containing dictionaries for equipments, ingredients, and recipes prices.
    """
    equipments,ingredients,recipes = {}, {}, {}
    if True:
        for job in result:
            job_name = job["name"]
            items = {}
            for item in job["items"]:
                items[item["name"]] = {"price": -1, "breakage_rate": -1, "quantity": 1, "img": item["img"]}
            equipments[job_name] = items
        for job in result:
            for item in job["items"]:
                process_recipe_ingredients (item["recipes"]["ingredients"], ingredients, recipes, equipments)
        json_writer(equipments_file, equipments)
        json_writer(ingredients_price_file, ingredients)
        json_writer(recipes_price_file, recipes)
    else :
        equipments = json_reader(equipments_file)
        ingredients = json_reader(ingredients_price_file)
        recipes = json_reader(recipes_price_file)
    return (equipments, ingredients, recipes)


def set_all_prices(equipments_file: str, ingredients_price_file: str, recipes_price_file: str, result: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Set all prices for equipments, ingredients, and recipes.

    Args:
        equipments_file (str): Path to the equipments JSON file.
        ingredients_price_file (str): Path to the ingredients price JSON file.
        recipes_price_file (str): Path to the recipes price JSON file.

    Returns:
        Dict[str, Any]: A dictionary containing the updated prices for equipments, ingredients, and recipes.
    """
    equipments,ingredients,recipes = generate_empty_list_of_prices(equipments_file, ingredients_price_file, recipes_price_file, result)

    print("Setting all prices...")
