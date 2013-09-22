"""Tests for the sentiment module"""

import unittest
import sentiment
import mock
import StringIO
import __builtin__

class TestCleanRowFunction(unittest.TestCase):
	"""Tests clean_row function cleans rows properly"""
	def test_clean_row_lowercase(self):
		"""Tests clean_row changes text to lower case"""
		obj_ut = sentiment.clean_row(
			'100\tAn APPLE so GOODforme')
		self.assertEqual(obj_ut[1], "an apple so goodforme")

	def test_clean_row_punctuation(self):
		"""Tests clean_row removes punctuation correctly"""
		obj_ut = sentiment.clean_row(
			'100\tan "apple...:" is it yellow-green, or red/orange?')
		self.assertEqual(obj_ut[1], "an apple is it yellowgreen or redorange")


def fake_open_library(*args):
	"""Fakes opening library file"""
	result = mock.Mock()
	result.__exit__ = mock.Mock(return_value=False)
	result.__enter__ = mock.Mock(return_value=StringIO.StringIO("good\t1\nbad\t-1"))
	return result

class TestSentimentFactory(unittest.TestCase):
	"""Tests for the SentimentFactory class"""
	def test_instantiate_sentiment_factory(self):
		"""Tests we can instantiate SentimentFactory"""
		obj_ut = sentiment.SentimentFactory("", "")
		self.assertIsInstance(obj_ut, sentiment.SentimentFactory)

	@mock.patch('__builtin__.open', fake_open_library)
	def test_get_library_from_file(self):
		"""Tests that library is loaded correctly"""
		test = sentiment.SentimentFactory("", "")
		obj_ut = test.get_library_from_file("")
		self.assertEqual(obj_ut, {'good':(1,0), 'bad':(-1,1)})

class TestLibraryRun(unittest.TestCase):
	"""Tests for the LibraryRun class"""
	def test_instantiate_library_run(self):
		obj_ut = sentiment.LibraryRun()
		self.assertIsInstance(obj_ut, sentiment.LibraryRun)


if __name__ == '__main__':
	unittest.main()

