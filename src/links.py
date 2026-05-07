import os
import requests
from bs4 import BeautifulSoup
from collections import defaultdict


class Links:
    def __init__(self, path_to_the_file_links, path_to_the_file_fields):
        self.limit = 1000
        self.links_file_path = path_to_the_file_links
        self.fields_file_path = path_to_the_file_fields

        if not os.path.exists(path_to_the_file_links):
            raise ValueError("File not found: " + str(path_to_the_file_links))
        if not os.path.exists(path_to_the_file_fields):
            raise ValueError("File not found: " + str(path_to_the_file_fields))

        self.links_file = {}
        self.movie_fields = {}
        self.load_bonus()

    def load_sample(self, limit):
        self.load_fields_site(limit)

    def load_bonus(self):
        with open(self.links_file_path, "r") as file:
            file.readline()
            for line in file:
                movie_id, imdb_id, _ = line.strip().split(",")
                self.links_file[movie_id] = imdb_id
        self.load_fields_file()

    def load_fields_site(self, limit):
        with open(self.fields_file_path.replace("csv", "_test.csv"), "w") as fields_file:
            fields_file.write(
                ";".join(
                    [
                        "movie_id",
                        "imdb_id",
                        "title",
                        "description",
                        "directors",
                        "writers",
                        "stars",
                        "runtime",
                        "budget",
                        "gross",
                    ]
                )
                + "\n"
            )

            with open(self.links_file_path, "r") as file:
                file.readline()
                for line in file:
                    movie_id, imdb_id, _ = line.strip().split(",")
                    if int(movie_id) > limit:
                        break
                    self.links_file[movie_id] = imdb_id
                    self.movie_fields[imdb_id] = Links.get_all_fields(imdb_id)
                    movie_values = [str(movie_id), str(imdb_id)] + [
                        str(value) for value in self.movie_fields[imdb_id].values()
                    ]
                    fields_file.write(";".join(movie_values) + "\n")

    def load_fields_file(self):
        with open(self.fields_file_path, "r") as file:
            file.readline()
            for line in file:
                line = line.strip().split(";")
                fields = {
                    "title": line[2].strip(),
                    "description": line[3].strip(),
                    "director": line[4].strip(),
                    "writers": line[5].strip(),
                    "stars": line[6].strip(),
                    "runtime": line[7].strip(),
                    "budget": line[8].strip(),
                    "gross": line[9].strip(),
                }
                self.movie_fields[line[1]] = fields

    @staticmethod
    def get_title(soup):
        title_tag = soup.find("title")
        return title_tag.text.replace(" - IMDb", "") if title_tag else "Unknown Title"

    @staticmethod
    def get_description(soup):
        desc_tag = soup.find(attrs={"name": "description"})
        return desc_tag["content"] if desc_tag else "Unknown Description"

    @staticmethod
    def get_directors(soup):
        director_label = soup.find(
            "span", class_="ipc-metadata-list-item__label", string="Director"
        )
        directors = []
        if director_label:
            director_container = director_label.find_next(
                "ul", class_="ipc-inline-list"
            )
            if director_container:
                directors = [a.text for a in director_container.find_all("a")]
            else:
                directors = ["Unknown Directors"]
        return ", ".join(directors)

    @staticmethod
    def get_writers(soup):
        writers_label = soup.find(
            "a", class_="ipc-metadata-list-item__label", string="Writers"
        )
        writers = []
        if writers_label:
            writers_container = writers_label.find_next("ul", class_="ipc-inline-list")
            if writers_container:
                writers = [a.text for a in writers_container.find_all("a")]
            else:
                writers = ["Unknown Writers"]
        return ", ".join(writers)

    @staticmethod
    def get_stars(soup):
        stars_label = soup.find(
            "a", class_="ipc-metadata-list-item__label", string="Stars"
        )
        stars = []
        if stars_label:
            stars_container = stars_label.find_next("ul", class_="ipc-inline-list")
            if stars_container:
                stars = [a.text for a in stars_container.find_all("a")]
            else:
                stars = ["Unknown Stars"]
        return ", ".join(stars)

    @staticmethod
    def get_runtime(soup):
        runtime_tag = soup.find("li", {"data-testid": "title-techspec_runtime"})
        return runtime_tag.find("div").text.strip() if runtime_tag else "Unknown Runtime"

    @staticmethod
    def get_budget(soup):
        budget_tag = soup.find("li", {"data-testid": "title-boxoffice-budget"})
        return budget_tag.find("div").text.strip() if budget_tag else "Unknown Budget"

    @staticmethod
    def get_gross(soup):
        gross_tag = soup.find(
            "li", {"data-testid": "title-boxoffice-cumulativeworldwidegross"}
        )
        return (
            gross_tag.find("div").text.strip()
            if gross_tag
            else "Unknown Cumulative Worldwide Gross"
        )

    @staticmethod
    def currency_to_decimal(currency_str):
        numeric_part = "".join(char for char in currency_str if char.isdigit() or char == ".")
        try:
            return float(numeric_part)
        except ValueError:
            return 0.0

    @staticmethod
    def time_to_minutes(time_str):
        hours = 0
        minutes = 0
        parts = time_str.split()
        for i, part in enumerate(parts):
            if part.isdigit():
                value = int(part)
                if i + 1 < len(parts):
                    nxt = parts[i + 1].lower()
                    if "hour" in nxt:
                        hours = value
                    elif "minute" in nxt:
                        minutes = value
        return hours * 60 + minutes

    @staticmethod
    def get_all_fields(imdb_id):
        url = f"https://www.imdb.com/title/tt{imdb_id}/"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return {
                "title": "Unknown Title",
                "description": "Unknown Description",
                "director": "Unknown Director",
                "writers": "Unknown Writers",
                "stars": "Unknown Stars",
                "runtime": "Unknown Runtime",
                "budget": "Unknown Budget",
                "gross": "Unknown Cumulative Worldwide Gross",
            }
        soup = BeautifulSoup(response.text, "html.parser")
        return {
            "title": Links.get_title(soup),
            "description": Links.get_description(soup),
            "director": Links.get_directors(soup),
            "writers": Links.get_writers(soup),
            "stars": Links.get_stars(soup),
            "runtime": Links.get_runtime(soup),
            "budget": Links.get_budget(soup),
            "gross": Links.get_gross(soup),
        }

    def get_imdb_id(self, movie_id):
        return self.links_file.get(str(movie_id), None)

    def get_imdb(self, list_of_movies, list_of_fields):
        field_mapping = {
            "Title": "title",
            "Description": "description",
            "Director": "director",
            "Writers": "writers",
            "Stars": "stars",
            "Runtime": "runtime",
            "Budget": "budget",
            "Cumulative Worldwide Gross": "gross",
        }

        for field in list_of_fields:
            if field not in field_mapping:
                allowed = ", ".join(field_mapping.keys())
                raise ValueError(f"Invalid field: {field}. Allowed fields are: {allowed}")

        list_of_fields = [field_mapping[field] for field in list_of_fields]

        imdb_infos = []
        for movie_id in list_of_movies:
            imdb_id = self.get_imdb_id(movie_id)
            if not imdb_id:
                imdb_infos.append([f"Unknown Movie Id: {movie_id}"])
                continue

            all_fields = self.movie_fields.get(imdb_id)
            if not all_fields:
                imdb_infos.append([f"Failed to fetch data for Movie Id: {movie_id}"])
                continue

            res = [int(movie_id)] + [all_fields[field] for field in list_of_fields]
            imdb_infos.append(res)

        imdb_infos.sort(key=lambda x: x[0], reverse=True)
        return imdb_infos

    def top_directors(self, n):
        n = min(n, self.limit)
        director_count = defaultdict(int)
        for imdb_id in self.links_file.values():
            data = self.movie_fields.get(imdb_id)
            if data:
                for director in data["director"].split(", "):
                    director = director.strip()
                    if director:
                        director_count[director] += 1
        return dict(sorted(director_count.items(), key=lambda x: x[1], reverse=True)[:n])

    def most_expensive(self, n):
        n = min(n, self.limit)
        budgets = {}
        for imdb_id in self.links_file.values():
            data = self.movie_fields.get(imdb_id)
            if data and data["budget"] != "Unknown":
                budgets[data["title"]] = Links.currency_to_decimal(data["budget"])
        return dict(sorted(budgets.items(), key=lambda x: x[1], reverse=True)[:n])

    def most_profitable(self, n):
        n = min(n, self.limit)
        profits = {}
        for imdb_id in self.links_file.values():
            data = self.movie_fields.get(imdb_id)
            try:
                if (
                    data
                    and data["budget"] != "Unknown Budget"
                    and data["gross"] != "Unknown Cumulative Worldwide Gross"
                ):
                    budget = Links.currency_to_decimal(data["budget"])
                    gross = Links.currency_to_decimal(data["gross"])
                    profits[data["title"]] = gross - budget
            except (ValueError, AttributeError):
                continue
        return dict(sorted(profits.items(), key=lambda x: x[1], reverse=True)[:n])

    def longest(self, n):
        n = min(n, self.limit)
        runtimes = {}
        for imdb_id in self.links_file.values():
            data = self.movie_fields.get(imdb_id)
            try:
                if data and data["runtime"] != "Unknown Runtime":
                    runtime = Links.time_to_minutes(data["runtime"])
                    runtimes[data["title"]] = runtime
            except Exception:
                continue
        return dict(sorted(runtimes.items(), key=lambda x: x[1], reverse=True)[:n])

    def top_cost_per_minute(self, n):
        n = min(n, self.limit)
        costs = {}
        for imdb_id in self.links_file.values():
            data = self.movie_fields.get(imdb_id)
            try:
                if (
                    data
                    and data["budget"] != "Unknown Budget"
                    and data["runtime"] != "Unknown Runtime"
                ):
                    budget = Links.currency_to_decimal(data["budget"])
                    runtime = Links.time_to_minutes(data["runtime"])
                    if runtime > 0:
                        costs[data["title"]] = round(budget / runtime, 2)
            except (ValueError, AttributeError):
                continue
        return dict(sorted(costs.items(), key=lambda x: x[1], reverse=True)[:n])


if __name__ == "__main__":
    links = Links("links.csv", "fields.csv")
    list_of_movies = [1, 2, 3]
    list_of_fields = ["Director", "Budget", "Cumulative Worldwide Gross", "Runtime"]
    imdb_info = links.get_imdb(list_of_movies, list_of_fields)
    for info in imdb_info:
        print(info)
