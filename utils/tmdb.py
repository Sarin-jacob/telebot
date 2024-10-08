import re
class TMDB(object):
    def __init__(self, api_key=None):
        self._api_key = api_key
        self._base_url = 'https://api.themoviedb.org/3'
        if not self._api_key:
            raise tmdbError("API key not provided.")
        auth = self._request_connection("/authentication").json()
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
            print("request url:",url)#Debugging
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
        yr=extract_last_year(query)
        query = clean_name(query)
        post_data = {"query": query}
        if yr:
            query = query.replace(yr, "").strip()
            post_data = {"query": query, "year": yr}
        res = self._request_connection(path, post_data).json()
        return self.unify(res)
    def search_tv(self, query:str)->dict:
        path = "/search/tv"
        yr=extract_last_year(query)
        query = clean_name(query)
        post_data = {"query": query}
        if yr:
            query = query.replace(yr, "").strip()
            post_data = {"query": query, "first_air_date_year": yr}
        res = self._request_connection(path, post_data).json()
        return self.unify(res,tv=True)
    def to_imdb(self, tmdb_id,tv=False)->str|int:
        path = f"/movie/{tmdb_id}/external_ids"
        if tv:
            path = f"/tv/{tmdb_id}/external_ids"
        res = self._request_connection(path)
        return res.json()["imdb_id"]
    def unify(self,resp,tv=False)->list:
        #initialise results dict with all elemets as list
        '''
        results = [("id", "title", "year", "popularity", "original_title","imdb_id")]
        '''
        results = []
        if tv:
            for item in resp['results']:
                if item['first_air_date'] != '':
                    yr=re.findall(r"\d{4}", item['first_air_date'])[0]
                results.append((item['id'],item['name'],yr,item['popularity'],item['original_name'],self.to_imdb(item['id'],tv=True)))
            return results
        for item in resp['results']:
            if item['release_date'] != '':
                yr=re.findall(r"\d{4}", item['release_date'])[0]
            results.append((item['id'], item['title'], yr, item['popularity'], item['original_title'], self.to_imdb(item['id'])))
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
    name = re.sub(r"[sS]\d{2}.*", "", name)
    name = name.strip()
    return name
def extract_last_year(text):
    # Regex pattern to match a year preceded by space, period, or underscore
    pattern = r"(?<=[_\s.])\d{4}"
    
    # Find all matches
    matches = re.findall(pattern, text)
    
    # Return the last match if there are any matches
    return matches[-1] if matches else None

