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
		with open(self.output_directory+self.output_filename, "a") as out:
			with open(text_filepath, "r") as full_text:
				texts = stream_lines(full_text)
				for text in texts:
					run_instance = LibraryRun(text, library)
					append_to_output_file(run_instance, out)
					#verbose_output(run_instance)

	def get_library_from_file(self, library_filepath):
		"""Load library from filepath"""
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
	"""Class that runs library on given input text"""
	def __init__(self):
		pass

