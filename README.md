# Information-Retrieval

## Project Introduction
This project is an information retrieval system that primarily sources data from the Nankai University News Network. The web interface is built using Flask, a lightweight Python web framework.

## Features
- **Data Collection**: Web scraping capabilities to gather data from specified sources.
- **Content Extraction**: Extracts and processes text content from web pages.
- **Search Functionality**:
  - Employs an inverted index and TF-IDF weighting model to deliver search results.
  - Supports document search, allowing users to retrieve specific documents based on keywords or phrases.
  - Enables phrase search by matching the exact sequence of words in the query for more precise results.
  - Allows wildcard searches using special characters to match patterns and find documents with word variations.
  - Captures and stores web page snapshots for quick preview without reloading the page.
  - Maintains a query log to record search queries and results, aiding in analyzing user behavior and optimizing performance.
- **Web Interface**: User-friendly web interface built with Flask for easy interaction.



## Project Structure
```
src/
├── get_data.py         # Web scraping (primary method)
├── get_data2.py        # Web scraping (backup method)
├── add_content.py      # Extract web page content
├── extract_links.py    # Extract web page hyperlinks
├── get_token.py        # Word segmentation processing
├── get_tfidf.py        # Calculate TF-IDF
├── get_page_rank.py    # Calculate PageRank
├── search.py           # Search feature implementation
├── app.py              # Web backend main program
└── templates/          # Frontend template directory
    ├── history.html    # Search history page
    ├── index.html      # Homepage
    └── search_result.html # Search results page
```

