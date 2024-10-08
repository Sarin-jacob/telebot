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
            temp=(i["kind"],i["title"],i["year"],i.movieID)
        except:
            continue
        if movie_or_tv(temp[0]):
            ser.append(temp)
        else:
            mov.append(temp)
    return mov, ser
def gen4mId(id):
    tem=ia.get_movie(id)
    if tem.get("genres"):
        gen=", ".join(tem["genres"])
        return gen if gen!='None' else None
    return None
if __name__ == "__main__":
    print(search_files("The Matrix"))
    # print(search_files("The Simpsons"))
    # print(search_files("The Big Bang Theory"))
    # print(search_files("The Office"))
    # print(search_files("ready player one"))