import json
from time import time
from os import remove
from threading import Thread, Lock
from typing import List, Dict, Any, Callable


print_lock = None

class FileError(Exception):
    """Exception raised for errors related to the file."""
    pass

def json_reader(file_path: str) -> List[Dict[str, Any]]:
    """Lit un fichier JSON et retourne son contenu.
    
    Args:
        file_path (str): Le chemin du fichier JSON à lire.
    Returns:
        List[Dict[str, Any]]: Le contenu du fichier JSON sous forme de liste de dictionnaires.
    Raises:
        FileError: Si le fichier n'existe pas ou s'il y a une erreur de décodage JSON.
    """
    print(f"Reading JSON file: {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as file:  # Ajout de encoding="utf-8"
            return json.load(file)
    except FileNotFoundError:
        raise FileError(f"File {file_path} not found.")
    except json.JSONDecodeError:
        raise FileError(f"Error decoding JSON from file {file_path}.")
    except Exception as e:
        raise FileError(f"An error occurred while reading the file: {e}")


def json_writer(file_path: str, data: List[Dict[str, Any]]) -> None:
    """Écrit des données dans un fichier JSON.
    
    Args:
        file_path (str): Le chemin du fichier JSON où écrire les données.
        data (List[Dict[str, Any]]): Les données à écrire dans le fichier JSON.
    Raises:
        FileError: Si une erreur se produit lors de l'écriture du fichier.
    """
    print(f"Writing JSON file: {file_path}")
    try:
        with open(file_path, "w", encoding="utf-8") as file:  # Ajout de encoding="utf-8"
            json.dump(data, file, indent=4, ensure_ascii=False)
    except Exception as e:
        raise FileError(f"An error occurred while writing to the file: {e}")


def delete_file(file_path: str) -> None:
    """Supprime un fichier.

    Args:
        file_path (str): Le chemin du fichier à supprimer.
    Raises:
        FileError: Si le fichier n'existe pas ou s'il y a une erreur lors de la suppression.
    """
    try:
        remove(file_path)
    except FileNotFoundError:
        raise FileError(f"File {file_path} not found.")
    except Exception as e:
        raise FileError(f"An error occurred while deleting the file: {e}")


def time_to_execute(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """
    Mesure le temps d'exécution d'une fonction.

    Args:
        func (Callable): La fonction à exécuter.
        *args: Les arguments positionnels à passer à la fonction.
        **kwargs: Les arguments nommés à passer à la fonction.

    Returns:
        Any: Le résultat de la fonction exécutée.
    """
    start_time = time()
    result = func(*args, **kwargs)
    end_time = time()
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time:.2f} seconds")
    return result


def threaded_execution(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Thread:
    """Exécute une fonction dans un thread.
    
    Args:
        func (Callable): La fonction à exécuter dans le thread.
        *args: Les arguments positionnels à passer à la fonction.
        **kwargs: Les arguments nommés à passer à la fonction.
    Returns:
        Thread: L'objet Thread créé pour exécuter la fonction.
    """
    thread = Thread(target=func, args=args, kwargs=kwargs)
    thread.start()
    return thread


def stop_thread(thread: Thread) -> None:
    """Attend la fin d'un thread.
    Args:
        thread (Thread): Le thread à arrêter.
    """
    thread.join()


def get_print_lock()-> Lock:
    """Obtient un verrou pour les impressions.
    
    Returns:
        Lock: Un verrou pour synchroniser les impressions.
    """
    global print_lock
    if print_lock is None:
        print_lock = Lock()
    return print_lock
