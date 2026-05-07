import os
from datetime import datetime, UTC
from collections import defaultdict, Counter
from movies import Movies as Other_Movies


class Ratings:
    def __init__(self, path_to_the_file_ratings, path_to_the_file_movies):
        self.limit = 1000
        self.path_movies = path_to_the_file_movies
        self.path_ratings = path_to_the_file_ratings

        if not os.path.exists(path_to_the_file_ratings):
            raise ValueError("File not found: " + str(path_to_the_file_ratings))
        if not os.path.exists(path_to_the_file_movies):
            raise ValueError("File not found: " + str(path_to_the_file_movies))

        with open(path_to_the_file_ratings, "r", encoding="utf-8") as f:
            f.readline()  # skip header
            self.ratings_file = f.readlines()

        self.movies = Other_Movies(path_to_the_file_movies)
        self.movie_titles = self.movies.movie_titles()

    class Movies:
        def __init__(self, ratings_file, movie_titles, limit=1000):
            self.limit = limit
            self.ratings_file = ratings_file
            self.movie_titles = movie_titles

        @staticmethod
        def get_year_from_line(line: str) -> int:
            ts = int(line.strip().split(",")[-1])
            return datetime.fromtimestamp(ts, tz=UTC).year

        @staticmethod
        def get_metric_value(ratings, metric: str):
            n = len(ratings)
            if n == 0:
                return 0.0

            if metric == "average":
                return sum(ratings) / n

            if metric == "median":
                s = sorted(ratings)
                return s[n // 2] if n % 2 == 1 else (s[n // 2 - 1] + s[n // 2]) / 2

            if metric == "variance":
                mean = sum(ratings) / n
                return sum((x - mean) ** 2 for x in ratings) / n

            raise ValueError("Unknown metric: " + str(metric))

        def dist_by_year(self):
            years = [self.get_year_from_line(line) for line in self.ratings_file]
            cnt = Counter(years)
            return dict(sorted(cnt.items())[: self.limit])

        def dist_by_rating(self):
            vals = [float(line.strip().split(",")[2]) for line in self.ratings_file]
            cnt = Counter(vals)
            return dict(sorted(cnt.items())[: self.limit])

        def top_by_num_of_ratings(self, n):
            n = min(n, self.limit)
            movie_ratings_count = defaultdict(int)
            for line in self.ratings_file:
                movie_id = int(line.strip().split(",")[1])
                movie_ratings_count[movie_id] += 1

            top = sorted(movie_ratings_count.items(), key=lambda x: x[1], reverse=True)[:n]
            return {
                self.movie_titles.get(mid, f"Unknown Movie ID: {mid}"): count
                for mid, count in top
            }

        def top_by_ratings(self, n, metric="average"):
            metric = metric.strip().lower()
            if metric not in {"average", "median"}:
                raise ValueError("Unknown metric for Movies.top_by_ratings")

            n = min(n, self.limit)
            by_movie = defaultdict(list)
            for line in self.ratings_file:
                user_id, movie_id, rating, *_ = line.strip().split(",")
                by_movie[int(movie_id)].append(float(rating))

            metrics = {
                mid: round(self.get_metric_value(rats, metric), 2)
                for mid, rats in by_movie.items()
            }
            top = sorted(metrics.items(), key=lambda x: x[1], reverse=True)[:n]
            return {
                self.movie_titles.get(mid, f"Unknown Movie ID: {mid}"): val
                for mid, val in top
            }

        def top_controversial(self, n):
            n = min(n, self.limit)
            by_movie = defaultdict(list)
            for line in self.ratings_file:
                user_id, movie_id, rating, *_ = line.strip().split(",")
                by_movie[int(movie_id)].append(float(rating))

            variances = {}
            for mid, rats in by_movie.items():
                if len(rats) > 1:
                    v = self.get_metric_value(rats, "variance")
                    variances[mid] = round(v, 2)
                else:
                    variances[mid] = 0.0

            top = sorted(variances.items(), key=lambda x: x[1], reverse=True)[:n]
            return {self.movie_titles.get(mid, f"Unknown Movie ID: {mid}"): v for mid, v in top}

    class Users(Movies):
        # Intentionally not calling super().__init__ because Users methods
        # don't need movie_titles; they only need ratings_file + limit.
        def __init__(self, ratings_file, limit):
            self.limit = limit
            self.ratings_file = ratings_file

        def dist_by_num_of_ratings(self):
            counts = defaultdict(int)
            for line in self.ratings_file:
                user_id = int(line.strip().split(",")[0])
                counts[user_id] += 1
            return dict(sorted(counts.items()))

        def dist_by_ratings(self, metric="average"):
            metric = metric.strip().lower()
            if metric not in {"average", "median"}:
                raise ValueError("Unknown metric for Users.dist_by_ratings")

            by_user = defaultdict(list)
            for line in self.ratings_file:
                user_id, _, rating, *_ = line.strip().split(",")
                by_user[int(user_id)].append(float(rating))

            out = {
                uid: round(self.get_metric_value(rats, metric), 2)
                for uid, rats in by_user.items()
            }
            return dict(sorted(out.items()))

        def top_controversial_users(self, n):
            n = min(n, self.limit)
            by_user = defaultdict(list)
            for line in self.ratings_file:
                user_id, _, rating, *_ = line.strip().split(",")
                by_user[int(user_id)].append(float(rating))

            variances = {}
            for uid, rats in by_user.items():
                if len(rats) > 1:
                    v = self.get_metric_value(rats, "variance")
                    variances[uid] = round(v, 2)
                else:
                    variances[uid] = 0.0

            top = sorted(variances.items(), key=lambda x: x[1], reverse=True)[:n]
            return dict(top)


if __name__ == "__main__":
    ratings = Ratings("ratings.csv", "movies.csv")

    movies = ratings.Movies(ratings.ratings_file, ratings.movie_titles, limit=ratings.limit)
    print("Distribution by year:")
    print(movies.dist_by_year())

    print("\nDistribution by rating:")
    print(movies.dist_by_rating())

    print("\nTop 5 movies by number of ratings:")
    print(movies.top_by_num_of_ratings(5))

    print("\nTop 5 movies by average rating:")
    print(movies.top_by_ratings(5))

    print("\nTop 5 most controversial movies:")
    print(movies.top_controversial(5))

    users = ratings.Users(ratings.ratings_file, ratings.limit)
    print("\nDistribution of users by number of ratings:")
    print(users.dist_by_num_of_ratings())

    print("\nDistribution of users by average rating:")
    print(users.dist_by_ratings())

    print("\nTop 5 most controversial users:")
    print(users.top_controversial_users(5))
