import requests
import json
from zipfile import ZipFile
import base64
import glob
import os

class Assignment:
    def __init__(self, info):
        self.info = info
        self.parts = []

class Vocareum_course:
    '''A class for handling requests to a vocareum course via the rest API'''
    
    def __init__(self, token, course_id, url='https://api.vocareum.com/api/v2/courses/'):
        self.token = token
        self.course_id = course_id
        self.assignment_list = []
        self.base_url = url + str(course_id) 
        self.auth_headers = {'Authorization': 'Token ' + token, 'Content-type': 'application/json'}
        self.debug_request = False
    
    def print_request(self, url, data_string):
        print("URL:\n" + url)
        print("Headers:\n" + json.dumps(self.auth_headers))
        print("Data:\n" + data_string)

    def GET(self, url_add, data):
        url = self.base_url + url_add
        data_string = json.dumps(data, indent = 4)
        print(".", end="")
        if self.debug_request:
            print("HTTP GET\n")
            self.print_request(url, data_string)
        r = requests.get(url, headers=self.auth_headers, data=data_string)
        return r.json()
    
    def PUT(self, url_add, data):
        url = self.base_url + url_add
        data_string = json.dumps(data, indent = 4)
        if self.debug_request:
            print("HTTP PUT\n")
            self.print_request(url, data_string)
        return requests.put(url, data = data_string, headers=self.auth_headers)
    
    def POST(self, url_add, data):
        url = self.base_url + url_add
        data_string = json.dumps(data, indent = 4)
        if self.debug_request:
            print("HTTP POST\n")
            self.print_request(url, data_string)
        return requests.post(url, data=data_string, headers=self.auth_headers)

    def zip_and_encode_files(self, file_list):
        with ZipFile("tmp.zip", "w") as zipfile:
            for filename in file_list:
                zipfile.write(filename, os.path.basename(filename))
        with open("tmp.zip", "rb") as file:
            return base64.b64encode(file.read()).decode("utf-8")
    
    def zip_and_encode_folder(self, folder):
        files = glob.glob(folder + "/**", recursive=True)
        files = [f for f in files if os.path.isfile(f)]
        files_zip = [f[len(folder)+1:] for f in files]
        with ZipFile("tmp.zip", "w") as zipfile:
            for file, file_zip in zip(files, files_zip):
                zipfile.write(file, file_zip)
        with open("tmp.zip", "rb") as file:
            return base64.b64encode(file.read()).decode("utf-8")
    
    def print_response(self, r):
        print(r)
        if "error" in r.json():
            print("\x1b[31m" + str(r.json()) + "\x1b[0m")        
        
    def add_rubric(self, rubric, assignment_index, part_index):
        '''Accepts a list of rubric dictionaries with keys "text" and "points"'''
        voc_rubric_list = []
        print("Adding:\n")
        for r in rubric:
            print(r['text'])
            voc_item = {}
            voc_item['name'] = r['text']
            voc_item['maxscore'] = r['points']
            voc_item['exclude'] = 0
            voc_item['auto']= 0
            voc_rubric_list.append(voc_item)
        data = {}
        data['rubrics'] = voc_rubric_list
        assignment_id = self.assignment_list[assignment_index].info['id']
        part_id = self.assignment_list[assignment_index].parts[part_index]['id']
        url_add = f"/assignments/{assignment_id}/parts/{part_id}/rubrics"
        self.print_response(self.POST(url_add, data))
        
    def set_part_name(self, name, assignment_index, part_index):
        data = {}
        data['name'] = name
        assignment_id = self.assignment_list[assignment_index].info['id']
        part_id = self.assignment_list[assignment_index].parts[part_index]['id']
        url_add = f"/assignments/{assignment_id}/parts/{part_id}"
        print(self.PUT(url_add, data))
      
    def update_asnlib(self, asnlib_folder, assignment_index, part_index, update=1):
        assignment_id = self.assignment_list[assignment_index].info['id']
        part_id = self.assignment_list[assignment_index].parts[part_index]['id']
        assignment_name = self.assignment_list[assignment_index].info['name']
        part_name = self.assignment_list[assignment_index].parts[part_index]['name']
        print("Uploading asnlib files in '%s' to:\n%s\n    %s" % (asnlib_folder, assignment_name, part_name))
        
        data = {}
        data['update'] = update
        content_dict = {}
        content_dict['target'] = "asnlib"
        content_dict['zipcontent'] = self.zip_and_encode_folder(asnlib_folder)
        data['content'] = [content_dict]
        
        url_add = f"/assignments/{assignment_id}/parts/{part_id}"
        self.print_response(self.PUT(url_add, data))

    def release_notebook(self, notebook_file, assignment_index, part_index, update=1):
        data = {}
        data['type'] = 'jupyter'
        data['zipfile'] = self.zip_and_encode_files([notebook_file])
        data['update'] = update
        
        assignment_id = self.assignment_list[assignment_index].info['id']
        part_id = self.assignment_list[assignment_index].parts[part_index]['id']
        assignment_name = self.assignment_list[assignment_index].info['name']
        part_name = self.assignment_list[assignment_index].parts[part_index]['name']
        print("Uploading '%s' to:\n%s\n    %s" % (notebook_file, assignment_name, part_name))
        
        url_add = f"/assignments/{assignment_id}/parts/{part_id}/release"
        self.print_response(self.PUT(url_add, data))
 
    def GET_pages(self, url_add, data):
        # Ironically, pagination did not make life easier...
        responses = []
        #print("getting page", 0)
        r = self.GET(url_add, {})
        responses.append(r)
        num_pages = r['total_records']//10+1
        for i in range(1,num_pages):
            #print("getting page", i)
            data['page'] = i
            r = self.GET(url_add, data=data)
            responses.append(r)
        return responses
    
    def check_rubric(self, assignment_index, part_index):
        assignment_id = self.assignment_list[assignment_index].info['id']
        part_id = self.assignment_list[assignment_index].parts[part_index]['id']
        url_add = f"/assignments/{assignment_id}/parts/{part_id}/rubrics"
        # Vocareum bug: total_records is incorrect for rubrics! crap.
        # A nasty hack...
        pages = []
        i=0
        pages.append(self.GET(url_add, {"page": i}))
        while len(pages[-1]['rubrics']) > 0:
            i += 1
            pages.append(self.GET(url_add, {"page": i}))
        print("\r", end="")
        total_points = 0
        for p in pages:
            for r in p['rubrics']:
                print(f"({r['maxscore']})", r['name'])
                total_points += float(r['maxscore'])
        print("Total points:", total_points)
        
    def fetch_assignments(self):
        pages = self.GET_pages("/assignments", {})
        self.assignment_list = []
        for page in pages:
            for assignment_info in page['assignments']:
                self.assignment_list.append(Assignment(assignment_info))
        for A in self.assignment_list:
            A.parts = self.fetch_parts(A)
    
    def fetch_parts(self, assignment):
        url_add = "/assignments/" + assignment.info['id'] + "/parts"
        pages = self.GET_pages(url_add, {})
        parts_list = []
        for p in pages:
            parts_list += p['parts']
        return parts_list
        
    def print_assignments(self, parts=True):
        print()
        i=0
        for A in self.assignment_list:
            print(A.info['name'], "(i = %d, id %s)" % (i,A.info['id']))
            i+=1
            if parts:
                j=0
                for part in A.parts:
                    print("     " + part['name'],  "(j = %d, id %s)" % (j, part['id']))
                    j+=1
