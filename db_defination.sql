create database 23bai0063;
use 23bai0063;
create table stock(
stock_id varchar(100) primary key ,company_name varchar(100)NOT NULL, 
industry varchar(100),
sector varchar(100),
exchange varchar(100),
currency varchar(100));
select * from stock;
create table users(
last_name varchar(100),
user_name varchar(100) not null,
email varchar(100),
user_id int primary key ,
firstname varchar(100),password_Hash int 
);
create table user_stocklist(
userstocklistid varchar(100) primary key, added_date date not null,
);
desc stock;
desc users;