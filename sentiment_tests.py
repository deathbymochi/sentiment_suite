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

	def test_clean_row_control_chars(self):
		pass

	# def test_clean_row_digits(self):
	# 	"""Tests clean_row removes digits"""
	# 	obj_ut = sentiment.clean_row(
	# 		'100\t1 apple three apple 123 apples')
	# 	self.assertEqual(obj_ut[1], ' apple three apple  apples')

class TestLibraryHelperFunctions(unittest.TestCase):
	"""Tests that library-making helper functions work correctly"""
	@mock.patch('__builtin__.open', fake_open_library)
	def test_get_library_from_file(self):
		"""Tests that library is loaded correctly"""
		obj_ut = sentiment.get_library_from_file("")
		self.assertEqual(obj_ut, {'good':(1,0), 'bad':(-1,1)})

	def test_create_negation_lib(self):
		"""Tests that negation library is created correctly"""
		obj_ut = sentiment.create_negation_lib(
			{'good': (1, 0), 'bad': (-1, 1)})
		self.assertEqual(obj_ut, 
			{'(not|dont|cant|wont|couldnt|shouldnt|never) \w{0,2} good': (-1, 0),
			'(not|dont|cant|wont|couldnt|shouldnt|never) \w{0,2} bad': (1, 1)})

	def test_get_opposite_meaning_add(self):
		"""Tests that get_opposite_meaning function correctly adds negation
		words to given phrase"""
		obj_ut = sentiment.get_opposite_meaning(
			"good")
		self.assertEqual(obj_ut, 
			"(not|dont|cant|wont|couldnt|shouldnt|never) \w{0,2} good")

	def test_get_opposite_meaning_subtract(self):
		"""Tests that get_opposite_meaning function correctly takes away
		negation words from given phrase"""
		obj_ut = sentiment.get_opposite_meaning(
			"(not|dont|cant|wont|couldnt|shouldnt|never) \w{0,2} good")
		self.assertEqual(obj_ut, "good")


class TestGetWordFreqFunction(unittest.TestCase):
	"""Tests get_word_freq function returns word frequency properly"""
	def test_get_word_freq(self):
		obj_ut = sentiment.get_word_freq(
			'apple orange orange orange mangosteen')
		self.assertDictEqual(obj_ut, {'apple': 1, 'orange': 3, 'mangosteen': 1})


class TestTokenizeFunction(unittest.TestCase):
	"""Tests tokenize function returns list of tokens properly"""
	def test_tokenize_min_words(self):
		"""Tests tokenize function creates tokens 
		no shorter than min_words long"""
		obj_ut = list(sentiment.tokenize(
			['a', 'brown', 'cat', 'chases', 'mice'], min_words=2))
		self.assertEqual(obj_ut, 
			[('a brown', 0), 
			('brown cat', 1), 
			('cat chases', 2), 
			('chases mice', 3)])

	def test_tokenize_no_min_no_max(self):
		"""Tests tokenize function creates 1-word tokens when
		no min_words or max_words args are provided"""
		obj_ut = list(sentiment.tokenize(
			['a', 'brown', 'cat', 'chases', 'mice']))
		self.assertEqual(obj_ut, 
			[('a', 0), ('brown', 1), ('cat', 2), ('chases', 3), ('mice', 4)])

	def test_tokenize_max_words(self):
		"""Tests tokenize function creates tokens up to max_words long"""
		obj_ut = list(sentiment.tokenize(
			['a', 'brown', 'cat', 'chases', 'mice'], max_words=4))
		self.assertEqual(obj_ut, 
			[('a', 0), ('brown', 1), ('cat', 2), ('chases', 3), ('mice', 4),
			('a brown', 0), ('brown cat', 1), ('cat chases', 2), ('chases mice', 3),
			('a brown cat', 0), ('brown cat chases', 1), ('cat chases mice', 2),
			('a brown cat chases', 0), ('brown cat chases mice', 1)])

	def test_tokenize_zero_value(self):
		"""Tests tokenize function correctly defaults to 1-word tokens if
		zero values given for min_words or max_words"""
		text = ['a', 'brown', 'cat', 'chases', 'mice']
		min_words = max_words = 0
		args = [text, min_words, max_words]
		func = sentiment.tokenize
		self.assertRaises(sentiment.SentimentException,
			lambda y: list(func(*y)), args)


class TestSentimentFactory(unittest.TestCase):
	"""Tests for the SentimentFactory class"""
	def test_instantiate_sentiment_factory(self):
		"""Tests we can instantiate SentimentFactory"""
		obj_ut = sentiment.SentimentFactory("", "")
		self.assertIsInstance(obj_ut, sentiment.SentimentFactory)

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
	def setUp(self):
		"""Define commonly used test things"""
		self.text = '100\ttoday was not a good day. it was pretty bad.'
		self.lib = {'good': (1, 0), 'bad': (-1, 1)}
		self.tokens_generator = [
		('today', 0), ('was', 1), ('not', 2), ('good', 3), ('today was', 0),
		('was not', 1), ('not good', 2)]
		## TO DO: FIX THE NEGATION MATCHES HITTING

	def test_instantiate_library_run(self):
		"""Tests that LibraryRun class instantiates"""
		obj_ut = sentiment.LibraryRun("", "", "")
		self.assertIsInstance(obj_ut, sentiment.LibraryRun)

	def test_find_phrase_matches(self):
		"""Tests find_phrase_matches finds correct matches in text using
		negation library and normal library"""
		test = sentiment.LibraryRun(self.text, self.lib)
		obj_ut = test.find_phrase_matches(self.tokens_generator)
		print obj_ut
		self.assertEqual(dict(obj_ut),
			{'not good': (2, -1, 0)})

if __name__ == '__main__':
	unittest.main()

