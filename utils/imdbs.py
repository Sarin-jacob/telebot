import imdb
ia=imdb.Cinemagoer()
test=ia.search_movie('winter soldier')
print(test[0:6])