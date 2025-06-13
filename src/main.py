from extract_functions_dofusdb import EndOfExecution, extract_management
from utilities import time_to_execute

RESULTS_FILE = "data/json/results.json"
EQUIPMENTS_FILE = "data/json/equipments.json"
INGREDIENTS_PRICE_FILE = "data/json/ingredients_price.json"
RECIPES_PRICE_FILE = "data/json/recipes_price.json"


def main() -> None:
    """Main function"""
    print("Starting main function...")
    try:
        results = extract_management(RESULTS_FILE)
    except EndOfExecution:
        print("Execution terminated by user.")
        return
    print(len(results))


if __name__ == "__main__":
    time_to_execute(main)
    print("Main function executed successfully.")
