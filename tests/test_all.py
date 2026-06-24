"""Tests unitaires — Projet Python Avancé."""
import unittest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import db
from report import (
    word_count, round_to_tens, split_paragraphs,
    parse_metadata, extract_first_chapter
)


class TestRoundToTens(unittest.TestCase):
    def test_123(self): self.assertEqual(round_to_tens(123), 120)
    def test_127(self): self.assertEqual(round_to_tens(127), 120)
    def test_129(self): self.assertEqual(round_to_tens(129), 120)
    def test_130(self): self.assertEqual(round_to_tens(130), 130)
    def test_zero(self): self.assertEqual(round_to_tens(0), 0)


class TestWordCount(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(word_count("Bonjour tout le monde"), 4)

    def test_empty(self):
        self.assertEqual(word_count(""), 0)

    def test_punctuation(self):
        self.assertEqual(word_count("Hello, world!"), 2)


class TestSplitParagraphs(unittest.TestCase):
    def test_two_paragraphs(self):
        txt = ("Voici un premier paragraphe avec suffisamment de mots pour le test.\n\n"
               "Et voici un deuxième paragraphe également assez long.")
        result = split_paragraphs(txt)
        self.assertEqual(len(result), 2)

    def test_short_ignored(self):
        txt = "Court.\n\nParagraphe long avec plein de mots pour dépasser le seuil minimum requis."
        result = split_paragraphs(txt)
        self.assertEqual(len(result), 1)


class TestParseMetadata(unittest.TestCase):
    def test_title_author(self):
        fake_text = "Title: Pride and Prejudice\nAuthor: Jane Austen\nSome content."
        title, author = parse_metadata(fake_text)
        self.assertEqual(title, "Pride and Prejudice")
        self.assertEqual(author, "Jane Austen")

    def test_missing(self):
        title, author = parse_metadata("No metadata here.")
        self.assertEqual(title, "Pride and Prejudice")
        self.assertEqual(author, "Jane Austen")


class TestDB(unittest.TestCase):
    TEST_DB = "test_countries.db"

    def setUp(self):
        import db as database
        database.DB_PATH = self.TEST_DB
        database.init_db()

    def tearDown(self):
        import db as database
        database.clear()
        if os.path.exists(self.TEST_DB):
            os.remove(self.TEST_DB)

    def test_insert_and_fetch(self):
        import db as database
        database.insert_many([("France", "Europe", 67000000, 551695.0)])
        rows = database.fetch_all()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], "France")

    def test_is_empty(self):
        import db as database
        self.assertTrue(database.is_empty())

    def test_clear(self):
        import db as database
        database.insert_many([("Germany", "Europe", 83000000, 357114.0)])
        database.clear()
        self.assertTrue(database.is_empty())

    def test_avg_population(self):
        import db as database
        database.insert_many([
            ("A", "Europe", 100, 0.0),
            ("B", "Europe", 200, 0.0),
        ])
        self.assertAlmostEqual(database.avg_population(), 150.0)

    def test_total_population(self):
        import db as database
        database.insert_many([
            ("A", "Europe", 100, 0.0),
            ("B", "Asia",   200, 0.0),
        ])
        self.assertEqual(database.total_population(), 300)


if __name__ == "__main__":
    unittest.main(verbosity=2)