CREATE DATABASE 23bai0063;
USE 23bai0063;
CREATE TABLE stock (
    stock_id VARCHAR(100) PRIMARY KEY,
    company_name VARCHAR(100) NOT NULL,
    industry VARCHAR(100),
    sector VARCHAR(100),
    exchange VARCHAR(100),
    currency VARCHAR(100)
) ENGINE=InnoDB;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    PasswordHash VARCHAR(255) NOT NULL,
    firstname VARCHAR(100),
    lastname VARCHAR(100),
    registration_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;
CREATE TABLE historical_prices (
    price_id INT AUTO_INCREMENT PRIMARY KEY,
    stock_id VARCHAR(100) NOT NULL,
    price_date DATE NOT NULL,
    open_price DECIMAL(12, 4),
    high_price DECIMAL(12, 4),
    low_price DECIMAL(12, 4),
    close_price DECIMAL(12, 4) NOT NULL,
    volume BIGINT,
    UNIQUE KEY unique_stock_date (stock_id, price_date),
    CONSTRAINT fk_historical_prices_stock
        FOREIGN KEY (stock_id)
        REFERENCES stock(stock_id)
        ON DELETE RESTRICT
) ENGINE=InnoDB;
CREATE TABLE user_stocklist (
    userstocklistid INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    stock_id VARCHAR(100) NOT NULL,
    added_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_user_stock (user_id, stock_id),
    CONSTRAINT fk_list_to_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_list_to_stock
        FOREIGN KEY (stock_id)
        REFERENCES stock(stock_id)
        ON DELETE CASCADE
) ENGINE=InnoDB;
SHOW TABLES;
