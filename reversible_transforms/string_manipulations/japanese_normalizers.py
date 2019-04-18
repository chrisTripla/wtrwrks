import nltk
import reversible_transforms.string_manipulations.diff as df
import unicodedata
import reversible_transforms.string_manipulations.ja_stopwords as jas
import tinysegmenter

tokenizer = tinysegmenter.TinySegmenter()


def default_normalizer(string_or_dict, half_width=False, remove_stopwords=False, inverse=False):
  """Tokenize, lemmatize, maybe strip out stop words, maybe lemmatize a Japanese string in a consistent manner.

  Parameters
  ----------
  string : str
    The string to be tokenized and normalized

  Returns
  -------
  list of strs
    The tokenized and normalized strings

  """
  if not inverse:
    string = string_or_dict
    r_tokens = []

    # If half_width then convert all full width characters to half width
    if half_width:
      string = unicodedata.normalize('NFKC', unicode(string))

    # Split the string into individual words/punctuation. Iterate through.
    for token in tokenizer.tokenize(string):

      # If you're removing stop words and this is a stop word continue.
      if remove_stopwords and token in jas.stopwords:
        continue
      r_tokens.append(token)
    diff_string = df.get_diff_string(''.join(r_tokens), string)

    return {'tokens': r_tokens, 'diff_string': diff_string}
  else:
    string = ''.join(string_or_dict['tokens'])
    string = df.reconstruct(string, string_or_dict['diff_string'])

    return string
