import requests, json
from flask import jsonify
import hashlib
from getpass import getpass

# Login functionality
username = input("Enter user username: ")
#password = getpass('Password:')
#passwordhash = hashlib.md5(password.encode())
#passwordhash = passwordhash.hexdigest()
logindetails={}
logindetails[username]=username
response = requests.post("http://localhost:5000/login",headers = {'Accept': 'application/json'}, json= logindetails)
user_id = response.text
print(user_id)
input("Press enter to view you current review list: ")
response_all={}
response_all = requests.get("http://localhost:5000/records/all/"+user_id)
#Performing a delete request to delete book review
print(response_all.text)
bookname = input("Enter a Book Name: ")
if response_all.text != "":
	response_book = requests.get("http://localhost:5000/records/"+bookname)
insertneeded = input("Do you want to add a book review? (Y/N)")
if insertneeded =="Y":
	input("Using the book name to search. Press enter. ")
	response_book = requests.get("http://openlibrary.org/search.json?title="+bookname)
	json_response = response_book.json()
	docs = json_response["docs"]
	bookdetails = []
	booklist = {}
	id = 1
	for line in docs:
		if "isbn" in line and "lending_edition_s" in line :
			bookdetails.append(line["title"])
			bookdetails.append(line["isbn"][0])
			bookdetails.append(line["lending_edition_s"])				
			booklist[id] = bookdetails
			id +=1
		bookdetails = []
	print(booklist)
	reviewid = input("Enter id to add review: ")
	print("Following is the book details to add review.")
	print(booklist[int(reviewid)])
	review = input("Add review and press enter: ")
	bookreview={}
	bookreview["bookname"]=booklist[int(reviewid)][0]
	bookreview["review"]=review
	bookreview["isbn"]=booklist[int(reviewid)][1]
	bookreview["libid"]=booklist[int(reviewid)][2]
	print(bookreview)
	input()
	response_book = requests.post("http://localhost:5000/records/add/"+user_id, 
			headers = {'Accept': 'application/json'}, json= bookreview)


deleleteneeded = input("Do you want to delete a book? (Y/N) ")
if deleleteneeded == "Y":
	bookid = input("Enter a Book id to delete: ")
	response_book = requests.delete("http://localhost:5000/records/delete/"+bookid)
	print(response_book.status_code)

#Performing a put request to update book review
else:
	updateneeded = input("Do you want to update a book? (Y/N) ")
	if updateneeded == "Y":
		bookreview={}
		bookid = input("Enter a Book id to update review : ")
		review = input("Enter the review content : ")
		bookreview[bookid] = review
		print(bookreview)
		response_book = requests.put("http://localhost:5000/records/update/"+bookid, 
			headers = {'Accept': 'application/json'}, json= bookreview)
		print(response_book)
print("Thank you")