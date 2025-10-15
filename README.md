# SARIF Rule Restructuring Script
This Python script is a utility designed to modify the structure of a SARIF (Static Analysis Results Interchange Format) file. It moves the rule definitions from the `tool.extensions` array into the primary `tool.driver.rules` array.

## 🚀 Purpose
Many static analysis tools (like SARIF formatters or wrappers) place rule metadata under the `tool.extensions` property. However, many SARIF consumers—including popular platforms—expect these definitions to be present directly under `tool.driver.rules`.

This script automates the following restructuring process:

1. Read the input SARIF file.
2. Extract the `rules` definitions from the `tool.extensions` array.
3. Remove the entire `extensions` property from the `tool` object.
4. Insert the extracted rules into the `tool.driver.rules` array.
5. Write the modified SARIF content to a new output file.

## 🛠️ Prerequisites
* Python 3.6+
* No external libraries are required; the script uses only standard Python modules (`sys`, `json`, `logging`, `copy`).

## ⚙️ Usage
The script must be executed from the command line and requires one argument: the path to the SARIF file you wish to process.

## Execution

```
python sarif_update_script.py <SARIF_FILENAME>
```

Example:

```
python sarif_update_script.py analysis.sarif
```

## Output File

The script will create a new SARIF file with the suffix -updated appended to the original filename.

* Input: `analysis.sarif`
* Output: `analysis-updated.sarif`

## Error Handling
If you run the script without providing a filename, it will exit with an error message:

```
Error: No SARIF filename provided.
Usage: python sarif_update_script.py <SARIF_FILENAME>
```

## 🔎 Technical Detail: The Transformation
The script performs the following structural change on the tool object:

Before (Original Structure):

```
{
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "MyTool",
          "rules": [] // Often empty or missing initially
        },
        "extensions": [ // Rules are incorrectly located here
          {
            "name": "Ruleset",
            "rules": [
              { "id": "RULE-101", "name": "..." },
              { "id": "RULE-102", "name": "..." }
            ]
          }
        ]
      }
    }
  ]
}
```

After (Updated Structure):
```
{
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "MyTool",
          "rules": [ // Rules are now correctly located here
            { "id": "RULE-101", "name": "..." },
            { "id": "RULE-102", "name": "..." }
          ]
        }
        // "extensions" property is completely removed
      }
    }
  ]
}
```