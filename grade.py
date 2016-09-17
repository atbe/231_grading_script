#!/usr/bin/env python3

########################################################
###   Grading Script for CSE 231                     ###
###   Built by Cody Littley                          ###
###   First used January 2014                        ###
########################################################

import sys
import os
import time
import argparse

DEBUG = False

ROOT_HANDIN_DIRECTORY = "/user/cse231/Handin/"        #this should point to the folder containing all of the handin data, filepath should end in a "/" character
SECTION_IDENTIFIER = "Section"                        #the prefix for a section folder
SCORE_SHEET_FILE_STYLE = "*.score"                    #this is the pattern for the file name used to open the score sheet.  Assumes "*" char is student netID
FILES_TO_OPEN = ["*.output","proj*.py"]               #these files will automatically be opened when grading each directory (other than the score sheet)
EDITOR = "gedit"

FILES_TO_OPEN.append(SCORE_SHEET_FILE_STYLE)

arg_parser = argparse.ArgumentParser(prog="CSE231 Grading Helper", usage="Assist in the grading of CSE231 projects.")
# cannot grade a section and a student at the same time, yet (menu wip)
section_vs_student_group = arg_parser.add_mutually_exclusive_group()
section_vs_student_group.add_argument("-s", "--section", help="Desired section to grade.", type=int)
section_vs_student_group.add_argument("-n", "--netid", help="Netid of specific student(s) to grade.", type=str, nargs='+')
arg_parser.add_argument("-p", "--project", help="Desired project to grade.", type=str)
arg_parser.add_argument("-f", "--file", help="Open a specific file for grading.", type=str, nargs='+')
arg_parser.add_argument("--debug", help="Put script in debug mode", action="store_true", default=False)
arg_parser.add_argument("-k", "--skip", help="TBD", action="store_true")
arg_parser.add_argument("-r", "--prompt", help="TBD", action="store_true")

args = arg_parser.parse_args()

def printd(*strings):
    if args.debug:
        print("DEBUG\t", ' '.join(map(str, strings)))

def parse_my_args():
    global sections
    # global students
    # global projects

    if args.debug:
        DEBUG = True
    if args.file:
        FILES_TO_OPEN.extend(args.file)
        printd("Files to open: ", FILES_TO_OPEN)

    if args.skip:
        mode_regrade = False
        printd("mode_regade = {}".format(mode_regrade))

    if args.prompt:
        mode_prompt = True
        FILES_TO_OPEN.remove(SCORE_SHEET_FILE_STYLE)
        printd("Files to open: ", FILES_TO_OPEN)
        printd("mode_prompt = {}".format(mode_prompt))

    if args.section is None and args.netid is None:
        default_prompt(students)
    else:
        printd("section = {} netid = {}". format(args.section, args.netid))

    if args.netid:
        for net_id in args.netid:
            students.append(validate_student(net_id)) if not DEBUG else students.append(net_id)
        printd("students: {}".format(students))

    if args.section:
        sections.append(args.section)
        if not DEBUG:
            sections = validate_sections(sections, student)
        printd("sections = {}".format(sections))

    if args.project:
        projects.append(args.project)
        printd("projects = {}".format(projects))

    if args.debug:
        input("\n\nPress enter when done.")

def process_args():
    '''Grab command line arguments'''
    flags_to_catch = ["-h","--help","-s","--section","-p","--project","-n","--netid","-k","--skip","-f","--file","-r","--prompt","__run_a_prompt_shell__"]
    prev_arg = ""
    arg_dict = {}
    for arg in sys.argv:
        if arg in flags_to_catch:
            if arg in arg_dict:
                pass
            else:
                arg_dict[arg] = []
            prev_arg = arg
        elif prev_arg != "":
            arg_dict[prev_arg].append(arg)
    return arg_dict

