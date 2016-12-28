#!/usr/bin/env python
import os
import pip
import subprocess
import sys
import time
import zipfile

package_content = ["marker.py", "Readme.md", "submission.zip", \
                   "test_filter.java", "test_filter.py", \
                   "emails", ".git"]

marking_criteria = """\
Part 1 (40%):
- [ ] Your program classifies the testing set with an accuracy significantly higher than random within 30 minutes
- [ ] Use very simple data preprocessing so that the emails can be read into the Naive Bayes (remove everything else other than words from emails)
- [ ] Write simple Naive Bayes multinomial classifier or use an implementation from a library of your choice
- [ ] Classify the data
- [ ] Report your results with a metric (e.g. accuracy) and method (e.g. cross validation) of your choice
- [ ] Choose a baseline and compare your classifier against it
Part 2 (30%):
- [ ] Use some smart feature processing techniques to improve the classification results
- [ ] Compare the classification results with and without these techniques
- [ ] Analyse how the classification results depend on the parameters (if available) of chosen techniques
- [ ] Compare (statistically) your results against any other algorithm of your choice (use can use any library); compare and contrast results, ensure fair comparison
Part 3 (30%):
- [ ] Calibration (15%): calibrate Naive Bayes probabilities, such that they result in low mean squared error
- [ ] Naive Bayes extension (15%): modify the algorithm in some interesting way (e.g. weighted Naive Bayes)

~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*
Classification evaluation:
"""

feedback_file = "feedback.txt"
archive_name = "submission.zip"
path_prefix = "./"
emails_path_prefix = "./"
emails_dir = ["emails"]
emails_dir = [os.path.join(emails_path_prefix, i) for i in emails_dir]

# If this flag is set to `True` Python packages are installed globally.
# Additionally, if directory is used as a parameter it will get tested,
# rather than being compressed for submission.
VIRTUAL_ENV = False

# Show progress in email testing
show_progress = True
try:
    from nyanbar import NyanBar
    progress_bar = "nyan"
except ImportError:
    progress_bar = "classic"

# Install requirements
install_requirements = False

def python_requirements(path):
    # Install requirements if Python
    if not install_requirements:
        return
    requirements = os.path.join(path, "requirements.txt")
    if os.path.isfile(requirements):
        pip_options = ["install"]
        if VIRTUAL_ENV:
            print "Installing Python requirements globally (hopefully VirtualEnv)"
        else:
            print "Installing Python requirements locally (--user)"
            pip_options += ["--user"]
        with open(requirements) as r:
            for l in r:
                pip.main(pip_options + [l])
    else:
        sys.exit("Unknown Python requirements file: " + requirements)

# Detect zip submission
if len(sys.argv) == 2:
    arg = sys.argv[1].strip()
    # Unpack zip for marking
    if os.path.isfile(arg):
        # Unpack zip for marking
        print "Unpacking archive"
        if arg.endswith(".zip"):
            if os.path.basename(arg) != archive_name:
                sys.exit("Archive must be named: " + archive_name)
            else:
                path_prefix = os.path.join(os.path.dirname(arg), os.path.splitext(archive_name)[0])
                with zipfile.ZipFile(arg, "r") as z:
                    z.extractall(path_prefix)
        # Install requirements if Python
        python_requirements(path_prefix)
    # Directory passed as an argument
    elif os.path.isdir(arg):
        if VIRTUAL_ENV:
            # Test submission (directory rather than zip)
            print "VIRTUAL_ENV=True; testing directory."
            path_prefix = arg
            # Install requirements if Python
            python_requirements(path_prefix)
        else:
            # Create zip for submission
            print "Creating zip for submission..."
            arg_files = os.listdir(arg)
            if "filter.java" not in arg_files and "filter.py" not in arg_files:
                sys.exit("Filter.{py,java} missing in indicated folder:\n    " + arg)
            arg_files = [os.path.join(arg, i) for i in arg_files if i not in package_content]
            with zipfile.ZipFile(archive_name, "w", zipfile.ZIP_DEFLATED) as z:
                while arg_files:
                    f = arg_files.pop()
                    if os.path.isfile(f):
                        z.write(f, os.path.relpath(f, arg))
                    elif os.path.isdir(f):
                        arg_files += [os.path.join(f, i) for i in os.listdir(f)]
            print "Please upload: %s" % archive_name
            sys.exit()

