import os
import Grader

class Section:
    """Model a section object."""

    @staticmethod
    def validate_sections(grader):
        '''Prompt the user for sections (if not specified in arguments) and check validity of sections'''
        if grader._sections == [] and grader._students == []:
            sections = input("Which section(s) would you like to grade?: ").split(",")
            for index,section in enumerate(sections):
                sections[index] = section.strip()
        #It is assumed that all section folders will be named with the following format: "SECTION_IDENTIFIERxxx" where xxx is an integer section number
        #This script will allow users to simply type the number of their section instead of the full name of the folder
        dirs_at_root = os.listdir(grader.root_handin_directory)
        valid_section_choices = []
        for directory in dirs_at_root:
            if directory.find(Grader.Grader.SECTION_IDENTIFIER) == 0:
                sNumber = directory[len(Grader.Grader.SECTION_IDENTIFIER):]
                try:
                    sNumber = int(sNumber)
                    valid_section_choices.append(sNumber)
                except Exception:
                    pass
        valid_sections = []
        for section in grader._sections:
            try:
                section = int(section)
                if section not in valid_section_choices:
                    raise Exception("invalid section")
                valid_sections.append(section)
            except Exception:
                if(section != ""):
                    print("\nSection",section,"is invalid.\n")
        if valid_sections == [] and grader._students == []:
            print("\nNo valid sections detected.  Program will now halt.\n")
            exit()
        #remove duplicates
        valid_sections = list(set(valid_sections))

        return valid_sections