def validate_sections(sections,students):
    '''Prompt the user for sections (if not specified in arguments) and check validity of sections'''
    if sections == [] and students == []:
        sections = input("Which section(s) would you like to grade?: ").split(",")
        for index,section in enumerate(sections):
            sections[index] = section.strip()
    #It is assumed that all section folders will be named with the following format: "SECTION_IDENTIFIERxxx" where xxx is an integer section number
    #This script will allow users to simply type the number of their section instead of the full name of the folder
    dirs_at_root = os.listdir(ROOT_HANDIN_DIRECTORY)
    valid_section_choices = []
    for directory in dirs_at_root:
        if directory.find(SECTION_IDENTIFIER) == 0:
            sNumber = directory[len(SECTION_IDENTIFIER):]
            try:
                sNumber = int(sNumber)
                valid_section_choices.append(sNumber)
            except Exception:
                pass
    valid_sections = []
    for section in sections:
        try:
            section = int(section)
            if section not in valid_section_choices:
                raise Exception("invalid section")
            valid_sections.append(section)
        except Exception:
            if(section != ""):
                print("\nSection",section,"is invalid.\n")
    if valid_sections == [] and students == []:
        print("\nNo valid sections detected.  Program will now halt.\n")
        exit()
    #remove duplicates
    valid_sections = list(set(valid_sections))
    return valid_sections

def validate_projects(projects,sections,student_list):
    '''Prompt the user for projects (if not specified in arguments) and check validity'''
    if projects == []:
        projects = input("Which project(s) would you like to grade?: ").split(",")
        for index,section in enumerate(projects):
            projects[index] = section.strip()
    #In order for a project to be valid, it must be contained in each of the student directories that is being graded (even if the directory is empty)
    #A project name does not need to be an integer
    invalid_projects = []
    dirs_at_root = os.listdir(ROOT_HANDIN_DIRECTORY)
    for directory in dirs_at_root:
        try:
            if directory.find(SECTION_IDENTIFIER) == 0 and int(directory[len(SECTION_IDENTIFIER):]) in sections:
                students_in_section = os.listdir(ROOT_HANDIN_DIRECTORY + directory)
                for student in students_in_section:
                    dirs_in_student_folder = os.listdir(ROOT_HANDIN_DIRECTORY + directory + "/" + student)
                    for index,student_directory in enumerate(dirs_in_student_folder):
                        try: #if it can be converted to an integer then do it (so that 001 is the same as 01 and 1)
                            dirs_in_student_folder[index] = int(student_directory)
                        except Exception:
                            pass
                    for project in projects:
                        if int(project) not in dirs_in_student_folder:
                            invalid_projects.append(str(project))
        except Exception:
            pass
    for student in student_list:
        students_section = ""
        for directory in dirs_at_root:
             if directory.find(SECTION_IDENTIFIER) == 0:
                 students_in_section = os.listdir(ROOT_HANDIN_DIRECTORY + directory)
                 if student in students_in_section:
                     students_section = directory
                     break
        dirs_in_student_folder = os.listdir(ROOT_HANDIN_DIRECTORY + directory + "/" + student)

        good_projects = []

        for index,student_directory in enumerate(dirs_in_student_folder):
            try: #if it can be converted to an integer then do it (so that 001 is the same as 01 and 1)
                dirs_in_student_folder[index] = int(student_directory)
            except Exception:
                pass
            for project in projects:
                try:
                    if int(project) in dirs_in_student_folder:
                        good_projects.append(str(project))
                except Exception:
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
    return valid_projects

def validate_student(student):
    '''Ensure that a student is in the file system.  Can handle partial names.  Returns multiple students if there are multiple matches'''
    dirs_at_root = os.listdir(ROOT_HANDIN_DIRECTORY)
    student_found = 0
    student_list = []
    for directory in dirs_at_root:
        if directory.find(SECTION_IDENTIFIER) == 0:
            students_in_section = os.listdir(ROOT_HANDIN_DIRECTORY + directory)
            for full_student_name in students_in_section:
                if full_student_name.find(student) == 0:
                    student_list.append(full_student_name)
    if student_list == []:
        print("\nNo student with netID pattern \""+student+"\" could be found.  Program will now halt.\n")
        exit()
    return student_list

