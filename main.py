import requests
import json
import os
import pandas as pd
from bs4 import BeautifulSoup

url =  'https://indeed.com/jobs?'
site = 'https://indeed.com'
params = {
        'q': 'Python',
        'l': 'New York State',
        '_ga':'2.197217574.828485429.1640080393 - 10507955.1640080393',
        'vjk': '71acc67a281f6038'
        # 'q': 'python',
        # 'l': 'Indonesia',
        # 'vjk' : '023e2b957ee6b91a'
    }
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}

res = requests.get(url, params=params, headers=headers)
soup = BeautifulSoup(res.text, 'html.parser')

def get_total_page(query, location):
    params = {
        'q': query,
        'l': location,
        'vjk': '71acc67a281f6038'
    }
    res = requests.get(url, params=params, headers=headers)

    try:
        os.mkdir('temp')
    except FileExistsError:
        pass

    with open('temp/res.html','w+') as outfile:
        outfile.write(res.text)
        outfile.close()

        total_pages = []
        # scraping step
        soup = BeautifulSoup(res.text, 'html.parser')
        pagination = soup.find('ul', 'pagination-list')
        pages = pagination.find_all('li')
        for page in pages:
            total_pages.append(page.text)

        total = int(max(total_pages))
        return total

def get_all_items(query, location, start, page):
    params = {
        'q': query,
        'l': location,
        'start': start,
        'vjk': '71acc67a281f6038'

    }
    res = requests.get(url, params=params, headers=headers)
    with open('temp/res.html','w+') as outfile:
        outfile.write(res.text)
        outfile.close()
        soup = BeautifulSoup(res.text, 'html.parser')

        #scraping process
        contents = soup.find_all('table','jobCard_mainContent')

        #pick items
        # * title
        # * company name
        # * company link
        # * company address

        job_list = []
        for item in contents:
            title = item.find('h2','jobTitle').text.strip('new')
            company = item.find('span', 'companyName')
            company_name = company.text
            try:
                company_link = site + company.find('a')['href']
            except:
                company_link = 'link is no available'

            #sorting data
            data_dict = {
                'title': title,
                'company name': company_name,
                'link': company_link
            }
            job_list.append(data_dict)


        #writing json
        try:
            os.mkdir('json_result')
        except FileExistsError:
            pass

        with open(f'json_result/{query}_in_{location}_page_{page}.json', 'w+') as json_data:
            json.dump(job_list, json_data)
        print('json created')
        return job_list

def create_document(DataFrame, filename):
    try:
        os.mkdir('data_result')
    except FileExistsError:
        pass

    df = pd.DataFrame(DataFrame)
    df.to_csv(f'data_result/{filename}.csv', index=False)
    df.to_excel(f'data_result/{filename}.xlsx', index=False)

    print(f'File {filename}.csv and {filename}.xlsx succesfully created')

def run():
    query = input('Enter your query: ')
    location = input('Enter your location: ')

    total = get_total_page(query, location)

    counter = 0
    final_result = []
    for page in range(total):
        page +=1
        counter +=10
        final_result += get_all_items(query, location, counter, page)

    #formating data
    try:
        os.mkdir('reports')
    except FileExistsError:
        pass

    with open(f'reports/{query}.json', 'w+') as final_data:
        json.dump(final_result,final_data)

    print('Data json created')

    #create document
    create_document(final_result, query)


if __name__ == '__main__':
    run()
