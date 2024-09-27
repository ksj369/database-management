import os
from pymongo import MongoClient
import pymongo
import JamesFunctions as James
import raphaelFunctions as raph


# check system
if os.name == "nt":
    clear = "cls"
else:
    clear = "clear"

#display main menu
def print_menu():
    print("1) search for articles")
    print("2) search for authors")
    print("3) list the venues")
    print("4) add an article")
    print("5) exit program")


# menu after user actions
def return_to_main():
    print("1) Go back to main menu")
    print("2) exit program")
    user=input("Enter your choice:")   # get next user action
    while user not in ["1","2"]:
        print("invalid choice press enter to try again")
        input()
        os.system(clear)
        print("1) Go back to main menu")
        print("2) exit program")
        user=input("Enter your choice:")
    if user=="1":
        return False  #continue program
    else:
        return True   #exit program



def main():
    os.system(clear)
    valid = 0
    while not valid:
        server_name = input("enter host server name: ")
        print("connecting to host...")
        try:
            client = MongoClient(server_name, serverSelectionTimeoutMS=10000)  # 10sec time limit to check connection
            client.server_info()
        except pymongo.errors.ServerSelectionTimeoutError:

            print("invalid host server")
            input("press enter to retry again")
            os.system(clear)
        else:
            valid = 1

    db = client["291db"]  # connect to database and get collection
    dblp = db["dblp"]

    exit=False

    while not exit:
        print_menu()
        user_input=input("Enter your choice: ")   # prompt user to select menu choice and validate
        while user_input not in ["1","2","3","4","5"]:
            print("invalid choice press enter to try again")
            input()
            os.system(clear)
            print_menu()
            user_input=input("Enter your choice: ")
        #implement user action and choose next action
        if user_input=="1":
            James.articleSearchUI(dblp)
            exit=return_to_main()
        elif user_input=="2":
            James.authorSearchUI(dblp)
            exit=return_to_main()
        elif user_input=="3":
            raph.listVenuesUI(dblp)
            exit=return_to_main()
        elif user_input=="4":
            raph.addArticleUI(dblp)
            exit=return_to_main()
        else:
            exit=True
        os.system(clear)
        

        
      

main()
