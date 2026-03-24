# SI 201 HW4 (Library Checkout System)
# Your name: Samuel Patrick
# Your student id: 5744 3372
# Your email: samjpat@umich.edu
# Who or what you worked with on this homework (including generative AI like ChatGPT):
# If you worked with generative AI also add a statement for how you used it.
# e.g.:
# Asked ChatGPT for hints on debugging and for suggestions on overall code structure
#
# Did your use of GenAI on this assignment align with your goals and guidelines in your Gen AI contract? If not, why?
#
# --- ARGUMENTS & EXPECTED RETURN VALUES PROVIDED --- #
# --- SEE INSTRUCTIONS FOR FULL DETAILS ON METHOD IMPLEMENTATION --- #

from bs4 import BeautifulSoup
import re
import os
import csv
import unittest
#import requests  # kept for extra credit parity


# IMPORTANT NOTE:
"""
If you are getting "encoding errors" while trying to open, read, or write from a file, add the following argument to any of your open() functions:
    encoding="utf-8-sig"
"""


def load_listing_results(html_path) -> list[tuple]:
    """
    Load file data from html_path and parse through it to find listing titles and listing ids.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples containing (listing_title, listing_id)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    results = []
    f = open(html_path, 'r', encoding="utf-8-sig")
    soup = BeautifulSoup(f, 'html.parser')
    titles = soup.find_all(attrs={"data-testid":"listing-card-title"})
    ids = soup.find_all(class_="l1j9v1wn bn2bl2p dir dir-ltr")
    for i in range(0, len(titles)):
        href = ids[i].get("href")
        id = re.findall(r"rooms\/(?:plus\/)?(\d+)?", href)[0]
        results.append((titles[i].text, id))

    f.close()

    return results
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def get_listing_details(listing_id) -> dict:
    """
    Parse through listing_<id>.html to extract listing details.

    Args:
        listing_id (str): The listing id of the Airbnb listing

    Returns:
        dict: Nested dictionary in the format:
        {
            "<listing_id>": {
                "policy_number": str,
                "host_type": str,
                "host_name": str,
                "room_type": str,
                "location_rating": float
            }
        }
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    html_path = f"html_files/listing_{listing_id}.html"
    dict = {}
    f = open(html_path, 'r', encoding="utf-8-sig")
    soup = BeautifulSoup(f, 'html.parser')

    policy_number = soup.find(class_="f19phm7j dir dir-ltr").text
    policy_number = policy_number.replace('\ufeff', '')
    policy_number = re.findall(r": (.+)", policy_number)[0]
    if re.search(r'pending|pending', policy_number):
        dict['policy_number'] = "Pending"
    elif policy_number == '':
        dict["policy_number"] = "Exempt"
    else:
        dict['policy_number'] = policy_number

    host_type = soup.find(string='Superhost')
    if host_type is None:
        dict['host_type'] = "regular"
    else:
        dict['host_type'] = "Superhost"

    host_name = soup.find(class_="tehcqxo dir dir-ltr")
    host_name = host_name.find('h2').text
    host_name = host_name.replace('\xa0', ' ')
    host_name = re.findall(r'by (.+)', host_name)[0]
    dict['host_name'] = host_name
    
    room_type = soup.find(class_="_14i3z6h").text
    if re.search(r'Private|private', room_type):
        dict['room_type'] = "Private Room"
    elif re.search(r'Shared|shared', room_type):
        dict['room_type'] = "Shared Room"
    else:
        dict['room_type'] = "Entire Room"

    location_rating = soup.find_all(class_="_4oybiu")
    if location_rating == []:
        dict['location_rating'] = 0.0
    else:
        location_rating = location_rating[3].text
        dict['location_rating'] = float(location_rating)

    ret = {}
    ret[listing_id] = dict

    f.close()
    return ret
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def create_listing_database(html_path) -> list[tuple]:
    """
    Use prior functions to gather all necessary information and create a database of listings.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples. Each tuple contains:
        (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    lst = []
    listing_results = load_listing_results(html_path)
    for item in listing_results:
        listing_details = get_listing_details(item[1])
        lst.append((item[0], item[1],
            listing_details[item[1]]['policy_number'],
            listing_details[item[1]]['host_type'],
            listing_details[item[1]]['host_name'],
            listing_details[item[1]]['room_type'],
            listing_details[item[1]]['location_rating']))
        
    return lst

    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def output_csv(data, filename) -> None:
    """
    Write data to a CSV file with the provided filename.

    Sort by Location Rating (descending).

    Args:
        data (list[tuple]): A list of tuples containing listing information
        filename (str): The name of the CSV file to be created and saved to

    Returns:
        None
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================        
    first_row = ["Listing Title", "Listing ID", "Policy Number", "Host Type", "Host Name", "Room Type", "Location Rating"]
    data = sorted(data, key=lambda item: item[6], reverse=True)
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(first_row)
        for row in data:
            writer.writerow(row)

    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def avg_location_rating_by_room_type(data) -> dict:
    """
    Calculate the average location_rating for each room_type.

    Excludes rows where location_rating == 0.0 (meaning the rating
    could not be found in the HTML).

    Args:
        data (list[tuple]): The list returned by create_listing_database()

    Returns:
        dict: {room_type: average_location_rating}
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    dict = {}
    private_count = 0
    private_total = 0
    shared_count = 0
    shared_total = 0
    entire_count = 0
    entire_total = 0
    for row in data:
        if row[6] != 0.0:
            if row[5] == "Private Room":
                private_total += row[6]
                private_count += 1
            elif row[5] == "Shared Room":
                shared_total += row[6]
                shared_count += 1
            else:
                entire_total += row[6]
                entire_count += 1
    
    if private_count != 0:
        dict['Private Room'] = private_total/private_count
    else:
        dict['Private Room'] = 0

    if shared_count != 0:
        dict['Shared Room'] = shared_total/shared_count
    else:
        dict['Shared Room'] = 0

    if entire_count != 0:
        dict['Entire Room'] = entire_total/entire_count
    else:
        dict['Entire Room'] = 0
    return dict


    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def validate_policy_numbers(data) -> list[str]:
    """
    Validate policy_number format for each listing in data.
    Ignore "Pending" and "Exempt" listings.

    Args:
        data (list[tuple]): A list of tuples returned by create_listing_database()

    Returns:
        list[str]: A list of listing_id values whose policy numbers do NOT match the valid format
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    list = []
    for row in data:
        policy_number = row[2]
        if policy_number != "Pending" and policy_number != "Exempt":
            if not re.search(r'20\d{2}-00\d{4}STR|STR-000\d{4}', policy_number):
                list.append(row[1])
    return list

    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


