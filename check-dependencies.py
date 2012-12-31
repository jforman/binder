#!/usr/bin/env python
"""Script to verify required/optional dependencies are installed."""

import sys
errors = 0

try:
    import BeautifulSoup
except ImportError:
    print "Could not import BeautifulSoup. This is a required module for Binder.\n"
    errors += 1

try:
    import django
except ImportError:
    print "Could not import Django. This is a required package for Binder.\n"
    errors += 1

try:
    import dns
except ImportError:
    print "Could not import dns. This is a required module for Binder."
    print "Package is typically called 'python-dnspython.'\n"
    errors += 1

try:
    import flup
except ImportError:
    print "Could not import flup. This is an optional module if you intend to run Binder under fastcgi."
    print "Package is typically called 'python-flup.'\n"

if errors:
    print "Critical missing packages found: %d.\n" % errors
    sys.exit(errors)
else:
    print "All required packages found!"
