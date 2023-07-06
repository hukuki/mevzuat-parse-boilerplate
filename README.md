# mevzuat-parse-boilerplate

## How to create a new scraper

Create a new branch. Branch name will be the name of your scraper.

Use `registry.json` file to report which files are parsed correctly with your scraper.

```json
{
    "branch_name": {
        "urls": [
            "http://mevzuat.gov.tr/mevzuat?...",
            "http://mevzuat.gov.tr/mevzuat?...",
        ]
    },...

    
}

```

Add scraper outputs to https://drive.google.com/drive/folders/1ysjxlKBmT9gaxQkqgLrPHS94SapAsxLZ?usp=sharing 