# Detect language
print "Testing on sample emails"
LANGUAGE = ""
if os.path.isfile(os.path.join(path_prefix, "filter.java")):
    LANGUAGE = "java"
    print "`filter.java` found!"
elif os.path.isfile(os.path.join(path_prefix, "filter.py")):
    LANGUAGE = "python"
    print "`filter.py` found!"
else:
    sys.exit("Neither `filter.java` nor `filter.py` was found in current directory!")

if LANGUAGE == "java":
    # Find all *.java* files
    java_files = [os.path.join(path_prefix, d) for d in os.listdir(path_prefix) if d.endswith(".java")]
    java_files = " ".join(java_files)

    java_compile = "javac %s" % java_files
    comp = subprocess.Popen(java_compile.split(), stdout=subprocess.PIPE)
    comp.communicate()

    classpath= ":".join([path_prefix,
                         os.path.join(path_prefix, "lib"),
                         "$CLASSPATH"])
    execute = "java -cp " + classpath + " filter %s"
elif LANGUAGE == "python":
    execute = "python " + os.path.join(path_prefix, "filter.py") + " %s"

evaluation_results = []
for ei, e in enumerate(emails_dir):
    evaluation = ""
    emails = []
    for d in os.listdir(e):
        if ("spam" in d or "ham" in d) and os.path.isfile(os.path.join(e,d)):
            emails.append(os.path.join(e,d))
        else:
            print "The test filename must either contain word *spam* or *ham* indicating its class!"
            print "The filter won't be tested on `%s` file." % os.path.join(e,d)

    if show_progress and progress_bar == "nyan":
        print "Test [%d/%d]" % (ei+1, len(emails_dir))
        progress = NyanBar(tasks=100)
    tp, tn, fp, fn = 0, 0, 0, 0
    evaluation_start_time = time.time()
    for ii, i in enumerate(emails):
        if show_progress and progress_bar == "classic":
            print "[%d/%d] %.2d%% (%s)" % (ei+1, len(emails_dir), 100.*ii/len(emails), i)
        elif show_progress and progress_bar == "nyan":
            progress.update(100.*ii/len(emails))
        current_email = execute % i
        if "spam" in i:
            ground_truth = "spam"
        elif "ham" in i:
            ground_truth = "ham"
        else:
            sys.exit("File %s has neither *ham* nor *spam* keyword in its name!" % i)

        exe = subprocess.Popen(current_email.split(), cwd=path_prefix, stdout=subprocess.PIPE)
        output, error = exe.communicate()

        output = output.strip()
        if output == "spam" and ground_truth == "spam":
            if not VIRTUAL_ENV: print "%s correctly predicted as SPAM" % i
            tp += 1
        elif output == "spam" and ground_truth == "ham":
            if not VIRTUAL_ENV: print "%s incorrectly predicted as SPAM" % i
            fp += 1
        elif output == "ham" and ground_truth == "ham":
            if not VIRTUAL_ENV: print "%s correctly predicted as HAM" % i
            tn += 1
        elif output == "ham" and ground_truth == "spam":
            if not VIRTUAL_ENV: print "%s incorrectly predicted as HAM" % i
            fn += 1
        else:
            print "Currently tested email is: %s" % i
            print "The output of your program should be either *spam* or *ham*."
            sys.exit("Current output:\n%s" % output)
    if show_progress and progress_bar == "classic":
        print "[%d/%d] %.2d%% (%s)" % (ei+1, len(emails_dir), 100, "")
    elif show_progress and progress_bar == "nyan":
        progress.finish()

    # Print statistics
    evaluation += "Test %s" % e
    evaluation += """
    Predicted:    | SPAM | HAM
    ----------------------------
    Ground Truth: |      |
        SPAM      | %4d | %4d
        HAM       | %4d | %4d
    """ % (tp, fn, fp, tn)
    acc = 100.0*(tp+tn)/(fp+fn+tp+tn)
    evaluation += "Accuracy: %.2f" % (acc) + "%"

    evaluation_end_time = time.time()
    evaluation_time = evaluation_end_time - evaluation_start_time
    evaluation += "\nEvaluation time: %s seconds" % evaluation_time
    if evaluation_time > 1800:
        evaluation += "\nFAILED time test"

    print "\n", evaluation
    evaluation_results.append(evaluation)

# Save feedback
if VIRTUAL_ENV:
    with open(os.path.join(path_prefix, feedback_file), "w") as ff:
        ff.write(marking_criteria)
        ff.write("\n\n++++++++++++++++++++++++++++++\n\n".join(evaluation_results))
