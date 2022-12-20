from glob import glob
from paddleocr import PaddleOCR
import os
import spacy
import re
import datetime
from PyPDF2 import PdfFileReader, PdfFileWriter
from glob import glob
from paddleocr import PaddleOCR
import os
import spacy
import re
import datetime
from PyPDF2 import PdfFileReader, PdfFileWriter


os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
ocr = PaddleOCR(use_angle_cls=True, lang='en')
t = os.getcwd() + '\\Disable_pdf_examples\\'
from glob import glob
from paddleocr import PaddleOCR
import os
import spacy
import re
import datetime
from PyPDF2 import PdfFileReader, PdfFileWriter


os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
ocr = PaddleOCR(use_angle_cls=True, lang='en')
#t = os.getcwd() + '\\Disable_pdf_examples\\'
t="C:\\Users\\amit.patel\\PycharmProjects\\JsonKeywordsFinding\\PDF_TO_JSON\\Disabled_Blue_Badge_Holder_14122022\\"
model_address = "C:\\Users\\amit.patel\\PycharmProjects\\JsonKeywordsFinding\\model-best"
nlp_ner = spacy.load(model_address)


# ***********************************************************
# Function accepts a list of text cases and their respective
# results as parameters and writes the results into text file
# ***********************************************************
def write_results(filenames, text_cases, results, counts, file):
    try:
        with open(file, 'a') as f:
            f.writelines("***********************************************************\n")
            f.writelines("Total Text cases tested: " + str(len(text_cases)) + "\n")
            f.writelines("Total Valid Text cases : " + str(counts[1]) + "\n")
            f.writelines("Total Text cases having no valid badge id found: " + str(counts[0]) + "\n")
            f.writelines("Total Text cases in which badges were expired: " + str(counts[2]) + "\n")
            f.writelines("Total Text cases in which there were no keywords found: " + str(counts[3]) + "\n")
            f.writelines("***********************************************************\n\n")
            f.writelines("Text cases summary: \n")
            f.writelines("-----------------------------------------------------------\n")
            length = len(text_cases)
            # index = 0
            for i in range(0, length):
                try:
                    f.writelines("Filename: " + filenames[i])
                    f.writelines("\nText case: " + text_cases[i])
                    f.writelines("\nResult: " + str(results[i]))
                    f.writelines("\n***********************************************************\n")
                except:
                    pass
    except Exception as x:
        print(x)

# ******************************************
# Function removes the string from the array
# of addresses accepted as parameter
# ******************************************
def removeString(arr, address):
    pdf = []
    l = len(arr)
    for i in range(0, l):
        pdf.append(arr[i].replace(address, ''))  # Removing address part from the pdf file address

    return pdf

# **********************************************
# Function accepts a badge path as parameter and
# returns its extracted expiry date
# **********************************************
def get_expiry_date(x):

    result = ocr.ocr(x, cls=True)  # Getting results from the paddleocr library functions
    # print(result)
    text = ""

    for idx in range(len(result)):
        res = result[idx]
        for line in res:
            text = text + ' ' + (line[-1][0]).lower()  # Appending all the lines extracted to the text
    dates = re.findall(
        '([1-9]|1[0-9]|2[0-9]|3[0-1]|0[0-9])(.|\/)([1-9]|1[0-2]|0[0-9])(.|\/)(20[0-9][0-9])',
        text)
    dates = [''.join(dates[i]) for i in range(len(dates))]

    length = len(dates)
    date = ""
    if (length == 0) or (
            (text.find('parking') < 0) and (text.find('uk') < 0) and (text.find('card') < 0)) or (
            (text.find('parking') < 0) and (text.find('badge') < 0)):
        date = "No valid expiry date found"
    elif length > 1:
        if (int(dates[-1][-4:]) > int(dates[-2][-4:])):
            date = dates[-1]
        else:
            date = dates[-2]
    elif ('valid from' in text) or ('validfrom' in text):
        date = "No valid expiry date found"
    else:
        date = dates[-1]

    # print(date)

    return date

# **********************************************
# Function extracts all the text from all the
# files and searches for expiry dates from the
# text and returns a list of these expiry dates
# **********************************************
def return_date(x):

    try:
        date = get_expiry_date(x)
        if (date != "") and (date[2] == '/') and (date[5] == '/'):
            # print("Valid")
            # print(date)
            print()
        else:
            date = "No valid expiry date found"

        return date

    except Exception as ex:
        print("***********************************")
        print(ex)
        print("***********************************")

# *********************************************
# Function accepts a text case as parameter and
# returns the attachments of this text case
# *********************************************
def check_attachments(text_case):

    keywords = ['supporting images for this appeal', 'attachments to this appeal', 'attachments for this appeal']
    result = ""

    try:
        txt = text_case
        check = True
        for key in keywords:
            if check and (key in txt.lower()):
                check = False
                index = (txt.lower()).find(key) - 2
                while txt[index] != ' ':
                    index = index - 1
                res = [int(i) for i in txt[index:].split() if i.isdigit()]
                result = str(res)
        if check:
            result = "No attachments found"

        return result

    except Exception as ex:
        print("****************************************")
        print(ex)
        print("****************************************")

# ***********************************************
# Function accepts a date as parameter and checks
# whether it's an expiry date or not and returns
# the respective result
# ***********************************************
def check_expiry(date):

    current_date = datetime.datetime.now()
    check = False
    if int(date[6:]) > current_date.year:
        check = True
    elif int(date[6:]) == current_date.year:
        if int(date[3:5]) > current_date.month:
            check = True
        elif (int(date[3:5]) == current_date.month) and (int(date[0:2]) >= current_date.day):
                check = True

    return check

