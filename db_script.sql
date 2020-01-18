show databases;
use  myflaskapp;
create table users(id int(11) auto_increment primary key, name varchar(100),email varchar(100),username varchar(30),password varchar(100), register_date Timestamp default current_timestamp);
show tables;
describe users;
select * from users;
delete from users where id =3;
create table articles (id int auto_increment primary key, title varchar(255),author varchar(100),body TEXT, create_date Timestamp default current_timestamp);
drop table articles;

select * from articles;

