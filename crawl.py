import urllib2
import re
import sys
import os
import string
import mechanize
import BeautifulSoup
import time
import pickle

link = "http://en.wikipedia.org/wiki/Category:Arts"

# Browser
br = mechanize.Browser()
br.set_handle_robots(False)
br.addheaders = [('User-agent', "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.22 (KHTML, like Gecko) Chrome/25.0.1364.97 Safari/537.22")]
level = 1
#MANUAL TREE
category = [["Culture",0]] # [0,1] 0-Name, 1-Level
curr_cat = ""
sub_cat_list = []
article_list = []
count  = 0


def mapCat(x):
    return [str(unicode(x.contents[0]).encode("utf-8")), level+1]

def mapArticle(x):
    x_content = str(unicode(x.contents[0]).encode("utf-8"))
    if(x_content in ["next 200", "previous 200"]):
        return x_content
    else:
        return x['href'][6:]

def linkify(x):
    x = x.replace(' ', '_')
    return "http://en.wikipedia.org/wiki/Category:" + x


while(category):
    count = count + 1
    if(count == 100):
        count = 0
        f = open("category_checkpoint", 'w')
        pickle.dump(category, f)
        # f.write(category)
        f.close()

    try:
        cat = category.pop()
        level = cat[1]
        if(level <= 1):
            curr_cat = cat[0]


        raw = br.open(linkify(cat[0])).read()
        soup = BeautifulSoup.BeautifulSoup(raw)

        # PARSE SUBCATEGORIES
        sub_cat_soup_list = soup.findAll("div", {"id" : "mw-subcategories"})

        if sub_cat_soup_list: #check if subcategory exists for this url or not.
            sub_cat_soup_list = sub_cat_soup_list[0].findAll("a") # extract all <a> elements
            sub_cat_list = map(mapCat, sub_cat_soup_list) 


            # If "(next 200)" links are present then fetch them all in loop. 
            while(sub_cat_soup_list[-1].contents[0][0:5] == "next "):
                next_link = "http://en.wikipedia.org" + str(sub_cat_soup_list[-1]['href'])
                raw = br.open(next_link).read()
                next_soup = BeautifulSoup.BeautifulSoup(raw)
                sub_cat_soup_list =  next_soup.findAll("div", {"id" : "mw-subcategories"})
                if sub_cat_soup_list:
                    sub_cat_soup_list = sub_cat_soup_list[0].findAll("a")
                    sub_cat_list = sub_cat_list + map(mapCat, sub_cat_soup_list)

                    # remove 'next 200' and 'previous 200' here.
                    while(["next 200", level+1] in sub_cat_list): sub_cat_list.remove(["next 200", level+1])
                    while(["previous 200", level+1] in sub_cat_list): sub_cat_list.remove(["previous 200", level+1])
        else:
            sub_cat_list = []



        if(level <= 1):
            f = open("final_tree", 'a')
            for c in sub_cat_list:
                f.write(curr_cat + ", " + c[0]  + "\n")
            f.close()
            
            
            

        # PARSE ARTICLES
        article_soup_list = soup.findAll("div", {"id" : "mw-pages"})
        if article_soup_list:
            article_soup_list = article_soup_list[0].findAll("a")[2:] 
            # [0]- to get soup out of list, "a" to get page links, [2:] to remove first two <a href...> which are useless.
            article_list = map(mapArticle, article_soup_list)

            # If "(next 200)" links are present then fetch them all in loop. 
            while(article_soup_list[-1].contents[0][0:5] == "next "):
                next_link = "http://en.wikipedia.org" + str(article_soup_list[-1]['href'])
                raw = br.open(next_link).read()
                next_soup = BeautifulSoup.BeautifulSoup(raw)
                article_soup_list =  next_soup.findAll("div", {"id" : "mw-pages"})[0].findAll("a")[2:]
                article_list = article_list + map(mapArticle, article_soup_list)

                # remove 'next 200' and 'previous 200' here.
                while("next 200" in article_list): article_list.remove("next 200")
                while("previous 200" in article_list): article_list.remove("previous 200")


        # print "\n***************************>>>>>>>>>>>"
        # print "Current Cat : " , curr_cat,"\n" , category , " :: Level : ", level
        # print "<<<<<<<<<<<****************************\n"
        # print 
        # print "\n\n\n======================================"
        # print sub_cat_list
        # print article_list

        f = open("article_category", 'a')
        for a in article_list:
            f.write(curr_cat + ", " + a  + "\n")
        f.close()

        print "OK: ", cat

        category = category + sub_cat_list
        
        
    except:
        print "Error: ", cat

