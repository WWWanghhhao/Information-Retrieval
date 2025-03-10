# Information-Retrieval

## Project Introduction
This project is an information retrieval system that primarily sources data from the Nankai University News Network. The web interface is built using Flask, a lightweight Python web framework.

## Features
- **Data Collection**: Web scraping capabilities to gather data from specified sources.
- **Content Extraction**: Extracts and processes text content from web pages.
- **Search Functionality**: Employs an inverted index and TF-IDF weighting model to deliver search results.
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