# ***************************************
# Function validates the text received as
# parameter and returns the valid text
# ***************************************
def return_valid_text(text):

    try:
        if text.find('Appeal Reason') == -1:
            text = ""
        else:
            index = text.find('Appeal Reason') + 13
            while text[index] == ' ':
                index = index + 1
            text = text[index:]
            if text.find('Please Note') > 0:
                p = text.find('Please Note')
                text = text[:p]
    except Exception as ex:
        print(ex)
        text = ""
        pass
    return text

# ******************************************************
# Function creates a new pdf of attachments
# ******************************************************
def write_attachments(inputpdf, attchments_dir_path, x):

    paths = []
    for i in range(1, inputpdf.numPages):
        name = attchments_dir_path + "\\" + 'attachment_' + str(i) + "_" + x.replace(t, '')
        output = PdfFileWriter()
        output.addPage(inputpdf.getPage(i))
        with open(name, "wb") as outputStream:
            output.write(outputStream)
        paths.append(name)

    return paths

# ***********************************************************************
# Function accepts a set of parameters and analysis the different results
# with respect to the data extracted and returns the respective results
# ***********************************************************************
def result_analysis(x, text, total_counts, attachments_dir_path, spans):

    inputpdf = PdfFileReader(open(x, "rb"))
    attachments = check_attachments(text.lower())
    if ('No' in attachments) and (inputpdf.numPages <= 1):  # if there are attachments
        s = "Appeal has no attachments\nKeywords: "
        total_counts[0] = total_counts[0] + 1
    else:
        att_atts = write_attachments(inputpdf, attachments_dir_path, x)
        date = 'No'
        for att in att_atts:
            date = return_date(att)
            if 'No' not in date:
                print(date)
                break
        for att in att_atts:
            os.remove(att)
        if 'No' in date:
            s = "There are attachments but not evidence of a valid id badge\nKeywords: "
            total_counts[0] = total_counts[0] + 1
        else:
            if check_expiry(date):
                s = 'Valid case accepted\nKeywords: '
                total_counts[1] = total_counts[1] + 1
            else:
                s = 'Badge expired - rejected case\nKeywords: '
                total_counts[2] = total_counts[2] + 1

    for key in spans:
        s = s + str(key) + ", "
    s = s[0:len(s) - 2]

    return s, total_counts

# *****************************************
# Function reads the appeal box text and
# writes the extracted text into jsonl file
# *****************************************
def test_model(def_paths):

    print("\n********************************* Model Testing *************************************")

    results = []
    text_cases = []
    total_counts = [0, 0, 0, 0]                # problem, valid, expired, no key
    d = 1
    filenames = []

    try:
        attachments_dir_path = os.getcwd() + '\\Temporary'
        if not os.path.isdir(attachments_dir_path):
            os.makedirs(attachments_dir_path)                # Creating a temporary folder to save attachments

        for x in def_paths:
            if d == 8:
                print()
            print(d)
            print(x)
            text = ""
            result = ocr.ocr(x, cls=True)               # Getting results from the paddleocr library functions
            res = result[0]
            for line in res:
                text = text + ' ' + (line[-1][0])       # Appending all the lines extracted to the text
                # print(line[-1][0])
            if text != "":
                valid_txt = return_valid_text(text)
                if valid_txt == "":
                    valid_txt = text
                doc = nlp_ner(valid_txt)
                spans = doc.spans["sc"]
                case_length = len(spans)
                if case_length > 0:
                    s, total_counts = result_analysis(x, text, total_counts, attachments_dir_path, spans)   # Getting results
                else:
                    s = 'No disable keyword found'
                    total_counts[3] = total_counts[3] + 1

                print(s)
                results.append(s)
                text_cases.append(valid_txt)
                filenames.append(x)

            d = d + 1

        os.rmdir(attachments_dir_path)                  # Deleting temporary folder

        filenames = removeString(filenames, t)

        return results, text_cases, total_counts, filenames

    except Exception as ex:
        print("***********************************")
        print(ex)  # Exception
        print("***********************************")


# *********************************************
# Our main driver function
# *********************************************
def main():

    def_paths = glob(t + '*.pdf')                       # Getting all the pdf files from the directory specified

    results, text_cases, counts, filenames = test_model(def_paths)

    # for i in range(len(text_cases)):
    #     print("***********************************")
    #     print(filenames[i])
    #     print(text_cases[i])
    #     print(results[i])
    #     print("***********************************")

    print(counts)

    write_results(filenames, text_cases, results, counts, 'complete_model_integration1.txt')


# *********************************************
# Calling our main driver function
# *********************************************
main()


# def_paths = glob(t + '*.pdf')                           # Getting all the pdf files from the directory specified
# for d in def_paths:
#     inputpdf = PdfFileReader(open(d, "rb"))
#     att_paths = write_attachments(inputpdf, 'E:\\Upwork\\JsonKeywordsFinding\\Attachments', d)
#     for x in att_paths:
#         date = return_date(x)
#         if 'No' not in date:
#             print(date)
#             break
#     for x in att_paths:
#         os.remove(x)
# model_address = "E:\\Upwork\\JsonKeywordsFinding\\model-last"
# nlp_ner = spacy.load(model_address)
