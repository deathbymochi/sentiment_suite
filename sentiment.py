"""A module for sentiment analysis"""

import re
import os
import collections
import string

class SentimentException(Exception):
	pass


def clean_row(row):
	"""Cleans row from text file, outputs tuple (ID, cleaned_text)"""
	text_id, text = row.split('\t')
	text = text.lower()
	text = re.sub(r'[^\w\s]', '', text)
	text = text.translate(string.maketrans('\n\t\r', '   '))
	#text = re.sub('\d', '', text)
	return (text_id, text)

def get_word_freq(text):
	"""Gets word freq for each word in a text string"""
	split_text = text.split()
	word_freq = collections.defaultdict(int)
	for word in split_text:
		word_freq[word] += 1
	return word_freq

def tokenize(text, min_words=1, max_words=None):
	"""Creates tokens out of text, of length ranging 
	from min_words to max_words

	text = list of single words in order of the text
	min_words = min number of words to make token out of
	max_words = max number of words to make token out of
	"""
	if max_words == None:
		max_words = min_words

	if min_words == 0 or max_words == 0:
		raise SentimentException("learn how to count!")

	for j in range(max_words - min_words + 1):
		for i in range(len(text)):
			if i > len(text) - min_words - j:
				break
			else:
				yield (' '.join(text[i:(i + j + min_words)]), i)


class SentimentFactory(object):
	"""Factory class for creating instances of library runs"""
	def __init__(self, text_filepath, library_filepath, output_directory="", 
		        output_filename="sentiment_summary.txt"):
		self.text_filepath = text_filepath
		self.library_filepath = library_filepath
		self.output_directory = output_directory
		self.output_filename = output_filename

	def run_suite(self):
		"""Starts library runs for each essay"""
		library = self.get_library_from_file(self.library_filepath)
		with open(self.output_directory+self.output_filename, "a") as out:
			with open(text_filepath, "r") as full_text:
				texts = self.stream_lines(full_text)
				for text in texts:
					run_instance = LibraryRun(text, library)
					self.append_to_output_file(run_instance, out)
					#verbose_output(run_instance)

	def get_library_from_file(self, library_filepath):
		"""Load library from filepath

		output = dictionary of library phrases to tuple of 
		(phrase score, rule index)"""
		with open(library_filepath, "r") as lib_file:
			library = {}
			for index, line in enumerate(lib_file):
				phrase, score = line.split('\t')
				library[phrase] = (int(score), index)
		return library

	def stream_lines(self, full_text):
		"""Stream lines from text file. This is a generator."""
		for line in full_text:
			yield clean_row(line)

	def append_to_output_file(self, run_instance, output_file):
		"""Appends single line to an output file"""
		output_file.write(run_instance.results)


class LibraryRun(object):
	"""Class that runs given library on given text string"""
	def __init__(self, text, library):
		self.text = text
		self.library = library

	def do_preprocessing(self):
		"""Preprocesses text to create needed data like tokens, 
		word count, word frequencies for returning results"""
		self.text_id = self.text[0]
		# get word position of each word in text
		word_pos = self.text[1].split() # [word1, word2,...]
		self.wordcount = len(word_pos) # total word count

		word_freq = get_word_freq(self.text[1]) # {word: count}

		tokens_list = tokenize(self.text[1]) # [[1-word tokens], [2-word tokens],...]
		
		return (word_pos, word_freq, tokens_list)

	def get_results(self):
		# lib = {phrase: (score, rule_num)}

		_, word_freq, tokens_list = self.do_preprocessing()
		

		matches_list = []
		for phrase in library:
			for (token, token_pos) in tokens_list:	
				matches_list.append((re.search('^(' + phrase + ')$', token).string, token_pos))








