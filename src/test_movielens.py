import os, pytest
from movielens_analysis import Movies, Ratings, Tags, Links

DATA_FILES = ["movies.csv","ratings.csv","tags.csv","links.csv","fields.csv"]
def have_all(): return all(os.path.exists(f) for f in DATA_FILES)

class TestMovies:
    def test_dist_by_release_types_and_sort(self):
        mv = Movies("movies.csv")
        d = mv.dist_by_release()
        assert isinstance(d, dict)
        vals = list(d.values())
        assert vals == sorted(vals, reverse=True)
    def test_dist_by_genres_types_and_sort(self):
        mv = Movies("movies.csv")
        d = mv.dist_by_genres()
        assert isinstance(d, dict)
        vals = list(d.values())
        assert vals == sorted(vals, reverse=True)
    def test_most_genres_topn(self):
        mv = Movies("movies.csv")
        d = mv.most_genres(5)
        assert isinstance(d, dict)
        vals = list(d.values())
        assert vals == sorted(vals, reverse=True)
    def test_movie_titles_types(self):
        mv = Movies("movies.csv")
        d = mv.movie_titles()
        assert isinstance(d, dict)
        assert all(isinstance(k,int) and isinstance(v,str) for k,v in d.items())

class TestTags:
    def test_most_words_types_and_sort(self):
        tg = Tags("tags.csv")
        d = tg.most_words(5)
        assert isinstance(d, dict)
        assert list(d.values()) == sorted(d.values(), reverse=True)
    def test_longest_types_and_sort(self):
        tg = Tags("tags.csv")
        lst = tg.longest(5)
        assert isinstance(lst, list)
        assert [len(x) for x in lst] == sorted([len(x) for x in lst], reverse=True)
        assert all(isinstance(x,str) for x in lst)
    def test_most_words_and_longest_types(self):
        tg = Tags("tags.csv")
        lst = tg.most_words_and_longest(5)
        assert isinstance(lst, list)
        assert all(isinstance(x,str) for x in lst)
    def test_most_popular_types_and_sort(self):
        tg = Tags("tags.csv")
        d = tg.most_popular(5)
        assert isinstance(d, dict)
        assert list(d.values()) == sorted(d.values(), reverse=True)
    def test_tags_with_types_and_sort(self):
        tg = Tags("tags.csv")
        lst = tg.tags_with("funny")
        assert isinstance(lst, list)
        assert lst == sorted(lst)

@pytest.mark.skipif(not have_all(), reason="missing CSVs")
class TestLinks:
    def test_get_imdb_types_and_sort(self):
        lk = Links("links.csv","fields.csv")
        res = lk.get_imdb([1,2,3], ["Director","Budget","Runtime"])
        assert isinstance(res, list)
        assert all(isinstance(x,list) for x in res)
        mids = [row[0] for row in res if isinstance(row,list) and row and isinstance(row[0],int)]
        assert mids == sorted(mids, reverse=True)
    def test_top_directors(self):
        lk = Links("links.csv","fields.csv")
        d = lk.top_directors(5)
        assert isinstance(d, dict)
        assert list(d.values()) == sorted(d.values(), reverse=True)
    def test_most_expensive(self):
        lk = Links("links.csv","fields.csv")
        d = lk.most_expensive(5)
        assert isinstance(d, dict)
        assert list(d.values()) == sorted(d.values(), reverse=True)
    def test_most_profitable(self):
        lk = Links("links.csv","fields.csv")
        d = lk.most_profitable(5)
        assert isinstance(d, dict)
        assert list(d.values()) == sorted(d.values(), reverse=True)
    def test_longest(self):
        lk = Links("links.csv","fields.csv")
        d = lk.longest(5)
        assert isinstance(d, dict)
        assert list(d.values()) == sorted(d.values(), reverse=True)
    def test_top_cost_per_minute(self):
        lk = Links("links.csv","fields.csv")
        d = lk.top_cost_per_minute(5)
        assert isinstance(d, dict)
        assert list(d.values()) == sorted(d.values(), reverse=True)

class TestRatings:
    def test_dist_by_year_types_and_sort(self):
        rs = Ratings("ratings.csv","movies.csv")
        rm = rs.Movies(rs.lines, rs.movie_titles)
        d = rm.dist_by_year()
        assert isinstance(d, dict)
        assert list(d.keys()) == sorted(d.keys())
    def test_dist_by_rating_types_and_sort(self):
        rs = Ratings("ratings.csv","movies.csv")
        rm = rs.Movies(rs.lines, rs.movie_titles)
        d = rm.dist_by_rating()
        assert isinstance(d, dict)
        assert list(d.keys()) == sorted(d.keys())
    def test_top_by_num_of_ratings(self):
        rs = Ratings("ratings.csv","movies.csv")
        rm = rs.Movies(rs.lines, rs.movie_titles)
        d = rm.top_by_num_of_ratings(5)
        assert isinstance(d, dict)
        assert list(d.values()) == sorted(d.values(), reverse=True)
    def test_top_by_ratings_average(self):
        rs = Ratings("ratings.csv","movies.csv")
        rm = rs.Movies(rs.lines, rs.movie_titles)
        d = rm.top_by_ratings(5, "average")
        assert isinstance(d, dict)
        assert list(d.values()) == sorted(d.values(), reverse=True)
    def test_top_controversial(self):
        rs = Ratings("ratings.csv","movies.csv")
        rm = rs.Movies(rs.lines, rs.movie_titles)
        d = rm.top_controversial(5)
        assert isinstance(d, dict)
        assert list(d.values()) == sorted(d.values(), reverse=True)
    def test_users_distributions_and_top(self):
        rs = Ratings("ratings.csv","movies.csv")
        u = rs.Users(rs.lines, rs.limit)
        a = u.dist_by_num_of_ratings()
        b = u.dist_by_ratings()
        c = u.top_controversial_users(5)
        assert isinstance(a, dict) and list(a.keys()) == sorted(a.keys())
        assert isinstance(b, dict) and list(b.keys()) == sorted(b.keys())
        assert isinstance(c, dict) and list(c.values()) == sorted(c.values(), reverse=True)
