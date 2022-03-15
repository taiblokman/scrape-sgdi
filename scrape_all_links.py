import email
from bs4 import BeautifulSoup
import requests
import time
import pandas as pd
   
# lists
urls_list=[]
all_sites_list=[]
site=''
people_expanded=[]
original_site=''
breadcrumb = ''
all_data_list=[]

headers = {
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
}
# people_list = []
# agency_title=''

# save output to file
def output():
    df = pd.DataFrame(all_data_list)
    df.to_csv('allurls_temp.csv', index=False)
    # df.to_json('alljobs_final_v3.json')
    print('saved to file')        

# function created
def scrape(site): 
    people_list = []
    site_dict = {}
    # getting the request from url
    
    try:
        r = requests.get(site, headers=headers, allow_redirects=False)
        # print(r.status_code)
    except Exception:
        return

    # converting the text
    soup = BeautifulSoup(r.text,"html.parser")
    # Extract Agency Title
    print(r.url)
    # print(soup)
    agency_title = soup.select_one("div.agency > div.agency-title > h1")
    print(agency_title)
    if (agency_title):
        title = agency_title.get_text(separator=" ").strip()
    else:
        title = "N/A"
    # print(title)

    # Extract the breadcrumb so we can guess which ministries/agency/department since we only keep agency title
    breadcrumb_element = soup.select_one("#breadcrumb_0_DivCode > div > span")
    if breadcrumb_element:
        breadcrumb = breadcrumb_element.get_text().replace(" ","").strip()
    else:
        breadcrumb = "N/A"
    # print(breadcrumb)

    # Now let's get all the available links and do and follow recursively
    links = soup.find_all('li')     
    # print(len(links))  
    for li in links:
        # print(li)
        a = li.find('a')
        # print("In 1:"+agency_title)                                  
        try:
          href = a['href'] 
        except:
          href='NAN'    
                    
        if href.startswith("/"):
            site = main_site+href
            # print(site)               
            if site not in urls_list:
                urls_list.append(site)                                
                # calling itself
                time.sleep(0.1)
                scrape(site)
        # add to site_data        
        site_dict = {            
            'agency_tile': title,
            'breadcrumb': breadcrumb,
            'site': site,             
        }        
    # print("...adding data\n")
    people_list = get_list_of_contacts(site)
    # code to flatten list of dictionary
    res = {k: v for d in people_list for k, v in d.items()}
    print(len(people_list))
    for people in people_list:
        # people_expanded.extend(people.values())
        people_list_expanded=list(people.values())
        site_list_expanded=list(site_dict.values())
        people_list_expanded.extend(site_list_expanded)
        all_data_list.append(people_list_expanded)
        # print(people_list_expanded)
    # print(all_data_list)
    # print(site_dict)
    # printing result
    # print ("result", str(res))    

    # all_sites.append(populate_list_of_contacts(site, site_data))    
    site_dict['people_list'] = people_list
    all_sites_list.append(site_dict)
    # print(all_sites_dict)


def get_list_of_contacts(site):
    people_list=[]
    r = requests.get(site, headers=headers, allow_redirects=False)       
    # converting the text
    soup = BeautifulSoup(r.text,"html.parser")	
    # Extract the people/contact info
    peoples = soup.select("div.agency > div.agency-info > div.section-info > ul > li")
    #readable > section > div.agency > div.agency-info > div.section-info > ul
    # print(len(peoples))
    for people in peoples:
        title = people.select_one("span.left > div.rank").get_text().replace(",","") 
        name = people.select_one("span.left > div.name").get_text().strip()
        tel = people.select_one("span.right > div.tel").get_text().strip()
        email = people.select_one("span.right > div.email").get_text().strip()
        people_data = {            
            'name': name,
            'title': title,
            'tel': tel,
            'email': email,            
        }        
        # print(people_data)
        people_list.append(people_data)        
    # print(len(people_list))            
    return people_list


def populate_list_of_contacts(site, site_data):
    people_list=[]
    r = requests.get(site)       
    # converting the text
    soup = BeautifulSoup(r.text,"html.parser")	
    # Extract the people/contact info
    peoples = soup.select("div.agency > div.agency-info > div.section-info > ul > li")
    #readable > section > div.agency > div.agency-info > div.section-info > ul
    # print(len(peoples))
    for people in peoples:
        title = people.select_one("span.left > div.rank").get_text().replace(",","") 
        name = people.select_one("span.left > div.name").get_text()
        tel = people.select_one("span.right > div.tel").get_text()
        email = people.select_one("span.right > div.email").get_text()
        people_data = {
            'title': title,
            'name': name,
            'tel': tel,
            'email': email,
        }
        # print(site_data)
        people_data.update(site_data)
        #Miss-CHAO-Yunn-Chyi_Senior-Director > span.left > div.name > span
        # print(people_data)
        people_list.append(people_data)        
    # print(people_list)            
    return people_list    

   
# main function
if __name__ =="__main__":
   
    # website to be scrape
    main_site = "https://www.sgdi.gov.sg"
    original_site="https://www.sgdi.gov.sg/ministries/pmo"
   
    # calling function
    scrape(original_site)
    output()