def construct_full_student_list(sections,students):
    '''Break apart sections into lists of students and merge with the students list'''
    dirs_at_root = os.listdir(ROOT_HANDIN_DIRECTORY)
    for directory in dirs_at_root:
        try:
            if directory.find(SECTION_IDENTIFIER) == 0 and int(directory[len(SECTION_IDENTIFIER):]) in sections:
                students_in_section = os.listdir(ROOT_HANDIN_DIRECTORY + directory)
                students += students_in_section
        except:
            pass
    students = list(set(students))
    return sorted(students)

def check_for_errors(section,student,project):
    '''Do a sanity check on the scores entered by the grader'''

    score_sheet = SCORE_SHEET_FILE_STYLE
    if SCORE_SHEET_FILE_STYLE.find("*") != -1:
        score_sheet = score_sheet.replace("*",student)

    grade_file = open(ROOT_HANDIN_DIRECTORY+section+"/"+student+"/"+project+"/"+score_sheet,"r")
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
                except Exception:
                    alarms.append("Could not parse score!")
                    state = -1
        elif state == 2:
            score_start_pos = line.find("__")
            score_end_pos = line[score_start_pos+2:].find("__") + score_start_pos + 2
            try:
                value = int(line[score_start_pos+2:score_end_pos])
                sum_of_parts += value
            except Exception:
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
        os.system("echo \"$USER\" > "+ROOT_HANDIN_DIRECTORY+section+"/"+student+"/"+project+"/.graded")
        return
    print("\n========================= Score sheet sanity check! =========================\n")
    for alarm in alarms:
        print(alarm+"\n")
    user_input = input("To ignore this warning, type \"i\".\nTo re-examine the score sheet, type anything else: ")
    if user_input == "i":
        #make a hidden log file
        #lets program know if file is already graded, can be used to track if a project has been graded
        #look at time stamp to see when it was graded if needed, also track which user completed the grading
        os.system("echo \"$USER\" > "+ROOT_HANDIN_DIRECTORY+section+"/"+student+"/"+project+"/.graded")
        return
    else:

        score_sheet = SCORE_SHEET_FILE_STYLE
        if SCORE_SHEET_FILE_STYLE.find("*") != -1:
            score_sheet = score_sheet.replace("*",student)

        os.system(EDITOR+" "+ROOT_HANDIN_DIRECTORY+section+"/"+student+"/"+project+"/"+score_sheet+" &")
        input("\nPress enter to continue\n")
        check_for_errors(section,student,project)

def prompt(section,student,project):
    '''Called if the optional "--prompt" flag is detected.  Allows the grader to enter scores and then adds them together.'''

    command = "python3 grade.py __run_a_prompt_shell__ " + section + " " + student + " " + project
    os.system("gnome-terminal -x " + command)

