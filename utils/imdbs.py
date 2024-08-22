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
    moser=ia.search_movie(query)
    for i in moser:
        try:
            tv=movie_or_tv(i["kind"])
            tem=ia.get_movie(i.movieID) 
            temp=(tem["kind"],tem["title"],tem["year"],tem.movieID,tem["genres"])
        except:
            continue
        if tv:
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