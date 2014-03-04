Include Finder finds include relationships for C/C++ source files. Running it on a file will print what files are included by that file, and what files are included by those files, and so on. It runs on Python2.7 with no extra dependencies required. Take a C++ source file and a C++ header file as an example:

```C++
// file.h
#include <set>
#include "otherstuff.h"

/* ... */
```

```C++
// file.cpp
#include "file.h"
#include <vector>

/* ... */
```

By default you'll see what headers the specified file is including recursively.

```Shell
$ include_finder.py file.h
otherstuff.h
set

$ include_finder.py file.cpp
file.h
otherstuff.h
set
vector
```

You can also go the other way and see what files the specified file is being included by recursively

```Shell
$ include_finder.py -r file.h
file.cpp

$ include_finder.py -r set
file.cpp
file.h
```

You can pass a --norecurse option to only see files directly included by a file (or directly including a file)

```Shell
$ include_finder.py -n file.h
otherstuff.h
set

$ include_finder.py -n file.cpp
file.h
vector

$ include_finder.py -rn file.h
file.cpp
```

If you want to see the shortest path from the specified file to a given include file

```Shell
$ include_finder.py file.cpp -i set
file.cpp
file.h
set

$ include_finder.py -r otherstuff.h -i file.cpp
otherstuff.h
file.h
file.cpp
```

Finally if you want to get the raw include info, you can use the --json option. You don't need to supply a file for this option.

```Shell
$ include_finder.py --json
{
    "file.cpp": [
        "file.h",
        "vector"
    ],
    "file.h": [
        "otherstuff.h",
        "set"
    ],
    "otherstuff.h": [],
    "set": [],
    "vector": []
}
```

