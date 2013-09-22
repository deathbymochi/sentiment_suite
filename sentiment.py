"""A module for sentiment analysis"""

import re
import os

def clean_row(row):
	"""Cleans row from text file, outputs tuple (ID, cleaned_text)"""
	text_id, text = row.split('\t')
	text = text.lower()
	text = re.sub(r'[^\w\s]', '', text)
	return (text_id, text)

class SentimentFactory(object):
	"""Factory class for creating instances of library runs"""
	def __init__(self, text_filepath, library_filepath, output_directory=None, 
		        output_filename=None):
		self.text_filepath = text_filepath
		self.library_filepath = library_filepath
		self.output_directory = output_directory
		self.output_filename = output_filename

	def run_suite(self):
		"""Starts library runs for each essay"""
		library = get_library_from_file(self.library_filepath)

		texts = get_next_text_from_file(self.text_filepath)
		for text in texts:
			append_to_output_file(LibraryRun(essay, library))

	def get_library_from_file(self, library_filepath):
		"""Load library from filepath"""
		pass

	def get_next_text_from_file(self, text_filepath):
		"""Stream next line from text file"""
		with open(text_filepath, "r") as full_text:
			next_clean_line = clean_row(full_text.readline())
			pass




	def append_to_output_file(self, output_line, output_filepath):
		"""Appends single line to an output file"""
		pass



class LibraryRun(object):
	"""Class that runs library on given input text"""
	def __init__(self):
		pass

