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
	"""Gets word freq for each word in a text string, outputs {word: count}"""
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

	output: generator objects of tokens, one for each token length
	desired
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

def get_library_from_file(library_filepath):
	"""Load library from filepath

	input = filepath of library file, where col 1 = phrase, 
	col 2 = score

	output = dictionary of library phrases to tuple of 
	(phrase score, rule index) for each phrase """
	with open(library_filepath, "r") as lib_file:
		library = {}
		for index, line in enumerate(lib_file):
			phrase, score = line.split('\t')
			library[phrase] = (int(score), index)
	return library

def get_opposite_meaning(phrase):
	"""Adds/removes negation words to/from phrase to get opposite meaning"""
	negation_words = '(not|dont|cant|wont|couldnt|shouldnt|never) (\w+ ){0,2} ?'
	if negation_words in phrase:
		phrase = phrase.replace(negation_words, "")
	else:
		phrase = negation_words + phrase
	return phrase

def create_negation_lib(library):
	"""Creates negation library from given library by adding 
	negation words to each phrase and reversing the score"""
	negation_lib = {}
	for phrase, (score, rule_num) in library.iteritems():
		negation_lib[get_opposite_meaning(phrase)] = (-score, rule_num)
	return negation_lib


class SentimentFactory(object):
	"""Factory class for creating instances of library runs"""
	def __init__(self, text_filepath, library_filepath, output_directory="", 
		        output_filename="sentiment_summary.txt"):
		self.text_filepath = text_filepath
		self.library_filepath = library_filepath
		self.output_directory = output_directory
		self.output_filename = output_filename

	def run_suite(self):
		"""Starts library runs for each essay

		Loads library files and texts, then iteratively appends to output file
		a line containing results of running library on each text. Texts are 
		streamed into Python and written to the output file one at a time

		"""
		library = get_library_from_file(self.library_filepath)
		negation_library = create_negation_lib(library)
		with open(self.output_directory+self.output_filename, "a") as out:
			with open(text_filepath, "r") as full_text:
				texts = self.stream_lines(full_text)
				for text in texts:
					run_instance = LibraryRun(text, library, negation_library)
					run_instance.do_run()
					results = run_instance.get_results()
					for line in results:
						self.append_to_output_file(line, out)
					#verbose_output(run_instance)

	def stream_lines(self, full_text):
		"""Stream lines from text file. This is a generator."""
		for line in full_text:
			yield clean_row(line)

	def append_to_output_file(self, line, output_file):
		"""Appends single line to an output file"""
		output_file.write(line)


class LibraryRun(object):
	"""Class that runs given library on given text

	text = (text_id, [single words in order of text])
	library = {library phrase: (phrase score, rule number)

	initializes with do_preprocessing()}
	"""
	def __init__(self, text, library, end_weight=1.5, end_threshold=0.75):
		self.text = text
		self.library = library
		self.word_freq, self.tokens_generator = self.do_preprocessing()
		self.end_weight = end_weight
		self.end_threshold = end_threshold

	def do_preprocessing(self):
		"""Preprocesses text to create needed data: text id, word count,
		and tokens generator for returning results"""
		self.text_id = self.text[0]

		# get word position of each word in text
		word_pos = self.text[1].split() # [word1, word2,...]
		self.wordcount = len(word_pos) # total word count

		word_freq = get_word_freq(self.text[1]) # {word: count}

		tokens_generator = tokenize(self.text[1]) # [(token, token_pos)]
		
		return word_freq, tokens_generator

	def find_phrase_matches(self, tokens_generator):
		"""Finds phrase matches between negation library and text, and 
		normal library and text, and returns matches

		tokens_generator = generator listing (token, token_pos) for text

		output = dict of phrase to list of tuples for each phrase hit 
		(token position, phrase score, rule number) """
		# lib = {phrase: (score, rule_num)}

		matches = collections.defaultdict(list)
		for phrase, (score, rule_num) in self.library.iteritems():
			found_neg_phrase = False
			for token, token_pos in tokens_generator:
				neg_phrase_search = re.search(
					'^(' + get_opposite_meaning(phrase) + ')$', token)
				if neg_phrase_search is not None:
					found_neg_phrase = True
					matches[token].append(
						(token_pos, -score, rule_num))
			if found_neg_phrase == False:
				for token, token_pos in tokens_generator:
					phrase_search = re.search('^(' + phrase + ')$', token)
					if phrase_search is not None:
						matches[token].append(
							(token_pos, score, rule_num))

		return matches

	def score_text(self, matches, end_weight=1.5, end_threshold=0.75):
		"""Scores text by averaging phrase-match scores. Optionally, 
		phrases at the end of the text are weighted (by default,
		phrases in last 25% weighted 1.5x)
	    
	    matches = {phrase: list of tuples for each phrase hit 
	    (token pos, phrase score, rule num)}

	    output = score for entire text
		"""
		# weight phrases at end of text
		all_scores = []
		for token in matches:
			for hit in matches[token]:
				if float(hit[0]) / float(self.wordcount) >= end_threshold:
					all_scores.append(hit[1] * end_weight)
				else:
					all_scores.append(hit[1])

		# calc score for whole text
		text_score = sum(all_scores) / len(all_scores)

		return text_score

	def do_run(self):
		"""Runs find_phrase_matches() and text_score() to create data
		that will be used by get_results() in creating results output"""
		self.matches = self.find_phrase_matches(self.tokens_generator)
		self.text_score = self.score_text(self.matches, 
			self.end_weight, self.end_threshold)

	def get_results(self):
		"""Creates results output from data gotten from running
		library on the text

		Each item in results list = data for one line
		"""
		results = []
		for token in self.matches:
			for hit in matches[token]:
				pass

	def format_results(self):
		"""Formats results into text strings geared for writing to file"""
		pass
