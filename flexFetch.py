import os
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import time
import pandas as pd
import io

retryCap = 10
seconds = 5

class Query:
    def __init__(self, query_id, query_name):
        self.id = query_id
        self.name = query_name
        self.reference_code = None

def importQueryID(path: str):
    query_list = []
    with open(path, 'r') as file:
        for line in file:
            line = line.strip()
            if line.isdigit():
                query_list.append(Query(line, line))
            elif ',' in line:
                parts = line.split(',')
                query_id = parts[0].strip()
                query_name = parts[1].strip()
                if query_id.isdigit():
                    query_list.append(Query(query_id, query_name))
    return query_list

def askQuery(base_url, t, q, v):
    params = {
        't': t,
        'q': q,
        'v': v
    }
    url = base_url + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url) as response:
        if response.status == 200:
            return response.read().decode('utf-8')
        else:
            raise Exception(f'Error fetching data: {response.status}')
        
def dumbCSV(inputString):
    first_line = inputString.split('\n', 1)[0]
    inputString = first_line.split(',')
    return all(map(lambda x: x.startswith('"'), inputString)) and all(map(lambda x: x.endswith('"'), inputString))
        
def getQuery(base_url, t, q, v, query_name):
    retry = 1
    params = {
        'q': q,
        't': t,
        'v': v
    }
    url = base_url + urllib.parse.urlencode(params)
    print(f"Accessing {url}")
    while retry <= retryCap:
        with urllib.request.urlopen(url) as response:
            response_data = response.read().decode('utf-8')
            if dumbCSV(response_data):
                csv_data = io.StringIO(response_data)
                df = pd.read_csv(csv_data)
                return df
            else:
                xml = ET.fromstring(response_data)
                if xml[0].tag == 'FlexStatements':
                    print(f'Query must export as CSV. Change the Flex Query "{query_name}" to export as CSV.')
                    return None
                elif xml.find('ErrorCode').text == '1019':
                    print(f'Query "{query_name}" still loading, attempt {retry}/{retryCap}.')
                    time.sleep(seconds)
                    retry += 1
                else:
                    print('Error: {}'.format(xml.find('ErrorMessage').text))
                    successCount -= 1
                    return None
    
    print(f'Query "{query_name}" failed to complete after {retryCap} attempts.')
    successCount -= 1
    return None

# Output:
def main():
    print("+-----------------------------------------------------------------------+")
    print("| This script will fetch reports from Interactive Brokers' Flex Query.  |")
    print("| The query file should contain the query ID on each line.              |")
    print("| Please ensure that the query file is in the correct format.           |")
    print("+-----------------------------------------------------------------------+")

    base_url = 'https://ndcdyn.interactivebrokers.com/AccountManagement/FlexWebService/SendRequest?'
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

    v = '3'

    try:
        with open(os.path.join(__location__,'token.txt'), 'r') as file:
            t = file.readline().strip()
    except FileNotFoundError:
        t = input("Enter token ID: ")

    try:
        query_list = importQueryID(os.path.join(__location__,'query.txt'))
    except FileNotFoundError:
        while True:
            query_file_path = input("Enter the path to the query file: ")
            if os.path.isfile(query_file_path):
                query_list = importQueryID(query_file_path)
                break
            else:
                print("Invalid file path. Please try again.")

    if len(query_list) == 0:
        print("Query list is empty. Please provide a valid query file.")
        input("Press Enter to continue...")
        exit()

    print("+-----------------------------------------------------------------------+")
    print(f"Total Number of Reports: {len(query_list)}")
    print("+-----------------------------------------------------------------------+")
    successCount = len(query_list)
    qCount = 0
    for query in query_list:
        qCount += 1
        print(f"Fetching reference code for query {query.name} ({qCount}/{len(query_list)})")
        try:
            xml = askQuery(base_url, t, query.id, v)
            root = ET.fromstring(xml)
            reference_code = root.findtext('ReferenceCode')
            query.reference_code = reference_code
        except Exception as e:
            print(f'Error fetching query {query.name}: {e}')
            input("Press Enter to continue...")
        time.sleep(seconds)

    req_url = root.find('Url').text + '?'

    for query in query_list:
        print(f"Fetching report for query {query.name}")
        data = getQuery(req_url, t, query.reference_code, v, query.name)
        if data is not None:
            filename = os.path.join(__location__,f"{query.name}_{time.strftime('%Y%m%d_%H%M%S')}")
            data.to_csv(f"{filename}.csv", index=False)
            print(f"Report saved as {filename}")
            
    print(f"{successCount} reports fetched successfully.")
    input("Press Enter to continue...")

if __name__ == "__main__":
    main()