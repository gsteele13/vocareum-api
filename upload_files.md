---
jupyter:
  jupytext:
    formats: ipynb,md
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.13.6
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

```python
import sys
from vocareum_course import Vocareum_course
import glob
```

```python
# update should be either 1 or 0
def deploy_part(key, update=1):
    notebook_file = glob.glob(folder[key] + "/*.ipynb")[0]
    course.release_notebook(notebook_file, key[0], key[1], update=update)
    asnlib_folder = folder[key] + "/resource/asnlib"
    course.update_asnlib(asnlib_folder, key[0], key[1], update=update)
```

# First, initialize the object and fetch the latest assignment lists

For now, I will make the mappings here by hand from our folders to the assignment "parts" in the course.

First, create the course object and fetch the assignment list. 

(The output is shown for our course, but, of course, this will not work if you run the cell since you don't have our course id, and also not our token either...)

```python
token = "your token generated from vocareum user settings here (don't store it in a public repo!)"
course_id = your_course_id 
course = Vocareum_course(token, course_id)
course.fetch_assignments()
course.print_assignments()
```

# Make a mapping of folders to assignment / part indices

This will be a bit of patchwork, but not too bad. (I hid the cell to keep it tidy, you won't see it if you have the "Hide Input" Nbextension enabled).

This is based on how we organise our repo

```python hide_input=true
l1 = sorted(glob.glob("00 Review Intro to Python Course/*"))
l2 = sorted(glob.glob("*/"))

#i=0
#for l in l1:
#    print(i, l)
#    i+=1

#i=0
#for l in l2:
#    print(i, l)
#    i+=1

folder = {}
for i in range(5):
    folder[0,i] = l1[i]
folder[0,5] = l2[1]
folder[0,6] = l2[2]

folder[1,0] = l2[3]
folder[1,1] = l2[4]

folder[2,0] = l2[15] # vocareum lists in created order, not displayed order...

folder[3,0] = l2[5]
folder[3,1] = l2[6]

folder[4,0] = l2[7]
folder[4,1] = l2[8]

folder[5,0] = l2[9]
folder[5,1] = l2[10]

folder[6,0] = l2[16]

folder[7,0] = l2[11]
folder[7,1] = l2[12]

folder[8,0] = l2[13]
folder[8,1] = l2[14]

folder[9,0] = l2[17]
```

```python
for k in folder.keys():
    print(k, folder[k])
```

# Deploy a specific notebook

```python
deploy_part((8,0))
```

# Deploy all notebooks

This assumes that there is only one ipynb per folder, which should (now) be the case.

```python
for key in list(folder.keys())[0:-1]:
    deploy_notebook(key)
```