def prompt_shell(args):
    '''This is a special function that is run as a stand alone program in another window.  It extends the prompt function.'''

    section = args[0]
    student = args[1]
    project = args[2]
    print("Now grading "+student+"'s solution to project "+project+":\n")
    print("To use a previously entered score, press enter.")
    print("To go \"up\" to re-grade a category, type the letter \"u\" instead of a number.\n")
    score_sheet = SCORE_SHEET_FILE_STYLE
    if SCORE_SHEET_FILE_STYLE.find("*") != -1:
        score_sheet = score_sheet.replace("*",student)
    score_file = open(ROOT_HANDIN_DIRECTORY+section+"/"+student+"/"+project+"/"+score_sheet,"r")
    score_file_list = []
    for line in score_file:
        score_file_list.append(line)
    score_file.close()
    primary_score_line = -1
    lines_with_scores = []
    actual_scores = []
    comments = len(score_file_list) -1
    for linum,line in enumerate(score_file_list):
        if line.find("Score: __") != -1:
            primary_score_line = linum
        elif line.strip().find("__") == 0:
            lines_with_scores.append(linum)
        elif line.strip().find("TA Comments") == 0:
            lines_with_scores.append(linum)
            break
    if linum == -1:
        exit()
    for line in lines_with_scores[:-1]:
        actual_scores.append(None)
    score_index = 0
    while(score_index < len(lines_with_scores)):
        if score_index == len(lines_with_scores)- 1:
            theSum = 0
            for s in actual_scores:
                theSum += s
            if int(theSum) == theSum:
                theSum = int(theSum)
            begin = score_file_list[primary_score_line].find("Score: __")
            end = score_file_list[primary_score_line].find("__",begin+len("Score: __"))
            score_file_list[primary_score_line] = score_file_list[primary_score_line][:begin+len("Score: __")] + str(theSum) + score_file_list[primary_score_line][end:]
            break
        print(score_file_list[lines_with_scores[score_index]])
        for description in range(lines_with_scores[score_index]+1,lines_with_scores[score_index+1]):
            if score_file_list[description].strip() != "" and score_file_list[description].strip() != "\n":
                print(score_file_list[description].replace("\n",""))
        print()
        grade_value = input("Enter new grade: ")
        print()
        begin = score_file_list[lines_with_scores[score_index]].find("__")
        end = score_file_list[lines_with_scores[score_index]].find("__",begin+2)
        if grade_value == "":
            try:
                actual_scores[score_index] = float(score_file_list[lines_with_scores[score_index]][begin+2:end])
            except Exception:
                actual_scores[score_index] = 0
        elif grade_value == "u":
            score_index -= 1
            continue
        else:
            try:
                actual_scores[score_index] = (float(grade_value))
            except Exception:
                print("Error: invalid input\n")
                continue
            score_file_list[lines_with_scores[score_index]] = score_file_list[lines_with_scores[score_index]][:begin+2] + grade_value + score_file_list[lines_with_scores[score_index]][end:]
        score_index += 1
    score_file = open(ROOT_HANDIN_DIRECTORY+section+"/"+student+"/"+project+"/"+score_sheet,"w")
    for line in score_file_list:
        score_file.write(line)
    score_file.close()
    score_sheet = SCORE_SHEET_FILE_STYLE
    if SCORE_SHEET_FILE_STYLE.find("*") != -1:
        score_sheet = score_sheet.replace("*",student)
    os.system(EDITOR+" "+ROOT_HANDIN_DIRECTORY+section+"/"+student+"/"+project+"/"+score_sheet+" &")
    print("<<< This window will automatically close >>>")
    time.sleep(5) #to ensure that the grade sheet has enough time to be opened
    exit()

def grade(students,projects,mode_regrade,mode_prompt):
    '''Step through the projects and students and allow them to be graded'''
    for project in projects:
        for student in students:
            os.system("clear")

            dirs_at_root = os.listdir(ROOT_HANDIN_DIRECTORY)
            section = ""
            for directory in dirs_at_root:
                if directory.find(SECTION_IDENTIFIER) != 0:
                    continue
                try:
                    students_in_section = os.listdir(ROOT_HANDIN_DIRECTORY+directory)
                except Exception:
                    continue
                if student in students_in_section:
                    section = directory
            #ensure that the proper project name is used, project 1 might actually be listed as project 01 or 001
            project = str(project)
            available_projects = os.listdir(ROOT_HANDIN_DIRECTORY+section+"/"+student)
            zeros = 0
            while project not in available_projects and zeros <= 3:
                zeros += 1
                project = "0"+project

            student_project_files = os.listdir(ROOT_HANDIN_DIRECTORY+section+"/"+student+"/"+project)
            if ".graded" in student_project_files:
                if mode_regrade == True:
                    user_response = input("Re-Grade project "+str(project)+" for "+student+"? (y/n): ")
                    if user_response == "n":
                        continue
                elif mode_regrade == False:
                    continue
            else:
                user_response = input("Grade project "+str(project)+" for "+student+"? (y/n): ")
                if user_response == "n":
                        continue

            #actually start the grading

            for file_to_open in FILES_TO_OPEN:
                os.system(EDITOR+" "+ROOT_HANDIN_DIRECTORY+section+"/"+student+"/"+project+"/"+file_to_open+" &")

            if mode_prompt:
                prompt(section,student,project)

            print()
            for f in os.listdir(ROOT_HANDIN_DIRECTORY+section+"/"+student+"/"+project):
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
                    check_for_errors(section,student,project)
                    exit_message()
                    exit()
                elif user_input == "c":
                    check_for_errors(section,student,project)
                    break
                elif user_input == "ls":
                    print()
                    for f in os.listdir(ROOT_HANDIN_DIRECTORY+section+"/"+student+"/"+project):
                        if f[0] != ".":
                            print(f)
                    print()

                elif user_input.find("run") == 0:
                    try:
                        command = "python3 -i "+ROOT_HANDIN_DIRECTORY+section+"/"+student+"/"+project+"/"+" ".join(user_input.split()[1:])
                        os.system("gnome-terminal --working-directory="+ROOT_HANDIN_DIRECTORY+section+"/"+student+"/"+project+" -x "+command)

                    except Exception as e:
                        print("Could not run program")

                elif user_input.find("open") == 0:
                    command = user_input.split()
                    os.system(EDITOR+" "+ROOT_HANDIN_DIRECTORY+section+"/"+student+"/"+project+"/"+" ".join(command[1:])+" &")
                else:
                    print("\nTo run a program-----------------\"run PROGRAM_NAME [arguments]\"")
                    print("To open a file-------------------\"open FILE_NAME\"")
                    print("To continue----------------------\"c\"")
                    print("To quit--------------------------\"q\"\n")
    exit_message()

