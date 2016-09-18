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

import Grader
from Section import Section
from Student import Student
from Project import Project

DEBUG = False

ROOT_HANDIN_DIRECTORY = "/user/cse231/Handin/"        #this should point to the folder containing all of the handin data, filepath should end in a "/" character
SECTION_IDENTIFIER = "Section"                        #the prefix for a section folder
SCORE_SHEET_FILE_STYLE = "*.score"                    #this is the pattern for the file name used to open the score sheet.  Assumes "*" char is student netID
FILES_TO_OPEN = ["*.output","proj*.py"]               #these files will automatically be opened when grading each directory (other than the score sheet)
EDITOR = "gedit"

FILES_TO_OPEN.append(SCORE_SHEET_FILE_STYLE)

def get_argv_dict():
    """Return dict of command line arguments."""
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
    arg_parser.add_argument("-d", "--directory", help="Point to different Handin directory.", default="/user/cse231/Handin/", type=str)

    # parse and return dict
    args = arg_parser.parse_args()
    args_dict = vars(args)
    return args_dict

def printd(*strings):
    """Assist when printing for debug mode only."""
    if DEBUG:
        print("DEBUG\t", ' '.join(map(str, strings)))

def parse_my_args():
    global sections
    # global students
    # global projects

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




if __name__ == "__main__":
   # get args from commands
    argv_dict = get_argv_dict()
    # debug mode if requested
    DEBUG = argv_dict["debug"]
    printd(argv_dict)

    # os.system("clear")

    # WIP
    grader = Grader.Grader(argv_dict["directory"])

    # extra file patterns to search for
    if argv_dict["file"]:
        grader._file_patterns.extend(argv_dict["file"])
        printd("File patterns to open: ", FILES_TO_OPEN)

    # keeping this in there for now
    if argv_dict.get("__run_a_prompt_shell__"):
        prompt_shell(argv_dict["__run_a_prompt_shell__"])

    # file patterns to skip
    if argv_dict["skip"]:
        grader._mode_regrade = False
        printd("mode_regade = {}".format(grader._mode_regrade))

    # mode prompt? still have not read the resulting code
    if argv_dict["prompt"]:
        grader._mode_prompt = True
        Grader.FILES_TO_OPEN.remove(Grader.SCORE_SHEET_FILE_STYLE)
        printd("Files to open: ", Grader.FILES_TO_OPEN)
        printd("mode_prompt = {}".format(grader._mode_prompt))

    # grade student(s) specifically
    if argv_dict["netid"]:
        for net_id in argv_dict["netid"]:
            if DEBUG:
                grader._students.append(net_id)
            else:
                grader._students.append(Student.validate_student(net_id))
        printd("grader._students: {}".format(grader._students))

    # grade section(s) specifically
    if argv_dict["section"]:
        grader._sections.append(argv_dict["section"])
        printd("sections = {}".format(grader._sections))

    # grade specific project
    if argv_dict["project"]:
        grader._projects.append(argv_dict["project"])
        printd("grader._projects = {}".format(grader._projects))

    # show me output before moving on when in debug mode
    if argv_dict["debug"]:
        input("\n\nPress enter when done.")

    # if "__run_a_prompt_shell__" in arg_dict:
        # prompt_shell(arg_dict["__run_a_prompt_shell__"])
        # exit()

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

    # default behaviour
    if argv_dict["section"] is None and argv_dict["netid"] is None:
        grader.default_prompt()
    else:
        printd("section = {} netid = {}". format(argv_dict["section"], argv_dict["netid"]))

    try:
        # validate sections
        grader._sections = Section.validate_sections(grader)
        # validate the projects' directories
        grader._projects = Project.validate_projects(grader)
        # students = full_student_list somehow
        grader._students = Student.construct_full_student_list(grader)
        # begin grading
        printd("Begin grading.")
        grader.grade()
        printd("Finished grading.")

    except EOFError:
        grader.exit_message()
        exit()
