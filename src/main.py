from extract_functions_dofusdb import job_management, try_all_jobs
from typing import List, Dict, Any
from utilities import json_reader, json_writer, time_to_execute, file_exists


class EndOfExecution(Exception):
    """Exception raised to indicate the end of execution."""
    def __init__(self):
        super().__init__("Execution terminated by user.")


def prompt_overwrite_results() -> bool:
    """Prompt user if they want to overwrite results.json.
    
    Returns:
        bool: True if the user wants to overwrite, False otherwise.
    Raises:
        EndOfExecution: If the user decides to quit the extraction process.
    """
    if file_exists("data/json/results.json"):
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


def extract_management() -> List[Dict[str, Any]]:
    """Gestion de l'extraction des données

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing the extracted data.
    Raises:
        EndOfExecution: If the user decides to quit the extraction process.
    """
    print("Starting extraction management...")
    results = []

    if not prompt_overwrite_results():
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
    json_writer("data/json/results.json", results)
    return results


def main() -> None:
    """Main function"""
    print("Starting main function...")
    try:
        results = extract_management()
    except EndOfExecution:
        print("Execution terminated by user.")
        return


if __name__ == "__main__":
    time_to_execute(main)
    print("Main function executed successfully.")
