from pymongo import MongoClient, collection
import os

def listVenuesUI(collection: collection):
    clear_screen()
    # UI for listVenues, run from main
    
    # Prompt user for integer, which will limit the output of listVenues
    
    validInput = False
    listVenueCursor = None
    while not validInput:
        n = input("Input number of venues to be shown: ")
        # Check if number is numeric
        if n.isnumeric():
            listVenueCursor = listVenues(int(n), collection)
            validInput = True
        else:
            clear_screen()
            print("Invalid input, enter an integer")
    
    clear_screen()
    print("Showing top", n, "venues")
    print()
    index = 1
    for venue in listVenueCursor:
        print("Venue #" + str(index))
        print("-"*100)
        print("Venue:", venue["_id"])
        print("# of Articles:", venue["ArticleCount"])
        print("# of Articles Referencing a Paper in the Venue:", venue["RefCount"])
        print("-"*100)
        print()
        index += 1
        
        
def listVenues(num: int, collection: collection):
    '''
    Prints the top "num" venues showing the venue name, number of articles in that venue, and number of articles that refereance a paper in that venue
    inputs
        int: num
        collection: collection
    output: 
        cursor: result
    '''
    
    result = collection.aggregate([
    {
        '$project': {
            'venue': 1, 
            'ref_by_count': 1
        }
    }, {
        '$match': {
            'venue': {
                '$ne': ''
            }
        }
    }, {
        '$group': {
            '_id': '$venue', 
            'ArticleCount': {
                '$sum': 1
            }, 
            'RefCount': {
                '$sum': '$ref_by_count'
            }
        }
    }, {
        '$sort': {
            'RefCount': -1
        }
    }, {
        '$limit': num
    }
    ])
    
    return result

def addArticleUI(collection: collection):
    clear_screen()
    # UI for add article, run from main
    
    # Prompt user to enter unique id, if empty string is entered then send user back to main
    inputID = input("Enter article ID or enter '' to return: ")
    
    # Account for multiple empty spaces
    if inputID.strip() == "":
        return
    else:
        
        # Search database if ID already exists
        validID = False
        while not validID:
            uniqueCheck = collection.find({"id": inputID})
            uniqueCheck2 = [x for x in uniqueCheck]
            
            # Check if results are empty, if yes then input is valid, otherwise prompt user to re-enter ID
            if not uniqueCheck2:
                validID = True
            else:
                clear_screen()
                print("ID already exists")
                inputID = input("Enter article ID: ")

        clear_screen()
        print("ID:", inputID)
        print("-" * 100)


        # Prompt user for article title, if empty string is entered then show error and prompt again
        validTitle = False
        while not validTitle:  
            inputTitle = input("Enter article title: ")
            if inputTitle.strip() == "":
                clear_screen()
                print("ID:", inputID)
                print("-" * 100)
                print("Invalid Title")
            else:
                validTitle = True
                
        clear_screen()
        print("ID:", inputID)
        print("Title:", inputTitle)
        print("-" * 100)

        
        validAuthors = False
        authors = []
        while not validAuthors:
            
            if authors:
                print("ID:", inputID)
                print("Title:", inputTitle)
                print("Authors added:")
                for name in authors:
                    print("  ", name)
                print("-" * 100)

                    
            # Prompt user for name(s) of author(s)
            print("Enter an author's name and press enter to add more authors, enter '' to finish")
            inputAuthors = input("Enter name: ")
            
            # If user inputs "" while authors list is not empty then exit loop
            if inputAuthors.strip() == "" and authors:
                validAuthors = True
                clear_screen()
                
            # If user inputs "" while authors list is empty then print error and prompt for name again
            elif inputAuthors.strip() == "":
                clear_screen()
                print("ID:", inputID)
                print("Title:", inputTitle)
                print("-" * 100)
                print("Invalid author name")
                
            # If user inputs valid string then add to authors list    
            else:
                clear_screen()
                authors.append(inputAuthors)
        
        # List inputs
        print("ID:", inputID)
        print("Title:", inputTitle)
        print("Author(s): ")
        for name in authors:
            print("  ", name)
        print("-" * 100)
        
        # Prompt for year
        inputYear = input("Enter year of publication: ")
        
        while not inputYear.isnumeric():
            clear_screen()
            # List inputs
            print("ID:", inputID)
            print("Title:", inputTitle)
            print("Author(s): ")
            for name in authors:
                print("  ", name)
            print("-" * 100)
            print("Enter a valid integer")
            inputYear = input("Enter year of publication: ")
    
    addArticle(inputID, inputTitle, authors, inputYear, collection)
    
    # Print success of addition of article and show details
    clear_screen()
    print("Succesfully added the article to collection")
    print("ID:", inputID)
    print("Title:", inputTitle)
    print("Author(s): ")
    for name in authors:
        print("  ", name)
    print("Year of publication:", inputYear)
    print("-" * 100)    
    
    input("Press Enter to continue")
    return
        
        
def addArticle(id: str, title: str, authors: "list[str]", year: int, collection: collection):
    '''
    Adds an article into the collection with the given inputs
    inputs:
        str:  id, title
        list: authors
        int:  year
        collection: collection
    outputs: None
    '''

    article = {"abstract": "", "authors": authors, "n_citations": 0, "references": [],  "title": title, "venue": "", "year": year, "id": id}
    collection.insert_one(article)

def clear_screen():
    # Clers the terminal
    os.system('cls' if os.name == 'nt' else 'clear')
    
