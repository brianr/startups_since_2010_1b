create table company (
  id int unsigned not null auto_increment,
  ident varchar(255) not null,
  name varchar(1000),
  category_code varchar(255),
  
  founded_day tinyint,
  founded_month tinyint,
  founded_year smallint,

  total_money_raised varchar(32),
  total_money_raised_int int,

  primary key (id),
  unique key (ident)
) engine=innodb default charset=utf8;

create table funding_round (
  id int unsigned not null auto_increment,
  company_id int unsigned not null,

  day tinyint,
  month tinyint,
  year smallint,
  round_code varchar(32),
  raised_amount int,

  primary key (id),
  foreign key (company_id) references company (id)
) engine=innodb default charset=utf8;

create table variable (
  name varchar(255),
  value_unsigned int unsigned,
  primary key (name)
) engine=innodb default charset=utf8;

insert into variable values ('fetch_company_details', 0);
