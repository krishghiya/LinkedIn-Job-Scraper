from collections import OrderedDict
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
import pickle
import time

USERNAME = ''
PASSWORD = ''

# Keep variable values lowercase to avoid conflicts

TITLE = ""  # Title of job you are looking for
LOCATION = "United States"  # City, State, or Country
EXCLUDE_KEYWORDS = []  # Exclude jobs with these words in description
EXCLUDE_JOBS = []  # Exclude jobs with these in the title
INCLUDE_KEYWORDS = [[], []]  # Include jobs with these words in description
INCLUDE_JOBS = []  # Include jobs whose title contains these words
JOB_TYPES = ["fulltime"]  # One of: internship, fulltime, part-time
PAGES = 40  # Number of jobs (PAGES * 25) to scan. Max 40
SITE = "https://www.linkedin.com/"
DRIVER = webdriver.Chrome(r'C:\Program Files (x86)\Google\chromedriver.exe')

companies = OrderedDict()

try:
    companies = pickle.load(open(TITLE + ".pickle", "rb"))
except (OSError, IOError):
    pickle.dump(companies, open(TITLE + ".pickle", "wb"))


def get_elem(attribute, tag="", value="", compare="=", multiple=False, lookup=DRIVER):
    wait = WebDriverWait(lookup, 10)
    if not multiple:
        return wait.until(ec.visibility_of_element_located((By.CSS_SELECTOR,
                                                            tag + "[" + attribute + compare + value + "]")))
    return wait.until(ec.visibility_of_all_elements_located((By.CSS_SELECTOR,
                                                             tag + "[" + attribute + compare + value + "]")))


DRIVER.get(SITE + "jobs")

# li_at cookie value from linkedin cookies inspect element
DRIVER.add_cookie({
    'name': 'li_at',
    # To avoid crashes use a new value every session
    'value': "AQEDASWTK4wEgkUkAAABdy1TwmIAAAF3UWBGYk4AJlUlYsB-UWGZSmwlR7TcmRGCxt9R4k88BtnGkYson1"
             "eQTzAahkzwDy6_oAzHESO3TvigQjVodQpe8WD_I4637DKQFoCHotZEaYD37h8uNVWYdu3s",
    'domain': '.linkedin.com'
})

DRIVER.maximize_window()
get_elem("class", value="nav__button-secondary").click()
username = get_elem("id", value="username")
username.clear()
username.send_keys(USERNAME)
password = get_elem("id", value="password")
password.send_keys(PASSWORD)
password.send_keys(Keys.RETURN)
search_boxes = get_elem("class", value="jobs-search-box__text-input", multiple=True)
search_boxes[0].click()
time.sleep(1)
search_boxes[0].send_keys(TITLE)
search = search_boxes[1]
search.clear()
search.send_keys(LOCATION)
search.send_keys(Keys.RETURN)
job_type = get_elem("aria-controls", value="job-type-facet-values")
job_type.click()

for job in JOB_TYPES:
    get_elem("for", value="jobType-" + job[0].upper(), lookup=DRIVER).click()

get_elem("class", value="msg-overlay-bubble-header", compare="=", lookup=DRIVER).click()
url = DRIVER.current_url
page = 1
no_results = []
time.sleep(1)

while not no_results and page <= PAGES:
    try:
        jobs = get_elem("data-occludable-entity-urn", compare="", multiple=True)
    except:
        print("Site crashed, saving data...")
        break

    next_page = None
    count = 0

    try:
        for i in jobs:
            DRIVER.execute_script("arguments[0].scrollIntoView();", i)
            time.sleep(0.5)
            job_link = get_elem("href", tag="a", compare="", lookup=i)
            job_link.click()
            job_link = job_link.get_attribute("href")
            job_info = get_elem("class", value="jobs-details-top-card__content-container").text
            job_info = job_info.split("\n")
            job_title = job_info[0].lower()

            if any(t in job_title for t in EXCLUDE_JOBS) and not any(t in job_title for t in INCLUDE_JOBS):
                continue

            description = get_elem("id", value="job-details").text.lower()

            if not any(s in description for s in EXCLUDE_KEYWORDS) and \
                    all(any(s in description for s in arr) for arr in INCLUDE_KEYWORDS):
                job_pair = job_info[0] + "--" + job_info[2]
                if job_pair not in companies:
                    count += 1
                    companies.update({job_pair: job_link})

        print("Page " + str(page) + " complete. Found " + str(count) + " jobs.")
        time.sleep(1)
        DRIVER.get(url + "&start=" + str(page * 25))
        page += 1
        no_results = DRIVER.find_elements_by_class_name("jobs-search-no-results__image")
        time.sleep(1)

    except (TimeoutException, StaleElementReferenceException):
        print('Timed out, retrying page')

print('Search completed')
pickle.dump(companies, open(TITLE + ".pickle", "wb"))
DRIVER.close()
