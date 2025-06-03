from extract_functions_dofusdb import job_management, try_all_jobs
from utilities import json_reader, json_writer, time_to_execute

def main() -> None:
    """Main function"""
    print("Starting main function...")
    results = []
    jobs = json_reader("data/json/jobs.json")

    #job_management("Sculpteur", 0, 200, jobs, results)
    try_all_jobs(jobs, results)

    json_writer("data/json/results.json", results)


if __name__ == "__main__":
    time_to_execute(main)
    print("Main function executed successfully.")
