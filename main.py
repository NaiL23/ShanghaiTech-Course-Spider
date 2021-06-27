from bs4 import BeautifulSoup
import pandas as pd
import requests
import logging
import random
import re

# Capture courses page
logging.captureWarnings(True)
agents = [
   'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 \
   Safari/535.1',
   'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0',
   'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; \
   .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; InfoPath.3)',
   'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1']
html = requests.get("https://lrc.shanghaitech.edu.cn/subject-lrc?nowpage=1&pagesize=1000", headers={'User-Agent': random.choice(agents)}, verify=False)
main_soup = BeautifulSoup(html.text)

# Use pandas dataframe to store course info
df = pd.DataFrame(columns=['id', 'code', 'name', 'en_name', 'college', 'teacher'])

# Access course info
for row in main_soup.find('table').tbody.find_all('tr'):
    # Access rough course info from table column
    col1, col2, col3 = row.find_all('td')
    id = int(re.compile("/course-detail\?course_id=(\d+)").match(col2.span.a['href']).group(1))
    code = col1.span.string
    name = col2.span.a['title']
    en_name = col2.find('span', class_='d-block').a['title']
    college = col3.span.string

    # Access detailed course info including teachers by capturing course page
    html = requests.get("https://lrc.shanghaitech.edu.cn/course-detail?course_id="+str(id), headers={'User-Agent': random.choice(agents)}, verify=False)
    soup = BeautifulSoup(html.text)
    teachers = set()
    for row in soup.find('div', id='JWopen').table.tbody.find_all('tr'):
        teachers.add(row.find_all('td')[2].string)
    df_new = pd.concat([pd.DataFrame({'id':id, 'code':code, 'name':name, 'en_name':en_name, 'college':college, 'teacher':teacher}, columns=['id', 'code', 'name', 'en_name', 'college', 'teacher'], index=[0]) for teacher in teachers],
          ignore_index=True)
    df = df.append(df_new, ignore_index=True)
    
# df.set_index(['id'], inplace=True)

# Write to .csv (use | to separate since some course name contains ,comma)
df.to_csv('courses.csv', sep='|')