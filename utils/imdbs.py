# from imdb import Cinemagoer
import imdb
ia = imdb.Cinemagoer()
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

if __name__ == "__main__":
    print(search_files("The Matrix"))
    print(search_files("The Simpsons"))
    print(search_files("The Big Bang Theory"))
    print(search_files("The Office"))
    print(search_files("ready player one"))