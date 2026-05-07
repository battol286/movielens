import os, re, csv, requests
from bs4 import BeautifulSoup
from collections import defaultdict, Counter
from datetime import datetime, timezone

class Movies:
    def __init__(self, path):
        self.limit = 1000
        if not os.path.exists(path): raise ValueError("File not found: " + str(path))
        with open(path, "r", encoding="utf-8") as f:
            f.readline()
            self.lines = f.readlines()
    @staticmethod
    def _parse_title_year(raw):
        s = raw.strip().replace('"', "")
        m = re.match(r"^(.*)\s\((\d{4})\)$", s)
        return (m.group(1), m.group(2)) if m else (s, "Unknown")
    def dist_by_release(self):
        out, c = {}, 0
        for line in self.lines:
            if c >= self.limit: break
            cols = line.rstrip("\n").split(",")
            title_field = ",".join(cols[1:-1]).replace('"', "")
            _, y = self._parse_title_year(title_field)
            out[y] = out.get(y, 0) + 1
            c += 1
        return dict(sorted(out.items(), key=lambda x: x[1], reverse=True))
    def dist_by_genres(self):
        out, c = {}, 0
        for line in self.lines:
            if c >= self.limit: break
            cols = line.rstrip("\n").split(",")
            for g in (cols[-1].split("|") if cols and cols[-1] else []):
                if g: out[g] = out.get(g, 0) + 1
            c += 1
        return dict(sorted(out.items(), key=lambda x: x[1], reverse=True))
    def most_genres(self, n):
        if n <= 0: raise ValueError("n must be positive")
        data, c = {}, 0
        for line in self.lines:
            if c >= self.limit: break
            cols = line.rstrip("\n").split(",")
            title_field = ",".join(cols[1:-1]).replace('"', "")
            title, _ = self._parse_title_year(title_field)
            genre_list = cols[-1].split("|") if cols and cols[-1] else []
            data[title] = len([g for g in genre_list if g])
            c += 1
        return dict(sorted(data.items(), key=lambda x: x[1], reverse=True)[:n])
    def movie_titles(self):
        out = {}
        for line in self.lines:
            cols = line.rstrip("\n").split(",")
            mid = int(cols[0])
            title = ",".join(cols[1:-1]).replace('"', "")
            out[mid] = title
        return out

