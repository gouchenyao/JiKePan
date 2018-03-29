import os
import re

from bs4 import BeautifulSoup

from app import app


def timetable_single_parser(html_doc):
    with app.app_context():
        soup = BeautifulSoup(html_doc, 'html.parser')
        courses_id_set = set()
        re_course_id = re.compile(r'[0-9A-Z]{8}')

        tds = soup.find(id="manualArrangeCourseTable").find_all('td')
        for td in tds:
            if td.has_attr('title'):
                for content in td.contents:
                    course_id = re_course_id.search(str(content))
                    if course_id:
                        courses_id_set.add(course_id.group(0))

        return list(courses_id_set)


def timetable_all_parser(html_doc):
    with app.app_context():
        soup = BeautifulSoup(html_doc, 'html.parser')

        teachers_name_set = set()
        courses_list = list()
        course_id = str()
        course_name = str()
        teacher_name = str()
        course_schedule = str()

        trs = soup.find_all('tr')

        for tr in trs:
            tds = tr.find_all('td')
            
            if course_id == tds[0].contents[0]:
                teachers_name_set.add(tds[6].contents[0])

            else:
                if course_id != '':
                    teacher_name = ''
                    for single_teacher_name in teachers_name_set:
                        teacher_name += single_teacher_name + ' | '
                    teacher_name = teacher_name.rstrip(' | ')
                    courses_list.append([course_id, course_name, teacher_name ,course_schedule])
                    teachers_name_set.clear()

                teachers_name_set.add(tds[6].contents[0])
                course_id = tds[0].contents[0]
                course_name = tds[1].contents[0]
                course_schedule = tds[10].contents[0]

        if course_id != '':
            teacher_name = ''
            for single_teacher_name in teachers_name_set:
                teacher_name += single_teacher_name + ' | '
            teacher_name = teacher_name.rstrip(' | ')
            courses_list.append([course_id, course_name, teacher_name ,course_schedule])
        
        print('添加全校课程{}个！'.format(len(courses_list)))
        return courses_list


if __name__ == '__main__':
    with open('./course tables/all_courses.txt', mode='r', encoding='utf-8') as html_all_courses:
        timetable_all_parser(html_all_courses)
    with open('./course tables/single_courses .txt', mode = 'r', encoding = 'utf-8') as html_single_courses:
        timetable_single_parser(html_single_courses)