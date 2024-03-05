# WebScraping

Web scraping is a technique used to extract large amounts of data from websites. The data on websites is unstructured, and web scraping enables us to convert this data into a structured form. Here's how it works:

1. Send an HTTP request to the URL of the webpage you want to access. The server responds to the request by returning the HTML content of the webpage.
2. Parse the HTML content. Since most of the HTML data is nested, you cannot extract data simply through string processing. One needs a parser which can create a nested/tree structure of the HTML data. There are many HTML parser libraries available, but the most advanced one is HTML5lib.
3. Search and navigate through the parse tree. Now, you have a parse tree of HTML tags that can be searched for the data you want to extract.

This Python script is designed to scrape football data from the website [https://football-data.co.uk/](https://football-data.co.uk/). It navigates through the website, identifies CSV files containing the data, and organizes the links to these files in a structured way.

Here's a breakdown of the main functions:

- `get_csv_links(url)`: This function takes a URL as input, sends a GET request to the URL, and parses the HTML response to find all CSV file links on the page.

- `split_link(link, separator='/')`: This function splits a given link into its components using the provided separator.

- `transform_to_years(years)`: This function transforms a 4-digit string into a string representing a range of years.

- `seasonify_from(csv_link)`: This function extracts the season from a CSV link.

- `get_all_csvlinks_webpages_as_dictionnary(base_url)`: This function retrieves all webpage links from the base URL and returns a dictionary where the keys are the links and the values are the country names.

- `process_weblink(football_data_co_uk_link)`: This function processes a given link by retrieving all CSV links from the webpages and organizing them in a dictionary structure.

- `save_data_in_file(output_folder, data_structure, filetype='json')`: This function saves the data structure into a file. The file type can be 'json', 'csv', or 'txt'.

The script is designed to be run from the command line and does not require any user interaction after it's started. It will continue to run until it has processed all the links and saved the data structure to a file.

Please note that web scraping should be done responsibly and in accordance with the website's terms of service. Also, the efficiency and success of the script may depend on the structure of the website, which can change over time. If the website structure changes, the script may need to be updated. 

