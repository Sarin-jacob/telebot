# from imdb import Cinemagoer
import imdb
ia = imdb.Cinemagoer()
def movie_or_tv(query):
    if query in ['movie', 'tv movie', 'short']:
        return False
    elif query in ['tv series', 'tv mini series', 'tv special', 'tv short']:
        return True
    return None
def search_files(query):
    mov=[]
    ser=[]
    lo=[]
    moser=ia.search_movie(query)
    for i in moser:
        try:
            tv=movie_or_tv(i["kind"])
            lo.append((i.movieID, tv, i["kind"]))
        except:
            continue
    for i in lo:
        try:
            tem=ia.get_movie(i[0]) 
            temp=(i[2],tem["title"],tem["year"],i[0],", ".join(tem["genres"]))
        except:
            continue
        if i[1]:
            ser.append(temp)
        else:
            mov.append(temp)
    return mov, ser

if __name__ == "__main__":
    print(search_files("The Matrix"))
    print(search_files("The Simpsons"))
    print(search_files("The Big Bang Theory"))
    print(search_files("The Office"))
    print(search_files("ready player one"))