class TMDB(object):
    def __init__(self, api_key=None):
        self._api_key = api_key
        self._base_url = 'https://api.themoviedb.org/3'
        if not self._api_key:
            raise tmdbError("API key not provided.")
        auth = self._request_connection("/authentication").json()
        print(auth)
    def _request_connection(self, path, post_data=None):
        import requests

        url = f"{self._base_url}{path}?api_key={self._api_key}"
        headers = {
                "accept": "application/json"
                # "Authorization": f"Bearer {self._api_key}"
                }
        try:
            if post_data:
                url = f"{url}&" + "&".join([f"{i}={j}" for i, j in post_data.items()])   
            res = requests.get(url=url, headers=headers, timeout=15)
            res.raise_for_status()
            res.json()
            return res
        except requests.exceptions.HTTPError as err:
            status = err.response.status_code
            if status == 401:
                raise tmdbError("Unauthorized error. Check authentication credentials.")
            else:
                raise tmdbError(f"HTTP Error {status}. Check SSL configuration.")
        except requests.exceptions.Timeout:
            raise tmdbError("Request timed out. ")
        except requests.exceptions.ConnectionError:
            raise tmdbError("Connection error. ")
        except requests.exceptions.TooManyRedirects:
            raise tmdbError("Too many redirects.")
        
    def get_movie(self, movie_id):
        path = f"/movie/{movie_id}"
        res = self._request_connection(path)
        return res.json()
    def search_movie(self, query:str)->dict:
        path = "/search/movie"
        query = clean_name(query)
        print("b4,extract year",query)
        yr=extract_last_year(query)
        post_data = {"query": query}
        if yr:
            query = query.replace(yr, "").strip()
            post_data = {"query": query, "year": yr}
        print("after,extract year")
        res = self._request_connection(path, post_data).json()
        print("res b4 unify",res)
        return self.unify(res)
    def search_tv(self, query:str)->dict:
        path = "/search/tv"
        query = clean_name(query)
        yr=extract_last_year(query)
        post_data = {"query": query}
        if yr:
            query = query.replace(yr, "").strip()
            post_data = {"query": query, "year": yr}
        res = self._request_connection(path, post_data).json()
        return self.unify(res,tv=True)
    def to_imdb(self, tmdb_id,tv=False)->str|int:
        path = f"/movie/{tmdb_id}/external_ids"
        if tv:
            path = f"/tv/{tmdb_id}/external_ids"
        res = self._request_connection(path)
        return res.json()["imdb_id"]
    def unify(self,resp,tv=False)->dict:
        #initialise results dict with all elemets as list
        results = {"id": [], "title": [], "year": [], "popularity": [], "original_title": [],"imdb_id":[]}
        if tv:
            for item in resp['results']:
                results["id"].append(item['id'])
                results["title"].append(item['name'])
                results["popularity"].append(item['popularity'])
                results["original_title"].append(item['original_name'])
                try:
                    yr=re.findall(r"\d{4}", item['first_air_date'])[0]
                except:
                    yr="0000"
                results["year"].append(yr)
                imdb_id=self.to_imdb(item['id'],tv=True)
                results["imdb_id"].append(imdb_id)
            return results
        for item in resp['results']:
            results["id"].append(item['id'])
            results["title"].append(item['title'])
            results["popularity"].append(item['popularity'])
            results["original_title"].append(item['original_title'])
            yr=re.findall(r"\d{4}", item['release_date'])[0]
            results["year"].append(yr)
            imdb_id=self.to_imdb(item['id'])
            results["imdb_id"].append(imdb_id)

        return results


class tmdbError(Exception):
    pass

import re
def clean_name(name):
    #replace .,_ with space
    name = re.sub(r'[._]', ' ', name)
    # Remove any non-alphanumeric characters  
    name = re.sub(r'\W+', ' ', name)
    # Remove any leading/trailing whitespaces
    name = re.sub(r"S\d{2}.*", "", name)
    name = name.strip()
    return name
def extract_last_year(text):
    # Regex pattern to match a year preceded by space, period, or underscore
    pattern = r"(?<=[_\s.])\d{4}"
    
    # Find all matches
    matches = re.findall(pattern, text)
    
    # Return the last match if there are any matches
    return matches[-1] if matches else None

