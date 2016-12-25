import os
import sys
from numpy.random import choice
from shutil import copyfile

if len(sys.argv) != 3:
    errmsg = "This program takes two arguments:\n" + \
        "  > folder with emails; and\n" + \
        "  > number of emails per class (ham:spam); e.g.\n" + \
        "python data_splitter.py emails 50:10"
    sys.exit(errmsg)

def mkdir(d):
    if not os.path.exists(d):
        os.makedirs(d)

SPLIT = sys.argv[1]
ROOT = os.path.split(os.path.abspath(SPLIT))[0]
LOG_FILE = os.path.join(ROOT, "log.txt")
SELECTED = os.path.join(ROOT, "selected")
REMAINING = os.path.join(ROOT, "remaining")
mkdir(SELECTED)
mkdir(REMAINING)

HAM_N, SPAM_N = [int(i) for i in sys.argv[2].split(":")]

log = []
ham, spam = [], []
for d in os.listdir(SPLIT):
    email = os.path.join(SPLIT,d)
    if os.path.isfile(email) and "ham" in d:
        ham.append(email)
    elif os.path.isfile(email) and "spam" in d:
        spam.append(email)
    else:
        print "ERROR! Unrecognised email: %s" % email

ham_train = choice(ham, size=HAM_N, replace=False)
spam_train = choice(spam, size=SPAM_N, replace=False)
for i, fname in enumerate(ham_train):
    d = os.path.join(SELECTED,"ham%.3d.txt"%i)
    copyfile(fname, d)
    log.append("%s -> %s" % (fname, d))
for i, fname in enumerate(spam_train):
    d = os.path.join(SELECTED,"spam%.3d.txt"%i)
    copyfile(fname, d)
    log.append("%s -> %s" % (fname, d))

for i in ham_train:
    ham.remove(i)
for i in spam_train:
    spam.remove(i)

for i, fname in enumerate(ham):
    d = os.path.join(REMAINING,"ham%.3d.txt"%i)
    copyfile(fname, d)
    log.append("%s -> %s" % (fname, d))
for i, fname in enumerate(spam):
    d = os.path.join(REMAINING,"spam%.3d.txt"%i)
    copyfile(fname, d)
    log.append("%s -> %s" % (fname, d))

with open(LOG_FILE, "w") as log_file:
    log_file.write("\n".join(ham_train) + "\n\n" + 40*"~+" + "\n\n" + \
                   "\n".join(spam_train) + "\n\n" + 2*(40*"~+"+"\n") + "\n" + \
                   "\n".join(log) + "\n")
