import os
import Grader

class Student():
    """Model of CSE231 student."""

    def __init__(self, net_id=None, section=None):
        self._net_id = net_id
        self._section = section

    def verify_net_id(self):
        # regex A#######
        #if invalid, try to make valid
        0

    @staticmethod
    def validate_student(grader, student):
        """Ensure that a student is in the file system.  Can handle partial
        names.  Returns multiple students if there are multiple matches"""
        dirs_at_root = os.listdir(grader.root_handin_directory)
        # student_found = 0
        student_list = []
        for directory in dirs_at_root:
            if directory.find(Grader.Grader.SECTION_IDENTIFIER) == 0:
                students_in_section = os.listdir(grader.root_handin_directory + directory)
                for full_student_name in students_in_section:
                    if full_student_name.find(student) == 0:
                        student_list.append(full_student_name)
        if student_list == []:
            print("\nNo student with netID pattern \""+student+"\" could be found.  Program will now halt.\n")
            exit()

        print("Student.py:\t student_list = {}".format(student_list))
        return student_list

    @staticmethod
    def construct_full_student_list(grader):
        '''Break apart sections into lists of students and merge with the students list'''
        students = []
        dirs_at_root = [name for name in os.listdir(grader.root_handin_directory) if os.path.isdir(os.path.join(grader.root_handin_directory, name))]
        print("DEBUG Student.py: dirs_at_root =", dirs_at_root)
        for directory in dirs_at_root:
            try:
                if directory.find(Grader.Grader.SECTION_IDENTIFIER) == 0 and int(directory[len(Grader.Grader.SECTION_IDENTIFIER):]) in grader._sections:
                    students_in_section = os.listdir(grader.root_handin_directory + directory)
                    students += students_in_section
            except Exception as e:
                print("Student.py ERROR: {}".format(e))
                pass
        students = list(set(students))

        return sorted(students)
