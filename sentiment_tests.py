"""Tests for the sentiment module"""

import unittest
import sentiment

class TestCleanRowFunction(unittest.TestCase):
	"""Tests clean_row function cleans rows properly"""
	def test_clean_row_punctuation(self):
		"""Tests clean_row removes punctuation correctly"""
		obj_ut = sentiment.clean_row(
			'100\tan "apple...:" is it yellow-green, or red/orange?')
		self.assertEqual(obj_ut[1], "an apple is it yellowgreen or redorange")
		
class TestSentimentFactory(unittest.TestCase):
	"""Tests for the SentimentFactory class"""
	def test_instantiate_sentiment_factory(self):
		"""Tests we can instantiate SentimentFactory"""
		obj_ut = sentiment.SentimentFactory("", "")
		self.assertIsInstance(obj_ut, sentiment.SentimentFactory)



class TestLibraryRun(unittest.TestCase):
	"""Tests for the LibraryRun class"""
	def test_instantiate_library_run(self):
		obj_ut = sentiment.LibraryRun()
		self.assertIsInstance(obj_ut, sentiment.LibraryRun)


if __name__ == '__main__':
	unittest.main()

