import pymongo
from pymongo import collection, MongoClient, cursor
import re

# everything in this file was written by James Laidlaw in nov 2022

# EXAMPLE CALLING AUTHOR SEARCH
# client = MongoClient()
# db = client["291db"]
# dblp = db["dblp"]
# authorSearchUI(dblp)

# EXAMPLE CALLING ARTICLE SEARCH
# client = MongoClient()
# db = client["291db"]
# dblp = db["dblp"]
# articleSearch(dblp)


def articleSearchUI(collection: collection):
    # run this from main UI loop, feed it the current collection, It'll deal with everything else & return when user return to main menu

    # prompt user for keywords
    userInput = input(
        "Please enter the keywords you would like to search by, seperated by a space or other whitespace: ")
    keywords = userInput.split()

    # search using keywords
    searchResults = SearchArticles(keywords, collection)

    # print results
    numberSpace = 6
    idSpace = 40
    yearSpace = 5
    resultList = []
    for i, searchResult in enumerate(searchResults):
        resultList.append(searchResult)
        print("-"*100)
        print("Result#:", str(i).ljust(numberSpace), "ID:", searchResult["id"].ljust(idSpace), "Year:", str(
            searchResult["year"]).ljust(yearSpace))
        print("Title:", searchResult["title"])
        if (searchResult["venue"] != ""):
            print("Venue:", searchResult["venue"])
    print("-"*100)
    print()
    userSelection = input(
        "To see more information about an article, please enter its result number, enter any other input to return to menu: ")

    # if user did not enter a valid rownumber, return to menu
    if (not userSelection.isnumeric() or int(userSelection) < 0 or int(userSelection) >= len(resultList)):
        return
    selectedArticle = resultList[int(userSelection)]

    # if user entered a valid rownumber, print all information about the article, then search for and display articles referencing it
    print("-"*100)
    print("ID:", selectedArticle["id"].ljust(idSpace), "Year:", str(
        selectedArticle["year"]).ljust(yearSpace))
    print("Title:", selectedArticle["title"])

    # only print venue if there is a venue
    if (selectedArticle["venue"] != ""):
        print("Venue:", selectedArticle["venue"])
    else:
        print("No Venue Listed")

    # only print abstact section if abstract exists
    if "abstract" in selectedArticle:
        print("Abstract:", selectedArticle["abstract"])
    else:
        print("No Abstract Listed")

    print("Authors: ")
    for author in selectedArticle["authors"]:
        print(author)

    referenceResults = getRefrencingArticles(selectedArticle["id"], collection)
    print("Referenced By: ")
    for reference in referenceResults:
        print("-"*100)
        print("ID:", reference["id"].ljust(idSpace), "Year:", str(
            reference["year"]).ljust(yearSpace))
        print("Title:", reference["title"])
    print("-"*100)


def SearchArticles(keywords: "list[str]", collection: collection):
    # takes a list of strings as input, as well as the collection being searched
    # returns cursor resulting from running the appropriate query

    # convert each keyowrd into a phrase (this causes AND rather than OR searching)
    phrases = []
    for keyword in keywords:
        phrases.append('\"'+keyword+'\"')

    # merge phrases into one string to feed into query
    mergedKeyword = " ".join(phrases)

    result: cursor = collection.find({"$text": {"$search": mergedKeyword}})

    return result


def getRefrencingArticles(articleID: str, collection: collection):
    # takes article id (NOTE: id NOT _id),  as well as collection being searched
    # returns cursor containing all db entries of articles that reference that id
    result = collection.find({"references": articleID})

    return result


def authorSearchUI(collection: collection):
    # run this from main UI loop, feed it the current collection, It'll deal with everything else & return when user return to main menu

    # prompt user for keywords
    userInput = input(
        "Please enter the keyword you would like to search by: ")

    searchResults = authorSearch(userInput, collection)

    rownumSpace = 6
    nameSpace = 40

    print("Row #".ljust(rownumSpace), "|", "Name".ljust(
        nameSpace), "|", "Publication Count")
    resultsList = []
    for i, result in enumerate(searchResults):
        resultsList.append(result)
        print(str(i).ljust(6), "|", result["_id"]["author"].ljust(
            nameSpace), "|", result["pub_count"])

    print()
    userSelection = input(
        "To see author's publications, please enter their row number, enter any other input to return to menu: ")

    # if user did not enter a valid rownumber, return to menu
    if (not userSelection.isnumeric() or int(userSelection) < 0 or int(userSelection) >= len(resultsList)):
        return
    selectedAuthor = resultsList[int(userSelection)]

    authorPubs = getAuthorPublications(
        selectedAuthor["_id"]["author"], collection)

    idSpace = 40
    yearSpace = 5

    print(selectedAuthor["_id"]["author"] + "'s", "publications: ")
    for publication in authorPubs:
        print("-"*100)
        print("Year:", str(
            publication["year"]).ljust(yearSpace), "Title:", publication["title"])
        if publication["venue"] != "":
            print("Venue:", publication["venue"])
    print("-"*100)


def authorSearch(keyword: str, collection: collection):
    # takes a keyword, returns all publications that have an author matching that keyword
    # returns cursor containing list of {_id: {author: str}, pub_count: int}
    # (author is name of author, pub_count is how many articles they have authored)

    # made in mongoDB compass and exported to python
    # comments for each phase of pipeline in order,
    # seperated by blank line, as you can't put coments inside a dict

    # get all items which have any match to keyword using text search

    # refine to only items containing keyword in authors

    # expand authors list so there is an object for each author
    # in the authors list for a given publication

    # clear out documents for unmatched authors

    # group documents by author, making a count of publications based on how many documents an author has
    results = collection.aggregate([
        {
            '$match': {
                '$text': {
                    '$search': keyword
                }
            }
        }, {
            '$match': {
                'authors': {
                    '$regex': re.compile(r"(?is)\b{}\b".format(keyword))
                }
            }
        }, {
            '$unwind': '$authors'
        }, {
            '$match': {
                'authors': {
                    '$regex': re.compile(r"(?is)\b{}\b".format(keyword))
                }
            }
        }, {
            '$group': {
                '_id': {
                    'author': '$authors'
                },
                'pub_count': {
                    '$sum': 1
                }
            }
        }
    ])

    return results


def getAuthorPublications(authorName: str, collection: collection):
    # takes full author name as input
    # returns all publications the auther authored, sorted descending by year

    # made in mongoDB compass and exported to python
    # comments for each phase of pipeline in order,
    # seperated by blank line, as you can't put coments inside a dict

    # use indexed text search to narrow down documents

    # filter for exact matching author name

    # sort articles, newest to oldest
    results = collection.aggregate([
        {
            '$match': {
                '$text': {
                    '$search': authorName
                }
            }
        }, {
            '$match': {
                'authors': authorName
            }
        }, {
            '$sort': {
                'year': -1
            }
        }
    ])

    return results
