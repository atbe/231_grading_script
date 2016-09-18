import Grader
import os
import sys

class Project:
    """Model of Project object."""

    def __init__(self, root_dir="/user/cse231/Handin/"):
        self._root_dir = root_dir

    @staticmethod
    def validate_projects(grader): #projects, sections, student_list):
        '''Prompt the user for projects (if not specified in arguments) and check validity'''
        if grader._projects == []:
            projects = input("Which project(s) would you like to grade?: ").split(",")
            for index,section in enumerate(projects):
                projects[index] = section.strip()
        #In order for a project to be valid, it must be contained in each of the student directories that is being graded (even if the directory is empty)
        #A project name does not need to be an integer
        invalid_projects = []
        dirs_at_root = os.listdir(grader.root_handin_directory)
        for directory in dirs_at_root:
            try:
                if directory.find(Grader.Grader.SECTION_IDENTIFIER) == 0 and int(directory[len(Grader.Grader.SECTION_IDENTIFIER):]) in grader._sections:
                    students_in_section = os.listdir(grader.root_handin_directory + directory)
                    for student in students_in_section:
                        dirs_in_student_folder = os.listdir(grader.root_handin_directory + directory + "/" + student)
                        for index,student_directory in enumerate(dirs_in_student_folder):
                            try: #if it can be converted to an integer then do it (so that 001 is the same as 01 and 1)
                                dirs_in_student_folder[index] = int(student_directory)
                            except Exception as e:
                                print("ERROR: {}".format(e))
                                pass
                        for project in projects:
                            if int(project) not in dirs_in_student_folder:
                                invalid_projects.append(str(project))
            except Exception as e:
                print("ERROR: {}".format(e))
                pass
        for student in grader._students:
            students_section = ""
            for directory in dirs_at_root:
                 if directory.find(Grader.Grader.SECTION_IDENTIFIER) == 0:
                     students_in_section = os.listdir(grader.root_handin_directory + directory)
                     if student in students_in_section:
                         students_section = directory
                         break
            dirs_in_student_folder = os.listdir(grader.root_handin_directory + directory + "/" + student)

            good_projects = []

            # print("DEBUG dirs_in_student_folder = {}".format(dirs_in_student_folder))
            for index,student_directory in enumerate(dirs_in_student_folder):
                try: #if it can be converted to an integer then do it (so that 001 is the same as 01 and 1)
                    # print("DEBUG: {}".format(student_directory))
                    dirs_in_student_folder[index] = int(student_directory)
                except Exception as e:
                    print("ERROR: {}".format(e))
                    pass
                for project in projects:
                    try:
                        if int(project) in dirs_in_student_folder:
                            good_projects.append(str(project))
                    except Exception as e:
                        print("ERROR: {}".format(e))
                        if project in dirs_in_student_folder:
                            good_projects.append(project)
            for P in projects:
                if P not in good_projects:
                    invalid_projects.append(P)

        valid_projects = []
        for project in projects:
            if project not in invalid_projects:
                valid_projects.append(project)
            else:
                print("\nProject " + project + " is invalid.")
        if valid_projects == []:
            print("\nNo valid projects detected.  Program will now halt.\n")
            exit()

        print("DEBUG valid_projects = ",valid_projects)
        return valid_projects
