import pickle

TITLE = "software"
companies = pickle.load(open(TITLE + ".pickle", "rb"))

for company in companies:
    print(company + "    " + companies.get(company))
print(len(companies))
exit()
