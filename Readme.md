# Spam assignment automarker #
To test your code before submission you can use this automarker.  
If your code doesn't work with this automarker we won't be able to test it, what will result in 0 marks!

## Testing your code ##
Please copy your filter.java or filter.py into this directory and run:
```
python marker.py
```

Please do not copy any emails that you use for training. As per coursework brief:

"*Since you do not specify the directory with the training files, the program needs to store its knowledge gained during training somewhere, e.g. in a separate file (which you can submit together with your code).*"

You can put emails that you want to test your code on in `emails` directory.

## External dependencies ##
### Java ###
If your program requires external libraries in `.jar` format please put them in `./lib/` directory.

### Python ###
If you use a Python package that is not available at MVB 2.11 machine, you can install it with:
```
pip install --user *package_name*
```

In this case please include with your submission `requirements.txt` file created with:
```
pip freeze --user > requirements.txt
```

## Submission ##
Please submit a single `zip` file with your code and report (in `pdf` format). To create a `zip` file for submission:
```
python marker.py /Users/xyz/my_filter
```

where `/Users/xyz/my_filter` is a folder with your code (`filter.{py,java}` and the report).

## Testing your submission ##
To test your submission you can execute the following line:
```
python marker.pu path/to/submission.zip
```

where `path/to/submission.zip` is path to `submission.zip` file created with this script.
