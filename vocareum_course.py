import requests
import json
from zipfile import ZipFile
import base64
import shutil
        
class Assignment:
    def __init__(self, info):
        self.info = info
        self.parts = []
        
class Vocareum_course:
    '''A class for handling requests to a vocareum course via the rest API'''
    
    def __init__(self, token, course_id):
        self.token = token
        self.course_id = course_id
        self.assignment_list = []
        self.base_url = 'https://api.vocareum.com/api/v2/courses/' + str(course_id) 
        self.auth_headers = {'Authorization': 'Token ' + token}

    def GET(self, url_add, data):
        url = self.base_url + url_add
        data_string = json.dumps(data, indent = 4)
        print(".", end="")
        r = requests.get(url, headers=self.auth_headers, data=data_string)
        return r.json()
    
    def PUT(self, url_add, data):
        url = self.base_url + url_add
        data_string = json.dumps(data, indent = 4)
        print("URL:")
        print(url)
        print("Data:")
        print(data_string)
        r = requests.put(url, data = data_str, headers=self.auth_headers)
        print(r.json())

    def zip_and_encode_files(self, file_list):
        with ZipFile("tmp.zip", "w") as zip:
            for filename in file_list:
                zip.write(filename)
        with open("tmp.zip", "rb") as file:
            return base64.b64encode(file.read()).decode("utf-8")
    
    def zip_and_encode_folder(self, folder):
        shutil.make_archive("tmp", 'zip', "resource/asnlib/")
        with open("tmp.zip", "rb") as file:
            return base64.b64encode(file.read()).decode("utf-8")
        
    def update_asnlib(self, asnlib_folder, assignment_index, part_index):
        data = {}
        content_dict = {}
        content_dict['target'] = "asnlib"
        content_dict['zipcontent'] = self.zip_and_encode_folder(asnlib_folder)
        data['content'] = [content_dict] 
        
        assignment_id = self.assignment_list[assignment_index].info['id']
        part_id = self.assignment_list[assignment_index].parts[part_index]['id']
        assignment_name = self.assignment_list[assignment_index].info['name']
        part_name = self.assignment_list[assignment_index].parts[part_index]['name']
        print("Uploading asnlib files in %s to:\n%s\n    %s" % (asnlib_folder, assignment_name, part_name))
        
        url_add = f"/assignments/{assignment_id}/parts/{part_id}"
        print(url_add)
        self.PUT(url_add, data)

    def release_notebook(self, notebook_file, assignment_index, part_index):
        data = {}
        data['type'] = 'jupyter'
        data['zipfile'] = self.zip_and_encode_files([notebook_file])
        
        assignment_id = self.assignment_list[assignment_index].info['id']
        part_id = self.assignment_list[assignment_index].parts[part_index]['id']
        assignment_name = self.assignment_list[assignment_index].info['name']
        part_name = self.assignment_list[assignment_index].parts[part_index]['name']
        print("Uploading %s to:\n%s\n    %s" % (notebook_file, assignment_name, part_name))
        
        url_add = f"/assignments/{assignment_id}/parts/{part_id}/release"
        self.PUT(url_add, data)
 
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
    
    def release_part(self, notebook_file, i, j):
        assignment_id = self.assignment_list[i].info["id"]
        part_id = self.assignment_list[i].parts[j]["id"]
        url
        
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
