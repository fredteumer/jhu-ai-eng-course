FROM php:8.3-apache

# mysqli is the exact extension the assignment discusses ("MySQLi library").
RUN docker-php-ext-install mysqli \
    && a2enmod rewrite

# Apache serves /var/www/html by default; our source is bind-mounted there.
