drop table if exists paper;
create table paper (
  id integer primary key autoincrement,
  url text not null,
  author text,
  author_number integer,
  title text,
  date_submitted real,
  date_extended real,
  abstract text,
  subject text,
  sources text,
  volunteer text,
  discussed integer default 0
);