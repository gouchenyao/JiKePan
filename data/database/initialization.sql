drop table if exists students;
create table students (
  student_id text not null primary key,
  password text not null
);

drop table if exists courses;
create table courses (
  course_id text not null primary key,
  course_name text not null,
  teacher_name text not null,
  course_schedule text not null
);

drop table if exists students_courses;
create table students_courses (
  course_id text not null,
  student_id text not null,
  primary key(course_id, student_id)
);

drop table if exists courses_files;
create table courses_files (
  file_name text not null primary key,
  course_id text not null,
  save_time text not null
);