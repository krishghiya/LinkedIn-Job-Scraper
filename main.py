from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
import pickle
import time

USERNAME = ''
PASSWORD = ''

# Keep variable values lowercase to avoid conflicts

TITLE = "data"  # Title of job you are looking for
LOCATION = "United States"  # City, State, or Country
EXCLUDE_KEYWORDS = ["years of"]  # Don't take jobs with these words in the description
EXCLUDE_JOBS = ["intern", "phd"]  # Exclude jobs with these in the title
INCLUDE_KEYWORDS = ["python"]  # Include jobs whose description contains these words
INCLUDE_JOBS = ["machine"]  # Include jobs whose title contains these words
JOB_TYPES = ["fulltime"]  # One of: internship, fulltime, part-time
PAGES = 20  # Number of jobs (PAGES * 25) to scan. Set to 100
SITE = "https://www.linkedin.com/"
DRIVER = webdriver.Edge(r'C:\Program Files (x86)\Microsoft\Edge\Application\msedgedriver.exe')

companies = {}

try:
    companies = pickle.load(open(TITLE + ".pickle", "rb"))
except (OSError, IOError) as _:
    pickle.dump(companies, open(TITLE + ".pickle", "wb"))


# for company in companies:
#     print(company + "    " + companies.get(company))
# print(len(companies))
# exit()


def get_elem(attribute, tag="", value="", compare="=", multiple=False, lookup=DRIVER):
    wait = WebDriverWait(lookup, 10)
    if not multiple:
        return wait.until(ec.visibility_of_element_located((By.CSS_SELECTOR,
                                                            tag + "[" + attribute + compare + value + "]")))
    return wait.until(ec.visibility_of_all_elements_located((By.CSS_SELECTOR,
                                                             tag + "[" + attribute + compare + value + "]")))


DRIVER.get(SITE + "uas/login")
DRIVER.add_cookie({
    'name': 'li_at',
    # li_at cookie value from linkedin cookies
    'value': "",
    'domain': '.linkedin.com'
})
DRIVER.maximize_window()
get_elem("id", value="username").send_keys(USERNAME)
password = get_elem("id", value="password")
password.send_keys(PASSWORD)
password.send_keys(Keys.RETURN)
get_elem("id", value="jobs-nav-item").click()
search_boxes = get_elem("class", value="jobs-search-box__text-input", multiple=True)
search_boxes[0].click()
time.sleep(1)
search_boxes[0].send_keys(TITLE)
search = search_boxes[1]
search.clear()
search.send_keys(LOCATION)
search.send_keys(Keys.RETURN)
job_type = get_elem("data-test-facet-name", value="jobType")
job_type.click()

for job in JOB_TYPES:
    get_elem("for", value="jobType-" + job[0].upper(), lookup=job_type).click()

get_elem("data-control-name", value="filter_pill_apply", lookup=job_type).click()
# time.sleep(3)
url = DRIVER.current_url
page = 1
no_results = []

while not no_results and page <= PAGES:
    jobs = get_elem("data-test-search-two-pane-search-result-item", value="true", multiple=True)
    next_page = None
    count = 0
    skipped = 0

    for i in jobs:
        try:
            DRIVER.execute_script("arguments[0].scrollIntoView();", i)
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
                    any(s in description for s in INCLUDE_KEYWORDS):
                count += 1
                companies.update({job_info[0] + "--" + job_info[2]: job_link})

        except Exception as e:
            skipped += 1
            print("Exception raised. Skipping...")
            DRIVER.back()
            continue

    print("Page " + str(page) + " complete. Found " + str(count) + " jobs and skipped " + str(skipped) + " jobs.")
    DRIVER.get(url + "&start=" + str(page * 25))
    page += 1
    no_results = DRIVER.find_elements_by_class_name("jobs-search-no-results__image")

pickle.dump(companies, open(TITLE + ".pickle", "wb"))
DRIVER.close()
