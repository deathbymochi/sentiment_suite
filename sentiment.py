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

def get_opposite_meaning(phrase, num_words_btwn=2):
	"""Adds/removes negation words to/from phrase to get opposite meaning"""
	negation_words = (
		'(not|dont|cant|wont|couldnt|shouldnt|never) (\w+ ){0,' + str(
			num_words_btwn) + '} ?')
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

def find_max_wordlength(phrase_list):
	"""Finds the max number of words a phrase consists of, 
	in a given list of phrases"""
	max_words = 0

	for phrase in phrase_list:
		if len(phrase.split()) > max_words:
			max_words = len(phrase.split())
		
	return max_words

def format_lines_list(lines_list):
	"""Formats list into text strings geared for writing to file

	requires list of lists as input, where each embedded list 
	represents the data to be written to a single line of the
	output file
	"""
	formatted = []
	for line in lines_list:
		joined_line = '\t'.join(str(el) for el in line)
		joined_line = joined_line + '\n'
		formatted.append(joined_line)

	return formatted


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

		library_phrases = [line[0] for line in self.library]
		max_words = (
		find_max_wordlength(library_phrases) + 2) # for word allowances from negation

		tokens_generator = list(
		tokenize(word_pos, max_words=max_words)) # [(token, token_pos)]
		
		return word_freq, tokens_generator

	def find_phrase_matches(self, tokens_generator):
		"""Finds phrase matches between negation library and text, and 
		normal library and text, and returns matches

		tokens_generator = generator listing (token, token_pos) for text

		output = dict of phrase to list of tuples for each phrase hit 
		(token position, phrase score, rule number) """
		# lib = {phrase: (score, rule_num)}

		hitcount_pos = 0
		hitcount_neg = 0

		matches = collections.defaultdict(list)
		for phrase, (score, rule_num) in self.library.iteritems():
			found_neg_phrase = False
			for token, token_pos in tokens_generator:
				neg_phrase_search = re.search(
					'^(' + get_opposite_meaning(phrase) + ')$', token)
				if neg_phrase_search is not None:
					found_neg_phrase = True
					matches[token].append(
						[token_pos, -score, rule_num])
					hitcount_neg += 1
			if found_neg_phrase == False:
				for token, token_pos in tokens_generator:
					phrase_search = re.search('^(' + phrase + ')$', token)
					if phrase_search is not None:
						matches[token].append(
							[token_pos, score, rule_num])
						hitcount_pos += 1

		return matches, hitcount_pos, hitcount_neg

	def score_text(self, matches, end_weight=1.5, end_threshold=0.75):
		"""Scores text by averaging phrase-match scores. Optionally, 
		phrases at the end of the text are weighted (by default,
		phrases in last 25% weighted 1.5x)
	    
	    matches = {phrase: list of tuples for each phrase hit 
	    (token pos, phrase score, rule num)}

	    output = score for entire text
		"""
		# create matches dict where we will
		# add weighted scores instead of unweighted scores
		matches_weighted = matches.copy()

		# weight phrases at end of text, put all scores into all_scores
		# to easily sum over for score of whole text, and
		# add weighted score to matches_weighted
		all_scores = []
		for token in matches_weighted:
			for hit in matches_weighted[token]:
				if float(hit[0]) / float(self.wordcount) >= end_threshold:
					all_scores.append(hit[1] * end_weight)
					hit[1] = hit[1] * end_weight
				else:
					all_scores.append(hit[1])

		# calc score for whole text, using weighted scores
		text_score = sum(all_scores) / len(all_scores)

		return text_score, matches_weighted

	def do_run(self):
		"""Runs find_phrase_matches() and text_score() to create data
		that will be used by get_results() in creating results output

		Creates: matches_unweighted, which is data for each phrase hit
		using unweighted scores; matches_weighted, which is data for 
		each phrase hit using weighted scores; test_score, which is the
		text's overall score
		"""
		self.matches_unweighted, hitcount_pos, hitcount_neg = (
		self.find_phrase_matches(self.tokens_generator))

		self.hitcount = {'pos': hitcount_pos, 'neg': hitcount_neg, 
		'total': hitcount_pos + hitcount_neg}

		self.text_score, self.matches_weighted = self.score_text(self.matches_unweighted, 
			self.end_weight, self.end_threshold)		 

	def make_results_verbose(self):
		"""Creates results output from data gotten from running
		library on the text

		Each item in results list = data for one line
		"""
		# add each phrase hit's data to a separate element of results list
		results = []
		for token in self.matches_weighted:
			for hit in self.matches_weighted[token]:
				results.append([self.text_id, token, hit[0], hit[1], hit[2]])

		self.results_verbose = sorted(results)

	def make_results_simple(self):
		"""Creates simple summary results for whole text"""
		results = {'.text id': self.text_id, '.text score': self.text_score, 
		'total wordcount': self.wordcount, 
		'total hits': self.hitcount['total'],
		'pos hits': self.hitcount['pos'], 'neg hits': self.hitcount['neg']}

		self.results_simple = results

	def get_results(self, simple=True):
		"""Gets results from LibraryRun for writing to file.
		If simple=True, then just returns a single line 
		showing summary stats for whole text: text_score, 
		word count, number of hits (total, pos, neg)

		If simple=False, then verbose output which is data for each
		individual phrase hit (phrase, word pos, weighted 
		phrase score, rule number) is returned

	    get_results() uses format_results() to put results in 
	    the write format for writing to file
		"""
		#import pdb; pdb.set_trace()
		if simple is True:
			self.make_results_simple()

			# get simple results into list of lists format, where
			# each embedded list represents one line of output - this
			# is so format_results() can format correctly
			results = []
			header = []

			sorted_results = sorted(list(self.results_simple.iteritems()))
			for item in sorted_results:
				results.append(item[1])
				header.append(item[0])
			results = [results]
			header = [header]
		else:
			self.make_results_verbose()
			results = self.results_verbose
			header = [['text id', 'phrase', 'word pos', 
			'weighted score', 'rule num']]

		results_formatted = format_lines_list(results)
		header_formatted = format_lines_list(header)
		
		complete_formatted = list(header_formatted)
		complete_formatted.extend(results_formatted)

		return complete_formatted



		
