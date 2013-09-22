"""Tests for the sentiment module"""

import unittest
import sentiment

class TestSentimentFactory(unittest.TestCase):
	"""Tests for the SentimentFactory class"""
	def test_instantiate_sentiment_factory(self):
		"""Tests we can instantiate SentimentFactory"""
		obj_ut = sentiment.SentimentFactory()
		self.assertIsInstance(obj_ut, sentiment.SentimentFactory)

class TestLibraryRun(unittest.TestCase):
	"""Tests for the LibraryRun class"""
	def test_instantiate_library_run(self):
		obj_ut = sentiment.LibraryRun()
		self.assertIsInstance(obj_ut, sentiment.LibraryRun)

if __name__ == '__main__':
	unittest.main()

