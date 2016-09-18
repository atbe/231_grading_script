import os
from Student import Student

class Grader():
    """Grader objects regulate grading process'."""

    SECTION_IDENTIFIER = "Section"                        #the prefix for a section folder
    SCORE_SHEET_FILE_STYLE = "*.score"                    #this is the pattern for the file name used to open the score sheet.  Assumes "*" char is student netID
    EDITOR = "gedit"

    def __init__(self, root_handin_directory="/user/cse231/Handin/"):
        self.root_handin_directory = root_handin_directory
        self._students = []
        self._sections = []
        self._projects = []
        self._netids = []
        self._file_patterns = ["*.output","proj*.py"]
        self._mode_regrade = True
        self._mode_prompt = False

    def __str__(self):
        return "Students = {}\nSections = {}\nProjects = {}\nNet-ID's = {}\nHandin = {}\nFile Patterns = {}".format(self._students, self._sections,
                self._projects, self._netids, self.root_handin_directory, self._file_patterns)

    def default_prompt(self):
        user_selection = input("\nWould you like to grade multiple students? (y/n): ")
        if (user_selection.lower() == "n"):
            student_to_grade = input("What is the netID of the student you would like to grade?: ")
            section_of_student = input("What section is {} in?: ".format(student_to_grade))
            self._sections.append(section_of_student)
            self._students += Student.validate_student(self, student_to_grade)

    def grade(self):
        '''Step through the projects and _students and allow them to be graded'''

        print(self)

        for project in self._projects:
            for student in self._students:
                os.system("clear")

                dirs_at_root = os.listdir(self.root_handin_directory)
                section = ""
                for directory in dirs_at_root:
                    if directory.find(Grader.SECTION_IDENTIFIER) != 0:
                        continue
                    try:
                        students_in_section = os.listdir(self.root_handin_directory+directory)
                    except Exception:
                        continue
                    if student in students_in_section:
                        section = directory
                #ensure that the proper project name is used, project 1 might actually be listed as project 01 or 001
                project = str(project)
                available_projects = os.listdir(self.root_handin_directory+section+"/"+student)
                zeros = 0
                while project not in available_projects and zeros <= 3:
                    zeros += 1
                    project = "0"+project

                student_project_files = os.listdir(self.root_handin_directory+section+"/"+student+"/"+project)
                if ".graded" in student_project_files:
                    if self._mode_regrade:
                        user_response = input("Re-Grade project "+str(project)+" for "+student+"? (y/n): ")
                        if user_response == "n":
                            continue
                    elif self._mode_regrade:
                        continue
                else:
                    user_response = input("Grade project "+str(project)+" for "+student+"? (y/n): ")
                    if user_response == "n":
                            continue

                #actually start the grading

                for file_to_open in self._file_patterns:
                    os.system(self.EDITOR+" "+self.root_handin_directory+section+"/"+student+"/"+project+"/"+file_to_open+" &")

                if self._mode_prompt:
                    self.prompt(section,student,project)

                print()
                for f in os.listdir(self.root_handin_directory+section+"/"+student+"/"+project):
                    if f[0] != ".":
                        print(f)
                print()

                print("To run a program-----------------\"run PROGRAM_NAME [arguments]\"")
                print("To list files--------------------\"ls\"")
                print("To open a file-------------------\"open FILE_NAME\"")
                print("To continue----------------------\"c\"")
                print("To quit--------------------------\"q\"\n")

                while(True):

                    user_input = input("--> ")
                    if user_input == "q":
                        self.check_for_errors(section,student,project)
                        self.exit_message()
                        exit()
                    elif user_input == "c":
                        self.check_for_errors(section,student,project)
                        break
                    elif user_input == "ls":
                        print()
                        for f in os.listdir(self.root_handin_directory+section+"/"+student+"/"+project):
                            if f[0] != ".":
                                print(f)
                        print()

                    elif user_input.find("run") == 0:
                        try:
                            command = "python3 -i "+self.root_handin_directory+section+"/"+student+"/"+project+"/"+" ".join(user_input.split()[1:])
                            os.system("gnome-terminal --working-directory="+self.root_handin_directory+section+"/"+student+"/"+project+" -x "+command)

                        except Exception as e:
                            print("ERROR: {}".format(e))
                            print("Could not run program")

                    elif user_input.find("open") == 0:
                        command = user_input.split()
                        os.system(self.EDITOR+" "+self.root_handin_directory+section+"/"+student+"/"+project+"/"+" ".join(command[1:])+" &")
                    else:
                        print("\nTo run a program-----------------\"run PROGRAM_NAME [arguments]\"")
                        print("To open a file-------------------\"open FILE_NAME\"")
                        print("To continue----------------------\"c\"")
                        print("To quit--------------------------\"q\"\n")
        self.exit_message()


    def check_for_errors(self, section,student,project):
        '''Do a sanity check on the scores entered by the grader'''

        score_sheet = self.SCORE_SHEET_FILE_STYLE
        if self.SCORE_SHEET_FILE_STYLE.find("*") != -1:
            score_sheet = score_sheet.replace("*",student)

        grade_file = open(self.root_handin_directory+section+"/"+student+"/"+project+"/"+score_sheet,"r")
        alarms = []
        max_score = None
        given_score = None
        sum_of_parts = 0
        state = 1
        for line in grade_file:
            line = line.strip()
            if state == 1:
                if line == "":
                    continue
                else:
                    given_score_pos = line.find("Score: __") + len("Score: __")
                    given_score_end = line[given_score_pos:].find("__") + given_score_pos
                    try:
                        max_score = int(line[given_score_end+5:])
                        given_score = int(line[given_score_pos:given_score_end])
                        state = 2
                    except Exception as e:
                        print("ERROR: {}".format(e))
                        alarms.append("Could not parse score!")
                        state = -1
            elif state == 2:
                score_start_pos = line.find("__")
                score_end_pos = line[score_start_pos+2:].find("__") + score_start_pos + 2
                try:
                    value = int(line[score_start_pos+2:score_end_pos])
                    sum_of_parts += value
                except Exception as e:
                    print("ERROR: {}".format(e))
                    pass
        if sum_of_parts != given_score:
            alarms.append("Sum of components do not match the given score.")
        if given_score > max_score:
            alarms.append("The given score is greater than the maximum allowable points.")
        if given_score == 0:
            alarms.append("You have given a Zero for this assignment.")
        if alarms == []:
            #make a hidden log file
            #lets program know if file is already graded, can be used to track if a project has been graded
            #look at time stamp to see when it was graded if needed, also track which user completed the grading
            os.system("echo \"$USER\" > "+self.root_handin_directory+section+"/"+student+"/"+project+"/.graded")
            return
        print("\n========================= Score sheet sanity check! =========================\n")
        for alarm in alarms:
            print(alarm+"\n")
        user_input = input("To ignore this warning, type \"i\".\nTo re-examine the score sheet, type anything else: ")
        if user_input == "i":
            #make a hidden log file
            #lets program know if file is already graded, can be used to track if a project has been graded
            #look at time stamp to see when it was graded if needed, also track which user completed the grading
            os.system("echo \"$USER\" > "+self.root_handin_directory+section+"/"+student+"/"+project+"/.graded")
            return
        else:

            score_sheet = self.SCORE_SHEET_FILE_STYLE
            if self.SCORE_SHEET_FILE_STYLE.find("*") != -1:
                score_sheet = score_sheet.replace("*",student)

            os.system(self.EDITOR+" "+self.root_handin_directory+section+"/"+student+"/"+project+"/"+score_sheet+" &")
            input("\nPress enter to continue\n")
            self.check_for_errors(section,student,project)


    def exit_message(self):
        print("\n")
        print("                        .   *        .       .")
        print("         *      -0-")
        print("            .                .  *       - )-")
        print("         .      *       o       .       *")
        print("   o   save         |")
        print("           your    -O-")
        print("  .            files!        *      .     -0-")
        print("         *  o     .    '       *      .        o")
        print("                .         .        |      *")
        print("     *             *              -O-          .")
        print("           .             *         |     ,")
        print("                  .           o")
        print("          .---.")
        print("    =   _/__~0_\_     .  *            o       '")
        print("   = = (_________)             .")
        print("                   .                        *")
        print("         *               - ) -       *")
        print("                .               .")
        print()


    def prompt(self, section, student, project):
        '''Called if the optional "--prompt" flag is detected.  Allows the grader to enter scores and then adds them together.'''

        command = "python3 grade.py __run_a_prompt_shell__ " + section + " " + student + " " + project
        os.system("gnome-terminal -x " + command)
