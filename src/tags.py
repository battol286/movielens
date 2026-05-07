import os
import re
from collections import Counter


class Tags:
    """
    Analyzing data from tags.csv
    """

    def __init__(self, path_to_the_file):
        """
        Initialize the Tags class with the path to the tags.csv file.
        """
        self.limit = 1000
        self.path = path_to_the_file

        if not os.path.exists(path_to_the_file):
            raise ValueError("File not found: ", path_to_the_file)

        with open(path_to_the_file, 'r') as file:
            file.readline()
            tags = file.readlines()

        self.tags_file = tags

    @staticmethod
    def get_count_words(tag):
        words = re.findall(r'\w+', tag)
        words = set(words)

        return len(words)

    def get_tags_with_count_words(self):
        res = []
        for line in self.tags_file:
            tag = line.split(',')[2].strip()
            res.append((tag, self.get_count_words(tag)))

        return res

    def most_words(self, n):
        """
        The method returns top-n tags with most words inside. It is a dict
        where the keys are tags and the values are the number of words inside the tag.
        Drop the duplicates. Sort it by numbers descendingly.
        """

        n = min(n, self.limit)

        unique_tags = list(set(self.get_tags_with_count_words()))
        big_tags = sorted(unique_tags, key=lambda x: x[1], reverse=True)

        return dict(big_tags[:n])

    def longest(self, n):
        """
        The method returns top-n longest tags in terms of the number of characters.
        It is a list of the tags. Drop the duplicates. Sort it by numbers descendingly.
        """

        n = min(n, self.limit)

        unique_tags = list(
            set([tag[0] for tag in self.get_tags_with_count_words()]))
        big_tags = sorted(unique_tags, key=lambda x: len(x), reverse=True)

        return big_tags[:n]

    def most_words_and_longest(self, n):
        """
        The method returns the intersection between top-n tags with most words inside and
        top-n longest tags in terms of the number of characters.
        Drop the duplicates. It is a list of the tags.
        """

        n = min(n, self.limit)

        most_words_tags = set(self.most_words(n).keys())
        longest_tags = set(self.longest(n))
        intersection = most_words_tags.intersection(longest_tags)

        return sorted(intersection)

    def most_popular(self, n):
        """
        The method returns the most popular tags.
        It is a dict where the keys are tags and the values are the counts.
        Drop the duplicates. Sort it by counts descendingly.
        """

        n = min(n, self.limit)

        tags = []
        for line in self.tags_file:
            tag = line.split(',')[2].strip()
            tags.append(tag)

        tag_counts = Counter(tags)
        popular_tags = sorted(tag_counts.items(),
                              key=lambda x: x[1], reverse=True)

        return dict(popular_tags[:n])

    def tags_with(self, word):
        """
        The method returns all unique tags that include the word given as the argument.
        Drop the duplicates. It is a list of the tags. Sort it by tag names alphabetically.
        """

        tags = []
        for line in self.tags_file:
            tag = line.split(',')[2].strip()
            if word.lower() in tag.lower():
                tags.append(tag)

        tags_with_word = sorted(set(tags))

        return tags_with_word


# if __name__ == "__main__":
#     tags = Tags('tags.csv')

#     print(tags.most_words(5))
#     print(tags.longest(5))
#     print(tags.most_words_and_longest(5))
#     print(tags.most_popular(5))
#     print(tags.tags_with('funny'))
