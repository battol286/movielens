import os
import re


class Movies:
    def __init__(self, path_to_the_file):
        self.limit = 1000
        self.path = path_to_the_file

        if not os.path.exists(path_to_the_file):
            raise ValueError("File not found: " + str(path_to_the_file))

        with open(path_to_the_file, "r", encoding="utf-8") as file:
            file.readline()  # skip header
            self.movies_file = file.readlines()

    @staticmethod
    def _parse_title_and_year(raw_title: str):
        """
        Robustly split 'Title (1995)' into ('Title', '1995').
        Leaves year as 'Unknown' if not matched.
        """
        raw_title = raw_title.strip().replace('"', "")
        m = re.match(r"^(.*)\s\((\d{4})\)$", raw_title)
        if m:
            return m.group(1), m.group(2)
        return raw_title, "Unknown"

    def dist_by_release(self):
        release_years = {}
        count = 0

        for line in self.movies_file:
            if count >= self.limit:
                break
            cols = line.rstrip("\n").split(",")
            # title may contain commas → join everything except first and last col
            title_field = ",".join(cols[1:-1]).replace('"', "")
            _, year = self._parse_title_and_year(title_field)
            release_years[year] = release_years.get(year, 0) + 1
            count += 1

        return dict(sorted(release_years.items(), key=lambda x: x[1], reverse=True))

    def dist_by_genres(self):
        genres = {}
        count = 0

        for line in self.movies_file:
            if count >= self.limit:
                break
            cols = line.rstrip("\n").split(",")
            genre_list = cols[-1].split("|") if cols and cols[-1] else []
            for g in genre_list:
                if g:
                    genres[g] = genres.get(g, 0) + 1
            count += 1

        return dict(sorted(genres.items(), key=lambda x: x[1], reverse=True))

    def most_genres(self, n):
        if n <= 0:
            raise ValueError(f"n must be positive, got {n}")

        movies = {}
        count = 0

        for line in self.movies_file:
            if count >= self.limit:
                break
            cols = line.rstrip("\n").split(",")
            title_field = ",".join(cols[1:-1]).replace('"', "")
            title, _ = self._parse_title_and_year(title_field)
            genre_list = cols[-1].split("|") if cols and cols[-1] else []
            movies[title] = len([g for g in genre_list if g])
            count += 1

        sorted_movies = sorted(movies.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_movies[:n])

    def movie_titles(self):
        result = {}
        for line in self.movies_file:
            cols = line.rstrip("\n").split(",")
            movie_id = int(cols[0])
            title_field = ",".join(cols[1:-1]).replace('"', "")
            result[movie_id] = title_field
        return result
