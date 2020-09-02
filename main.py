from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import pickle

USERNAME = ''
PASSWORD = ''

# Keep variable values lowercase to avoid conflicts

TITLE = "software"  # Title of job you are looking for
LOCATION = "United States"  # City, State, or Country
EXCLUDE_KEYWORDS = ["years of"]  # Don't take jobs with these words in the description
EXCLUDE_JOBS = ["front", "full", "intern"]  # Exclude jobs with these in the title
INCLUDE_KEYWORDS = ["python"]  # Include jobs whose description contains these words
INCLUDE_JOBS = ["science", "scientist", "machine"]  # Include jobs whose title contains these words
JOB_TYPES = ["fulltime"]  # One of: internship, fulltime, part-time
PAGES = 10  # Number of jobs (PAGES * 25) to scan. Set to 100
SITE = "https://www.linkedin.com/"

companies = {}

try:
    companies = pickle.load(open(TITLE+".pickle", "rb"))
except (OSError, IOError) as _:
    pickle.dump(companies, open(TITLE+".pickle", "wb"))

for company in companies:
    print(company)
print(len(companies))
exit()

driver = webdriver.Edge(r'C:\Program Files (x86)\Microsoft\Edge\Application\msedgedriver.exe')
driver.get(SITE + "uas/login")
driver.add_cookie({
                'name': 'li_at',
                # li_at cookie value from linkedin cookies
                'value': "",
                'domain': '.linkedin.com'
            })
driver.maximize_window()
driver.find_element_by_id("username").send_keys(USERNAME)
password = driver.find_element_by_id("password")
password.send_keys(PASSWORD)
password.send_keys(Keys.RETURN)
time.sleep(2)
driver.find_element_by_id("jobs-nav-item").click()
time.sleep(2)
search_boxes = driver.find_elements_by_class_name('jobs-search-box__text-input')
keyword = search_boxes[0]
time.sleep(1)
keyword.send_keys(TITLE)
search = search_boxes[2]
search.clear()
search.send_keys(LOCATION)
search.send_keys(Keys.ARROW_DOWN)
search.send_keys(Keys.RETURN)
time.sleep(1)
job_type = driver.find_element_by_css_selector("[data-test-facet-name=jobType]")
job_type.click()

for job in JOB_TYPES:
    job_type.find_element_by_css_selector("[for=jobType-" + job[0].upper() + "]").click()

job_type.find_element_by_css_selector("[data-control-name=filter_pill_apply]").click()
time.sleep(2)
url = driver.current_url
page = 1
no_results = []

while not no_results and page <= PAGES:
    jobs = driver.find_elements_by_css_selector("[data-test-search-two-pane-search-result-item=true]")
    next_page = None
    count = 0

    for i in jobs:
        try:
            driver.execute_script("arguments[0].scrollIntoView();", i)
            i.click()
            time.sleep(1)
            job_link = i.find_element_by_css_selector("a[href]").get_attribute("href")
            job_info = driver.find_element_by_class_name("jobs-details-top-card__content-container").text
            job_info = job_info.split("\n")
            job_title = job_info[0].lower()

            if any(t in job_title for t in EXCLUDE_JOBS) and not any(t in job_title for t in INCLUDE_JOBS):
                continue

            description = driver.find_element_by_id("job-details").text.lower()

            if not any(s in description for s in EXCLUDE_KEYWORDS) and \
                    any(s in description for s in INCLUDE_KEYWORDS):
                count += 1
                companies.update({job_info[0]+"--"+job_info[2]: job_link})

        except Exception:
            print("Exception raised. Skipping...")
            driver.back()
            time.sleep(1)
            continue

    print("Page " + str(page) + " complete. Found " + str(count) + " jobs")
    driver.get(url + "&start=" + str(page * 25))
    time.sleep(2)
    page += 1
    no_results = driver.find_elements_by_class_name("jobs-search-no-results__image")


pickle.dump(companies, open(TITLE+".pickle", "wb"))

