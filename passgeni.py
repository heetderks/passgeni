#!/usr/bin/python

# PASSGENI -- generate pass-phrases
# -by- Thoams Heetderks

import sqlite3, sys
from optparse import OptionParser

version = '0.2'
default_len_lower = 3   # default word length (lower bound)
default_len_upper = 5   # default word length (upper bound)
dbfile = 'passgeni-sqlite'

def main():
  usage = """
  %%prog INIT|ADD <filename>
      INITialize and/or ADD words to PASS-PHRASE database
  %%prog CHECK
      list summary of words in PASS-PHRASE database
  %%prog [options] <words> <length-lower> <length-upper>
      generate PASS-PHRASE of <words> words (word length)
      using words of length range <length-lower> to <length-upper>

  <filename> = file of words to be ADDED to the password database
  <words> = number of words to generate in pass-prase
  <length-lower> = length (lower bound) of words to use (Default=%s)
  <length-upper> = length (upper bound) of words to use (Default=%s)
  """%(default_len_lower,default_len_upper)

  parser = OptionParser(usage=usage, version="%prog ver "+version)
  parser.add_option("--UC", "--uc", dest="ucase", action="store_true", default=False, 
                    help="generate pass-prase all uppercase")
  parser.add_option("--LC", "--lc", dest="ucase", action="store_false", 
                    help="generate pass-prase all lowercase (Default)")
  parser.add_option("--delim", "-d", dest="delim", action="store", type="string", 
                    metavar="DELIMETER", default=" ", 
                    help="pass-prase word delimeter char (Default is <space>)")
  (options,args) = parser.parse_args()

  if not args: return parser.print_help()
  conn = sqlite3.connect(dbfile)
  cursor = conn.cursor()
  if args[0]=='CHECK':
    ###PRINT DB SUMMARY
    print 'PASS-PHRASE WORDS SUMMARY:'
    wordsum = 0
    result = cursor.execute('SELECT wsize,count(word) FROM words GROUP BY wsize')
    for line in result.fetchall():
      print "%s letter words = %s "%(line[0],line[1])
      wordsum += int(line[1])
    print "\n   TOTAL WORDS = %s \n"%wordsum
    cursor.close()
    return

  if len(args)>1 and args[0] in ['INIT','ADD']:
    ###INIT/ADD
    filename = args[1]
    added = 0
  
    try: wfile = open(filename)
    except: 
      return 'ERROR: could not open file (%s)'%filename+'\n\n'

    if args[0]=='INIT':
      try: cursor.execute('DROP TABLE words')
      except: pass
      cursor.execute('CREATE TABLE words (word VARCHAR NOT NULL UNIQUE, wsize INT)')
      conn.commit()

    for word in wfile:
      word = word.strip().lower()
      if not word: continue
      try: cursor.execute('INSERT INTO words (word,wsize) VALUES (?,?)', (word,len(word)))
      except: continue
      added += 1
      print word
      conn.commit()
  
    cursor.close()
    wfile.close()
    return '\n%s words added to PASS-PHRASE database.'%added+'\n\n'

  if args and sum([ x.isdigit() for x in args[0:3]]):
    ###GENERATE (>=2 NUMERIC ARGS)
    generate = []
    nwords = int(args[0])
    szlow = default_len_lower
    szhigh = default_len_upper
    if len(args)>1: szlow = szhigh = args[1]
    if len(args)>2: szhigh = args[2]
 
    for idx in range(nwords):
      result = cursor.execute('SELECT word FROM words WHERE wsize>=? AND wsize<=? ORDER BY RANDOM() LIMIT 1', (szlow,szhigh))
      word = result.fetchall()
      if not word: return 'NO WORDS AVAILABLE!\n'
      word = word[0][0]
      if options.ucase: word = word.upper()
      generate.append(word)
  
    cursor.close()
    return '\n'+options.delim[0].join(generate)+'\n'

if __name__ == "__main__":
  sys.exit(main())
