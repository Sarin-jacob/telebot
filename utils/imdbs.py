import imdb

# print(test[0:6])
def search_files(query):
    mov=[]
    ser=[]
    moser=ia.search_movie(query)
    for i in moser:
        try:
            temp=(i["kind"],i["title"],i["year"],i.movieID)
        except:
            continue
        if temp[0] in ['movie', 'tv movie', 'short']:
            mov.append(temp)
        elif temp[0] in ['tv series', 'tv mini series', 'tv special', 'tv short']:
            ser.append(temp)
    return mov, ser
