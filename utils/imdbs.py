import imdb
ia=imdb.Cinemagoer()
# test=ia.search_movie('winter soldier')
# print(test[0:6])
def search_files(query):
    dlist=[]
    moser=ia.search_movie(query)
    for i in moser:
        print(i.keys())
        try:
            dlist.append((i["title"],i["year"],i["kind"],i.movieID))
        except:
            dlist.append((i["title"],i["kind"]))
    return dlist
print(search_files('winter soldier'))