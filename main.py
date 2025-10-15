import sys
import json
import logging
from typing import Dict, Any, List
from copy import deepcopy


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

SARIF_FILENAME = 'analysis.sarif'
UPDATED_SARIF_FILENAME = f"{SARIF_FILENAME.replace('.sarif', '')}-updated.sarif"


def read_sarif_file(file_path: str) -> Dict[str, Any]:
    """Reads and parses a SARIF JSON file."""
    logger.info(f"Attempting to read file: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            sarif_data = json.load(f)
    except FileNotFoundError:
        logger.error(f"Error: File not found at {file_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"Error: Could not decode JSON from {file_path}. Details: {e}")
        sys.exit(1)
    except IOError as e:
        logger.error(f"Error reading file {file_path}: {e}")
        sys.exit(1)

    logger.info("File read and JSON parsed successfully")
    return sarif_data


def remove_extensions(sarif_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Removes the 'extensions' key from the tool object in the first run
    and returns its value (the extensions list).
    Modifies sarif_data in place.
    """
    # Note: Assumes there's only one run in the file
    tool = sarif_data['runs'][0].get('tool')

    if not tool:
        logger.error("Could not find 'tool' key in 'runs'")
        sys.exit(1)

    extensions = tool.pop('extensions', None)

    if not extensions:
        logger.error("Could not find and remove 'extensions' in 'tool'")
        sys.exit(1)

    logger.info("Removed and extracted 'extensions' successfully")
    return extensions


def extract_rules_from_extensions(extensions: List[dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Collects and returns a list of all 'rules' found across all SARIF extensions.
    """
    for extension in extensions:
        rules = extension.get('rules')

        if rules:
            logger.info(f"Found {len(rules)} rules in an extension.")
            return rules

    logger.error("Could not find any 'rules' in the provided 'extensions' list.")
    sys.exit(1)


def insert_rules_into_driver(sarif_data: Dict[str, Any], rules: List[Dict[str, Any]]) -> None:
    """
    Inserts a list of rules into sarif_data['runs'][0]['tool']['driver']['rules'].
    Modifies sarif_data in place.
    """
    try:
        driver = sarif_data['runs'][0]['tool']['driver']
    except (KeyError, IndexError):
        logger.error("SARIF structure missing 'runs[0].tool.driver'. Cannot insert rules.")
        sys.exit(1)

    driver['rules'] = rules

    logger.info(f"Successfully inserted {len(rules)} rules into runs[0].tool.driver.rules.")
    logger.info("SARIF data restructuring complete.")
    return


def write_sarif_file(file_path: str, sarif_data: Dict[str, Any]) -> None:
    """Writes the SARIF dictionary data back to a JSON file."""
    logger.info(f"Attempting to write updated SARIF data to file: {file_path}")
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(sarif_data, f, indent=2)
    except IOError as e:
        logger.error(f"Error writing file {file_path}: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred while writing to {file_path}: {e}")
        sys.exit(1)

    logger.info(f"Updated SARIF data successfully written to {file_path}")


def main():
    original_sarif_data = read_sarif_file(SARIF_FILENAME)
    updated_sarif_data = deepcopy(original_sarif_data)
    logger.info("Created a deep copy of sarif_data for modification.")

    extensions = remove_extensions(updated_sarif_data)
    rules = extract_rules_from_extensions(extensions)

    insert_rules_into_driver(updated_sarif_data, rules)
    write_sarif_file(UPDATED_SARIF_FILENAME, updated_sarif_data)


if __name__ == '__main__':
    main()