# EXTRA CREDIT
def google_scholar_searcher(query):
    """
    EXTRA CREDIT

    Args:
        query (str): The search query to be used on Google Scholar
    Returns:
        List of titles on the first page (list)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


class TestCases(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.abspath(os.path.dirname(__file__))
        self.search_results_path = os.path.join(self.base_dir, "html_files", "search_results.html")

        self.listings = load_listing_results(self.search_results_path)
        self.detailed_data = create_listing_database(self.search_results_path)

    def test_load_listing_results(self):
        # TODO: Check that the number of listings extracted is 18.
        # TODO: Check that the FIRST (title, id) tuple is  ("Loft in Mission District", "1944564").
        self.assertEqual(len(self.listings), 18)
        self.assertEqual(self.listings[0], ("Loft in Mission District", "1944564"))

    def test_get_listing_details(self):
        html_list = ["467507", "1550913", "1944564", "4614763", "6092596"]

        # TODO: Call get_listing_details() on each listing id above and save results in a list.
        details_list = []
        for html in html_list:
            details_list.append(get_listing_details(html))
        # TODO: Spot-check a few known values by opening the corresponding listing_<id>.html files.
        # 1) Check that listing 467507 has the correct policy number "STR-0005349".
        # 2) Check that listing 1944564 has the correct host type "Superhost" and room type "Entire Room".
        # 3) Check that listing 1944564 has the correct location rating 4.9.
        self.assertEqual(details_list[0][html_list[0]]['policy_number'], "STR-0005349")
        self.assertEqual(details_list[2][html_list[2]]['host_type'], "Superhost")
        self.assertEqual(details_list[2][html_list[2]]['room_type'], "Entire Room")
        self.assertEqual(details_list[2][html_list[2]]['location_rating'], 4.9)



    def test_create_listing_database(self):
        # TODO: Check that each tuple in detailed_data has exactly 7 elements:
        # (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)
        for item in self.detailed_data:
            self.assertEqual(len(item), 7)
        # TODO: Spot-check the LAST tuple is ("Guest suite in Mission District", "467507", "STR-0005349", "Superhost", "Jennifer", "Entire Room", 4.8).
        self.assertEqual(self.detailed_data[-1], ("Guest suite in Mission District", "467507",  "STR-0005349",  "Superhost",  "Jennifer",  "Entire Room", 4.8))

    def test_output_csv(self):
        out_path = os.path.join(self.base_dir, "test.csv")

        # TODO: Call output_csv() to write the detailed_data to a CSV file.
        # TODO: Read the CSV back in and store rows in a list.
        # TODO: Check that the first data row matches ["Guesthouse in San Francisco", "49591060", "STR-0000253", "Superhost", "Ingrid", "Entire Room", "5.0"].
        output_csv(self.detailed_data, out_path)

        rows = []
        with open(out_path, mode='r', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                rows.append(row)
        
        self.assertEqual(rows[1], ["Guesthouse in San Francisco", "49591060", "STR-0000253", "Superhost", "Ingrid", "Entire Room", "5.0"])

        os.remove(out_path)
        

    def test_avg_location_rating_by_room_type(self):
        # TODO: Call avg_location_rating_by_room_type() and save the output.
        # TODO: Check that the average for "Private Room" is 4.9.
        avgs = avg_location_rating_by_room_type(self.detailed_data)
        self.assertEqual(avgs['Private Room'], 4.9)

    def test_validate_policy_numbers(self):
        # TODO: Call validate_policy_numbers() on detailed_data and save the result into a variable invalid_listings.
        # TODO: Check that the list contains exactly "16204265" for this dataset.
        not_valid = validate_policy_numbers(self.detailed_data)
        self.assertEqual(not_valid, ['16204265'])


def main():
    detailed_data = create_listing_database(os.path.join("html_files", "search_results.html"))
    output_csv(detailed_data, "airbnb_dataset.csv")


if __name__ == "__main__":
    main()
    unittest.main(verbosity=2)