import pickle

TITLE = "data scientist"
companies = pickle.load(open(TITLE + ".pickle", "rb"))

index = 0
for company in companies:
    print(str((index := index + 1)) + ". " + company + "    " + companies.get(company))

