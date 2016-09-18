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
    def validate_student(student):
        """Ensure that a student is in the file system.  Can handle partial
        names.  Returns multiple students if there are multiple matches"""
        dirs_at_root = os.listdir(Grader.ROOT_HANDIN_DIRECTORY)
        student_found = 0
        student_list = []
        for directory in dirs_at_root:
            if directory.find(Grader.SECTION_IDENTIFIER) == 0:
                students_in_section = os.listdir(Grader.ROOT_HANDIN_DIRECTORY + directory)
                for full_student_name in students_in_section:
                    if full_student_name.find(student) == 0:
                        student_list.append(full_student_name)
        if student_list == []:
            print("\nNo student with netID pattern \""+student+"\" could be found.  Program will now halt.\n")
            exit()
        return student_list
