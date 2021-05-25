from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from re import sub
from random import randint
from markdown2 import markdown

from . import util

def index(request):
    """ Shows all entries in a list. """
    
    # if a search query is provided (e.g. "?q=value"), go ahead and return search function
    if request.GET.get('q'):
        return search(request, request.GET.get('q'))
    
    # if website reached without query string, render the homepage with all Wiki entries
    else:
        return render(request, "encyclopedia/index.html", {
            "entries": util.list_entries()
        })
    
def wiki(request, title):
    """ Shows individual entries at their respective URLs. """
    
    # if a search query is provided (e.g. "?q=value"), go ahead and return search function
    if request.GET.get('q'):
        return search(request, request.GET.get('q'))
    
    # go ahead if website reached without query string
    else:
        
        # check if title provided in URL exists
        if util.get_entry(title):
            
            # retrieve current title's correct name (e.g. capitalized/lowercase) and store it in a new variable
            for entry in util.list_entries():
                if title.lower() in entry.lower():
                    entry_name = entry
                    
            content = markdown(util.get_entry(title))    
                
            # render a page for the title, passing the content and title to HTML
            return render(request, "encyclopedia/entry.html", {
                "entry": content,
                "title": entry_name
            })
            
        # return apology if title in URL doesn't have an entry 
        else:
            return render(request, "encyclopedia/apology.html", {
                "apology": "No page found for this query."
            })

def search(request, query):
    """ Searches for a provided query. If query is not found, search returns a list of entries containing the query as a substring. """
    
    # store all entries in a dictionary and initialize a new dictionary for later use
    entries = util.list_entries()
    results = []
    
    # if query matches an existing entry, redirect to 'wiki' function and return the query's page
    if util.get_entry(query):
        return redirect('wiki', title=query)
    
    # go ahead if query not matching any entries
    else:
        
        # loop over existing entries and check whether query is contained in any of them as a substring (e.g. 'cs' in 'CSS')
        for entry in entries: 
            
            # add the matching entry to the results dictionary
            if query.lower() in entry.lower():
                results.append(entry)
                
        # if at least one result found, render a results page and display all matching entries
        if results:
            return render(request, "encyclopedia/results.html", {
                "entries": results
            })
            
        # return an apology if no search results found
        else:
            return render(request, "encyclopedia/apology.html", {
                "apology": "There are no search results for this query."
            })
        
def create(request):
    """ Creates a new entry. """
    
    # if user reaches page by clicking on a link or typing in the URL
    if request.method == "GET":
        
        # return a page for creating a new entry
        return render(request, "encyclopedia/create.html")
    
    # if user submits the form
    else:
        
        # store title and content from HTML in separate variables
        title = request.POST.get('title')
        content = sub("\r", "", request.POST.get('content'))
        
        # if title provided doesn't already have an entry, go ahead
        if not util.get_entry(title):
            
            # save new entry and redirect user to the new entry's page
            util.save_entry(title, content)
            return redirect('wiki', title=title)
        
        # if entry already exists for title provided, return an apology
        else:
            return render(request, "encyclopedia/apology.html", {
                "apology": "An entry already exists for this query."
            })
            
def edit(request, title):
    """ Edits a selected existing entry. """
    
    # if user reaches page by clicking on a link or typing in the URL
    if request.method == "GET":
        
        # check if title provided has an existing entry
        if util.get_entry(title):
            
            # retrieve current title's correct name (e.g. capitalized/lowercase) and store it in a new variable
            for entry in util.list_entries():
                if title.lower() in entry.lower():
                    entry_name = entry
                    
            # render the edit page, passing title and content to HTML
            return render(request, "encyclopedia/edit.html", {
                "title": entry_name,
                "content": util.get_entry(title)
            })
        # return an apology if no entry exists for provided title
        else:
            return render(request, "encyclopedia/apology.html", {
                    "apology": "No page found for this query."
            })
    
    # if user submits the form
    else:
        # store content provided by user in HTML in a new variable
        content = sub("\r", "", request.POST.get('content'))
                
        # store new content and overwrite current entry's file
        util.save_entry(title, content)
        
        # redirect user to current entry's updated page
        return redirect('wiki', title=title)

def random(request):
    """ Returns a random entry from the list of all existing entries. """
    
    # stores the last entry's position in the list of entries
    last_entry = len(util.list_entries()) - 1
    
    # stores a randomly selected number picked from the range of 0 to the last entry (inclusive)
    random_number = randint(0, last_entry)
    
    # returns a random encyclopedia entry  
    return redirect('wiki', title=util.list_entries()[random_number])