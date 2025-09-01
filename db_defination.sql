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
userstocklistid varchar(100) primary key, added_date date not null
);
desc stock;
desc users;
use 23bai0063;
desc stock;
desc users;
alter table users
add  registration_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;
alter table stock
add ticker_symbol VARCHAR(10) NOT NULL UNIQUE,
add  INDEX idx_ticker_symbol (ticker_symbol) ;
CREATE TABLE historical_prices (
    price_id INT AUTO_INCREMENT PRIMARY KEY,
    stock_id varchar(100) NOT NULL,
    price_date DATE NOT NULL,
    open_price DECIMAL(12, 4),
    high_price DECIMAL(12, 4),
    low_price DECIMAL(12, 4),
    close_price DECIMAL(12, 4) NOT NULL,
    volume BIGINT,
    UNIQUE KEY unique_stock_date (stock_id, price_date),
    INDEX idx_stock_id_price_date (stock_id, price_date DESC),
    CONSTRAINT fk_historical_prices_stock
        FOREIGN KEY (stock_id)
        REFERENCES stock(stock_id)
        ON DELETE RESTRICT
        );
desc historical_prices;
ALTER TABLE users MODIFY COLUMN PasswordHash VARCHAR(255) NOT NULL;
ALTER TABLE users MODIFY COLUMN email VARCHAR(100) NOT NULL UNIQUE;
ALTER TABLE users ADD CONSTRAINT username UNIQUE (username);
ALTER TABLE stock DROP COLUMN ticker_symbol;
ALTER TABLE user_stocklist ADD COLUMN user_id INT NOT NULL;
ALTER TABLE user_stocklist ADD COLUMN stock_id VARCHAR(100) NOT NULL;
ALTER TABLE user_stocklist ADD CONSTRAINT fk_list_to_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE;
ALTER TABLE user_stocklist ADD CONSTRAINT fk_list_to_stock FOREIGN KEY (stock_id) REFERENCES stock(stock_id) ON DELETE CASCADE;
ALTER TABLE user_stocklist ADD CONSTRAINT unique_user_stock UNIQUE (user_id, stock_id);
ALTER TABLE user_stocklist DROP PRIMARY KEY;
ALTER TABLE user_stocklist DROP COLUMN userstocklistid;
ALTER TABLE user_stocklist ADD COLUMN userstocklistid INT AUTO_INCREMENT PRIMARY KEY FIRST;
ALTER TABLE user_stocklist MODIFY COLUMN added_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;
desc users;
desc stock;
desc user_stocklist;
SELECT * FROM stock;
-- This should show all 5 stocks you loaded.
SELECT COUNT(*) FROM historical_prices;
-- This should now show a very large number (e.g., 30,000+).

DESCRIBE users;
ALTER TABLE users MODIFY COLUMN user_id INT AUTO_INCREMENT;
ALTER TABLE user_stocklist DROP FOREIGN KEY fk_list_to_user;
ALTER TABLE users MODIFY COLUMN user_id INT AUTO_INCREMENT;
ALTER TABLE user_stocklist ADD CONSTRAINT fk_list_to_user
FOREIGN KEY (user_id) REFERENCES users(user_id)
ON DELETE CASCADE;
SELECT * FROM users;
SELECT * FROM user_stocklist;