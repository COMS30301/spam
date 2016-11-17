#!/usr/bin/env python
import os
import subprocess
import sys

root = "./emails"
emails = []
for d in os.listdir(root):
    if ("spam" in d or "ham" in d) and os.path.isfile(os.path.join(root,d)):
        emails.append(os.path.join(root,d))
    else:
        print "The test filename must either contain word *spam* or *ham* indicating its class!"
        print "The filter won't be tested on `%s` file." % os.path.join(root,d)

LANGUAGE = ""

if os.path.isfile("./filter.java"):
    LANGUAGE = "java"
    print "`filter.java` found!"
elif os.path.isfile("./filter.py"):
    LANGUAGE = "python"
    print "`filter.py` found!"
else:
    sys.exit("Neither `filter.java` nor `filter.py` was found in current directory!")

if LANGUAGE == "java":
    # Find all *.java* files
    java_files = [d for d in os.listdir("./") if d.endswith(".java")]
    java_files = " ".join(java_files)

    java_compile = "javac %s" % java_files
    comp = subprocess.Popen(java_compile.split(), stdout=subprocess.PIPE)
    comp.communicate()

    execute = "java filter %s"
elif LANGUAGE == "python":
    execute = "python filter.py %s"

tp, tn, fp, fn = 0, 0, 0, 0
for i in emails:
    current_email = execute % i
    if "spam" in i:
        ground_truth = "spam"
    elif "ham" in i:
        ground_truth = "ham"
    else:
        sys.exit("File %s has neither *ham* nor *spam* keyword in its name!" % i)

    exe = subprocess.Popen(current_email.split(), stdout=subprocess.PIPE)
    output, error = exe.communicate()

    output = output.strip()
    if output == "spam" and ground_truth == "spam":
        print "%s correctly predicted as SPAM" % i
        tp += 1
    elif output == "spam" and ground_truth == "ham":
        print "%s incorrectly predicted as SPAM" % i
        fp += 1
    elif output == "ham" and ground_truth == "ham":
        print "%s correctly predicted as HAM" % i
        tn += 1
    elif output == "ham" and ground_truth == "spam":
        print "%s incorrectly predicted as HAM" % i
        fn += 1
    else:
        print "Currently tested email is: %s" % i
        print "The output of your program should be either *spam* or *ham*."
        sys.exit("Current output:\n%s" % output)

# Print statistics
print "Contingency table:"
print """
Predicted:    | SPAM | HAM
----------------------------
Ground Truth: |      |
    SPAM      | %4d | %4d
    HAM       | %4d | %4d
""" % (tp, fn, fp, tn)
acc = 100.0*(tp+tn)/(fp+fn+tp+tn)
print "Accuracy: %.2f" % (acc) + "%"