def exit_message():
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

def default_prompt(students):
    user_selection = input("\nWould you like to grade multiple students? (y/n): ")
    if(user_selection.lower() == "n"):
        student_to_grade = input("What is the netID of the student you would like to grade?: ")
        students += validate_student(student_to_grade)

if __name__ == "__main__":
    try:
        os.system("clear")

        arg_dict = process_args()
        mode_regrade = True
        mode_prompt = False
        sections = []
        students = []
        projects = []
        netIDs = []

        if "__run_a_prompt_shell__" in arg_dict:
            prompt_shell(arg_dict["__run_a_prompt_shell__"])
            exit()

        #because art
        print(" ".join(sys.argv))
        print("                                                        ")
        print("                            o                           ")
        print("                    o                o                  ")
        print("                            o                           ")
        print("             o        o            o       o            ")
        print("                                                        ")
        print("           \_O__o                       o__O_/          ")
        print("             |                             |            ")
        print("            / )                           ( \           ")
        print("     +=============================================+    ")
        print("     |           CSE 231 Grading Script            |    ")
        print("                                                        ")

        ####################
        #   Configuration  #
        ####################

        parse_my_args()

        # if "-f" in arg_dict or "--file" in arg_dict:
            # try:
                # FILES_TO_OPEN += arg_dict["-f"]
            # except Exception:
                # pass
            # try:
                # FILES_TO_OPEN += arg_dict["--file"]
            # except Exception:
                # pass

        # if "-k" in arg_dict or "--skip" in arg_dict:
            # mode_regrade = False

        # if "-r" in arg_dict or "--prompt" in arg_dict:
            # mode_prompt = True
            # FILES_TO_OPEN.remove(SCORE_SHEET_FILE_STYLE)

        # if "-s" not in arg_dict and "--section" not in arg_dict and "-n" not in arg_dict and "--netid" not in arg_dict:
            # default_prompt(students)

        # if "-n" in arg_dict or "--netid" in arg_dict:
            # nedIDs_to_add = []
            # try:
                # nedIDs_to_add += arg_dict["-n"]
            # except Exception:
                # pass
            # try:
                # nedIDs_to_add += arg_dict["--netid"]
            # except Exception:
                # pass
            # for netID in nedIDs_to_add:
                # students += validate_student(netID)

        # if "-s" in arg_dict or "--section" in arg_dict:
            # try:
                # sections += arg_dict["-s"]
            # except Exception:
                # pass
            # try:
                # sections += arg_dict["--section"]
            # except Exception:
                # pass
        # sections = validate_sections(sections,students)

        # if "-p" in arg_dict or "--project" in arg_dict:
            # try:
                # projects += arg_dict["-p"]
            # except Exception:
                # pass
            # try:
                # projects += arg_dict["--projects"]
            # except Exception:
                # pass

        projects = validate_projects(projects,sections,students)

        students = construct_full_student_list(sections,students)

        grade(students,projects,mode_regrade,mode_prompt)

    except EOFError:
        exit_message()
        exit()
