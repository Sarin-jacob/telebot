import imdb
ia=imdb.Cinemagoer()
# test=ia.search_movie('winter soldier')
# print(test[0:6])
def search_files(query):
    mov=[]
    ser=[]
    moser=ia.search_movie(query)
    for i in moser:
        try:
            temp=(i["title"],i["year"],i["kind"],i.movieID)
        except:
            continue
        if temp[2] in ['movie', 'tv movie', 'short']:
            mov.append(temp)
        elif temp[2] in ['tv series', 'tv mini series', 'tv special', 'tv short']:
            ser.append(temp)
    return mov, ser
print(search_files('winter soldier'))