class Ratings:
    def __init__(self, ratings_path, movies_path):
        self.limit = 1000
        if not os.path.exists(ratings_path): raise ValueError("File not found: " + str(ratings_path))
        if not os.path.exists(movies_path): raise ValueError("File not found: " + str(movies_path))
        with open(ratings_path, "r", encoding="utf-8") as f:
            f.readline()
            self.lines = f.readlines()
        self.movies = Movies(movies_path)
        self.movie_titles = self.movies.movie_titles()
    class Movies:
        def __init__(self, ratings_lines, movie_titles, limit=1000):
            self.limit = limit
            self.lines = ratings_lines
            self.movie_titles = movie_titles
        @staticmethod
        def _year(line):
            ts = int(line.strip().split(",")[-1])
            return datetime.fromtimestamp(ts, tz=timezone.utc).year
        @staticmethod
        def _metric(vals, name):
            n = len(vals)
            if n == 0: return 0.0
            if name == "average": return sum(vals) / n
            if name == "median":
                s = sorted(vals)
                return s[n//2] if n % 2 else (s[n//2-1] + s[n//2]) / 2
            if name == "variance":
                m = sum(vals) / n
                return sum((x - m) ** 2 for x in vals) / n
            raise ValueError("unknown metric")
        def dist_by_year(self):
            yrs = [self._year(x) for x in self.lines]
            return dict(sorted(Counter(yrs).items())[:self.limit])
        def dist_by_rating(self):
            vals = [float(x.strip().split(",")[2]) for x in self.lines]
            return dict(sorted(Counter(vals).items())[:self.limit])
        def top_by_num_of_ratings(self, n):
            n = min(n, self.limit)
            cnt = defaultdict(int)
            for line in self.lines:
                mid = int(line.strip().split(",")[1])
                cnt[mid] += 1
            top = sorted(cnt.items(), key=lambda x: x[1], reverse=True)[:n]
            return {self.movie_titles.get(mid, f"Unknown Movie ID: {mid}"): c for mid, c in top}
        def top_by_ratings(self, n, metric="average"):
            metric = metric.strip().lower()
            if metric not in {"average","median"}: raise ValueError("unknown metric")
            n = min(n, self.limit)
            bym = defaultdict(list)
            for line in self.lines:
                _, mid, rating, *_ = line.strip().split(",")
                bym[int(mid)].append(float(rating))
            pairs = {mid: round(self._metric(vals, metric), 2) for mid, vals in bym.items()}
            top = sorted(pairs.items(), key=lambda x: x[1], reverse=True)[:n]
            return {self.movie_titles.get(mid, f"Unknown Movie ID: {mid}"): v for mid, v in top}
        def top_controversial(self, n):
            n = min(n, self.limit)
            bym = defaultdict(list)
            for line in self.lines:
                _, mid, rating, *_ = line.strip().split(",")
                bym[int(mid)].append(float(rating))
            var = {mid: (round(self._metric(vals, "variance"), 2) if len(vals)>1 else 0.0) for mid, vals in bym.items()}
            top = sorted(var.items(), key=lambda x: x[1], reverse=True)[:n]
            return {self.movie_titles.get(mid, f"Unknown Movie ID: {mid}"): v for mid, v in top}
    class Users(Movies):
        def __init__(self, ratings_lines, limit):
            self.limit = limit
            self.lines = ratings_lines
            self.movie_titles = {}
        def dist_by_num_of_ratings(self):
            cnt = defaultdict(int)
            for line in self.lines:
                uid = int(line.strip().split(",")[0])
                cnt[uid] += 1
            return dict(sorted(cnt.items()))
        def dist_by_ratings(self, metric="average"):
            metric = metric.strip().lower()
            if metric not in {"average","median"}: raise ValueError("unknown metric")
            byu = defaultdict(list)
            for line in self.lines:
                uid, _, rating, *_ = line.strip().split(",")
                byu[int(uid)].append(float(rating))
            out = {uid: round(self._metric(vals, metric), 2) for uid, vals in byu.items()}
            return dict(sorted(out.items()))
        def top_controversial_users(self, n):
            n = min(n, self.limit)
            byu = defaultdict(list)
            for line in self.lines:
                uid, _, rating, *_ = line.strip().split(",")
                byu[int(uid)].append(float(rating))
            var = {uid: (round(self._metric(vals, "variance"), 2) if len(vals)>1 else 0.0) for uid, vals in byu.items()}
            return dict(sorted(var.items(), key=lambda x: x[1], reverse=True)[:n])

class Tags:
    def __init__(self, path):
        self.limit = 1000
        if not os.path.exists(path): raise ValueError("File not found: " + str(path))
        with open(path, "r", encoding="utf-8") as f:
            f.readline()
            self.lines = f.readlines()
    @staticmethod
    def _count_words(tag):
        return len(set(re.findall(r"\w+", tag)))
    def _tags_with_counts(self):
        out = []
        for line in self.lines:
            tag = line.split(",")[2].strip()
            out.append((tag, self._count_words(tag)))
        return out
    def most_words(self, n):
        n = min(n, self.limit)
        uniq = list(set(self._tags_with_counts()))
        return dict(sorted(uniq, key=lambda x: x[1], reverse=True)[:n])
    def longest(self, n):
        n = min(n, self.limit)
        uniq = list(set([t for t,_ in self._tags_with_counts()]))
        return sorted(uniq, key=lambda s: len(s), reverse=True)[:n]
    def most_words_and_longest(self, n):
        n = min(n, self.limit)
        a = set(self.most_words(n).keys())
        b = set(self.longest(n))
        return sorted(a & b)
    def most_popular(self, n):
        n = min(n, self.limit)
        tags = [line.split(",")[2].strip() for line in self.lines]
        return dict(sorted(Counter(tags).items(), key=lambda x: x[1], reverse=True)[:n])
    def tags_with(self, word):
        res = []
        for line in self.lines:
            tag = line.split(",")[2].strip()
            if word.lower() in tag.lower():
                res.append(tag)
        return sorted(set(res))

class Links:
    def __init__(self, links_path, fields_path):
        self.limit = 1000
        self.links_file_path = links_path
        self.fields_file_path = fields_path
        if not os.path.exists(links_path): raise ValueError("File not found: " + str(links_path))
        if not os.path.exists(fields_path): raise ValueError("File not found: " + str(fields_path))
        self.links_file = {}
        self.movie_fields = {}
        with open(self.links_file_path, "r", encoding="utf-8") as f:
            f.readline()
            for line in f:
                movie_id, imdb_id, _ = line.strip().split(",")
                self.links_file[movie_id] = imdb_id
        with open(self.fields_file_path, "r", encoding="utf-8") as f:
            f.readline()
            for line in f:
                p = line.strip().split(";")
                self.movie_fields[p[1]] = {
                    "title": p[2].strip(),
                    "description": p[3].strip(),
                    "director": p[4].strip(),
                    "writers": p[5].strip(),
                    "stars": p[6].strip(),
                    "runtime": p[7].strip(),
                    "budget": p[8].strip(),
                    "gross": p[9].strip(),
                }
    @staticmethod
    def _title(soup):
        t = soup.find("title")
        return t.text.replace(" - IMDb", "") if t else "Unknown Title"
    @staticmethod
    def _desc(soup):
        m = soup.find(attrs={"name":"description"})
        return m["content"] if m else "Unknown Description"
    @staticmethod
    def _directors(soup):
        lab = soup.find("span", class_="ipc-metadata-list-item__label", string="Director")
        if not lab: return "Unknown Directors"
        ul = lab.find_next("ul", class_="ipc-inline-list")
        return ", ".join(a.text for a in ul.find_all("a")) if ul else "Unknown Directors"
    @staticmethod
    def _writers(soup):
        lab = soup.find("a", class_="ipc-metadata-list-item__label", string="Writers")
        if not lab: return "Unknown Writers"
        ul = lab.find_next("ul", class_="ipc-inline-list")
        return ", ".join(a.text for a in ul.find_all("a")) if ul else "Unknown Writers"
    @staticmethod
    def _stars(soup):
        lab = soup.find("a", class_="ipc-metadata-list-item__label", string="Stars")
        if not lab: return "Unknown Stars"
        ul = lab.find_next("ul", class_="ipc-inline-list")
        return ", ".join(a.text for a in ul.find_all("a")) if ul else "Unknown Stars"
    @staticmethod
    def _runtime(soup):
        li = soup.find("li", {"data-testid":"title-techspec_runtime"})
        return li.find("div").text.strip() if li else "Unknown Runtime"
    @staticmethod
    def _budget(soup):
        li = soup.find("li", {"data-testid":"title-boxoffice-budget"})
        return li.find("div").text.strip() if li else "Unknown Budget"
    @staticmethod
    def _gross(soup):
        li = soup.find("li", {"data-testid":"title-boxoffice-cumulativeworldwidegross"})
        return li.find("div").text.strip() if li else "Unknown Cumulative Worldwide Gross"
    @staticmethod
    def currency_to_decimal(s):
        num = "".join(ch for ch in s if ch.isdigit() or ch == ".")
        try: return float(num)
        except: return 0.0
    @staticmethod
    def time_to_minutes(s):
        h = m = 0
        parts = s.split()
        for i, p in enumerate(parts):
            if p.isdigit():
                v = int(p)
                if i+1 < len(parts):
                    nxt = parts[i+1].lower()
                    if "hour" in nxt: h = v
                    elif "minute" in nxt: m = v
        return h*60 + m
    @staticmethod
    def get_all_fields(imdb_id):
        url = f"https://www.imdb.com/title/tt{imdb_id}/"
        try:
            r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=10)
            r.raise_for_status()
        except:
            return {
                "title":"Unknown Title","description":"Unknown Description","director":"Unknown Director",
                "writers":"Unknown Writers","stars":"Unknown Stars","runtime":"Unknown Runtime",
                "budget":"Unknown Budget","gross":"Unknown Cumulative Worldwide Gross"
            }
        soup = BeautifulSoup(r.text, "html.parser")
        return {
            "title": Links._title(soup),
            "description": Links._desc(soup),
            "director": Links._directors(soup),
            "writers": Links._writers(soup),
            "stars": Links._stars(soup),
            "runtime": Links._runtime(soup),
            "budget": Links._budget(soup),
            "gross": Links._gross(soup),
        }
    def get_imdb_id(self, movie_id):
        return self.links_file.get(str(movie_id))
    def get_imdb(self, movie_ids, fields):
        fmap = {"Title":"title","Description":"description","Director":"director","Writers":"writers",
                "Stars":"stars","Runtime":"runtime","Budget":"budget","Cumulative Worldwide Gross":"gross"}
        for f in fields:
            if f not in fmap: raise ValueError("Invalid field: " + f + " Allowed: " + ", ".join(fmap.keys()))
        keys = [fmap[f] for f in fields]
        out = []
        for mid in movie_ids:
            iid = self.get_imdb_id(mid)
            if not iid: out.append([f"Unknown Movie Id: {mid}"]); continue
            data = self.movie_fields.get(iid)
            if not data: out.append([f"Failed to fetch data for Movie Id: {mid}"]); continue
            row = [int(mid)] + [data[k] for k in keys]
            out.append(row)
        out.sort(key=lambda x: x[0], reverse=True)
        return out
    def top_directors(self, n):
        n = min(n, self.limit)
        cnt = defaultdict(int)
        for iid in self.links_file.values():
            d = self.movie_fields.get(iid)
            if d:
                for name in d["director"].split(", "):
                    if name.strip(): cnt[name.strip()] += 1
        return dict(sorted(cnt.items(), key=lambda x: x[1], reverse=True)[:n])
    def most_expensive(self, n):
        n = min(n, self.limit)
        b = {}
        for iid in self.links_file.values():
            d = self.movie_fields.get(iid)
            if d and d["budget"] != "Unknown":
                b[d["title"]] = Links.currency_to_decimal(d["budget"])
        return dict(sorted(b.items(), key=lambda x: x[1], reverse=True)[:n])
    def most_profitable(self, n):
        n = min(n, self.limit)
        p = {}
        for iid in self.links_file.values():
            d = self.movie_fields.get(iid)
            try:
                if d and d["budget"] != "Unknown Budget" and d["gross"] != "Unknown Cumulative Worldwide Gross":
                    p[d["title"]] = Links.currency_to_decimal(d["gross"]) - Links.currency_to_decimal(d["budget"])
            except: pass
        return dict(sorted(p.items(), key=lambda x: x[1], reverse=True)[:n])
    def longest(self, n):
        n = min(n, self.limit)
        rt = {}
        for iid in self.links_file.values():
            d = self.movie_fields.get(iid)
            try:
                if d and d["runtime"] != "Unknown Runtime":
                    rt[d["title"]] = Links.time_to_minutes(d["runtime"])
            except: pass
        return dict(sorted(rt.items(), key=lambda x: x[1], reverse=True)[:n])
    def top_cost_per_minute(self, n):
        n = min(n, self.limit)
        cpm = {}
        for iid in self.links_file.values():
            d = self.movie_fields.get(iid)
            try:
                if d and d["budget"] != "Unknown Budget" and d["runtime"] != "Unknown Runtime":
                    budget = Links.currency_to_decimal(d["budget"])
                    minutes = Links.time_to_minutes(d["runtime"])
                    if minutes > 0: cpm[d["title"]] = round(budget/minutes, 2)
            except: pass
        return dict(sorted(cpm.items(), key=lambda x: x[1], reverse=True)[:n])

class Tests:
    @staticmethod
    def is_list_of_type(x, t): return isinstance(x, list) and all(isinstance(i, t) for i in x)
    @staticmethod
    def is_dict_of_types(d, kt, vt): return isinstance(d, dict) and all(isinstance(k, kt) and isinstance(v, vt) for k,v in d.items())
    @staticmethod
    def sorted_keys(d, reverse=False): return list(d.keys()) == sorted(d.keys(), reverse=reverse)

if __name__ == "__main__":
    pass
