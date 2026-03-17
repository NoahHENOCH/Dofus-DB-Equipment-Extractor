from extract_functions_dofusdb import EndOfExecution, extract_management
from set_price import set_all_prices
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
        set_all_prices(EQUIPMENTS_FILE, INGREDIENTS_PRICE_FILE, RECIPES_PRICE_FILE, results)

        said = []
        tmp_effects = {
            'Intelligence': 'Ine', 
            'Agilité': 'Age', 
            'Fuite': 'Fui', 
            'Dommages Poussée': 'Do Pou', 
            'Vitalité': 'Vi', 
            'Tacle': 'Tac', 
            'Dommages Feu': 'Do Feu', 
            '% Critique': 'Cri', 
            'Sagesse': 'Sa', 
            'Soin': 'So', 
            'Dommages': 'Do', 
            'Puissance': 'Pui', 
            'Force': 'Fo', 
            'Chance': 'Cha', 
            'Initiative': 'Ini', 
            'Esquive PM': 'Ré Pme', 
            'Dommages Terre': 'Do Terre', 
            'Dommages Air': 'Do Air', 
            'Invocation': 'Invo', 
            'Dommages Eau': 'Do Eau', 
            'Prospection': 'Prospe',
            '% Résistance Neutre': "Ré Per Neutre",
            '% Résistance Feu': "Ré Per Feu",
            '% Résistance Air': "Ré Per Air",
            'Retrait PA': "Ret Pa",
            'Retrait PM': "Ret Pme",
            'Portée': "Po",
            'Dommages Critiques': "Do Cri",
            '% Résistance Terre': "Ré Per Terre",
            '% Résistance Eau': "Ré Per Eau",
            'Dommages Neutre': "Do Neutre",
            'Résistance Neutre': "Ré Neutre",
            'Résistance Terre': "Ré Terre",
            'Résistance Feu': "Ré Feu",
            'Résistance Eau': "Ré Eau",
            'Résistance Air': "Ré Air",
            'Résistance Poussée': "Ré Pou",
            'Esquive PA': "Ré Pa",
            'Dommages Renvoyés': "Do Ren",
            'Arme de chasse': "Chasse",
            'Résistance Critiques': "Ré Cri",
            'PA': "Ga Pa",
            'PM': "Ga Pme",
            'Pod': "Pod",
            'Puissance Pièges': "Pui"
        }
        tmp_res = []
        ressources = []
        for job in results:
            for item in job["items"]:
                tmp_item = []
                tmp_item.append(item["name"])
                tmp_item.append(job["name"])
                tmp_item.append("")
                tmp_item.append("")
                tmp_item.append(item["level"])
                tmp_item.append("")
                tmp_item.append("")
                tmp_item.append("")
                tmp_item.append("")
                tmp_item.append("")
                tmp_item.append("")
                for ingredient in item["recipes"]["ingredients"]:
                    if ingredient["name"] not in ressources:
                        ressources.append(ingredient["name"])
                    tmp_item.append(ingredient["name"])
                    tmp_item.append(ingredient["quantity"])
                    tmp_item.append("")
                for _ in range(8-len(item["recipes"]["ingredients"])):
                    tmp_item.append("-")
                    tmp_item.append("0")
                    tmp_item.append("")

                for effect in item["effects"]:
                #    if effect["name"] not in tmp_effects and effect["name"] not in said:
                #        print(effect["name"])
                #        said.append(effect["name"])
                    
                    tmp_item.append(tmp_effects[effect["name"]])
                    tmp_item.append(effect["value1"])
                    tmp_item.append(effect["value2"])
                    tmp_item.append("")
                    tmp_item.append("")
                    tmp_item.append("")
                
                for _ in range(20-len(item["effects"])):
                    tmp_item.append("-")
                    tmp_item.append("0")
                    tmp_item.append("0")
                    tmp_item.append("")
                    tmp_item.append("")
                    tmp_item.append("")
                
                tmp_res.append(tmp_item)
        

        import csv
        """
        with open("data/csv/results.csv", "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(tmp_res) """
        
        """ 
        with open("data/csv/ressources.csv", "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            for ressource in ressources:
                writer.writerow([ressource, "-1"]) """





    except EndOfExecution:
        print("Execution terminated by user.")
        return
    


if __name__ == "__main__":
    time_to_execute(main)
    print("Main function executed successfully.")
