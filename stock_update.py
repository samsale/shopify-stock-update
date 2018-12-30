import email
import imaplib
import os
import csv
import json
import requests
import math
import os
import time

api_key = '504c14a434d42d87db6ad111f22fb1cb'
password = '3a83a71ec14949dc43f40fff3244e95d'

username = 'sales@rubys-garden-boutique.co.uk'
pw = 'Mummys6912'
save_path = '/'


def connect_to_gmail():
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(username, pw)
    print("Script Log - Connected to Gmail")
    return mail


def download_csv(inbox):
    inbox.select("StockUpdates")
    results, data = inbox.uid('search', None, "ALL")
    inbox_list = data[0].split()
    email_id = inbox_list[-1]
    newest_result, email_data = inbox.uid('fetch', email_id, '(RFC822)')
    raw_email = email_data[0][1].decode("utf-8")
    email_message = email.message_from_string(raw_email)
    for part in email_message.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        filename = part.get_filename()
        if filename == 'europa stock report.csv':
            with open(os.path.join('/tmp/', filename), 'wb') as fp:
                print("Script Log Downloaded csv",fp)
                fp.write(part.get_payload(decode=True))


def get_file():
    # f = input('What is the file name?')
    # f_ext = f+'.csv'
    file_name = '/tmp/europa stock report.csv'
    return file_name


def get_number_of_pages():
    url = 'https://rubysgardenboutique.myshopify.com/admin/products/count.json'
    r = requests.get(url, auth=(api_key, password))
    json_data = r.json()
    t = int(json_data['count'])
    print ("Script Log - Number of Products ",t)
    pages = math.ceil(t / 250.0)
    print ("Script Log - Got number of pages")
    return pages


def get_all_products(pages):
    d = []
    i = 1
    while i <= pages:
        url = 'https://rubysgardenboutique.myshopify.com/admin/variants.json?limit=250&page={}&fields=id,sku'.format(i)
        r = requests.get(url, auth=(api_key, password))
        json_data = r.json()
        d += json_data['variants']
        i = i + 1
    print ("Script Log - Got products")
    return d


def create_sku_to_id_mapping(website_data):
    sku_to_id_map = {}
    for web_item in website_data: # For each 'variant' on your shopify
        sku = web_item['sku'] # Get the sku
        sku_to_id_map[sku] = web_item['id'] # Add the item to the dictionary, with the sku as the key!
    return sku_to_id_map



def select_supplier(file_name):
    if clientId == 'cb':
        output = csv_cb(file_name)
    elif clientId == 'el':
        output = csv_el(file_name)
    elif clientId == 'wgf':
        output = csv_wgf(file_name)
    elif clientId == 'west':
        output = csv_west(file_name)
    return (output)

def csv_el(file_name):
    output = []
    hide = []
    not_in_store = []
    sku_col = 1
    quantity_col = 3
    finished_col = 5
    skips = 3
    stock = ['GOOD', 'LOW']
    # file_path = '/Users/SamSale/Desktop/csv_drop/{}'.format(file_name)
    with open(file_name) as f:
        for skip in range(skips):
            next(f)
        for csv_item in csv.reader(f):  # For each item in the CSV
            if csv_item[quantity_col] in stock:
                converted_inv = 69
            elif csv_item[quantity_col] == 'OUT':
                converted_inv = 0
            sku_in_csv = csv_item[sku_col]
            if sku_in_csv in website_dict:
                id = website_dict[sku_in_csv]  # Use the sku as the key to get our web item from the dictionary
                output.append({"variant":
                                   {'id': id, "inventory_quantity": converted_inv,
                                    'inventory_management': 'shopify'}})
                if csv_item[quantity_col] == 'OUT' and csv_item[finished_col] == 'FINISHED':
                    hide.append
                    print('DEBUG: SKU {} is now deleted from store. Status: finished'.format(csv_item[sku_col]))
            else:
                not_in_store.append(sku_in_csv)
        print ("Script Log - Created LUT")
        return output
    f.close(file_name)


def update_stock(output):
    count = 0
    for item in output:
        id = (item['variant']['id'])
        payload = json.dumps(item)
        url = 'https://rubysgardenboutique.myshopify.com/admin/variants/{}.json'.format(id)
        r = requests.put(url, data=payload, auth=(api_key, password), headers={"Content-Type": "application/json"})
        count += 1
        time.sleep(.100)
    if r.status_code != 200:
        print ('error! with', item['variant']['id'], r.status_code)
    get_sku = requests.get(url, auth=(api_key, password))
    sku_list = get_sku.json()
    skus = sku_list['variant']['sku']
    qty = sku_list['variant']['inventory_quantity']

    print (count, "Items in total")


def delete_source_csv(file_name):
    os.remove(file_name)
    fn = file_name.rsplit('/', 1)[-1]
    print (fn, 'was deleted.')


inbox = connect_to_gmail()
newest_mail = download_csv(inbox)
file_name = get_file()
clientId = 'el'
pages = get_number_of_pages()
website_data = get_all_products(pages)
website_dict = create_sku_to_id_mapping(website_data)
output = select_supplier(file_name)
update_stock(output)
delete_source_csv(file_name)
