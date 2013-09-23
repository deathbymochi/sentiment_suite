"""Tests for the sentiment module"""

import unittest
import sentiment
import mock
import StringIO
import __builtin__

def fake_open_library(*args):
	"""Fakes opening library file"""
	result = mock.Mock()
	result.__exit__ = mock.Mock(return_value=False)
	result.__enter__ = mock.Mock(return_value=StringIO.StringIO("good\t1\nbad\t-1"))
	return result

def fake_clean_row(row):
	"""Fakes the clean_row function"""
	return row

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

	@mock.patch('sentiment.clean_row', fake_clean_row)
	def test_stream_lines(self):
		"""Tests that stream_lines function streams lines"""
		test_fo = StringIO.StringIO("this is line 1\nthis is line 2\n")
		test = sentiment.SentimentFactory("", "")
		obj_ut = [line for line in test.stream_lines(test_fo)]
		self.assertEqual(obj_ut, ['this is line 1\n', 'this is line 2\n'])

	def test_append_to_output_file(self):
		"""Tests that append_to_output_file appends line to output file.
		This maybe doesn't test appending as you would expect, but we couldn't
		figure out how to do it using a StringIO object and this is probably
		cleaner than mocking everything"""
		test = sentiment.SentimentFactory("", "")
		run_instance = mock.Mock()
		run_instance.results = "this is a line to append\n"
		output_file = StringIO.StringIO()
		target = "this is a line to append\n"
		test.append_to_output_file(run_instance, output_file)
		self.assertEqual(output_file.getvalue(), target)


class TestLibraryRun(unittest.TestCase):
	"""Tests for the LibraryRun class"""
	def test_instantiate_library_run(self):
		obj_ut = sentiment.LibraryRun()
		self.assertIsInstance(obj_ut, sentiment.LibraryRun)


if __name__ == '__main__':
	unittest.main()

